# Leaderboard & Ranking System HLD

A **Leaderboard System** is a classic High-Level Design problem that centers around the **Top K problem**. The core challenge is balancing high-write throughput (constant score updates) with low-latency read requirements (fetching the top 100 players or a specific user's rank) across millions of users.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Update Score**: Update a player's score in real-time.
*   **Get Top K**: Retrieve the top $K$ players (e.g., Top 10, Top 100) with their scores.
*   **Get User Rank**: Retrieve the current rank and score of a specific user.
*   **Time-based Leaderboards**: Support different time windows (Daily, Weekly, All-time).

### Non-Functional Requirements
*   **Low Latency**: Getting the Top K or a user's rank must be near-instantaneous (< 100ms).
*   **High Scalability**: Must handle millions of users and high QPS (queries per second) during peak events.
*   **High Availability**: The leaderboard should be available even if some nodes fail.
*   **Eventual Consistency**: For millions of players, absolute real-time precision for rank #1,000,001 is less critical than system availability.

### Scale Assumptions
| Metric | Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | 10 Million |
| **Write QPS (Score Updates)** | 100,000 / sec |
| **Read QPS (Top K / User Rank)** | 1,000,000 / sec |
| **Data Volume** | $10\text{M users} \times (8\text{ bytes ID} + 8\text{ bytes Score}) \approx 160\text{ MB}$ per leaderboard |

---

## 2. High-Level System Architecture

The system follows a **Write-Heavy, Read-Intensive** pattern. To achieve $O(\log N)$ performance for both updates and rank retrieval, we move the primary computation from a relational database to an in-memory data structure.

### Architecture Components
1.  **API Gateway**: Handles authentication, rate limiting, and request routing.
2.  **Leaderboard Service**: The core business logic layer that interacts with the cache and database.
3.  **Redis (Sorted Sets)**: The primary engine for ranking. Redis `ZSet` uses a combination of a **Hash Table** and a **Skip List** to provide efficient ranking.
4.  **Message Queue (Kafka)**: Decouples the real-time ranking update from the permanent storage update to ensure write durability without blocking the user.
5.  **Database (PostgreSQL/Cassandra)**: Acts as the source of truth for persistent storage and historical audits.

### The Write & Read Path
*   **Write Path**: `User` $\rightarrow$ `API` $\rightarrow$ `Leaderboard Service` $\rightarrow$ `Redis (ZADD)` $\rightarrow$ `Kafka` $\rightarrow$ `DB`.
*   **Read Path (Top K)**: `User` $\rightarrow$ `API` $\rightarrow$ `Leaderboard Service` $\rightarrow$ `Redis (ZREVRANGE)`.
*   **Read Path (User Rank)**: `User` $\rightarrow$ `API` $\rightarrow$ `Leaderboard Service` $\rightarrow$ `Redis (ZREVRANK)`.

---

## 3. Key HLD Concepts & Component Design

### The Core Engine: Redis Sorted Sets (ZSet)
The most critical design choice is using Redis **Sorted Sets**. A ZSet stores a mapping of `member` $\rightarrow$ `score`. 

*   **Internal Structure**: Redis implements ZSets using a **Skip List** and a **Hash Map**.
    *   **Hash Map**: Provides $O(1)$ access to a user's score.
    *   **Skip List**: A probabilistic data structure that allows $\log N$ search, insertion, and deletion, while keeping elements sorted. This allows the system to "jump" over large sections of the list to find a rank.

### Scaling the Leaderboard (Sharding Strategies)
When the number of users exceeds the memory of a single Redis node or the QPS exceeds the CPU limit, we must shard.

#### Strategy A: Fixed-Range Sharding (Score-based)
Split users into buckets based on score ranges (e.g., 0-1000, 1001-2000).
*   **Pros**: Easy to fetch the absolute Top K (just query the highest shard).
*   **Cons**: **Hotspots**. Most users cluster in the lower ranges, while a few "whales" saturate the top shard.

#### Strategy B: User-ID Sharding (Hash-based)
Partition users across $N$ shards using `hash(userId) % N`.
*   **Pros**: Even distribution of load.
*   **Cons**: To get the global Top K, the service must query **all $N$ shards**, retrieve the top $K$ from each, and then merge-sort them in the application layer.
    *   *Complexity*: $O(N \times \log(\text{shard\_size}) + N \cdot K \log(N \cdot K))$.

### Handling Time-based Leaderboards
To implement Daily/Weekly leaderboards, we use **Key Versioning**:
*   `leaderboard:daily:2023-10-27`
*   `leaderboard:weekly:2023-W43`
*   `leaderboard:all_time`

**TTL (Time to Live)**: Daily leaderboards are assigned a TTL of 48 hours to automatically reclaim memory after they are no longer relevant.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Walkthrough: Updating a Score
1.  **Request**: User completes a game level; client sends `userId` and `score_increment`.
2.  **Processing**: The Leaderboard Service calculates the new score.
3.  **Cache Update**: Executes `ZINCRBY leaderboard:all_time <increment> <userId>`. This returns the new score in $O(\log N)$.
4.  **Async Persistence**: The service pushes an event `(userId, newScore, timestamp)` to Kafka.
5.  **Persistence**: A consumer group reads from Kafka and updates the SQL database in batches to reduce IOPS.

### Fault Tolerance & Reliability
*   **Redis Persistence**: Enable **AOF (Append Only File)** and **RDB snapshots** to prevent data loss during crashes.
*   **Replication**: Use **Redis Sentinel** or **Redis Cluster** with primary-replica sets. If the primary fails, a replica is promoted.
*   **Database Recovery**: If Redis is wiped, the system can rebuild the ZSet by scanning the SQL database: `SELECT userId, score FROM users ORDER BY score DESC`.
*   **Kafka Buffer**: If the database is slow or down, Kafka buffers the updates, ensuring no score updates are lost.

---

## 5. Production Trade-offs & Complexity

### Time and Space Complexity
| Operation | Redis ZSet Complexity | SQL (Naive) Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Update Score** | $O(\log N)$ | $O(1)$ (update) | Redis must re-sort the skip list. |
| **Get Top K** | $O(\log N + K)$ | $O(N \log N)$ | SQL requires a full sort unless indexed. |
| **Get User Rank**| $O(\log N)$ | $O(N)$ | SQL requires counting all users with higher scores. |
| **Space** | $O(N)$ | $O(N)$ | Redis requires RAM; SQL uses Disk. |

### Trade-offs: CAP Theorem
*   **Consistency vs. Availability**: This system chooses **Availability and Partition Tolerance (AP)**. 
*   **Reasoning**: In a gaming context, if a user sees they are rank #10 instead of #11 for a few seconds due to replication lag, it is acceptable. Strong consistency (CP) would require distributed locks or synchronous writes to all shards, which would destroy the low-latency requirement.

### Summary Table for Implementation Choice
| Feature | Choice | Justification |
| :--- | :--- | :--- |
| **Storage** | Redis $\rightarrow$ SQL | Speed for ranking, Durability for storage. |
| **Data Structure**| Skip List | Perfect balance of search and insertion speed. |
| **Communication**| Asynchronous (Kafka) | Decouples high-frequency writes from slow disk I/O. |
| **Scaling** | User-ID Sharding | Prevents hotspots in high-traffic games. |
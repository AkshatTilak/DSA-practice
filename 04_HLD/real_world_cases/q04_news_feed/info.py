INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/design-news-feed-system-system-design/',
    'description': 'Design Twitter feed timeline aggregation.',
    'type': 'design',
    'groups': ['Real-World Systems', 'Distributed Systems'],
    'readme_content': """# News Feed System Design HLD

This guide provides a comprehensive architectural deep-dive into designing a News Feed system similar to Twitter or Facebook. The primary challenge of this system is the **Fan-out** problem: how to efficiently deliver updates from a few users to millions of followers in real-time.

---

## 1. Overview & System Requirements

The goal is to build a system where users can post updates (tweets) and see a curated timeline of updates from people they follow, sorted by reverse chronological order (or an algorithm).

### Functional Requirements
- **Post Tweets**: Users should be able to publish short text updates.
- **Follow/Unfollow**: Users can follow other users to subscribe to their updates.
- **News Feed Retrieval**: Users should see a feed of tweets from all the people they follow.
- **Timeline Pagination**: Feed should be loadable in chunks (infinite scroll).

### Non-Functional Requirements (SLAs)
- **High Availability**: The system must be available $99.99\%$ of the time. Availability is prioritized over strict consistency (CAP Theorem).
- **Low Latency**: Feed generation/loading should happen in under $200\text{ms}$.
- **Scalability**: Must handle hundreds of millions of Daily Active Users (DAU).
- **Eventual Consistency**: It is acceptable if a tweet takes a few seconds to appear in a follower's feed.

### Scale Assumptions
| Metric | Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | $300 \text{ Million}$ |
| **Avg. Follows per User** | $200$ |
| **Tweets per Day** | $500 \text{ Million}$ |
| **Read/Write Ratio** | $100:1$ (Read-heavy) |
| **QPS (Read)** | $\approx 100\text{k} - 500\text{k}$ requests per second |

---

## 2. High-Level System Architecture

The system follows a **decoupled microservices architecture** to allow independent scaling of the write path (posting) and the read path (viewing).

### Architecture Components
1. **API Gateway / Load Balancer**: Routes requests, handles authentication, and rate-limiting.
2. **Tweet Service**: Handles the creation and storage of tweets.
3. **Social Graph Service**: Manages follow/unfollow relationships (typically using a Graph Database or heavily indexed SQL).
4. **Fan-out Service**: The "brain" of the system. It pushes new tweets to the feeds of followers.
5. **Feed Service**: Aggregates and serves the pre-computed feed to the user.
6. **Cache Layer (Redis)**: Stores the pre-computed "News Feed" for active users for $O(1)$ retrieval.
7. **Database Layer**: 
    - **User/Follow DB**: Relational (PostgreSQL/MySQL) for strong consistency on identity.
    - **Tweet DB**: NoSQL (Cassandra or MongoDB) for high write throughput and horizontal scaling.

---

## 3. Key HLD Concepts & Component Design

### The Core Challenge: Fan-out Strategies
Fan-out is the process of delivering a single tweet to all the followers' feeds.

#### A. Push Model (Fan-out on Write)
When a user posts a tweet, the system immediately pushes that tweet into the pre-computed feed caches of all their followers.
- **Pros**: Read latency is extremely low ($O(1)$ to fetch the cache).
- **Cons**: Write latency is high. If a user has $10\text{M}$ followers, $10\text{M}$ cache writes must occur. This is the **"Celebrity Problem."**

#### B. Pull Model (Fan-out on Load)
The feed is not pre-computed. When a user requests their feed, the system fetches the list of people they follow and pulls the most recent tweets from those users.
- **Pros**: Writes are extremely fast ($O(1)$). No write amplification.
- **Cons**: Reads are slow. The system must perform a multi-get/join across many users' tweet lists and sort them.

#### C. Hybrid Model (The Optimal Approach)
We categorize users based on their follower count:
- **Regular Users**: Use the **Push Model**. Since they have few followers, the write amplification is manageable.
- **Celebrities (High Follower Count)**: Use the **Pull Model**. We do not push their tweets to millions of caches. Instead, when a follower loads their feed, the system pulls the celebrity's latest tweets and merges them into the pre-computed feed.

### Storage Selection
- **Redis (Feed Cache)**: We use Redis `ZSET` (Sorted Sets) to store the feed. The `score` is the `timestamp`, allowing for efficient range queries (pagination) and $O(\log N)$ insertion.
- **Cassandra (Tweet Store)**: A wide-column store is ideal here. Partition key = `user_id`, Clustering key = `tweet_id` (sorted by time). This allows very fast retrieval of a specific user's latest tweets.

---

## 4. Data Flows & Fault Tolerance

### Write Path (Posting a Tweet)
1. **User $\to$ Tweet Service**: User submits a tweet.
2. **Tweet Service $\to$ Tweet DB**: Tweet is persisted in Cassandra.
3. **Tweet Service $\to$ Fan-out Service**: An event is pushed to a Message Queue (Kafka).
4. **Fan-out Service**:
    - Checks the author's status (Regular vs. Celebrity).
    - If **Regular**: Fetches follower list from Social Graph $\to$ Updates the Redis Feed Caches of all active followers.
    - If **Celebrity**: Only marks the tweet as "Celebrity Content" in the DB; no push occurs.

### Read Path (Viewing the Feed)
1. **User $\to$ Feed Service**: Request for "Home Timeline."
2. **Feed Service $\to$ Redis**: Fetch the pre-computed list of tweet IDs for the user.
3. **Feed Service $\to$ Social Graph**: Identify which "Celebrities" the user follows.
4. **Feed Service $\to$ Tweet DB**: Pull recent tweets from those celebrities.
5. **Merge & Sort**: Merge the Redis list and the Celebrity list by timestamp $\to$ Return to user.

### Fault Tolerance & Reliability
- **Message Queue (Kafka)**: If the Fan-out service crashes, Kafka ensures that the "push" events are not lost and can be re-processed.
- **Cache Eviction**: We only store feeds for **Active Users** (e.g., users who logged in within the last 30 days) to save memory. Inactive users' feeds are computed on-demand (Pull model).
- **Replication**: Cassandra uses a replication factor of 3 across different availability zones to prevent data loss during node failure.

---

## 5. Production Trade-offs

### CAP Theorem Analysis
This system chooses **AP (Availability and Partition Tolerance)**. 
- In a global system, we cannot afford to block a user's "Post" request just because a follower's cache in another region is unreachable.
- **Trade-off**: We accept **Eventual Consistency**. A follower might see a tweet 2 seconds after it was posted.

### Complexity Analysis
| Operation | Push Model (Regular) | Pull Model (Celebrity) | Hybrid (Optimal) |
| :--- | :--- | :--- | :--- |
| **Write (Post)** | $O(\text{Followers})$ | $O(1)$ | $O(\text{Followers if Regular})$ |
| **Read (Feed)** | $O(1)$ | $O(\text{Followings} \times \text{AvgTweets})$ | $O(1) + O(\text{Celebs followed})$ |
| **Storage** | High (Duplicate feeds) | Low | Balanced |

### Summary of Trade-offs
- **Memory vs. Latency**: Pre-computing feeds in Redis uses massive amounts of RAM but provides sub-millisecond read response times.
- **Write Amplification vs. Read Latency**: The hybrid approach mitigates the "Thundering Herd" problem where a celebrity tweet would otherwise crash the database if everyone tried to "pull" it simultaneously.""",
    'solutions': """# System Design: Twitter Feed Timeline Aggregation

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Tweet Posting:** Users can publish short text updates (tweets).
*   **Following:** Users can follow and unfollow other users.
*   **Home Timeline:** Users can view a chronological feed of tweets from everyone they follow.
*   **User Timeline:** Users can view a chronological feed of their own tweets.
*   **Timeline Pagination:** The feed must support pagination (loading more tweets as the user scrolls).

### 1.2 Non-Functional Requirements
*   **High Availability:** The system must be available for reads even if some components are lagging.
*   **Low Latency:** Home timeline retrieval should be near-instant (< 200ms).
*   **Eventual Consistency:** It is acceptable if a tweet takes a few seconds to appear in a follower's feed.
*   **Scalability:** Must handle hundreds of millions of Daily Active Users (DAU) and billions of tweets.

### 1.3 Scale Estimations (HLD)
*   **DAU:** 300 Million.
*   **Average Tweets/Day:** 500 Million.
*   **Average Follows:** Assume an average user follows 200 people.
*   **Read/Write Ratio:** Extremely read-heavy (e.g., 100:1).
*   **Feed Reads:** 300M users $\times$ 10 feed refreshes/day = 3 Billion reads/day.
*   **Throughput:**
    *   Write QPS: $500M / 86400 \approx 5,800$ tweets/sec.
    *   Read QPS: $3B / 86400 \approx 35,000$ requests/sec (peak could be 10x higher).

---

## 2. High-Level Architecture

The core challenge is the **Fan-out** process: how to deliver a single tweet to millions of followers efficiently. We employ a **Hybrid Approach** (Push for normal users, Pull for celebrities).

### 2.1 Architecture Diagram (Mermaid)

```mermaid
graph TD
    User((User)) --> LB[Load Balancer]
    LB --> API[API Gateway]
    
    API --> TweetSvc[Tweet Service]
    API --> FollowSvc[Follow Service]
    API --> TimelineSvc[Timeline Service]
    
    TweetSvc --> TweetDB[(Tweet Store - NoSQL)]
    TweetSvc --> Kafka[Message Queue - Kafka]
    
    FollowSvc --> FollowDB[(Follow Graph - SQL/NoSQL)]
    
    Kafka --> FanoutWorker[Fan-out Worker]
    FanoutWorker --> FollowDB
    FanoutWorker --> FeedCache[(Feed Cache - Redis)]
    
    TimelineSvc --> FeedCache
    TimelineSvc --> TweetDB
    TimelineSvc --> FollowDB
```

### 2.2 Core Component Interactions
1.  **Write Path (Posting a Tweet):**
    *   User posts a tweet $\rightarrow$ `Tweet Service` $\rightarrow$ Persisted in `Tweet Store`.
    *   `Tweet Service` pushes an event to `Kafka`.
    *   `Fan-out Workers` consume the event, look up the author's followers in `Follow DB`, and inject the Tweet ID into the `Feed Cache` (Redis) of each follower.
2.  **Read Path (Viewing Home Feed):**
    *   `Timeline Service` checks the user's `Feed Cache`.
    *   If the cache exists, it fetches the list of Tweet IDs and hydrates them with full content from the `Tweet Store`.
    *   **The Celebrity Twist:** For users following "celebrities" (high follower count), the `Timeline Service` pulls celebrity tweets directly from the `Tweet Store` at read-time and merges them with the cached feed.

---

## 3. Detailed Database Schema Design

### 3.1 Tweet Store (NoSQL - Cassandra/HBase)
We use a Wide-Column store because tweets are immutable, write-heavy, and retrieved by user ID in chronological order.
*   **Table:** `tweets`
*   **Partition Key:** `user_id` (groups all tweets of a user together on a node).
*   **Clustering Key:** `tweet_id` (descending, usually a Snowflake ID containing a timestamp).
*   **Fields:** `tweet_id (bigint)`, `user_id (bigint)`, `content (text)`, `created_at (timestamp)`.

### 3.2 Follow Graph (SQL - PostgreSQL or NoSQL - DynamoDB)
Requires fast lookups of "Who do I follow?" and "Who follows me?".
*   **Table:** `follows`
*   **Fields:** `follower_id (bigint)`, `followee_id (bigint)`, `created_at (timestamp)`.
*   **Indices:** 
    *   Primary Key: `(follower_id, followee_id)`
    *   Secondary Index on `followee_id` to find all followers of a user.

### 3.3 Feed Cache (In-Memory - Redis)
Stores the pre-computed Home Timeline for active users.
*   **Data Structure:** `Redis Sorted Set (ZSet)`
*   **Key:** `feed:user_id`
*   **Score:** `tweet_id` (or timestamp).
*   **Value:** `tweet_id`.
*   **Retention:** Limit to the most recent 1,000 tweet IDs per user to save memory.

---

## 4. Core API Design

### 4.1 Post a Tweet
`POST /v1/tweets`
*   **Request:**
    ```json
    {
      "text": "Hello world! #systemdesign",
      "media_ids": ["m123", "m456"]
    }
    ```
*   **Response:** `201 Created` with `tweet_id`.

### 4.2 Follow User
`POST /v1/follows/{userId}`
*   **Response:** `204 No Content`.

### 4.3 Get Home Timeline
`GET /v1/timeline/home?limit=20&max_id=1712345678`
*   **Request Params:** `limit` (number of tweets), `max_id` (for pagination/cursor).
*   **Response:**
    ```json
    {
      "tweets": [
        {
          "tweet_id": "1712345678",
          "user": { "id": "u1", "name": "Alice" },
          "content": "Latest news!",
          "created_at": "2023-10-01T10:00:00Z"
        },
        ...
      ],
      "next_cursor": "1712345000"
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 The "Celebrity" Problem (Fan-out Optimization)
If a user has 50 million followers, pushing a tweet to 50 million Redis lists is too slow and causes "write amplification" (the "Thundering Herd" on the cache).
*   **Hybrid Strategy:** 
    *   **Normal Users:** Use the **Push Model**. Tweet is pushed to followers' caches.
    *   **Celebrities:** Use the **Pull Model**. Their tweets are NOT pushed. Instead, when a follower requests their feed, the `Timeline Service` fetches the celebrity's recent tweets and merges them into the result set.

### 5.2 Caching Strategy
*   **User Timeline Cache:** Cache a user's own tweets in Redis to avoid hitting the `Tweet Store` for profile page loads.
*   **LRU Eviction:** Evict feed caches for users who haven't logged in for 30 days.

### 5.3 Sharding and Partitioning
*   **Tweet Store:** Shard by `user_id`. This ensures all tweets for a single user are co-located, making the "User Timeline" query extremely efficient.
*   **Follow DB:** Shard by `follower_id` to quickly retrieve the list of people a user follows.

### 5.4 Reliability & Fault Tolerance
*   **Kafka for Decoupling:** If the `Fan-out Worker` crashes, events remain in Kafka. Once recovered, it resumes processing from the last offset.
*   **Read-through Cache:** If the `Feed Cache` is empty, the system falls back to a "Pull" approach (querying `Follow DB` $\rightarrow$ `Tweet Store`), then populates the cache.

---

## 6. Trade-off Analysis

| Trade-off | Decision | Reasoning |
| :--- | :--- | :--- |
| **Latency vs. Storage** | Favor Latency | Pre-computing feeds in Redis consumes significant RAM but ensures $O(1)$ or $O(\log N)$ retrieval, which is critical for UX. |
| **Consistency vs. Availability** | Availability (AP) | In a social feed, it's better to show a slightly stale feed than to show an error page. Eventual consistency is acceptable. |
| **Push vs. Pull** | Hybrid | Pure Push fails for celebrities; Pure Pull fails for read latency. Hybrid optimizes for the 99% of users while handling outliers. |
| **SQL vs. NoSQL** | Polyglot Persistence | SQL is used for relationships (Follows) where integrity matters; NoSQL is used for Tweets (time-series/high volume) for horizontal scalability. |""",
}

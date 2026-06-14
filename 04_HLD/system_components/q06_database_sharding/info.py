INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/database-sharding-system-design/',
    'description': 'Horizontal databases partitioning schemes.',
    'type': 'design',
    'groups': ['Databases', 'Distributed Systems'],
    'readme_content': """# Database Sharding HLD

Database sharding is a method for distributing a single dataset across multiple databases (shards) to achieve horizontal scalability. Unlike vertical scaling (upgrading hardware), sharding allows a system to handle massive growth in data volume and request throughput by adding more commodity servers.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Horizontal Scalability**: The ability to increase storage and throughput capacity by adding more database nodes.
*   **Data Distribution**: Efficiently partitioning data so that no single node becomes a bottleneck.
*   **Query Routing**: A mechanism to route queries to the correct shard based on a **Shard Key**.
*   **Availability**: Ensuring the system remains operational even if a specific shard fails.

### Non-Functional Requirements
*   **Low Latency**: Routing logic should add negligible overhead to the request-response cycle.
*   **High Throughput**: Support millions of Queries Per Second (QPS).
*   **Durability**: No data loss during sharding or re-sharding processes.
*   **Elasticity**: Ability to add or remove shards with minimal data movement.

### Scale Assumptions
*   **Data Volume**: Petabytes of data, exceeding the storage capacity of a single high-end server.
*   **Traffic**: Hundreds of thousands to millions of concurrent users.
*   **Growth**: Rapid data growth requiring a system that doesn't require a full rewrite when scaling.

---

## 2. High-Level System Architecture

A sharded architecture introduces a **Routing Layer** between the application and the data storage.

### Architecture Components
1.  **Application Layer**: The business logic that initiates data requests.
2.  **Routing Layer (Shard Director)**: 
    *   Acts as a proxy or a library within the app.
    *   Uses the **Shard Key** to determine which physical shard holds the requested data.
    *   Maintains a **Shard Map** (the mapping of keys to nodes).
3.  **Database Shards**: Independent database instances. Each shard is a complete database containing a subset of the total data.
4.  **Configuration Service (Zookeeper/Etcd)**: Stores the shard metadata (e.g., which server IP corresponds to which shard ID) to ensure consistency across multiple app servers.
5.  **Replication Layer**: Each shard typically has followers (replicas) to ensure high availability and read scalability.

### Write and Read Paths
*   **Write Path**: `Client` $\rightarrow$ `App Server` $\rightarrow$ `Routing Logic` $\rightarrow$ `Target Shard (Leader)` $\rightarrow$ `Replication to Followers`.
*   **Read Path**: `Client` $\rightarrow$ `App Server` $\rightarrow$ `Routing Logic` $\rightarrow$ `Target Shard (Leader or Follower)`.

---

## 3. Key HLD Concepts & Component Design

### Sharding Strategies
The choice of partitioning scheme defines the system's performance and complexity.

| Strategy | Mechanism | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Range-Based** | Data split by ranges of the shard key (e.g., A-M in Shard 1, N-Z in Shard 2). | Efficient range queries; simple to implement. | **Hotspots**: If most users have names starting with 'S', Shard 2 is overloaded. |
| **Hash-Based** | `Shard = Hash(ShardKey) % NumberOfShards`. | Uniform data distribution; prevents hotspots. | Range queries are impossible; Adding/removing shards requires massive data migration. |
| **Directory-Based** | A lookup table (Directory) stores the mapping: `Key $\rightarrow$ ShardID`. | Extremely flexible; allows moving individual keys between shards. | Directory becomes a **Single Point of Failure (SPOF)** and a performance bottleneck. |

### Consistent Hashing (The Optimal Approach)
To solve the "re-sharding" problem in hash-based sharding, **Consistent Hashing** is used.

*   **The Ring**: Imagine the hash space as a circle (0 to $2^{32}-1$).
*   **Nodes on Ring**: Servers are hashed and placed on this ring.
*   **Data Placement**: A key is hashed and placed on the ring; it belongs to the first server encountered while moving clockwise.
*   **Adding/Removing Nodes**: Only $K/N$ keys need to be moved (where $K$ is total keys and $N$ is number of nodes), rather than re-hashing everything.
*   **Virtual Nodes**: To prevent imbalance (skew), each physical server is mapped to multiple "virtual nodes" across the ring.

### Choosing the Shard Key
The shard key is the most critical decision. A poor key leads to "hot shards."
*   **High Cardinality**: The key should have many unique values (e.g., `user_id` is better than `country_id`).
*   **Uniform Access**: The key should distribute requests evenly.
*   **Query Alignment**: The key should align with the most frequent queries to avoid **Scatter-Gather** (querying every single shard).

---

## 4. Data Flows & Fault Tolerance

### Request Walkthrough: Fetching User Profile
1.  **Request**: Client sends `GET /profile?user_id=12345`.
2.  **Routing**: The Routing Layer extracts `user_id=12345`.
3.  **Calculation**: It applies the consistent hashing algorithm: `Hash(12345) $\rightarrow$ Node B`.
4.  **Execution**: The request is routed to the leader of Node B.
5.  **Response**: Node B returns the profile data to the client.

### Handling Failures
*   **Shard Failure**: Each shard is a **Replication Group**. If the leader fails, a follower is promoted via a consensus algorithm (e.g., Raft or Paxos).
*   **Routing Layer Failure**: The routing logic is stateless and deployed across multiple instances behind a Load Balancer.
*   **Network Partition**: The system follows the **CAP Theorem**. In a partition, the system typically chooses **Availability (AP)** by allowing reads from stale replicas or **Consistency (CP)** by refusing writes until the partition heals.

---

## 5. Production Trade-offs

### The Challenges of Sharding
Sharding is a "nuclear option"—it solves scale but introduces significant complexity.

| Feature | Before Sharding (Monolith) | After Sharding (Distributed) |
| :--- | :--- | :--- |
| **Joins** | Simple `JOIN` queries in SQL. | **Cross-shard joins** are prohibited. Must perform joins in the Application Layer. |
| **Transactions** | ACID compliance is guaranteed by the DB. | Requires **Distributed Transactions** (Two-Phase Commit or Saga Pattern), which are slow. |
| **Complexity** | Simple deployment and backup. | Complex backup/restore across $N$ shards; complex monitoring. |
| **Referential Integrity** | Foreign keys ensure data consistency. | Foreign keys cannot be enforced across different physical shards. |

### Summary Complexity Analysis

| Operation | Range Sharding | Hash Sharding | Consistent Hashing | Directory Sharding |
| :--- | :--- | :--- | :--- | :--- |
| **Point Lookup** | $O(1)$ | $O(1)$ | $O(\log N)$ | $O(1)$ (via lookup) |
| **Range Query** | $O(K)$ (Efficient) | $O(N \cdot K)$ (Scatter-Gather) | $O(N \cdot K)$ (Scatter-Gather) | $O(N \cdot K)$ |
| **Re-sharding Cost** | Low (Split range) | High (Re-hash all) | Low (Move $1/N$ data) | Low (Update map) |
| **Hotspot Risk** | High | Low | Very Low | Low |

*(Where $N$ = number of shards, $K$ = number of records in range)*""",
    'solutions': """# System Design Guide: Horizontal Database Sharding

## 1. Requirements & System Constraints

This document outlines the architectural approach for implementing horizontal database sharding for a high-scale User Profile and Activity System. 

### 1.1 Functional Requirements
*   **User Management:** Ability to create, update, and retrieve user profiles by a unique identifier.
*   **Scalable Storage:** Support for billions of user records and associated activity logs.
*   **Low Latency:** Sub-100ms response time for point lookups.
*   **Global Distribution:** Ability to route requests to the nearest data center/shard.

### 1.2 Non-Functional Requirements
*   **High Availability:** The system must remain operational even if a single shard fails (99.99% availability).
*   **Linear Scalability:** Adding more hardware should linearly increase the system's throughput and storage capacity.
*   **Fault Isolation:** A failure in one shard should not impact the availability of data in other shards (blast radius limitation).
*   **Consistency:** Strong consistency for individual user updates; eventual consistency for cross-user analytics.

### 1.3 Scale Estimations
*   **Total Users:** 1 Billion.
*   **Avg. Profile Size:** 2 KB $\rightarrow$ Total Storage $\approx$ 2 TB for profiles.
*   **Activity Logs:** 100 events/user/day $\rightarrow$ 100 Billion events/day $\approx$ 10-20 TB/day.
*   **Read Throughput:** 1 Million Requests Per Second (RPS).
*   **Write Throughput:** 100 Thousand Requests Per Second (RPS).

---

## 2. High-Level Architecture

The architecture moves from a monolithic database to a distributed cluster where data is partitioned across multiple independent database nodes.

### 2.1 Core Components
1.  **API Gateway:** Handles authentication, rate limiting, and request routing.
2.  **Sharding Router (Application Layer or Middleware):** The "brain" that determines which shard holds the requested data based on the Shard Key.
3.  **Configuration Store (Control Plane):** A highly available store (e.g., etcd, ZooKeeper) that maintains the shard map (which range/hash belongs to which physical node).
4.  **Shard Nodes:** Independent database instances (e.g., PostgreSQL or MySQL) containing a subset of the total data.
5.  **Global Index / Lookup Table:** An optional service to map secondary keys (like email) to the Shard Key (`user_id`).

### 2.2 Architecture Diagram

```mermaid
graph TD
    Client[Client App] --> Gateway[API Gateway]
    Gateway --> Router[Sharding Router / Logic]
    Router --> ConfigStore[(Config Store: Shard Map)]
    
    subgraph Shard Cluster
        Router --> Shard1[(Shard 1: Users A-M)]
        Router --> Shard2[(Shard 2: Users N-Z)]
        Router --> Shard3[(Shard 3: Users ...)]
    end
    
    Router --> GlobalIndex[(Global Index: Email -> UserID)]
    GlobalIndex --> Shard1
    GlobalIndex --> Shard2
    GlobalIndex --> Shard3
```

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection: SQL vs. NoSQL
For this specific use case, we utilize **Relational Databases (PostgreSQL)** for the shards. 
*   **Reasoning:** User profiles require ACID properties for updates (e.g., changing a password or email). While NoSQL (Cassandra/DynamoDB) handles sharding natively, a sharded SQL approach allows for complex joins within a single shard and strong consistency.

### 3.2 Schema Definition
**Table: `users`**
| Field | Type | Constraint | Index | Note |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | BIGINT | PRIMARY KEY | B-Tree | Shard Key (Snowflake ID) |
| `email` | VARCHAR(255) | UNIQUE | B-Tree | Global Index Key |
| `username` | VARCHAR(50) | NOT NULL | B-Tree | |
| `profile_data` | JSONB | | GIN | Flexible attributes |
| `created_at` | TIMESTAMP | | | |
| `updated_at` | TIMESTAMP | | | |

**Table: `user_activities`**
| Field | Type | Constraint | Index | Note |
| :--- | :--- | :--- | :--- | :--- |
| `activity_id` | BIGINT | PRIMARY KEY | B-Tree | |
| `user_id` | BIGINT | FOREIGN KEY | B-Tree | Shard Key (Co-located) |
| `action` | VARCHAR(50) | | | |
| `timestamp` | TIMESTAMP | | B-Tree | For range queries |

### 3.3 Sharding Strategy: The Shard Key
The `user_id` is chosen as the **Shard Key**.
*   **Selection Criteria:** High cardinality, uniform distribution, and used in the majority of queries.
*   **ID Generation:** We use **Twitter Snowflake IDs** (64-bit) to ensure IDs are unique across shards and roughly time-sorted without requiring a central auto-increment bottleneck.

---

## 4. Core API Design

### 4.1 User Profile Retrieval
**Endpoint:** `GET /v1/users/{userId}`
*   **Request:** `userId` in path.
*   **Internal Logic:** `shard_id = hash(userId) % total_shards`.
*   **Response:**
```json
{
  "user_id": 123456789,
  "username": "johndoe",
  "email": "john@example.com",
  "profile": { "theme": "dark", "lang": "en" }
}
```

### 4.2 User Creation
**Endpoint:** `POST /v1/users`
*   **Payload:** `{"username": "johndoe", "email": "john@example.com"}`
*   **Internal Logic:** Generate Snowflake ID $\rightarrow$ Calculate Shard $\rightarrow$ Write to Shard $\rightarrow$ Update Global Index.
*   **Response:** `201 Created` with `user_id`.

### 4.3 Search by Email (Cross-Shard Query)
**Endpoint:** `GET /v1/users/search?email=john@example.com`
*   **Internal Logic:** 
    1. Query `GlobalIndex` table $\rightarrow$ returns `user_id: 123456789`.
    2. Use `user_id` to route to specific shard.
*   **Response:** User profile JSON.

---

## 5. Scalability & Advanced Topics

### 5.1 Horizontal Partitioning Schemes
We evaluate three primary schemes:

1.  **Key-Based (Hash) Sharding:**
    *   *Mechanism:* `shard = hash(key) % N`.
    *   *Pros:* Even data distribution.
    *   *Cons:* Adding new shards requires massive data migration (resharding).

2.  **Range-Based Sharding:**
    *   *Mechanism:* `0-1M -> Shard 1`, `1M-2M -> Shard 2`.
    *   *Pros:* Efficient range queries.
    *   *Cons:* Leads to "Hot Spots" (e.g., new users hitting the latest shard).

3.  **Consistent Hashing (The Staff Architect's Choice):**
    *   *Mechanism:* Map keys and nodes onto a logical circle (ring).
    *   *Pros:* Minimizes data movement during scaling. Only $K/N$ keys need to move when a shard is added.
    *   *Implementation:* Use **virtual nodes** to prevent uneven distribution.

### 5.2 Handling the "Hot Key" Problem
If a specific user (e.g., a celebrity) generates massive traffic:
*   **Caching Layer:** Implement a distributed cache (Redis) in front of the shards.
*   **Read Replicas:** Create read-only replicas for the specific shard containing the hot key.

### 5.3 Resharding and Migration
To move from $N$ to $M$ shards without downtime:
1.  **Dual Writes:** Start writing new data to both old and new shards.
2.  **Backfill:** Migrate historical data from old to new shards in the background.
3.  **Verification:** Compare checksums between old and new shards.
4.  **Cutover:** Update the Config Store to point to the new shard map.

### 5.4 Cross-Shard Queries (Scatter-Gather)
For queries that don't include the shard key (e.g., "Find all users aged 20-30"):
*   **Scatter:** The Router sends the query to *all* shards in parallel.
*   **Gather:** The Router aggregates results, performs final sorting/filtering, and returns the response.
*   *Optimization:* Use an asynchronous message queue or an OLAP database (ClickHouse/StarRocks) for these queries to avoid overloading the OLTP shards.

---

## 6. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs. Availability** | **Availability (AP)** | For global user profiles, high availability is prioritized. We accept eventual consistency for the Global Index but maintain strong consistency within a single shard. |
| **Latency vs. Storage** | **Latency** | We introduce a Global Index (extra storage) to avoid "Scatter-Gather" queries for common lookups (email $\rightarrow$ id), reducing latency from $O(N_{shards})$ to $O(1)$. |
| **Complexity vs. Scalability** | **Complexity** | Sharding adds significant architectural complexity (router, config store, migration logic), but it is the only way to handle 1B+ users where a single vertical instance reaches hardware limits. |
| **Hash vs. Range** | **Consistent Hashing** | While range sharding is simpler for time-series data, consistent hashing prevents the "hot shard" problem and makes scaling predictable. |""",
}

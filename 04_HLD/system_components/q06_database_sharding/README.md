# Database Sharding HLD

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

*(Where $N$ = number of shards, $K$ = number of records in range)*
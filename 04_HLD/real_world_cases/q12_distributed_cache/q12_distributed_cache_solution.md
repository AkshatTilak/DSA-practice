# System Design Document: Distributed Cache (Redis-like)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Core Operations**: Support `get(key)`, `put(key, value, ttl)`, and `delete(key)`.
*   **TTL (Time-to-Live)**: Ability to set an expiration time for keys.
*   **Eviction Policies**: Automatically remove items when memory is full (e.g., Least Recently Used - LRU, Least Frequently Used - LFU).
*   **Data Distribution**: Spread data across multiple nodes to ensure no single node is a bottleneck.
*   **High Availability**: Ensure the system remains operational if a node fails.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency**: Sub-millisecond response times for reads and writes.
*   **High Throughput**: Support millions of requests per second.
*   **Scalability**: Ability to add or remove nodes horizontally without significant downtime.
*   **Consistency**: Eventual consistency for replicated data; strong consistency for primary keys (depending on configuration).

### 1.3 Scale Estimations (HLD)
*   **Throughput**: 10 Million requests per second (RPS).
*   **Average Object Size**: 1 KB.
*   **Total Data Volume**: 1 TB of in-memory data.
*   **Read/Write Ratio**: 80% Read / 20% Write.
*   **Bandwidth Requirement**: $10^7 \text{ req/sec} \times 1 \text{ KB} \approx 10 \text{ GB/s}$.

---

## 2. High-Level Architecture

The system follows a **distributed shared-nothing architecture** where data is partitioned across a cluster of cache nodes.

### 2.1 Component Overview
*   **Client Library**: Handles request routing, hashing, and connection pooling.
*   **Consistent Hashing Ring**: Determines which node is responsible for a specific key to minimize data reshuffling during scaling.
*   **Cache Node**: The worker unit that stores data in memory and handles local eviction.
*   **Configuration Service (Zookeeper/Etcd)**: Maintains the cluster state, node health, and the current hash ring mapping.
*   **Replication Manager**: Handles data synchronization between Primary and Replica nodes.

### 2.2 Architecture Diagram (ASCII)

```text
                                 +-------------------+
                                 |  Config Service   |
                                 | (Zookeeper/Etcd)  |
                                 +---------+---------+
                                           ^
                                           | Cluster State / Heartbeats
                                           v
      +-------------------------------------------------------------------------+
      |                            Consistent Hashing Ring                      |
      |    [Node A] <------> [Node B] <------> [Node C] <------> [Node D]        |
      +-------------------------------------------------------------------------+
               ^                      ^                      ^
               |                      |                      |
      +--------+----------+  +--------+----------+  +--------+----------+
      |  Cache Node A      |  |  Cache Node B      |  |  Cache Node C      |
      |  (Primary)         |  |  (Primary)         |  |  (Primary)         |
      |  +-------------+   |  |  +-------------+   |  |  +-------------+   |
      |  | In-Mem Store|   |  |  | In-Mem Store|   |  |  | In-Mem Store|   |
      |  +-------------+   |  |  +-------------+   |  |  +-------------+   |
      |  +-------------+   |  |  +-------------+   |  |  +-------------+   |
      |  | LRU Queue   |   |  |  | LRU Queue   |   |  |  | LRU Queue   |   |
      |  +-------------+   |  |  +-------------+   |  |  +-------------+   |
      +--------+-----------+  +--------+----------+  +--------+----------+
               |                      |                      |
               v                      v                      v
      +-------------------------------------------------------------------------+
      |                            Replica Nodes                                |
      |    [Replica A] <------> [Replica B] <------> [Replica C]                 |
      +-------------------------------------------------------------------------+
```

---

## 3. Detailed Design

### 3.1 Data Structure Design (Inside a Node)
Since this is an in-memory cache, we do not use a traditional disk-based database. Instead, we use a combination of data structures to achieve $O(1)$ time complexity.

1.  **Primary Storage**: A **Hash Map** stores the mapping from `Key` $\rightarrow$ `Value`.
2.  **Eviction Logic (LRU)**: A **Doubly Linked List** stores the keys. 
    *   When a key is accessed, it moves to the head.
    *   When memory is full, the tail is evicted.
3.  **Expiration Logic (TTL)**: A **Min-Priority Queue (Heap)** or a **Sorted Set** stores `(ExpirationTimestamp, Key)`.
    *   A background thread periodically polls the top of the heap to delete expired keys.
    *   Alternatively, "Lazy Expiration" is used: check if a key is expired only when it is accessed.

### 3.2 Data Distribution (Consistent Hashing)
To avoid $O(N)$ data movement when adding/removing nodes, we use **Consistent Hashing with Virtual Nodes**.
*   The hash space is treated as a circle (0 to $2^{32}-1$).
*   Each physical node is mapped to multiple "virtual nodes" on the ring.
*   **Lookup**: `hash(key)` $\rightarrow$ find the first node clockwise on the ring.
*   **Benefit**: Adding a node only requires moving keys from its immediate neighbor, not the entire cluster.

### 3.3 Replication & Availability
*   **Leader-Follower Model**: Each shard has one Primary and $N$ Replicas.
*   **Writes**: Sent to the Primary $\rightarrow$ synchronously or asynchronously propagated to Replicas.
*   **Reads**: Can be served by the Primary (Strong Consistency) or Replicas (Eventual Consistency/Read Scaling).
*   **Failover**: If the Primary fails, the Config Service detects the heartbeat loss and promotes a Replica to Primary.

---

## 4. Core API Design

The cache uses a binary protocol (like RESP) for performance, but is represented here as a REST-like interface for clarity.

### 4.1 Put Operation
`POST /cache/set`
*   **Payload**:
    ```json
    {
      "key": "user:123:session",
      "value": "eyJhbGciOiJIUzI1...",
      "ttl_seconds": 3600
    }
    ```
*   **Response**: `200 OK` or `500 Internal Server Error`.

### 4.2 Get Operation
`GET /cache/get/{key}`
*   **Response**:
    ```json
    {
      "key": "user:123:session",
      "value": "eyJhbGciOiJIUzI1...",
      "expires_at": "2023-10-27T10:00:00Z"
    }
    ```
*   **Error**: `404 Not Found` if key is missing or expired.

### 4.3 Delete Operation
`DELETE /cache/delete/{key}`
*   **Response**: `200 OK` or `404 Not Found`.

---

## 5. Scalability & Advanced Topics

### 5.1 Eviction Strategies
*   **LRU (Least Recently Used)**: Best for workloads with "temporal locality" (recently accessed items are likely to be accessed again).
*   **LFU (Least Frequently Used)**: Best for workloads where some items are globally popular regardless of when they were last accessed.
*   **TTL-based**: Hard expiration based on timestamp.

### 5.2 Handling "Hot Keys"
A single key (e.g., a celebrity profile) may receive millions of requests, overwhelming one node.
*   **Solution**: **Local L1 Cache**. The client library maintains a small, short-lived in-memory cache for the most popular keys, reducing the number of network hops to the distributed cache.

### 5.3 Cache Stampede / Thundering Herd
When a hot key expires, multiple clients may simultaneously try to fetch the data from the database and write it back to the cache.
*   **Solution**: **Distributed Locking (Mutex)**. Only one client is allowed to refresh the cache for a specific key; others wait or receive a slightly stale value.

### 5.4 Memory Management
*   **Slab Allocation**: To avoid memory fragmentation (especially in C/C++), pre-allocate memory in chunks (slabs) of fixed sizes.
*   **Serialization**: Use Protobuf or MessagePack instead of JSON to reduce the memory footprint and network bandwidth.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem
In the context of the CAP theorem, a distributed cache is typically designed as an **AP (Availability and Partition Tolerance)** system.
*   **Why**: Low latency is the primary goal. Waiting for a global consensus (CP) on every `set` operation would introduce unacceptable latency.
*   **Trade-off**: We accept eventual consistency between replicas to ensure the system remains highly available and fast.

### 6.2 Latency vs. Storage
*   **Compression**: We could compress values to save memory, but this increases CPU latency for every `get/put`.
*   **Decision**: Use compression only for values larger than a specific threshold (e.g., > 1KB).

### 6.3 Consistent Hashing vs. Centralized Directory
*   **Consistent Hashing**: No central bottleneck, fast lookups, but can have slight imbalances in data distribution.
*   **Centralized Directory**: Perfect balance, but the directory becomes a single point of failure and a latency bottleneck.
*   **Decision**: Consistent Hashing with Virtual Nodes to balance both.

### 6.4 Write-Through vs. Write-Back
*   **Write-Through**: Data written to cache and DB simultaneously. High consistency, higher write latency.
*   **Write-Back**: Data written to cache and asynchronously flushed to DB. Lowest latency, risk of data loss if the cache node crashes.
*   **Decision**: Provide configurable strategies based on the application's durability requirements.
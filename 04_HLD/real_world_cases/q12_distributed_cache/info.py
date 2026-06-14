INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Distributed Cache (Redis-like).',
    'groups': ['Real-World Systems', 'Caching & Storage'],
    'readme_content': """# Distributed Cache HLD (Redis-like System)

A Distributed Cache is a high-performance, in-memory key-value store spread across multiple nodes. Its primary goal is to reduce data access latency and offload pressure from primary databases by storing frequently accessed data in RAM.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Basic KV Operations**: Support `get(key)`, `put(key, value)`, and `delete(key)`.
- **TTL (Time-to-Live)**: Ability to set an expiration time for keys to ensure data freshness.
- **Eviction Policies**: Automatic removal of old data when memory is full (e.g., LRU, LFU).
- **Scalability**: Ability to add or remove cache nodes without flushing the entire cache.

### Non-Functional Requirements
- **Ultra-Low Latency**: Read/Write operations should be in the sub-millisecond range.
- **High Throughput**: Support millions of Queries Per Second (QPS).
- **High Availability**: The system must remain operational even if individual nodes fail.
- **Eventual Consistency**: While strict consistency is possible, eventual consistency is usually traded for performance.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million |
| **Read/Write Ratio** | 80% Read / 20% Write |
| **Average QPS** | 1 Million requests/sec |
| **Data Size per Entry** | 1 KB average |
| **Total Storage Needed** | $\sim 1\text{ TB}$ (across a cluster) |
| **Latency Target** | $< 1\text{ms}$ (p99) |

---

## 2. High-Level System Architecture

The architecture consists of a client library (or proxy) and a cluster of cache nodes. To avoid a single point of failure and bottlenecks, the data is partitioned across the cluster.

### Architecture Components
1.  **Client / Cache Proxy**: The entry point. It determines which cache node holds a specific key using a distribution algorithm.
2.  **Configuration Service (Zookeeper/Etcd)**: Maintains the "Cluster State" (which nodes are healthy, the hash ring mapping).
3.  **Cache Nodes**: Individual servers holding a segment of the data in RAM.
4.  **Replication Group**: Each primary node has one or more replicas to ensure high availability.

### High-Level Diagram (Conceptual)
`Client` $\rightarrow$ `Consistent Hashing Logic` $\rightarrow$ `Target Cache Node (Primary)` $\rightarrow$ `Replication to Followers`

---

## 3. Key HLD Concepts & Component Design

### A. Data Partitioning: Consistent Hashing
Traditional modulo hashing (`hash(key) % N`) causes a "cache storm" if $N$ changes (adding/removing a node), as almost all keys map to different nodes.

**Consistent Hashing** solves this by:
- Mapping both servers and keys onto a circular logical ring ($0$ to $2^{32}-1$).
- A key is assigned to the first server encountered moving clockwise on the ring.
- **Virtual Nodes**: To prevent "hotspots" (where one node gets more data than others), each physical node is mapped to multiple points (virtual nodes) on the ring. This ensures a uniform distribution of data.

### B. Eviction Policy: LRU (Least Recently Used)
Since memory is finite, we must evict data. LRU is the industry standard.
- **Implementation**: A combination of a **Hash Map** (for $O(1)$ lookup) and a **Doubly Linked List** (for $O(1)$ updates to the "recency" order).
- **Process**: When a key is accessed, move it to the head. When memory is full, remove the tail.

### C. Concurrency Model
- **Single-Threaded Event Loop (Redis Approach)**: Uses a non-blocking I/O multiplexer (like `epoll`). This eliminates lock contention and context switching overhead, relying on the fact that memory access is orders of magnitude faster than network I/O.
- **Multi-Threaded (Memcached Approach)**: Uses locks or lock-free data structures to utilize multi-core CPUs.

### D. Persistence Options
While primarily in-memory, a distributed cache may need persistence to avoid "cold start" latency:
- **RDB (Redis Database)**: Point-in-time snapshots at intervals. High performance, but risks data loss between snapshots.
- **AOF (Append Only File)**: Logs every write operation. Higher durability, but larger file sizes and slower recovery.

---

## 4. Data Flows & Fault Tolerance

### Read Path (The "Get" Flow)
1. **Request**: Client calls `get("user_123")`.
2. **Route**: Client calculates `hash("user_123")` $\rightarrow$ finds the corresponding node on the **Consistent Hash Ring**.
3. **Fetch**: Client sends a request to the identified node.
4. **Result**: Node checks local RAM. If found, return value; if not, return `Cache Miss`.

### Write Path (The "Put" Flow)
1. **Route**: Client identifies the Primary node via the hash ring.
2. **Write**: Client sends `put("user_123", "data")` to the Primary.
3. **Replicate**: Primary writes to local memory and asynchronously propagates the write to **Follower Nodes**.
4. **Ack**: Primary returns success to the client.

### Handling Failures
| Scenario | Strategy | Result |
| :--- | :--- | :--- |
| **Node Crash** | **Failover** | The Configuration Service detects the heartbeat failure. A Follower is promoted to Primary. |
| **Network Partition** | **Quorum/Sensing** | The system may enter read-only mode or allow stale reads depending on the CAP preference. |
| **Hot Key** | **Replication/Local Cache** | For extremely popular keys (e.g., celebrity profiles), the system can replicate that specific key to all nodes or implement a small L1 cache on the client side. |

---

## 5. Production Trade-offs

### CAP Theorem: AP vs CP
A distributed cache typically chooses **AP (Availability and Partition Tolerance)**. 
- **Why?** In a caching scenario, it is usually better to return a slightly stale value (or a cache miss) than to bring the entire application to a halt because the cache cannot reach a consensus.

### Consistency vs. Latency
- **Strong Consistency**: Requires synchronous replication (Wait for all replicas to ack). This increases write latency significantly.
- **Eventual Consistency**: Asynchronous replication. Low latency, but a read from a follower immediately after a write to a primary might return the old value.

### Memory Management Trade-offs
| Strategy | Pro | Con |
| :--- | :--- | :--- |
| **Write-Through** | Data always consistent between cache and DB. | Higher write latency (must write to both). |
| **Write-Around** | Prevents cache pollution with data that isn't read immediately. | First read is always a cache miss. |
| **Write-Back** | Extremely fast writes (write to cache only). | Risk of data loss if cache crashes before DB update. |

### Complexity Summary
| Operation | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| `Get` / `Put` | $O(1)$ | $O(1)$ |
| `LRU Eviction` | $O(1)$ | $O(1)$ |
| `Node Lookup` | $O(\log (\text{Virtual Nodes}))$ | $O(\text{Nodes})$ |""",
    'solutions': """# System Design Document: Distributed Cache (Redis-like)

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
*   **Decision**: Provide configurable strategies based on the application's durability requirements.""",
}

# Distributed Cache HLD (Redis-like System)

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
| `Node Lookup` | $O(\log (\text{Virtual Nodes}))$ | $O(\text{Nodes})$ |
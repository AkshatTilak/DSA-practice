# Redis Caching & Write Policies HLD

This study guide focuses on the architectural implementation of caching systems using **Redis**, specifically diving deep into **Cache Invalidation** and **Write Policies**. Caching is a critical component of High-Level Design (HLD) used to reduce latency and offload pressure from the primary database.

---

## 1. Overview & System Requirements

The primary goal of a Redis caching layer is to store frequently accessed data in memory to avoid expensive disk-based database queries.

### Functional Requirements
- **Fast Data Retrieval**: Provide near-instant access to "hot" data.
- **Data Consistency**: Ensure that the data in the cache does not deviate significantly from the source of truth (Database).
- **Efficient Invalidation**: Remove or update stale data when the underlying database changes.

### Non-Functional Requirements
- **Low Latency**: Sub-millisecond response times for cache hits.
- **High Availability**: The cache should be available even if a single node fails (Redis Sentinel/Cluster).
- **Scalability**: Ability to handle millions of requests per second (QPS) via sharding.
- **Durability**: While caches are volatile, certain policies (like Write-Back) require persistence (RDB/AOF) to prevent data loss.

### Scale Assumptions
- **DAU**: 10M+ daily active users.
- **QPS**: 100k+ Read QPS / 10k+ Write QPS.
- **Data Volume**: Working set size of 100GB - 1TB (distributed across a Redis Cluster).

---

## 2. High-Level System Architecture

The caching layer sits between the **Application Server** and the **Primary Database**.

### Component Roles
1. **Application Server**: Logic layer that decides whether to fetch data from the cache or the DB.
2. **Redis Cluster**: Distributed in-memory store. Uses **Consistent Hashing** to distribute keys across multiple shards.
3. **Primary Database**: The permanent storage (e.g., PostgreSQL, MongoDB, DynamoDB).
4. **Cache Manager**: A logic component within the app that implements the write policies (Write-through, Write-around, etc.).

### High-Level Data Flow
`Client` $\rightarrow$ `API Gateway` $\rightarrow$ `App Server` $\rightarrow$ `Redis Cache` $\leftrightarrow$ `Primary Database`

---

## 3. Key HLD Concepts: Cache Write Policies

The most critical part of caching design is deciding how to handle writes. This determines the balance between **latency** and **consistency**.

### A. Write-Through Cache
In this policy, data is written to the cache and the database **simultaneously**.
- **Process**: App $\rightarrow$ Cache $\rightarrow$ Database $\rightarrow$ Success.
- **Pros**: High consistency; reads are always up-to-date.
- **Cons**: Higher write latency (must wait for both writes).
- **Best Use Case**: Systems where data consistency is critical and write volume is moderate.

### B. Write-Around Cache
Data is written **directly to the database**, bypassing the cache.
- **Process**: App $\rightarrow$ Database $\rightarrow$ Success. (Cache is updated only on a subsequent read miss).
- **Pros**: Prevents "Cache Pollution" (prevents filling the cache with data that isn't read frequently).
- **Cons**: "Cache Miss" on the first read after a write, increasing initial read latency.
- **Best Use Case**: Data that is written once but read infrequently.

### C. Write-Back (Write-Behind) Cache
Data is written **only to the cache**, and the database is updated **asynchronously** after a delay.
- **Process**: App $\rightarrow$ Cache $\rightarrow$ Success $\rightarrow$ (Async) $\rightarrow$ Database.
- **Pros**: Extremely low write latency; reduces load on the DB by batching updates.
- **Cons**: Risk of data loss if the Redis node crashes before the data is persisted to the DB.
- **Best Use Case**: High-write workloads (e.g., real-time gaming leaderboards, view counters).

### Summary Comparison Table

| Policy | Write Latency | Read Latency | Consistency | DB Load | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Write-Through** | High | Low | Strong | High | Low |
| **Write-Around** | Medium | Medium | Eventual | Medium | Low |
| **Write-Back** | Very Low | Low | Eventual | Low | High (Data Loss) |

---

## 4. Cache Invalidation & Eviction

Since memory is finite, we must decide which data to discard.

### Invalidation Strategies
1. **TTL (Time to Live)**: Each key is assigned an expiration time. Once expired, Redis automatically deletes it.
2. **Manual Invalidation**: The application explicitly deletes the cache key (`DEL key`) when the database is updated.

### Eviction Policies (Redis `maxmemory-policy`)
When Redis reaches its memory limit, it uses these algorithms to free space:
- **LRU (Least Recently Used)**: Discards the least recently accessed keys. (Most common for general caching).
- **LFU (Least Frequently Used)**: Discards keys that are accessed the fewest number of times.
- **FIFO (First In First Out)**: Discards the oldest keys regardless of access frequency.
- **Random**: Randomly removes keys to make space.

---

## 5. Data Flows & Fault Tolerance

### Read Path (Cache-Aside Pattern)
1. App checks Redis for `key`.
2. **Cache Hit**: Return data immediately.
3. **Cache Miss**: 
    - Fetch data from Database.
    - Store data in Redis for future requests.
    - Return data to user.

### Handling Edge Case Failures
| Problem | Description | Solution |
| :--- | :--- | :--- |
| **Cache Penetration** | Requests for keys that exist in neither Cache nor DB. | Use **Bloom Filters** to quickly reject non-existent keys. |
| **Cache Stampede** | Many requests for a single expired key simultaneously. | Implement **Locking** (Mutex) so only one request fetches from DB. |
| **Cache Avalanche** | Many keys expire at the same time, crashing the DB. | Add **Random Jitter** to TTLs (e.g., $TTL = 3600s + \text{random}(0, 300s)$). |

---

## 6. Production Trade-offs

### CAP Theorem Analysis
In the context of Redis:
- **Consistency vs. Availability**: Redis typically favors **Availability** and **Partition Tolerance** (AP). In a clustered setup, asynchronous replication can lead to "stale reads" (Eventual Consistency).
- **Latency vs. Durability**: Using **Write-Back** optimizes for latency but sacrifices durability. Using **AOF (Append Only File)** with `fsync always` increases durability but destroys performance.

### Redis vs. Memcached
- **Redis**: Supports complex data structures (Hashes, Lists, Sets, Sorted Sets), persistence, and replication. Choose this for complex caching needs.
- **Memcached**: Purely a key-value store, multi-threaded. Choose this for extremely simple, high-throughput caching of small strings/objects.

---

## 7. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **GET/SET** | $O(1)$ | $O(1)$ per key | Constant time access. |
| **ZADD (Sorted Set)** | $O(\log N)$ | $O(N)$ | Used for leaderboards. |
| **LRU Eviction** | $O(1)$ | $O(1)$ | Redis approximates LRU via sampling. |
| **Consistent Hashing** | $O(\log N)$ | $O(N)$ | To locate which shard holds the key. |
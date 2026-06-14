# Distributed Rate Limiter HLD

## 1. Overview & System Requirements

A **Distributed Rate Limiter** is a critical infrastructure component used to control the rate of traffic sent by a client to a service. Its primary goal is to protect backend services from being overwhelmed (DoS attacks, noisy neighbors, or buggy clients) and to enforce API quotas.

### Functional Requirements
*   **Request Throttling**: Limit the number of requests a user/client can make within a specific time window (e.g., 100 requests per minute).
*   **Multiple Granularities**: Support limiting by various keys (User ID, IP Address, API Key, or Endpoint).
*   **Clear Feedback**: Return a standard HTTP `429 Too Many Requests` response when the limit is exceeded.
*   **Dynamic Configuration**: Ability to update rate limits without restarting the service.

### Non-Functional Requirements
*   **Ultra-Low Latency**: The rate-limiting check is in the critical path of every request. It must add minimal overhead (typically $< 5\text{ms}$).
*   **High Scalability**: Must handle millions of users and hundreds of thousands of requests per second (QPS).
*   **High Availability**: If the rate limiter service goes down, the system should **fail-open** (allow requests) to ensure user experience isn't degraded by infrastructure failure.
*   **Accuracy**: In a distributed environment, the count should be as accurate as possible, avoiding "double counting" or "missing counts" due to race conditions.

### Scale Assumptions
| Metric | Estimated Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | $10^7$ users |
| **Peak QPS** | $100,000+$ requests per second |
| **Storage Needs** | Minimal (Counters and Timestamps) |
| **Latency Budget** | $\le 2\text{ms}$ for the cache lookup |

---

## 2. High-Level System Architecture

The rate limiter is typically implemented as a **Middleware** or as part of an **API Gateway**.

### Architecture Components
1.  **Client**: The entity making the request.
2.  **API Gateway/Load Balancer**: The entry point that intercepts requests and communicates with the Rate Limiter.
3.  **Rate Limiter Middleware**: The logic layer that decides whether a request should be dropped or passed through.
4.  **Distributed Cache (Redis)**: A high-performance, in-memory store used to track request counts across multiple server nodes.
5.  **Configuration Service**: A store (e.g., ZooKeeper, Consul, or a DB) that holds the limit rules (e.g., `User_A: 100req/min`).

### High-Level Design Diagram (Conceptual)
`Client` $\rightarrow$ `API Gateway` $\rightarrow$ `[Rate Limiter Logic]` $\leftrightarrow$ `[Redis Cluster]` $\rightarrow$ `Backend Services`

---

## 3. Key HLD Concepts & Component Design

### Rate Limiting Algorithms
Choosing the right algorithm depends on the trade-off between memory, accuracy, and the ability to handle bursts.

| Algorithm | How it Works | Pros | Cons | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Fixed Window** | Divide time into fixed slots (e.g., 1 min). Increment counter per slot. | Simple, memory efficient. | "Burst" problem: $2\times$ limit possible at window boundaries. | Simple API quotas. |
| **Sliding Window Log** | Store timestamp of every request. Filter out old timestamps. | Extremely accurate. | Memory intensive ($O(N)$ space per user). | Low-traffic, high-precision limits. |
| **Sliding Window Counter** | Weighted average: $\text{count} = \text{current\_window} + \text{prev\_window} \times \text{overlap\_percentage}$. | Smooths boundaries, memory efficient. | Approximation (not 100% precise). | Most general-purpose APIs. |
| **Token Bucket** | Bucket fills with tokens at a constant rate. Request consumes a token. | Allows bursts, memory efficient. | Slightly more complex to implement. | Cloud-native services (AWS/GCP). |
| **Leaky Bucket** | Requests enter a queue and are processed at a constant rate. | Smooths traffic flow completely. | Bursts are queued; can lead to high latency. | Traffic shaping. |

### Why Redis?
Redis is the industry standard for distributed rate limiting because:
*   **In-Memory Speed**: Sub-millisecond latency.
*   **Atomic Operations**: Commands like `INCR` and `EXPIRE` prevent race conditions.
*   **TTL (Time-to-Live)**: Automatically cleans up old counters, preventing memory leaks.
*   **Lua Scripting**: Allows multiple commands to be executed as a single atomic transaction on the server side.

### Handling Distributed Race Conditions
In a distributed setup, a "read-modify-write" cycle (Get count $\rightarrow$ Increment $\rightarrow$ Set count) is prone to race conditions.
*   **Solution 1: Lua Scripts**: Redis executes Lua scripts atomically. The entire logic of "check limit $\rightarrow$ increment $\rightarrow$ return result" happens in one step.
*   **Solution 2: Redis Sorted Sets (ZSet)**: For Sliding Window Logs, use `ZREMRANGEBYSCORE` to remove old entries and `ZCARD` to count current ones in one transaction.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Flow
1.  **Request Arrival**: Client sends a request to the API Gateway.
2.  **Key Extraction**: Gateway extracts the identifier (e.g., `user_id: 123`).
3.  **Rule Lookup**: Gateway fetches the limit for that user (e.g., 100/min) from a local cache or Configuration Service.
4.  **Cache Check**: Gateway calls the Rate Limiter Logic $\rightarrow$ Redis.
    *   *Lua Script execution*:
        *   `current_count = GET(user_123)`
        *   `if current_count < 100: INCR(user_123); return ALLOW`
        *   `else: return REJECT`
5.  **Response**:
    *   If **ALLOW**: Forward request to the backend service.
    *   If **REJECT**: Return `HTTP 429` with a `Retry-After` header.

### Fault Tolerance & Reliability
*   **Redis Cluster/Sentinel**: Use Redis replication and sharding to ensure the cache is not a single point of failure.
*   **Fail-Open Strategy**: If the Redis cluster is unreachable, the middleware should log the error and **allow the request**. It is better to let a few extra requests through than to block 100% of legitimate traffic.
*   **Local In-Memory Cache (L1 Cache)**: To reduce Redis load, use a tiny local cache (e.g., Caffeine in Java) to store "blocked" users for a few seconds. If a user is already heavily rate-limited, don't even call Redis.

---

## 5. Production Trade-offs

### Consistency vs. Latency (CAP Theorem)
In a global distributed system, you face a choice:
*   **Strong Consistency**: Use a single global Redis cluster. **Pros**: Perfectly accurate. **Cons**: High latency for users far from the cluster.
*   **Eventual Consistency**: Use local Redis clusters in each region and sync them asynchronously. **Pros**: Ultra-low latency. **Cons**: Users might exceed their limit slightly because regions aren't synced in real-time.
*   **Decision**: Most companies choose **Eventual Consistency** or **Regional Limits** (e.g., 100 req/min per region) because availability and latency are more critical for API performance than strict counting.

### Memory vs. Precision
*   **Fixed Window**: Uses $O(1)$ space per user. Low precision at edges.
*   **Sliding Window Log**: Uses $O(N)$ space per user (where $N$ is number of requests). High precision.
*   **Trade-off**: For a system with $10^7$ users, $O(N)$ is unsustainable. **Sliding Window Counter** is the optimal production compromise.

### Complexity Analysis Summary
| Metric | Fixed Window | Sliding Window Log | Token Bucket |
| :--- | :--- | :--- | :--- |
| **Time Complexity** | $O(1)$ | $O(N)$ or $O(\log N)$ | $O(1)$ |
| **Space Complexity** | $O(1)$ | $O(N)$ | $O(1)$ |
| **Accuracy** | Low (Edge cases) | High | High |
| **Implementation** | Trivial | Complex | Moderate |
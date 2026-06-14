INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Distributed Rate Limiter (Token Bucket / Sliding Window).',
    'groups': ['OOP Case Studies', 'Concurrency'],
    'readme_content': """# Distributed Rate Limiter LLD

A **Rate Limiter** is a critical component in modern distributed systems used to control the rate of traffic sent or received by a network interface or a service. It prevents resource starvation, protects against Denial of Service (DoS) attacks, and manages "noisy neighbor" problems in multi-tenant environments.

---

## 1. Overview & System Requirements

### Core Entities
- **Client**: The entity making requests (identified by API Key, User ID, or IP address).
- **Rate Limiter**: The middleware logic that decides whether a request should be allowed or dropped.
- **Storage Layer**: A fast, centralized data store (e.g., Redis) to maintain counters across multiple distributed application servers.
- **Rule Engine**: Defines the limits (e.g., "100 requests per minute for User A").

### Functional Requirements
- **Allow/Deny**: Given a `userId`, determine if the request is within the permitted limit.
- **Dynamic Configuration**: Ability to set different limits for different tiers of users.
- **Distributed State**: Must work consistently across multiple server nodes.
- **Low Latency**: The check must be extremely fast (sub-millisecond) to avoid becoming a bottleneck.

### Non-Functional Requirements
- **Accuracy**: Minimal drift in counting.
- **Scalability**: Handle millions of requests per second.
- **Availability**: The system should fail-open (allow request) if the rate limiter storage is down, rather than blocking all traffic.

---

## 2. Design Principles & Patterns

### OOP Design Principles
- **Single Responsibility Principle (SRP)**: The `RateLimiterManager` handles the orchestration, while the `RateLimitStrategy` handles the specific counting logic, and the `Storage` class handles data persistence.
- **Open/Closed Principle (OCP)**: The system is open for extension (new algorithms like Leaky Bucket can be added) but closed for modification of the core manager.
- **Dependency Inversion Principle (DIP)**: The manager depends on an abstraction (`IRateLimitStrategy`) rather than concrete implementations.

### Design Patterns Applied
| Pattern | Application | Problem Solved |
| :--- | :--- | :--- |
| **Strategy Pattern** | Used to encapsulate different rate-limiting algorithms (Token Bucket, Sliding Window). | Allows switching algorithms at runtime without changing the client code. |
| **Singleton Pattern** | The `RateLimiterManager` is implemented as a singleton. | Ensures a single point of coordination and prevents redundant storage connections. |
| **Factory Pattern** | A `StrategyFactory` creates the required strategy based on configuration. | Decouples the creation logic from the business logic. |

---

## 3. Class Structure & Relationships

### Class Diagram (Text-Based)
```text
+-------------------------+          +----------------------------+
|   RateLimiterManager    |--------->|     IRateLimitStrategy     | (Interface)
|-------------------------|          +----------------------------+
| - storage: IStorage     |          | + allowRequest(id, limit): bool |
| - strategy: IStrategy   |          +-------------^--------------+
| + isAllowed(userId)     |                        |
+-------------------------+                        |
                                    +--------------+---------------+
                                    |                              |
                         +---------------------+        +-----------------------+
                         |  TokenBucketStrategy|        | SlidingWindowStrategy |
                         +---------------------+        +-----------------------+
                         | - refillRate        |        | - windowSize          |
                         +---------------------+        +-----------------------+

+-------------------------+
|       IStorage          | (Interface)
|-------------------------|
| + get(key): value       |
| + set(key, val, ttl)    |
| + increment(key)        |
+-------------------------+
       ^             ^
       |             |
+--------------+ +--------------+
| RedisStorage | | LocalStorage |
+--------------+ +--------------+
```

---

## 4. Step-by-Step Logic & Code Walkthrough

### Algorithm Deep Dive

#### 1. Token Bucket
- **Logic**: Imagine a bucket that holds tokens. Tokens are added at a constant rate. Every request consumes one token. If the bucket is empty, the request is rejected.
- **Formula**: $\text{Current Tokens} = \min(\text{Capacity}, \text{Last Tokens} + (\text{Current Time} - \text{Last Refill Time}) \times \text{Refill Rate})$

#### 2. Sliding Window Log
- **Logic**: Keep a sorted set of timestamps for every request. When a new request arrives, remove all timestamps older than `(Current Time - Window Size)`. If the remaining count is less than the limit, allow the request.

### Implementation

```python
import time
from abc import ABC, abstractmethod
from threading import Lock
from collections import deque

# ==========================================
# Storage Layer (Abstraction for Distributed)
# ==========================================
class IStorage(ABC):
    @abstractmethod
    def get(self, key): pass
    @abstractmethod
    def set(self, key, value, ttl=None): pass
    @abstractmethod
    def incr(self, key): pass

class InMemoryStorage(IStorage):
    \"\"\"Simulates Redis for local demonstration\"\"\"
    def __init__(self):
        self.data = {}
        self.lock = Lock()

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ttl=None):
        with self.lock:
            self.data[key] = value

    def incr(self, key):
        with self.lock:
            self.data[key] = self.data.get(key, 0) + 1
            return self.data[key]

# ==========================================
# Strategy Layer (Algorithm Implementation)
# ==========================================
class IRateLimitStrategy(ABC):
    @abstractmethod
    def is_allowed(self, user_id: str, limit: int, window: int, storage: IStorage) -> bool:
        pass

class TokenBucketStrategy(IRateLimitStrategy):
    def is_allowed(self, user_id: str, limit: int, window: int, storage: IStorage) -> bool:
        # In a real distributed system, this would be a Lua script in Redis 
        # to ensure atomicity.
        key = f"tb_{user_id}"
        now = time.time()
        
        state = storage.get(key) or {"tokens": limit, "last_refill": now}
        
        # Calculate refill
        refill_rate = limit / window 
        elapsed = now - state["last_refill"]
        new_tokens = state["tokens"] + elapsed * refill_rate
        
        current_tokens = min(limit, new_tokens)
        
        if current_tokens >= 1:
            storage.set(key, {"tokens": current_tokens - 1, "last_refill": now})
            return True
        return False

class SlidingWindowStrategy(IRateLimitStrategy):
    def is_allowed(self, user_id: str, limit: int, window: int, storage: IStorage) -> bool:
        # Sliding Window Log implementation
        now = time.time()
        key = f"sw_{user_id}"
        
        # Retrieve request timestamps
        timestamps = storage.get(key) or deque()
        
        # Remove expired timestamps
        while timestamps and timestamps[0] <= now - window:
            timestamps.popleft()
        
        if len(timestamps) < limit:
            timestamps.append(now)
            storage.set(key, timestamps)
            return True
        return False

# ==========================================
# Manager Layer (Context)
# ==========================================
class RateLimiterManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.storage = InMemoryStorage()
                cls._instance.strategy = TokenBucketStrategy() # Default
        return cls._instance

    def set_strategy(self, strategy: IRateLimitStrategy):
        self.strategy = strategy

    def is_allowed(self, user_id: str, limit: int, window: int) -> bool:
        return self.strategy.is_allowed(user_id, limit, window, self.storage)

# ==========================================
# Client Execution
# ==========================================
if __name__ == "__main__":
    limiter = RateLimiterManager()
    
    user = "user_123"
    limit = 5
    window = 10 # seconds

    print("Testing Token Bucket Strategy...")
    for i in range(7):
        allowed = limiter.is_allowed(user, limit, window)
        print(f"Request {i+1}: {'Allowed' if allowed else 'Rejected'}")
    
    print("\nSwitching to Sliding Window Strategy...")
    limiter.set_strategy(SlidingWindowStrategy())
    for i in range(7):
        allowed = limiter.is_allowed(user, limit, window)
        print(f"Request {i+1}: {'Allowed' if allowed else 'Rejected'}")
```

---

## 5. Complexity Analysis

### Time and Space Complexity

| Algorithm | Time Complexity | Space Complexity | Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **Token Bucket** | $O(1)$ | $O(K)$ | Handles bursts, memory efficient. | Slight inaccuracy if not atomic. |
| **Sliding Window** | $O(N)$ | $O(N \times K)$ | Extremely precise. | High memory usage (stores every timestamp). |

*Where $K$ is the number of users and $N$ is the number of requests per window.*

### Distributed Considerations
To make this production-ready for a distributed environment:
1. **Atomicity**: Use **Redis Lua Scripts**. Since Redis is single-threaded, a Lua script ensures that the "read-modify-write" cycle of updating tokens happens atomically.
2. **Race Conditions**: In a multi-node setup, simple `get` and `set` lead to race conditions. Lua scripts or `SETNX` (Set if Not Exists) are mandatory.
3. **Clock Drift**: In a distributed system, system clocks are never perfectly synchronized. The sliding window depends on timestamps; using a centralized Redis server time (`TIME` command) mitigates this.

## 6. Real-World Applications

1. **API Gateways (AWS API Gateway, Kong, Apigee)**: Every professional API gateway implements these patterns to prevent backend services from being overwhelmed.
2. **Payment Gateways (Stripe, PayPal)**: To prevent "carding" attacks (brute-forcing credit card numbers), strict rate limits are applied to the `/charge` endpoints.
3. **Cloud Rate Limiting (Google Cloud Armor, Cloudflare)**: These systems use distributed rate limiting at the edge to mitigate DDoS attacks before traffic even reaches the application origin.
4. **Microservices Sidecars (Istio, Linkerd)**: Service meshes use rate limiting to implement "Circuit Breaker" patterns and protect internal service-to-service communication.""",
    'solutions': """# Design Document: Distributed Rate Limiter

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Request Throttling:** Limit the number of requests a user/client can make to an API within a specific time window.
*   **Multi-tenant Support:** Apply different rate limits based on user tiers (e.g., Free: 100 req/min, Premium: 1000 req/min).
*   **Granular Control:** Ability to set limits per API endpoint, per user ID, or per IP address.
*   **Standard Response:** Return `HTTP 429 Too Many Requests` when the limit is exceeded, including headers indicating the remaining quota and reset time.
*   **Dynamic Configuration:** Update rate limits without requiring a service restart.

### 1.2 Non-Functional Requirements
*   **Low Latency:** The rate limiting check must add negligible overhead (typically < 2ms) to the request pipeline.
*   **High Availability:** The system must be highly available. If the rate limiter fails, the system should "fail-open" (allow requests) to ensure user experience isn't broken.
*   **Distributed Accuracy:** The count must be synchronized across multiple application nodes in a distributed cluster.
*   **Scalability:** Handle millions of unique users and hundreds of thousands of requests per second (RPS).

### 1.3 Scale Estimations (Example)
*   **Traffic:** 100,000 RPS.
*   **Users:** 10 million active users.
*   **Storage:** If using a sliding window log with 100 requests per window, we might store $10^7 \times 100$ timestamps. However, using a counter-based approach reduces this significantly.
*   **Latency Budget:** $\approx 1 \text{ms}$ for Redis lookup + $\approx 0.5 \text{ms}$ for network round-trip.

---

## 2. High-Level Architecture

The Distributed Rate Limiter is implemented as a middleware layer (or a sidecar) that intercepts requests before they reach the backend business logic.

### 2.1 Component Interaction
1.  **Client** sends a request.
2.  **API Gateway / Middleware** intercepts the request and extracts the identifier (API Key, User ID, or IP).
3.  **Rate Limiter Service** fetches the applicable rule for that identifier.
4.  **Distributed Cache (Redis)** stores the current counters/buckets. The service executes an atomic operation (via Lua script) to check if the request is allowed.
5.  **Decision:**
    *   **Allowed:** Request is forwarded to the **Backend Service**.
    *   **Throttled:** Request is rejected with `HTTP 429`.

### 2.2 Architecture Diagram

```mermaid
graph TD
    Client[Client/User] --> LB[Load Balancer]
    LB --> Gateway[API Gateway / Middleware]
    
    subgraph "Rate Limiting Layer"
        Gateway --> RL_Logic[Rate Limiter Logic]
        RL_Logic --> LocalCache[L1 Local Cache - Rules]
        RL_Logic --> Redis[(Redis Cluster - Counters)]
    end
    
    RL_Logic --> Backend[Backend Microservices]
    
    ConfigDB[(Configuration DB)] --> ConfigSvc[Config Service]
    ConfigSvc --> LocalCache
```

---

## 3. Detailed Design

### 3.1 Algorithm Selection

We will implement a hybrid approach supporting both **Token Bucket** (for bursty traffic) and **Sliding Window Counter** (for smooth limiting).

#### A. Token Bucket (Best for Bursts)
*   **Concept:** A bucket has a maximum capacity $C$. Tokens are added at a constant rate $R$. Each request consumes one token.
*   **Distributed Logic:** Instead of a background timer to refill tokens, we calculate the refill amount lazily upon request:
    $$\text{tokens\_to\_add} = (\text{current\_time} - \text{last\_refill\_time}) \times \text{refill\_rate}$$

#### B. Sliding Window Counter (Best for Precision)
*   **Concept:** Divide time into small buckets (e.g., 1 minute divided into 60 one-second buckets). 
*   **Logic:** Current window count = $\text{count in current bucket} + (\text{count in previous bucket} \times \text{overlap percentage})$.

### 3.2 Database & Storage Design

#### 3.2.1 Configuration Store (SQL)
Used for managing rate limit rules. A relational database is chosen for strong consistency and easy querying.

**Table: `rate_limit_rules`**
| Field | Type | Description |
| :--- | :--- | :--- |
| `rule_id` | UUID (PK) | Unique identifier for the rule |
| `resource_path` | String | API endpoint (e.g., `/v1/payment`) |
| `tier` | Enum | FREE, PREMIUM, ENTERPRISE |
| `limit` | Integer | Max requests allowed |
| `window_size` | Integer | Time window in seconds |
| `algorithm` | Enum | TOKEN_BUCKET, SLIDING_WINDOW |

**Index:** `idx_resource_tier` on `(resource_path, tier)`.

#### 3.2.2 Distributed State Store (Redis)
Redis is used for counters due to its in-memory speed and atomic operations.

**Token Bucket Key Schema:**
*   **Key:** `rl:token_bucket:{userId}:{resourceId}`
*   **Value:** Hash map `{ "tokens": 45, "last_updated": 1625000000 }`

**Sliding Window Key Schema:**
*   **Key:** `rl:sliding_window:{userId}:{resourceId}`
*   **Value:** Sorted Set (ZSET). Member = `unique_request_id`, Score = `timestamp`.

### 3.3 Core API Design (Management)

These endpoints allow administrators to modify rate limits dynamically.

**1. Create/Update Rule**
`POST /admin/rate-limits`
```json
{
  "resource_path": "/api/v1/upload",
  "tier": "FREE",
  "limit": 50,
  "window_size": 3600,
  "algorithm": "TOKEN_BUCKET"
}
```

**2. Get Current Limit Status (Internal/Debug)**
`GET /admin/rate-limits/status?userId=123&resource=/api/v1/upload`
```json
{
  "userId": "123",
  "remaining": 12,
  "reset_time": "2023-10-27T10:05:00Z",
  "limit": 50
}
```

---

## 4. Scalability & Advanced Topics

### 4.1 Atomicity and Race Conditions
In a distributed environment, a "read-modify-write" cycle leads to race conditions. To prevent this, we use **Redis Lua Scripts**. Lua scripts are executed atomically in Redis, ensuring that the check and the decrement of tokens happen as a single operation.

**Example Lua Logic for Token Bucket:**
```lua
local key = KEYS[1]
local rate = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local bucket = redis.call('hmget', key, 'tokens', 'last_updated')
local tokens = tonumber(bucket[1]) or capacity
local last_updated = tonumber(bucket[2]) or now

local delta = math.max(0, now - last_updated) * rate
tokens = math.min(capacity, tokens + delta)

if tokens >= requested then
    redis.call('hmset', key, 'tokens', tokens - requested, 'last_updated', now)
    return 1 -- Allowed
else
    return 0 -- Throttled
end
```

### 4.2 Optimization Strategies
*   **L1 Local Cache:** To avoid hitting Redis for every request just to fetch the *rule* (e.g., "FREE tier = 100 req/min"), we cache rules in the application memory for 1-5 minutes.
*   **Redis Sharding:** Partition the Redis cluster based on the `userId` hash to ensure load is distributed across multiple Redis nodes.
*   **Batching:** For extremely high volume, use a "local aggregation" strategy where the middleware counts requests locally and syncs with Redis every 100ms. (Trade-off: slight loss in accuracy).

### 4.3 Fault Tolerance
*   **Fail-Open Mechanism:** If the Redis cluster is unreachable, the middleware should log an error and allow the request to pass. It is better to allow a few extra requests than to take down the entire API.
*   **Redis Sentinel/Cluster:** Use Redis Sentinel for automatic failover and Redis Cluster for horizontal scaling.

---

## 5. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs. Latency** | Eventual Consistency (for rules) / Strong (for counters) | Rules change rarely, so L1 caching is fine. Counters must be accurate to prevent API abuse, hence Redis Lua scripts. |
| **Accuracy vs. Memory** | Sliding Window Counter | A Sliding Window Log (ZSET) is perfectly accurate but consumes $O(N)$ memory per user. A Counter approach uses $O(1)$ memory per window. |
| **Availability vs. Strictness** | Fail-Open | In a production environment, denying legitimate traffic due to a rate-limiter outage is a higher business risk than allowing a temporary burst of traffic. |
| **Storage: SQL vs NoSQL** | Hybrid | SQL for structured, relational rule management; NoSQL (Redis) for high-throughput, ephemeral state. |

## 6. Summary of Time and Space Complexity

*   **Time Complexity:** $O(1)$ for Token Bucket and Sliding Window Counter per request.
*   **Space Complexity:** $O(U \times R)$ where $U$ is the number of unique users and $R$ is the number of resources being limited.""",
}

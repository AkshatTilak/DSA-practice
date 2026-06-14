# Distributed Rate Limiter LLD

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
    """Simulates Redis for local demonstration"""
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
4. **Microservices Sidecars (Istio, Linkerd)**: Service meshes use rate limiting to implement "Circuit Breaker" patterns and protect internal service-to-service communication.
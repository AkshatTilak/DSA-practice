# Key-Value (KV) Store LLD

A Key-Value store is a non-relational database that uses an associative array as the fundamental data model. Designing a system like **Redis** requires a deep understanding of memory management, concurrency, and efficient data structures to ensure low-latency operations.

---

## 1. Overview & System Requirements

The goal is to design an in-memory Key-Value store that supports basic CRUD operations, time-to-live (TTL) for keys, and an eviction policy to handle memory constraints.

### Functional Requirements
| Feature | Description |
| :--- | :--- |
| **Basic CRUD** | Support `put(key, value)`, `get(key)`, and `delete(key)`. |
| **TTL (Time-to-Live)** | Allow keys to be set with an expiration time. Expired keys should be treated as non-existent. |
| **Eviction Policy** | When the store reaches maximum capacity, it must evict keys based on a strategy (e.g., **LRU - Least Recently Used**). |
| **Thread Safety** | The store must handle concurrent reads and writes safely. |
| **Generic Values** | Support for different data types (Strings, Integers, etc.) through generic handling. |

### Non-Functional Requirements
- **Low Latency**: All primary operations should ideally run in $O(1)$ average time complexity.
- **Extensibility**: Easy to add new eviction policies (LFU, FIFO) without modifying the core store logic.
- **Reliability**: Ensure no data corruption during concurrent access.

---

## 2. Design Principles & Patterns

### OOP Design Principles (SOLID)
- **Single Responsibility Principle (SRP)**: The `KVStore` class manages the API, the `StorageEngine` manages data retrieval, and the `EvictionPolicy` manages memory constraints.
- **Open/Closed Principle (OCP)**: By using an interface for `EvictionPolicy`, we can add new policies (like LFU) without changing the `KVStore` code.
- **Dependency Inversion Principle (DIP)**: `KVStore` depends on the `EvictionPolicy` abstraction rather than a concrete `LRUPolicy` class.

### Design Patterns Applied
1. **Strategy Pattern**: Used for the **Eviction Policy**. Since different use cases require different eviction logic (LRU vs. LFU), the strategy pattern allows switching the algorithm at runtime.
2. **Singleton Pattern**: The `KVStore` instance is typically implemented as a singleton to ensure a single point of truth for the in-memory cache across the application.
3. **Facade Pattern**: The `KVStore` class acts as a facade, hiding the complexity of the `StorageEngine`, `TTLManager`, and `EvictionPolicy` from the end user.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
+-------------------+           +-----------------------+
|     KVStore       |---------->|    EvictionPolicy     | (Interface)
+-------------------+           +-----------------------+
| - capacity: int   |           | + keyAccessed(key)    |
| - store: Map      |           | + evict() : key       |
| - policy: IPolicy |           | + removeKey(key)      |
+-------------------+           +-----------^-----------+
| + put(k, v, ttl)  |                       |
| + get(k)          |           +-----------+-----------+
| + delete(k)       |           |           |           |
+-------------------+    +------+------+ +---+---+ +-----+-----+
                         | LRUPolicy   | | LFUPolicy | | FIFOPolicy |
                         +-------------+ +-----------+ +-----------+

+-------------------+
|      KVEntry      |
+-------------------+
| - value: any      |
| - expiry: timestamp|
+-------------------+
```

### Relationship Definitions
- **Composition**: `KVStore` **has-a** `EvictionPolicy`.
- **Association**: `KVStore` stores `KVEntry` objects in a Hash Map.
- **Inheritance**: `LRUPolicy` and `LFUPolicy` **implement** the `EvictionPolicy` interface.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
import time
from threading import Lock
from collections import OrderedDict
from abc import ABC, abstractmethod
from typing import Any, Optional

# 1. Strategy Pattern for Eviction Policies
class EvictionPolicy(ABC):
    @abstractmethod
    def key_accessed(self, key: str):
        pass

    @abstractmethod
    def evict(self) -> Optional[str]:
        pass

    @abstractmethod
    def remove_key(self, key: str):
        pass

class LRUPolicy(EvictionPolicy):
    def __init__(self):
        self.order = OrderedDict()

    def key_accessed(self, key: str):
        # Move to end to mark as most recently used
        if key in self.order:
            self.order.move_to_end(key)
        else:
            self.order[key] = True

    def evict(self) -> Optional[str]:
        if not self.order:
            return None
        # Pop the first item (Least Recently Used)
        key, _ = self.order.popitem(last=False)
        return key

    def remove_key(self, key: str):
        if key in self.order:
            del self.order[key]

# 2. Entity to store value and metadata
class KVEntry:
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.expiry = (time.time() + ttl_seconds) if ttl_seconds else None

    def is_expired(self) -> bool:
        if self.expiry is None:
            return False
        return time.time() > self.expiry

# 3. Main KV Store Implementation
class KVStore:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # Singleton Pattern
        with cls._lock:
            if not cls._instance:
                cls._instance = super(KVStore, cls).__new__(cls)
        return cls._instance

    def __init__(self, capacity: int = 100, policy: EvictionPolicy = None):
        if hasattr(self, 'initialized'): return
        self.capacity = capacity
        self.store = {}
        self.policy = policy if policy else LRUPolicy()
        self.lock = Lock()
        self.initialized = True

    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        with self.lock:
            if key not in self.store and len(self.store) >= self.capacity:
                evicted_key = self.policy.evict()
                if evicted_key:
                    print(f"Evicting key: {evicted_key}")
                    del self.store[evicted_key]

            self.store[key] = KVEntry(value, ttl)
            self.policy.key_accessed(key)

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            entry = self.store.get(key)
            if not entry:
                return None

            if entry.is_expired():
                print(f"Key {key} expired.")
                self.delete(key)
                return None

            self.policy.key_accessed(key)
            return entry.value

    def delete(self, key: str):
        with self.lock:
            if key in self.store:
                del self.store[key]
                self.policy.remove_key(key)

# --- Testing the Implementation ---
if __name__ == "__main__":
    # Initialize store with capacity of 2
    kv = KVStore(capacity=2, policy=LRUPolicy())

    kv.put("a", 1)
    kv.put("b", 2)
    print(f"Get a: {kv.get('a')}") # a is accessed, becomes MRU
    
    kv.put("c", 3) # Capacity reached, should evict 'b' (LRU)
    
    print(f"Get b: {kv.get('b')}") # Should be None
    print(f"Get c: {kv.get('c')}") # Should be 3

    kv.put("d", 4, ttl=1) # Key d expires in 1 second
    print(f"Get d immediately: {kv.get('d')}")
    time.sleep(1.1)
    print(f"Get d after 1s: {kv.get('d')}") # Should be None
```

### Logic Walkthrough
1.  **`put(key, value, ttl)`**:
    *   Acquires a **Thread Lock** to ensure atomicity.
    *   Checks if the key exists. If it's a new key and the store is at `capacity`, it calls `policy.evict()` to free space.
    *   Creates a `KVEntry` object (storing the value and calculated expiry timestamp).
    *   Updates the `EvictionPolicy` to mark the key as "accessed".
2.  **`get(key)`**:
    *   Retrieves the `KVEntry`.
    *   **Lazy Expiration**: Instead of a background thread constantly scanning for expired keys, the store checks if a key is expired at the moment it is accessed. If expired, it deletes it and returns `None`.
    *   Updates the `EvictionPolicy` to move the key to the "most recently used" position.
3.  **`evict()`**:
    *   In the `LRUPolicy`, we use an `OrderedDict`. The first item in the dictionary is always the least recently used. `popitem(last=False)` removes it in $O(1)$.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| **Put** | $O(1)$ | $O(1)$ | Hash map insertion and OrderedDict update are constant time. |
| **Get** | $O(1)$ | $O(1)$ | Hash map lookup and OrderedDict move are constant time. |
| **Delete** | $O(1)$ | $O(1)$ | Hash map and OrderedDict removal are constant time. |
| **Evict** | $O(1)$ | $O(1)$ | Popping from the head of an `OrderedDict` is constant time. |
| **Overall** | - | $O(N)$ | Where $N$ is the maximum capacity of the store. |

---

## 6. Real-World Applications

This LLD pattern is the foundation for several industry-standard systems:

1.  **Redis**: Uses a similar approach but implements more complex data structures (SkipLists for sorted sets, ZipLists for memory efficiency) and active expiration (periodic random sampling of keys).
2.  **Memcached**: A high-performance distributed memory object caching system that uses LRU for eviction.
3.  **Database Buffer Pools**: SQL databases (like MySQL/PostgreSQL) use LRU-based page replacement algorithms to decide which data pages to keep in RAM.
4.  **Browser Caches**: Web browsers use similar KV structures to store cached assets, evicting old files based on size and access frequency.
# Caching Framework LLD

A **Caching Framework** is a critical system component designed to store frequently accessed data in high-speed memory to reduce latency and decrease the load on primary storage (like databases). This LLD focuses on creating a **pluggable, thread-safe framework** that supports multiple eviction policies, primarily **LRU (Least Recently Used)** and **LFU (Least Frequently Used)**.

---

## 1. Overview & System Requirements

### Core Objective
Design a generic caching system where the eviction logic is decoupled from the storage logic, allowing developers to swap eviction strategies at runtime or configuration time without altering the core cache code.

### Functional Requirements
- **`get(key)`**: Retrieve the value associated with the key. This operation must notify the eviction policy that the key was accessed.
- **`put(key, value)`**: Insert or update a value. If the cache reaches its maximum capacity, the eviction policy must determine which key to remove.
- **Pluggable Policies**: Support for **LRU** (evict based on time of last access) and **LFU** (evict based on frequency of access).
- **Thread Safety**: The framework must handle concurrent access from multiple threads without data corruption.
- **Genericity**: The cache should support any data type for keys and values.

### Non-Functional Requirements
- **Time Complexity**: All primary operations (`get`, `put`) should ideally operate in $O(1)$ time.
- **Space Complexity**: $O(N)$ where $N$ is the maximum capacity of the cache.

---

## 2. Design Principles & Patterns

### OOP Design Principles
- **Single Responsibility Principle (SRP)**: 
    - The `Cache` class manages data storage and synchronization.
    - The `EvictionPolicy` classes manage the logic of *which* key to remove.
- **Open/Closed Principle (OCP)**: The system is open for extension (adding new policies like FIFO or ARC) but closed for modification (no need to change the `Cache` class to add a policy).
- **Dependency Inversion Principle (DIP)**: The `Cache` class depends on the `EvictionPolicy` interface, not on concrete implementations like `LRUPolicy` or `LFUPolicy`.

### Design Patterns Applied
- **Strategy Pattern**: This is the core pattern used here. The `EvictionPolicy` acts as the strategy interface, and `LRUPolicy` and `LFUPolicy` are concrete strategies. This decouples the cache's storage mechanism from its eviction algorithm.
- **Singleton Pattern (Optional)**: Often applied to the Cache instance in production to ensure a single global cache across an application.
- **Factory Pattern**: Can be used to instantiate the `Cache` with a specific policy based on a configuration string (e.g., `"LRU"` $\rightarrow$ `LRUPolicy`).

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
+-------------------+           +-----------------------+
|       Cache       | --------> |    EvictionPolicy     | (Interface)
+-------------------+           +-----------------------+
| - capacity: int   |           | + keyAccessed(key)    |
| - storage: Map    |           | + keyAdded(key)       |
| - policy: Policy  |           | + evict(): Key        |
| - lock: RLock     |           | + keyRemoved(key)     |
+-------------------+           +-----------^-----------+
| + get(key)        |                       |
| + put(key, val)   |           +-----------+-----------+
+-------------------+           |                       |
                        +-------------------+   +-------------------+
                        |    LRUPolicy      |   |    LFUPolicy      |
                        +-------------------+   +-------------------+
                        | - dll: DoublyList |   | - freqMap: Map    |
                        | - map: Map        |   | - lists: Map      |
                        +-------------------+   +-------------------+
```

### Relationship Definitions
- **Composition**: `Cache` has a `EvictionPolicy`.
- **Inheritance/Implementation**: `LRUPolicy` and `LFUPolicy` implement the `EvictionPolicy` interface.
- **Association**: `Cache` uses a `Map` for $O(1)$ storage access.

---

## 4. Implementation

```python
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, OrderedDict

# ==========================================
# 1. Eviction Policy Interface
# ==========================================
class EvictionPolicy(ABC):
    @abstractmethod
    def key_accessed(self, key):
        pass

    @abstractmethod
    def key_added(self, key):
        pass

    @abstractmethod
    def evict(self):
        pass

    @abstractmethod
    def key_removed(self, key):
        pass

# ==========================================
# 2. Concrete Policy: LRU (Least Recently Used)
# ==========================================
class LRUPolicy(EvictionPolicy):
    def __init__(self):
        # OrderedDict maintains insertion order; we move accessed items to the end
        self.order = OrderedDict()

    def key_accessed(self, key):
        if key in self.order:
            self.order.move_to_end(key)

    def key_added(self, key):
        self.order[key] = None

    def evict(self):
        # Pop the first item (the least recently used)
        key, _ = self.order.popitem(last=False)
        return key

    def key_removed(self, key):
        if key in self.order:
            del self.order[key]

# ==========================================
# 3. Concrete Policy: LFU (Least Frequently Used)
# ==========================================
class LFUPolicy(EvictionPolicy):
    def __init__(self):
        self.key_freq = {} # key -> frequency
        self.freq_keys = defaultdict(OrderedDict) # freq -> {key: None}
        self.min_freq = 0

    def key_accessed(self, key):
        freq = self.key_freq[key]
        # Remove from current freq bucket
        del self.freq_keys[freq][key]
        
        # If this was the min_freq bucket and it's now empty, increment min_freq
        if freq == self.min_freq and not self.freq_keys[freq]:
            self.min_freq += 1
            
        # Update frequency and move to next bucket
        new_freq = freq + 1
        self.key_freq[key] = new_freq
        self.freq_keys[new_freq][key] = None

    def key_added(self, key):
        self.key_freq[key] = 1
        self.freq_keys[1][key] = None
        self.min_freq = 1

    def evict(self):
        # Evict the oldest item (LRU) from the lowest frequency bucket (LFU)
        key, _ = self.freq_keys[self.min_freq].popitem(last=False)
        del self.key_freq[key]
        return key

    def key_removed(self, key):
        freq = self.key_freq.get(key)
        if freq:
            del self.freq_keys[freq][key]
            del self.key_freq[key]

# ==========================================
# 4. Main Cache Framework
# ==========================================
class Cache:
    def __init__(self, capacity: int, policy: EvictionPolicy):
        self.capacity = capacity
        self.storage = {}
        self.policy = policy
        self.lock = threading.RLock() # Re-entrant lock for thread safety

    def get(self, key):
        with self.lock:
            if key not in self.storage:
                return None
            
            self.policy.key_accessed(key)
            return self.storage[key]

    def put(self, key, value):
        with self.lock:
            if key in self.storage:
                self.storage[key] = value
                self.policy.key_accessed(key)
                return

            if len(self.storage) >= self.capacity:
                evicted_key = self.policy.evict()
                del self.storage[evicted_key]

            self.storage[key] = value
            self.policy.key_added(key)

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # Test LRU
    print("Testing LRU Cache...")
    lru_cache = Cache(2, LRUPolicy())
    lru_cache.put(1, "A")
    lru_cache.put(2, "B")
    lru_cache.get(1)       # Access 1, making 2 the LRU
    lru_cache.put(3, "C")  # Evicts 2
    print(f"Key 2 (evicted): {lru_cache.get(2)}") # Expected: None
    print(f"Key 1 (kept): {lru_cache.get(1)}")    # Expected: A

    # Test LFU
    print("\nTesting LFU Cache...")
    lfu_cache = Cache(2, LFUPolicy())
    lfu_cache.put(1, "A")
    lfu_cache.put(2, "B")
    lfu_cache.get(1)       # Freq of 1 becomes 2
    lfu_cache.put(3, "C")  # Evicts 2 (freq 1)
    print(f"Key 2 (evicted): {lfu_cache.get(2)}") # Expected: None
    print(f"Key 1 (kept): {lfu_cache.get(1)}")    # Expected: A
```

---

## 5. Step-by-Step Logic Walkthrough

### The `get(key)` Workflow
1. **Locking**: Acquire the `RLock` to prevent other threads from modifying the cache during the read and policy update.
2. **Lookup**: Check if the key exists in the `storage` map.
3. **Policy Update**: If it exists, call `policy.key_accessed(key)`. 
   - For **LRU**, this moves the key to the "most recent" end of the list.
   - For **LFU**, this increments the frequency count and moves the key to the corresponding frequency bucket.
4. **Return**: Return the value.

### The `put(key, value)` Workflow
1. **Locking**: Acquire the `RLock`.
2. **Update existing**: If the key is already present, update the value and call `key_accessed`.
3. **Capacity Check**: If the key is new and the cache is full:
   - Call `policy.evict()`.
   - The policy returns the key that should be removed (e.g., the head of the LRU list or the oldest item in the `min_freq` bucket).
   - Remove that key from `storage`.
4. **Insertion**: Add the new value to `storage` and notify the policy via `key_added(key)`.

---

## 6. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| `get(key)` | $O(1)$ | $O(1)$ | Hash map lookup + Policy update (DLL/Bucket movement) |
| `put(key, val)` | $O(1)$ | $O(1)$ | Hash map insertion + Policy eviction ($O(1)$ removal) |
| **Total Space** | - | $O(N)$ | Storage map and Policy tracking structures scale linearly with capacity |

---

## 7. Real-World Applications

1. **Redis**: Uses various eviction policies including `allkeys-lru`, `volatile-lru`, and `allkeys-lfu` to manage memory limits.
2. **Memcached**: Primarily utilizes an LRU-based eviction mechanism.
3. **CPU Cache**: Hardware-level caches use Pseudo-LRU algorithms to decide which cache line to replace.
4. **Web Browsers**: Browsers cache images and scripts using LRU to ensure that the most frequently visited pages load fastest while staying within a disk quota.
5. **Database Buffer Pool**: Databases like PostgreSQL and MySQL use sophisticated caching (often based on LRU or a variation called "Clock" algorithm) to keep hot pages in RAM.
INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Caching Framework (LRU/LFU, Thread-safe).',
    'groups': ['OOP Case Studies', 'Caching & Storage'],
    'readme_content': """# Caching Framework LLD

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
5. **Database Buffer Pool**: Databases like PostgreSQL and MySQL use sophisticated caching (often based on LRU or a variation called "Clock" algorithm) to keep hot pages in RAM.""",
    'solutions': """# Solution Guide: Generic Thread-Safe Caching Framework

## 1. Requirements & System Constraints

The objective is to design a professional-grade, generic caching framework that allows developers to store key-value pairs in memory with a defined eviction policy to prevent memory exhaustion.

### 1.1 Functional Requirements
*   **Generic Support**: The cache must support any data type for keys (`K`) and values (`V`).
*   **Basic Operations**:
    *   `put(K key, V value)`: Insert or update a value. If the cache is at capacity, trigger eviction.
    *   `get(K key)`: Retrieve a value. This operation should update the "recency" or "frequency" of the key.
    *   `remove(K key)`: Explicitly remove an item from the cache.
*   **Eviction Policies**:
    *   **LRU (Least Recently Used)**: Discard the least recently accessed items first.
    *   **LFU (Least Frequently Used)**: Discard items with the lowest access frequency first.
*   **Capacity Management**: A fixed maximum size must be configurable at initialization.

### 1.2 Non-Functional Requirements
*   **Time Complexity**: Both `get` and `put` operations must operate in $O(1)$ average time complexity.
*   **Thread Safety**: The framework must be safe for concurrent access by multiple threads without corrupting the internal state.
*   **Extensibility**: It should be easy to add new eviction policies (e.g., FIFO, MRU) using the Strategy Pattern.
*   **Low Overhead**: Minimal memory overhead beyond the storage of the data itself.

---

## 2. High-Level Architecture

The system is designed using a decoupled architecture where the cache management logic is separated from the specific eviction strategy.

### 2.1 Component Overview
*   **`Cache<K, V>`**: The primary interface providing the API to the user.
*   **`EvictionPolicy<K>`**: An interface/abstract class that defines how keys are tracked and which key should be evicted.
*   **`LRUEvictionPolicy` / `LFUEvictionPolicy`**: Concrete implementations of the eviction logic.
*   **`StorageEngine`**: A thread-safe map (e.g., `ConcurrentHashMap`) that stores the actual data.
*   **`CacheManager`**: Orchestrates the interaction between the storage engine and the eviction policy.

### 2.2 Architecture Diagram

```mermaid
graph TD
    User((Client/User)) --> CacheAPI[Cache Interface]
    CacheAPI --> CacheManager[Cache Manager]
    CacheManager --> Storage[(Storage Engine - Map)]
    CacheManager --> EvictionStrategy{Eviction Strategy}
    EvictionStrategy --> LRU[LRU Implementation]
    EvictionStrategy --> LFU[LFU Implementation]
    
    subgraph "Internal Logic"
        LRU --> DLL1[Doubly Linked List]
        LFU --> FreqMap[Frequency Map + Linked Lists]
    end
```

---

## 3. Detailed Design (Data Structures)

Since this is a Low-Level Design (LLD), we replace "Database Schema" with "Internal Data Structure Design."

### 3.1 LRU Implementation Design
To achieve $O(1)$ for both access and update, we combine a **HashMap** with a **Doubly Linked List (DLL)**.

*   **HashMap**: Stores `Key -> Node` mapping. Provides $O(1)$ access to any node in the DLL.
*   **Doubly Linked List**: Maintains the order of usage. 
    *   **Head**: Most Recently Used (MRU).
    *   **Tail**: Least Recently Used (LRU).
*   **Operation Logic**:
    *   `get(key)`: Find node via map $\rightarrow$ Move node to Head $\rightarrow$ Return value.
    *   `put(key, value)`: 
        *   If key exists: Update value $\rightarrow$ Move node to Head.
        *   If key is new: Create node $\rightarrow$ Add to Head $\rightarrow$ If size > capacity, remove node at Tail $\rightarrow$ Remove Tail key from map.

### 3.2 LFU Implementation Design
LFU is more complex because it requires tracking the number of hits. We use a **HashMap** for values and a **Frequency Map** containing sets of keys.

*   **Value Map**: `Map<K, CacheNode>` where `CacheNode` contains the value and current frequency.
*   **Frequency Map**: `Map<Integer, DoublyLinkedList<K>>`.
    *   Key: The frequency count (e.g., 1, 2, 5).
    *   Value: A doubly linked list of all keys that have been accessed that many times.
*   **Min Frequency Tracker**: An integer `minFreq` to track the lowest current frequency for $O(1)$ eviction.
*   **Operation Logic**:
    *   `get(key)`: 
        1. Access node $\rightarrow$ current frequency $f$.
        2. Remove key from `FreqMap.get(f)`.
        3. If `FreqMap.get(f)` is empty and $f == minFreq$, increment `minFreq`.
        4. Add key to `FreqMap.get(f + 1)`.
    *   `put(key, value)`: 
        1. If key exists: Update value $\rightarrow$ Perform `get(key)` logic to update frequency.
        2. If key is new:
           - If size == capacity: Evict the first node from `FreqMap.get(minFreq)`.
           - Insert new node $\rightarrow$ Set freq = 1 $\rightarrow$ Add to `FreqMap.get(1)` $\rightarrow$ Set `minFreq = 1`.

### 3.3 Thread-Safety Mechanism
To ensure thread safety while maintaining high throughput:
1.  **Fine-Grained Locking**: Instead of synchronizing the entire `put`/`get` methods (which creates a bottleneck), use a `ReentrantReadWriteLock`.
    *   `ReadLock`: Allows multiple threads to perform `get()` if the eviction policy doesn't require a structural write (though LRU/LFU usually do, making `get` effectively a write operation).
2.  **Concurrent Collections**: Use `ConcurrentHashMap` for the primary storage to handle concurrent bucket access.
3.  **Synchronized Blocks**: Use synchronization specifically around the manipulation of the Doubly Linked List pointers to prevent race conditions.

---

## 4. Core API Design

The framework is designed as a generic library.

### 4.1 Interface Definitions (Java-style)

```java
public interface Cache<K, V> {
    V get(K key);
    void put(K key, V value);
    void remove(K key);
    void clear();
    int size();
}

public interface EvictionPolicy<K> {
    void keyAccessed(K key);
    K evict();
    void keyAdded(K key);
    void keyRemoved(K key);
}
```

### 4.2 Example Usage

```java
// Create a thread-safe LRU Cache with capacity of 1000
Cache<String, UserProfile> userCache = CacheFactory.createCache(
    1000, 
    EvictionStrategy.LRU, 
    ConcurrencyLevel.HIGH
);

userCache.put("user_123", profileObj);
UserProfile profile = userCache.get("user_123");
```

---

## 5. Scalability & Advanced Topics

### 5.1 Memory Management & GC
*   **Soft References**: To prevent `OutOfMemoryError`, values can be wrapped in `SoftReference<V>`. This allows the JVM Garbage Collector to reclaim cache memory if the heap is full, even before the eviction policy triggers.
*   **Off-Heap Storage**: For extremely large caches, use `DirectByteBuffer` or libraries like Ohc to move data outside the JVM heap, reducing GC pause times.

### 5.2 Distributed Caching (Expansion)
If this LLD needs to scale to a distributed environment:
*   **Consistent Hashing**: Use consistent hashing to distribute keys across multiple cache nodes to minimize reshuffling when nodes are added/removed.
*   **Cache Protocols**:
    *   **Write-through**: Write to cache and DB simultaneously.
    *   **Write-behind (Write-back)**: Write to cache, then asynchronously update DB.
    *   **Cache-aside**: Application checks cache; on miss, loads from DB and populates cache.

### 5.3 Performance Optimizations
*   **Striping**: Divide the cache into segments (similar to `ConcurrentHashMap` in Java 7) to reduce lock contention. Each segment has its own lock and eviction list.
*   **Approximate LRU**: Instead of a perfect DLL (which requires a lock on every `get`), use a "Clock Algorithm" or "Segmented LRU" to reduce synchronization overhead.

---

## 6. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **LRU vs LFU** | LRU (Default) | LRU is generally better for workloads with "temporal locality" (recently accessed items are likely to be accessed again). LFU is better for "frequency-based" patterns but suffers from "cache pollution" (items accessed many times in the past but no longer needed). |
| **Locking vs Lock-Free** | ReadWriteLock | While lock-free structures (using CAS) are faster, the complexity of maintaining a Doubly Linked List lock-free is extremely high. `ReadWriteLock` provides a balance of safety and performance. |
| **Time vs Space** | $O(1)$ Time | We sacrifice space (storing pointers in DLL and keys in a Map) to ensure that cache lookups do not become the bottleneck of the application. |
| **Strong vs Eventual Consistency** | Strong | Since this is an in-memory framework, we prioritize strong consistency for `put` and `get` operations within a single JVM instance. |

### Complexity Summary
| Operation | LRU Time | LFU Time | Space Complexity |
| :--- | :--- | :--- | :--- |
| `get(key)` | $O(1)$ | $O(1)$ | $O(N)$ |
| `put(key, val)` | $O(1)$ | $O(1)$ | $O(N)$ |
| `evict()` | $O(1)$ | $O(1)$ | $O(N)$ |""",
}

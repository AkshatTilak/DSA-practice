INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Key-Value Store like Redis (LLD).',
    'groups': ['OOP Case Studies', 'Caching & Storage'],
    'readme_content': """# Key-Value (KV) Store LLD

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
4.  **Browser Caches**: Web browsers use similar KV structures to store cached assets, evicting old files based on size and access frequency.""",
    'solutions': """# Low-Level Design: Distributed Key-Value Store (Redis-like)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Core Operations**: Support basic CRUD operations: `GET(key)`, `SET(key, value)`, `DEL(key)`.
*   **TTL (Time-to-Live)**: Ability to set an expiration time on keys.
*   **Diverse Data Types**: Support for Strings, Lists, Sets, Sorted Sets, and Hashes.
*   **Persistence**: Options to persist in-memory data to disk to prevent data loss on restart (Snapshotting and Append-only logs).
*   **Atomic Operations**: Ensure that individual commands are executed atomically.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency**: Sub-millisecond response times for basic operations.
*   **High Throughput**: Ability to handle hundreds of thousands of requests per second per node.
*   **High Availability**: Support for replication and automatic failover.
*   **Scalability**: Support for horizontal scaling via sharding.
*   **Consistency**: Strong consistency for single-key operations; eventual consistency for replicated data.

### 1.3 Scale Estimations (Typical Production Node)
*   **Memory**: 64GB - 256GB per node.
*   **Request Rate**: ~100k to 1M ops/sec.
*   **Network**: 10Gbps NIC to handle high throughput.

---

## 2. High-Level Architecture

The system follows a **Single-Threaded Event-Loop** architecture for the core execution engine to eliminate locking overhead and context switching, while using background threads for heavy I/O tasks (persistence and deletion).

### 2.1 Component Diagram

```mermaid
graph TD
    Client[Client Application] -->|RESP Protocol| NetworkLayer[Network Layer/TCP]
    NetworkLayer -->|Command Queue| EventLoop[Event Loop / Command Processor]
    
    subgraph CoreEngine [Core Execution Engine]
        EventLoop --> CommandParser[Command Parser]
        CommandParser --> ExecutionEngine[Execution Engine]
        ExecutionEngine --> MemoryStore[In-Memory Store]
    end
    
    subgraph Storage [Data Structures]
        MemoryStore --> GlobalHash[Global Hash Map]
        GlobalHash --> RedisObject[Redis Objects: Strings, Lists, Sets, etc.]
    end
    
    subgraph Persistence [Persistence Manager]
        ExecutionEngine --> AOF[AOF - Append Only File]
        ExecutionEngine --> RDB[RDB - Snapshotting]
        RDB --> Disk[(Disk)]
        AOF --> Disk
    end
    
    subgraph Expiration [TTL Manager]
        EventLoop --> TTLWorker[TTL Cleanup Worker]
        TTLWorker --> MemoryStore
    end
```

### 2.2 Interaction Flow
1.  **Request**: Client sends a command (e.g., `SET name "John" EX 60`) via TCP using the RESP (Redis Serialization Protocol).
2.  **Parsing**: The Event Loop picks up the request, and the Command Parser converts it into an executable operation.
3.  **Execution**: The Execution Engine interacts with the `GlobalHash` map to store/retrieve the value.
4.  **TTL**: If an expiration is set, the key is added to a priority queue or a randomized sampling list for the TTL Worker.
5.  **Persistence**: The command is logged to the AOF buffer and periodically flushed to disk.

---

## 3. Detailed Low-Level Design

### 3.1 In-Memory Data Structures
Instead of a traditional database schema, we design the internal memory representation.

#### A. The Global Key Map
The core is a **Hash Table** where:
*   **Key**: `String`
*   **Value**: `RedisObject` (a wrapper containing metadata and the actual data structure).

#### B. RedisObject Structure
```cpp
struct RedisObject {
    ObjectType type;       // STRING, LIST, SET, ZSET, HASH
    void* data;            // Pointer to the actual data structure
    long long expiryTime;  // Epoch timestamp for TTL (0 if no expiry)
    int refCount;          // For memory management/garbage collection
};
```

#### C. Specialized Data Structures
| Type | Implementation | Reasoning |
| :--- | :--- | :--- |
| **String** | SDS (Simple Dynamic String) | Pre-allocated buffers to avoid frequent reallocations. |
| **List** | Quicklist (Doubly Linked List of ziplists) | Balance between random access and efficient insertions. |
| **Set** | IntSet (for ints) or Hash Table | $O(1)$ lookup and uniqueness. |
| **Sorted Set** | Skip List + Hash Map | Hash map for $O(1)$ score lookup; Skip List for $O(\log N)$ range queries. |
| **Hash** | ZipList (small) or Hash Table (large) | Memory efficiency for small objects, performance for large. |

### 3.2 Persistence Strategy

#### RDB (Redis Database File)
*   **Mechanism**: Point-in-time snapshot.
*   **LLD Implementation**: Use `fork()` to create a child process. The child has a "copy-on-write" view of the memory and writes the entire dataset to a binary file.
*   **Trade-off**: Fast restart, but potential data loss between snapshots.

#### AOF (Append Only File)
*   **Mechanism**: Logs every write operation.
*   **LLD Implementation**: A write-ahead log (WAL). Commands are appended to a buffer and flushed to disk based on policies (`always`, `everysec`, `no`).
*   **AOF Rewrite**: To prevent the file from growing indefinitely, the system reads the current memory state and writes a condensed version of the AOF.

---

## 4. Core API Design

Since this is a KV store, the "API" is the protocol. We use a request-response model.

### 4.1 Command Set

| Command | Payload | Response | Description |
| :--- | :--- | :--- | :--- |
| `SET` | `key, value, [EX seconds]` | `OK` | Sets key to value with optional TTL. |
| `GET` | `key` | `value` or `nil` | Retrieves value of the key. |
| `DEL` | `key...` | `integer (count)` | Deletes one or more keys. |
| `EXPIRE`| `key, seconds` | `integer (1/0)` | Sets a timeout on a key. |
| `HSET` | `key, field, value` | `integer` | Sets value of a field in a hash. |
| `ZADD` | `key, score, member` | `integer` | Adds member to a sorted set. |

### 4.2 Protocol Example (RESP)
**Request (`SET key "val"`)**:
```text
*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$3\r\nval\r\n
```
*(Explanation: Array of 3 elements: "SET", "key", "val")*

---

## 5. Scalability & Advanced Topics

### 5.1 Sharding (Horizontal Scaling)
To scale beyond one node, we implement **Consistent Hashing**.
*   **Slot-based Sharding**: The keyspace is divided into 16,384 hash slots.
*   `slot = CRC16(key) mod 16384`.
*   Each node in the cluster is responsible for a range of slots.
*   **Redirection**: If a client hits Node A for a key belonging to Node B, Node A returns a `MOVED` error with Node B's address.

### 5.2 Replication & High Availability
*   **Leader-Follower**: One Master handles writes; multiple Replicas handle reads.
*   **Asynchronous Replication**: Master streams the AOF to replicas.
*   **Sentinel/Quorum**: A separate monitoring process tracks health. If the Master fails, a Sentinel triggers an election among Replicas to promote a new Master.

### 5.3 Eviction Policies (Memory Management)
When `maxmemory` is reached, the system must evict keys:
*   **LRU (Least Recently Used)**: Approximate LRU by sampling $N$ keys and evicting the oldest.
*   **LFU (Least Frequently Used)**: Tracks access frequency using a logarithmic counter.
*   **TTL Eviction**: Actively delete keys that have expired.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem
*   **Priority**: Redis prioritizes **Availability (A)** and **Partition Tolerance (P)**.
*   **Consistency**: It provides **Eventual Consistency**. In a master-replica setup, a write is acknowledged by the master before it reaches replicas. If the master crashes before replication, data loss occurs.

### 6.2 Latency vs. Durability
*   **fsync always**: Maximum durability, but latency increases to disk I/O speed (Slow).
*   **fsync everysec**: Balance; max 1 second of data loss, but maintains high throughput (Standard).
*   **No fsync**: Maximum performance, high risk of data loss (Caching use-case).

### 6.3 Single-Threaded vs. Multi-Threaded
*   **Single-Threaded (Core)**: Eliminates locking/mutex contention and race conditions. Simplifies the implementation of atomic operations.
*   **Multi-Threaded (I/O)**: Modern Redis (6.0+) uses multiple threads for reading/writing to sockets, but the **Execution Engine** remains single-threaded to maintain the simplicity of the data model.""",
}

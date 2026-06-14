INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Thread-safe Blocking Queue.',
    'groups': ['OOP Case Studies', 'Concurrency'],
    'readme_content': """# Blocking Queue LLD

A **Blocking Queue** is a thread-safe queue that supports operations that wait for the queue to become non-empty when retrieving an element and wait for space to become available when storing an element. It is the fundamental synchronization primitive used to implement the **Producer-Consumer Pattern**.

---

## 1. Overview & System Requirements

### Core Functional Requirements
- **Bounded Capacity**: The queue must have a maximum size to prevent memory exhaustion (backpressure).
- **Thread-Safe Enqueue (`put`)**: 
    - If the queue is not full, add the element.
    - If the queue is full, the calling thread must block until space becomes available.
- **Thread-Safe Dequeue (`take`)**: 
    - If the queue is not empty, remove and return the element.
    - If the queue is empty, the calling thread must block until an element is added.
- **Atomic Operations**: Ensure that no two threads can modify the internal state of the queue simultaneously, preventing race conditions.

### Actors
- **Producer Threads**: Entities that generate data and attempt to `put` it into the queue.
- **Consumer Threads**: Entities that process data by attempting to `take` it from the queue.

---

## 2. Design Principles & Patterns

### OOP Principles Applied
- **Single Responsibility Principle (SRP)**: The `BlockingQueue` class is solely responsible for managing the storage and the synchronization logic of the data flow.
- **Encapsulation**: The internal storage (e.g., a list or deque) and the synchronization primitives (locks/conditions) are kept private to prevent external corruption of the queue state.

### Concurrency Patterns
- **Monitor Pattern**: The design uses a "Monitor" approach where all access to the shared resource is synchronized via a lock, and threads communicate their state changes using condition variables.
- **Producer-Consumer Pattern**: This is the primary architectural pattern solved by this LLD, decoupling the rate of production from the rate of consumption.

### Why Condition Variables?
A simple `Lock` (Mutex) is insufficient because it only provides mutual exclusion. If a consumer finds the queue empty, it cannot simply hold the lock and wait (as the producer would never be able to enter and add an item). **Condition Variables** allow a thread to release the lock and sleep until another thread signals that a specific condition (e.g., "not empty") has been met.

---

## 3. Class Structure & Relationships

The design relies on a composition relationship where the `BlockingQueue` contains a data structure for storage and synchronization objects for thread coordination.

### Class Diagram (ASCII)
```text
+---------------------------------------+
|             BlockingQueue             |
+---------------------------------------+
| - capacity: int                       |
| - queue: Deque                        |
| - lock: Lock                          |
| - not_full: Condition                 |
| - not_empty: Condition                |
+---------------------------------------+
| + put(item: T): void                  |
| + take() -> T: T                      |
| + size() -> int: int                  |
+---------------------------------------+
```

- **`capacity`**: Defines the upper bound of the queue.
- **`queue`**: The underlying storage (Double Ended Queue).
- **`lock`**: A mutual exclusion object to ensure atomicity.
- **`not_full`**: A condition variable that producers wait on.
- **`not_empty`**: A condition variable that consumers wait on.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
import threading
from collections import deque

class BlockingQueue:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()
        # The lock ensures mutual exclusion
        self.lock = threading.Lock()
        # Condition variables are associated with the lock
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def put(self, item):
        \"\"\"
        Adds an item to the queue. Blocks if the queue is full.
        \"\"\"
        with self.not_full:
            # Use 'while' instead of 'if' to handle spurious wake-ups
            while len(self.queue) == self.capacity:
                print(f"[Producer] Queue full. Waiting...")
                self.not_full.wait()
            
            self.queue.append(item)
            print(f"[Producer] Produced: {item}")
            
            # Notify any waiting consumers that the queue is no longer empty
            self.not_empty.notify()

    def take(self):
        \"\"\"
        Removes and returns an item from the queue. Blocks if the queue is empty.
        \"\"\"
        with self.not_empty:
            # Use 'while' instead of 'if' to handle spurious wake-ups
            while len(self.queue) == 0:
                print(f"[Consumer] Queue empty. Waiting...")
                self.not_empty.wait()
            
            item = self.queue.popleft()
            print(f"[Consumer] Consumed: {item}")
            
            # Notify any waiting producers that the queue is no longer full
            self.not_full.notify()
            return item

    def size(self):
        with self.lock:
            return len(self.queue)

# --- Testing the implementation ---
if __name__ == "__main__":
    bq = BlockingQueue(capacity=5)

    def producer():
        for i in range(10):
            bq.put(i)

    def consumer():
        for i in range(10):
            bq.take()

    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
```

### Detailed Logic Walkthrough

1.  **The `put` Operation**:
    *   The producer acquires the `not_full` condition lock.
    *   It checks if the queue is full. If `len(queue) == capacity`, it calls `wait()`. This atomically releases the lock and puts the thread to sleep.
    *   When a consumer calls `take()`, it triggers `not_full.notify()`, waking the producer.
    *   The producer re-acquires the lock, checks the `while` condition again, and if space is available, appends the item.
    *   Finally, it calls `not_empty.notify()` to alert any sleeping consumers.

2.  **The `take` Operation**:
    *   The consumer acquires the `not_empty` condition lock.
    *   It checks if the queue is empty. If `len(queue) == 0`, it calls `wait()`, releasing the lock and sleeping.
    *   When a producer calls `put()`, it triggers `not_empty.notify()`, waking the consumer.
    *   The consumer re-acquires the lock, pops the element from the left of the deque, and notifies waiting producers via `not_full.notify()`.

3.  **The "Spurious Wake-up" Problem**:
    *   We use `while` instead of `if` because in multi-threaded environments, a thread might wake up even if the condition wasn't actually met (spurious wake-up) or another thread might have grabbed the item/slot between the notification and the wake-up.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Description |
| :--- | :--- | :--- | :--- |
| `put()` | $O(1)$ | $O(1)$ | Appending to a deque is constant time. |
| `take()` | $O(1)$ | $O(1)$ | Popping from the left of a deque is constant time. |
| `size()` | $O(1)$ | $O(1)$ | Getting the length of a deque is constant time. |
| **Overall** | - | $O(N)$ | Space is proportional to the `capacity` $N$. |

---

## 6. Real-World Applications

The Blocking Queue is a cornerstone of concurrent system design:

1.  **Thread Pools**: In Java's `ThreadPoolExecutor` or Python's `ThreadPoolExecutor`, a blocking queue holds tasks waiting to be executed by worker threads.
2.  **Log Aggregators**: Applications produce log messages rapidly. These are pushed into a blocking queue, and a background "Writer" thread consumes them and writes them to a disk or network, ensuring the main application isn't slowed down by I/O.
3.  **Message Brokers**: Simplified versions of RabbitMQ or Kafka use internal blocking buffers to manage the flow of messages between the network layer and the storage layer.
4.  **Pipeline Processing**: In data engineering pipelines, each stage of the pipeline (Filter $\rightarrow$ Transform $\rightarrow$ Load) is connected by a blocking queue to maintain a steady flow and handle spikes in data volume (smoothing).""",
    'solutions': """# Design Document: Thread-Safe Blocking Queue

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
A Blocking Queue is a thread-safe queue that supports operations that wait for the queue to become non-empty when retrieving an element, and wait for space to become available when storing an element.

*   **`put(item)`**: Adds an item to the tail of the queue. If the queue is full, the calling thread must block until space becomes available.
*   **`take()`**: Removes and returns the item from the head of the queue. If the queue is empty, the calling thread must block until an item is added.
*   **`offer(item, timeout)`**: Attempts to add an item. If the queue is full, it waits for the specified timeout before returning `false`.
*   **`poll(timeout)`**: Attempts to remove an item. If the queue is empty, it waits for the specified timeout before returning `null`.
*   **`size()`**: Returns the current number of elements in the queue.
*   **`isEmpty()`**: Returns true if the queue contains no elements.

### 1.2 Non-Functional Requirements
*   **Thread Safety**: Multiple producers and multiple consumers must be able to access the queue concurrently without data corruption.
*   **Liveness**: The system must be free of deadlocks and livelocks.
*   **Ordering**: Must maintain First-In-First-Out (FIFO) semantics.
*   **Low Latency**: Minimizing the overhead of lock acquisition and context switching.
*   **Fairness (Optional)**: Ability to ensure that threads are served in the order they arrived to prevent thread starvation.

### 1.3 Scale Estimations
Since this is a Low-Level Design (LLD) for a data structure:
*   **Time Complexity**: `put` and `take` should be $O(1)$.
*   **Space Complexity**: $O(N)$ where $N$ is the capacity of the queue.

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **Storage Mechanism**: A circular buffer (array) or a doubly linked list to store elements.
2.  **Synchronization Primitive**: A Mutex/Lock to ensure mutual exclusion.
3.  **Condition Variables**: 
    *   `notFull`: Used to signal producers that space has been vacated.
    *   `notEmpty`: Used to signal consumers that an item has been added.
4.  **Concurrency Controller**: Manages the blocking and waking of threads based on queue state.

### 2.2 Interaction Diagram

```mermaid
sequenceDiagram
    participant P as Producer Thread
    participant Q as BlockingQueue
    participant C as Consumer Thread

    P->>Q: put(item)
    Note over Q: Lock Acquired
    alt Queue Full
        Q->>Q: wait(notFull)
        Note over P: Thread Blocked
    end
    Q->>Q: insert item at tail
    Q->>Q: signal(notEmpty)
    Note over Q: Lock Released
    P->>P: Continue Execution

    C->>Q: take()
    Note over Q: Lock Acquired
    alt Queue Empty
        Q->>Q: wait(notEmpty)
        Note over C: Thread Blocked
    end
    Q->>Q: remove item from head
    Q->>Q: signal(notFull)
    Note over Q: Lock Released
    C->>C: Process Item
```

---

## 3. Detailed Design

### 3.1 Storage Selection
For a professional implementation, we choose a **Circular Array**.
*   **Reasoning**: Arrays provide better cache locality compared to linked lists and avoid the overhead of creating new node objects for every `put` operation, reducing GC pressure in languages like Java.

### 3.2 State Management
*   `T[] buffer`: The array storing elements.
*   `int head`: Index of the next element to be taken.
*   `int tail`: Index where the next element will be put.
*   `int count`: Current number of elements.
*   `Lock lock`: Reentrant lock for thread safety.
*   `Condition notFull`, `Condition notEmpty`: Condition variables.

### 3.3 Persistence (Optional)
Typically, a Blocking Queue is in-memory. However, for "Durability" requirements:
*   **Write-Ahead Log (WAL)**: Every `put` operation is logged to a sequential disk file before updating the memory buffer.
*   **Recovery**: Upon restart, the system replays the WAL to rebuild the queue state.
*   **Database**: A SQL table `queue_items (id BIGINT PRIMARY KEY, payload BLOB, status VARCHAR, created_at TIMESTAMP)` could be used, but this would introduce significant latency and move the design from LLD to HLD.

---

## 4. Core API Design

Since this is an LLD challenge, the "API" refers to the Class Interface.

### 4.1 Interface Definition (Java-style)

```java
public interface IBlockingQueue<T> {
    /** Blocks if full */
    void put(T item) throws InterruptedException;

    /** Blocks if empty */
    T take() throws InterruptedException;

    /** Waits for timeout if full, returns false if timeout expires */
    boolean offer(T item, long timeout, TimeUnit unit) throws InterruptedException;

    /** Waits for timeout if empty, returns null if timeout expires */
    T poll(long timeout, TimeUnit unit) throws InterruptedException;

    int size();
    boolean isEmpty();
}
```

### 4.2 Implementation Logic (Pseudo-code)

```python
class BlockingQueue<T>:
    def __init__(self, capacity):
        self.buffer = array of size capacity
        self.head = 0
        self.tail = 0
        self.count = 0
        self.lock = ReentrantLock()
        self.notFull = self.lock.newCondition()
        self.notEmpty = self.lock.newCondition()

    def put(self, item):
        with self.lock:
            while self.count == self.capacity:
                self.notFull.wait()
            
            self.buffer[self.tail] = item
            self.tail = (self.tail + 1) % self.capacity
            self.count += 1
            
            self.notEmpty.signal()

    def take(self):
        with self.lock:
            while self.count == 0:
                self.notEmpty.wait()
            
            item = self.buffer[self.head]
            self.buffer[self.head] = null # avoid memory leak
            self.head = (self.head + 1) % self.capacity
            self.count -= 1
            
            self.notFull.signal()
            return item
```

---

## 5. Scalability & Advanced Topics

### 5.1 Fine-Grained Locking (Two-Lock Queue)
A single lock creates a bottleneck because producers and consumers contend for the same lock.
*   **Optimization**: Use two separate locks: `putLock` and `takeLock`.
*   **Mechanism**: The `putLock` protects the `tail` and `put` operations; the `takeLock` protects the `head` and `take` operations. 
*   **Atomic Integer**: Use an `AtomicInteger` for the `count` to allow both locks to track the size without interfering with each other.

### 5.2 Lock-Free Implementation
For extreme performance, use a **Non-blocking Queue** based on the Michael-Scott algorithm.
*   **CAS (Compare-And-Swap)**: Use `AtomicReference` to update the head and tail.
*   **Pros**: No thread suspension, no context switching overhead.
*   **Cons**: Extremely complex to implement correctly; "Spinning" can consume high CPU if the queue is empty/full.

### 5.3 Fairness
By default, `ReentrantLock` is non-fair. In high-contention scenarios, some threads might be starved.
*   **Solution**: Initialize the lock with `new ReentrantLock(true)`. This ensures a FIFO grant of the lock to waiting threads.

---

## 6. Trade-off Analysis

| Trade-off | Single Lock (Coarse) | Two-Lock (Fine) | Lock-Free (CAS) |
| :--- | :--- | :--- | :--- |
| **Complexity** | Low | Medium | High |
| **Throughput** | Low (High contention) | Medium/High | Very High |
| **CPU Usage** | Low (Threads sleep) | Low (Threads sleep) | High (Spinning/Retry) |
| **Fairness** | Easy to implement | Moderate | Difficult |

### 6.1 CAP Theorem Application
While CAP is typically for distributed systems, in a concurrent data structure context:
*   **Consistency**: This design prioritizes **Strong Consistency**. Every `take` is guaranteed to see the latest `put`.
*   **Availability**: By using blocking calls, we trade off immediate availability (the thread stops) for correctness and resource efficiency.

### 6.2 Space vs. Time
*   **Circular Array**: Fixed space, $O(1)$ time, excellent cache locality.
*   **Linked List**: Dynamic space, $O(1)$ time, but higher overhead due to pointer storage and frequent object allocation/deallocation.""",
}

# Blocking Queue LLD

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
        """
        Adds an item to the queue. Blocks if the queue is full.
        """
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
        """
        Removes and returns an item from the queue. Blocks if the queue is empty.
        """
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
4.  **Pipeline Processing**: In data engineering pipelines, each stage of the pipeline (Filter $\rightarrow$ Transform $\rightarrow$ Load) is connected by a blocking queue to maintain a steady flow and handle spikes in data volume (smoothing).
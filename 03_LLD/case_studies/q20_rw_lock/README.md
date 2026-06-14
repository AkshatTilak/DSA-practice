# Readers-Writers Lock (RW Lock) LLD

## 1. Overview & System Requirements

The **Readers-Writers Lock** is a classic synchronization primitive used in concurrent programming to manage access to a shared resource. Unlike a standard Mutex (Mutual Exclusion lock), which allows only one thread to access a resource regardless of the operation, an RW Lock distinguishes between **reading** (shared access) and **writing** (exclusive access).

### Core Functional Requirements
- **Multiple Readers**: Many threads should be able to read the shared resource simultaneously, provided no thread is writing.
- **Exclusive Writer**: Only one thread can write to the resource at a time. While a writer is active, no other readers or writers can access the resource.
- **Thread Safety**: The lock must prevent race conditions and ensure data consistency.
- **Avoidance of Deadlocks**: The implementation must ensure that threads do not enter a state of permanent waiting.

### Behavioral Matrix

| Current State | Request: Read | Request: Write | Result |
| :--- | :--- | :--- | :--- |
| **Idle** | Allowed | Allowed | State changes to `Reading` or `Writing` |
| **Reading** | Allowed | **Blocked** | New readers join; writer waits for all readers to finish |
| **Writing** | **Blocked** | **Blocked** | All other threads wait until writer releases |

---

## 2. Design Principles & Patterns

### Design Principles
- **Single Responsibility Principle (SRP)**: The `RWLock` class is solely responsible for managing the synchronization state and coordinating thread access. It does not concern itself with *what* is being protected, only *how* it is accessed.
- **Interface Segregation**: By providing distinct methods for `acquire_read` and `acquire_write`, the system ensures that the caller explicitly declares their intent, allowing the lock to optimize concurrency.

### Concurrency Patterns
- **Monitor Pattern**: The implementation uses a combination of a **Mutex** (to protect internal state) and a **Condition Variable** (to put threads to sleep and wake them up). This avoids "busy-waiting" (spinning), which wastes CPU cycles.
- **State Management**: The lock tracks the number of active readers and the presence of a writer to make deterministic decisions about granting access.

---

## 3. Class Structure & Relationships

The design is encapsulated within a single coordinator class. Since this is a synchronization primitive, it acts as a "Guard" for any shared resource.

### Class Diagram (ASCII)
```text
+-------------------------------------------------------+
|                      RWLock                           |
+-------------------------------------------------------+
| - _lock: Lock (Mutex)                                  |
| - _condition: ConditionVariable                        |
| - _readers: Integer (Count of active readers)          |
| - _writer_active: Boolean (Is a writer currently in?)  |
+-------------------------------------------------------+
| + acquire_read(): void                                |
| + release_read(): void                                |
| + acquire_write(): void                               |
| + release_write(): void                               |
+-------------------------------------------------------+
```

### Relationships
- **Composition**: The `RWLock` contains a `Lock` and a `Condition` object.
- **Association**: Multiple Worker Threads (Readers/Writers) associate with a single `RWLock` instance to synchronize access to a shared data object.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
import threading

class RWLock:
    def __init__(self):
        # Mutex to protect the internal state variables
        self._lock = threading.Lock()
        # Condition variable to manage thread sleeping/waking
        self._condition = threading.Condition(self._lock)
        self._readers = 0
        self._writer_active = False

    def acquire_read(self):
        """Acquire the lock for reading. Multiple readers allowed."""
        with self._lock:
            # Wait if a writer is currently modifying the resource
            while self._writer_active:
                self._condition.wait()
            self._readers += 1

    def release_read(self):
        """Release the read lock."""
        with self._lock:
            self._readers -= 1
            # If this was the last reader, notify waiting writers
            if self._readers == 0:
                self._condition.notify_all()

    def acquire_write(self):
        """Acquire the lock for writing. Exclusive access required."""
        with self._lock:
            # Wait if there are any active readers OR another active writer
            while self._writer_active or self._readers > 0:
                self._condition.wait()
            self._writer_active = True

    def release_write(self):
        """Release the write lock."""
        with self._lock:
            self._writer_active = False
            # Notify all waiting readers and writers
            self._condition.notify_all()

# ==========================================
# Example Usage/Testing
# ==========================================
import time
import random

shared_resource = 0
rw_lock = RWLock()

def reader(tid):
    global shared_resource
    for _ in range(3):
        rw_lock.acquire_read()
        print(f"Reader {tid} read: {shared_resource}")
        time.sleep(random.uniform(0.1, 0.3)) # Simulate read time
        rw_lock.release_read()
        time.sleep(random.uniform(0.1, 0.3))

def writer(tid):
    global shared_resource
    for _ in range(2):
        rw_lock.acquire_write()
        shared_resource += 1
        print(f"Writer {tid} updated resource to: {shared_resource}")
        time.sleep(random.uniform(0.2, 0.4)) # Simulate write time
        rw_lock.release_write()
        time.sleep(random.uniform(0.2, 0.4))

if __name__ == "__main__":
    threads = []
    for i in range(3): threads.append(threading.Thread(target=reader, args=(i,)))
    for i in range(2): threads.append(threading.Thread(target=writer, args=(i,)))
    
    for t in threads: t.start()
    for t in threads: t.join()
```

### Logic Walkthrough

1.  **`acquire_read()`**:
    *   Enter the critical section using `_lock`.
    *   Check if `_writer_active` is `True`. If so, the thread calls `wait()`, releasing the lock and entering the wait queue.
    *   Once woken and `_writer_active` is `False`, increment `_readers` and exit.

2.  **`release_read()`**:
    *   Enter the critical section.
    *   Decrement `_readers`.
    *   If `_readers` becomes `0`, it means the resource is now completely free. Call `notify_all()` to wake up any waiting writers.

3.  **`acquire_write()`**:
    *   Enter the critical section.
    *   A writer must wait if **any** readers are active (`_readers > 0`) or if **another writer** is active (`_writer_active == True`).
    *   Once the condition is met, set `_writer_active = True`.

4.  **`release_write()`**:
    *   Enter the critical section.
    *   Set `_writer_active = False`.
    *   Call `notify_all()` to wake up all waiting threads (both readers and writers) to compete for the lock.

---

## 5. Complexity & Trade-offs

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| `acquire_read` | $O(1)$ | $O(1)$ | Excluding wait time in the queue. |
| `release_read` | $O(1)$ | $O(1)$ | |
| `acquire_write` | $O(1)$ | $O(1)$ | Excluding wait time in the queue. |
| `release_write` | $O(1)$ | $O(1)$ | |

### Critical Design Trade-off: Starvation
The implementation above is a **Reader-Preference Lock**. 

- **The Problem**: If a steady stream of readers keeps arriving, `_readers` will never reach `0`, and a waiting writer will **starve** (wait indefinitely).
- **The Solution (Writer-Preference)**: To solve this, we can introduce a `waiting_writers` counter. If `waiting_writers > 0`, new readers are forced to wait, even if the lock is currently in "Read Mode," allowing the pending writer to take over as soon as the current batch of readers finishes.

---

## 6. Real-World Applications

The RW Lock pattern is used extensively in systems where read operations are significantly more frequent than write operations:

1.  **Database Management Systems (DBMS)**: In MVCC (Multi-Version Concurrency Control), reads typically do not block other reads, but writes require exclusive access to specific data pages.
2.  **Caching Layers (e.g., Redis, Memcached)**: When updating a cache entry, a writer locks the entry; however, thousands of concurrent users can read the cached value simultaneously.
3.  **Operating System Kernels**: Used in filesystem drivers where many processes read file metadata, but only one process can rename or delete a file.
4.  **Configuration Managers**: A system where application settings are read by every request but updated only occasionally by an admin.
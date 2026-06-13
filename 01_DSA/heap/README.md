# Heaps & Priority Queues

A Heap is a specialized tree-based data structure that satisfies the heap property: in a Max Heap, the key of a parent node is always greater than or equal to the keys of its children; in a Min Heap, it is less than or equal. Heaps are highly efficient for implementing Priority Queues, where elements are dequeued in order of priority rather than FIFO order.

---

## 🗺️ ASCII Execution Flow: Max Heap Insertion

Here is the step-by-step "bubble-up" or "heapify-up" flow when inserting a value `15` into an existing Max Heap:

```text
Initial Array representation: [ 20, 10, 12, 5, 8 ]
Tree Form:
         [ 20 ]
        /      \
    [ 10 ]    [ 12 ]
    /    \
  [5]    [8]

1. Insert 15 at next empty leaf (index 5):
         [ 20 ]
        /      \
    [ 10 ]    [ 12 ]
    /    \    /
  [5]    [8][15]

2. Compare 15 with parent 12: Since 15 > 12, swap them:
         [ 20 ]
        /      \
    [ 10 ]    [ 15 ]
    /    \    /
  [5]    [8][12]

3. Compare 15 with new parent 20: Since 15 < 20, stop. Heap property restored!
Final Array: [ 20, 10, 15, 5, 8, 12 ]
```

---

## 📊 Complexity Analysis

| Operations | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Peek Min / Max | $O(1)$ | $O(1)$ |
| Push / Insert | $O(\log N)$ | $O(1)$ (iterative swap) |
| Pop / Evict Top | $O(\log N)$ | $O(1)$ |
| Build Heap (Heapify Array) | $O(N)$ | $O(1)$ |

---

## 🏢 Real-World Production Use-Case

### Operating Systems: CPU Process Task Scheduler
Operating systems schedule system and user processes for CPU execution based on priority class.
1. Active processes are stored in a priority queue backed by a **binary min-heap** (or balanced red-black tree).
2. The heap key is the computed execution deadline or nice priority.
3. The scheduler always pops the root element of the heap to allocate the next CPU time-slice to the highest priority task in $O(\log N)$ time.
4. When new threads spawn or request I/O, they are inserted into the heap. This maintains optimal responsiveness even with thousands of active system threads.
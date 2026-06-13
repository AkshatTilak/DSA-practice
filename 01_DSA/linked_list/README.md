# Linked List

A Linked List is a linear data structure where elements (nodes) are not stored in contiguous memory locations. Instead, each node consists of a data value and a pointer (or reference) to the next node in the sequence. Linked lists allow for efficient insertions and deletions ($O(1)$ time) at arbitrary positions if the node reference is known, but they do not support random access ($O(N)$ lookup).

---

## 🗺️ ASCII Execution Flow: Reverse Linked List

Here is the step-by-step pointer reassignment flow for reversing a singly linked list `1 -> 2 -> 3 -> Null`:

```text
Initial State:
  [ 1 ] ──> [ 2 ] ──> [ 3 ] ──> Null
   ▲
  curr (prev = Null)

Iteration 1:
  - Save: nxt = curr.next (2)
  - Redirect: curr.next = prev (Null)
  - Move: prev = curr (1), curr = nxt (2)
  Null <── [ 1 ]   [ 2 ] ──> [ 3 ] ──> Null
            ▲       ▲
           prev    curr

Iteration 2:
  - Save: nxt = curr.next (3)
  - Redirect: curr.next = prev (1)
  - Move: prev = curr (2), curr = nxt (3)
  Null <── [ 1 ] <── [ 2 ]   [ 3 ] ──> Null
                      ▲       ▲
                     prev    curr

Iteration 3:
  - Reassign pointers for Node 3. curr becomes Null.
  Null <── [ 1 ] <── [ 2 ] <── [ 3 ]
                                ▲     ▲
                               prev  curr
Return prev ── New Head: [ 3 ]
```

---

## 📊 Complexity Analysis

| Operations | Linked List | Array / Vector |
| :--- | :--- | :--- |
| Prepend / Append (with tail pointer) | $O(1)$ | $O(N)$ (average amortized) |
| Insert / Delete at Middle (reference known)| $O(1)$ | $O(N)$ |
| Search / Random Access | $O(N)$ | $O(1)$ |

---

## 🏢 Real-World Production Use-Case

### Cache Systems: LRU Cache Eviction Lists
Memcached and Redis implement Least Recently Used (LRU) cache policies by combining Hash Maps and Doubly Linked Lists.
1. A **Doubly Linked List** keeps track of cache keys ordered by their usage timestamp.
2. The most recently used element is moved to the head of the list; the least recently used element resides at the tail.
3. A Hash Map maps cache keys to corresponding nodes in the Doubly Linked List.
4. When a cache hit occurs, the map gives $O(1)$ node access, and the list adjusts the node pointers in $O(1)$ time to move it to the head. This keeps cache reads and eviction operations extremely fast.
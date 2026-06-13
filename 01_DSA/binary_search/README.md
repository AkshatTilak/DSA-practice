# Binary Search

Binary Search is a logarithmic search pattern that finds the position of a target value within a sorted collection (like arrays or lists). It works by repeatedly dividing the search interval in half. If the value of the search key is less than the item in the middle of the interval, the search narrows to the lower half; otherwise, it narrows to the upper half.

---

## 🗺️ ASCII Execution Flow: Standard Binary Search

Here is the search flow looking for `target = 9` in a sorted array `[-1, 0, 3, 5, 9, 12]`:

```text
Array: [ -1,  0,  3,  5,  9, 12 ]
          ▲       ▲          ▲
          │       │          │
         Low     Mid        High
        (idx 0) (idx 2)    (idx 5)

Iteration 1:
  - Mid element is array[2] = 3.
  - target (9) > 3 ──> Shift Low to Mid + 1 (idx 3)

Array: [ -1,  0,  3,  5,  9, 12 ]
                      ▲   ▲   ▲
                      │   │   │
                     Low Mid High
                    (idx 3)(idx 4)(idx 5)

Iteration 2:
  - Mid element is array[4] = 9.
  - target (9) == 9 ──> Target Found! Return index 4.
```

---

## 📊 Complexity Analysis

| Operations | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Iterative Binary Search | $O(\log N)$ | $O(1)$ |
| Recursive Binary Search | $O(\log N)$ | $O(\log N)$ (call stack) |

---

## 🏢 Real-World Production Use-Case

### Databases: B-Tree Index Leaf Node Search
Relational databases (like PostgreSQL, MySQL) store primary key indices in balanced B-Tree index files to avoid full table scans.
1. When querying a row by ID, the storage engine reads index page blocks from disk.
2. Each index page block contains a sorted list of key entries pointing to actual disk sectors.
3. The database engine executes **binary search** in memory on the page key entries to quickly locate the target sector pointer.
4. Using logarithmic binary search instead of linear search reduces the CPU instruction footprint, allowing the database to sustain hundreds of thousands of key lookups per second.
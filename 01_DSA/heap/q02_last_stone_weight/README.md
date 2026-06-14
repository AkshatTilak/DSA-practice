# Last Stone Weight

## 1. Overview & Problem Explanation

The **Last Stone Weight** problem is a simulation challenge where we are given a collection of stones, each with a specific weight. The goal is to simulate a "smashing" process until either one stone remains or no stones are left.

### The Rules of Smashing
1. We always choose the **two heaviest stones** currently available. Let's call their weights $x$ and $y$, where $x \le y$.
2. **If $x == y$**: Both stones are completely destroyed.
3. **If $x \neq y$**: The stone with weight $x$ is destroyed, and the stone with weight $y$ is reduced to $y - x$. This new stone is then placed back into the collection.

### Goal
Determine the weight of the last remaining stone. If no stones are left, return `0`.

### Inputs, Outputs & Constraints
- **Input**: An integer array `stones` (e.g., `[2, 7, 4, 1, 8, 1]`).
- **Output**: A single integer representing the final stone's weight.
- **Constraints**:
    - `1 <= stones.length <= 30`
    - `1 <= stones[i] <= 1000`
- **Edge Cases**:
    - Only one stone initially: The answer is that stone's weight.
    - All stones destroy each other perfectly: The answer is `0`.
    - All stones have the same weight.

---

## 2. Core Concepts & Data Structures

### The Priority Queue (Max Heap)
To solve this problem efficiently, we need a way to repeatedly retrieve and remove the **two largest elements** and potentially insert a new value back into the collection.

While we could sort the array after every smash, that would be computationally expensive. Instead, we use a **Max Heap**.

**Why a Max Heap?**
- **Efficient Extraction**: A Max Heap allows us to extract the maximum element in $O(\log N)$ time.
- **Efficient Insertion**: Inserting a new stone weight back into the heap also takes $O(\log N)$ time.
- **Dynamic Ordering**: Unlike a static sorted array, a heap maintains its partial ordering property automatically as elements are added or removed.

### Implementation Detail (Python)
Python's `heapq` module implements a **Min Heap** by default. To simulate a **Max Heap**, we multiply all stone weights by `-1` before pushing them into the heap. When we pop an element, we multiply it by `-1` again to restore the original positive weight.

---

## 3. Step-by-Step Logic

### Optimal Approach: Max Heap Simulation

1. **Initialization**: Transform the `stones` list into a Max Heap. (In Python: negate all values and call `heapq.heapify()`).
2. **Simulation Loop**: While there is more than one stone in the heap:
   - **Pop** the heaviest stone ($y$).
   - **Pop** the second heaviest stone ($x$).
   - **Compare**:
     - If $y > x$, calculate the difference $y - x$ and **push** the result back into the heap.
     - If $y == x$, do nothing (both are destroyed).
3. **Final Result**: 
   - If the heap contains one element, return that element (negated back to positive).
   - If the heap is empty, return `0`.

### Dry Run Example
**Input**: `stones = [2, 7, 4, 1, 8, 1]`

1. **Heapify (Max Heap)**: `[-8, -7, -4, -2, -1, -1]`
2. **Round 1**:
   - Pop `-8` (8) and `-7` (7).
   - Difference: $8 - 7 = 1$.
   - Push `-1`. Heap: `[-4, -2, -1, -1, -1, -1]`
3. **Round 2**:
   - Pop `-4` (4) and `-2` (2).
   - Difference: $4 - 2 = 2$.
   - Push `-2`. Heap: `[-2, -1, -1, -1, -1, -1]`
4. **Round 3**:
   - Pop `-2` (2) and `-1` (1).
   - Difference: $2 - 1 = 1$.
   - Push `-1`. Heap: `[-1, -1, -1, -1, -1]`
5. **Round 4**:
   - Pop `-1` (1) and `-1` (1).
   - Difference: 0. Nothing pushed back.
   - Heap: `[-1, -1, -1]`
6. **Round 5**:
   - Pop `-1` (1) and `-1` (1).
   - Difference: 0.
   - Heap: `[-1]`
7. **End**: Only one stone left. **Result: 1**.

### Implementation

```python
import heapq

def solve_optimal(stones):
    # 1. Python heapq is a min-heap. 
    # To use it as a max-heap, negate all values.
    max_heap = [-s for s in stones]
    heapq.heapify(max_heap)
    
    # 2. Continue smashing until 0 or 1 stone remains
    while len(max_heap) > 1:
        # Extract the two heaviest stones
        first = -heapq.heappop(max_heap)
        second = -heapq.heappop(max_heap)
        
        # If they are not equal, push the difference back
        if first != second:
            heapq.heappush(max_heap, -(first - second))
            
    # 3. Return the last stone or 0 if none left
    return -max_heap[0] if max_heap else 0
```

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Max Heap** | $O(N \log N)$ | $O(N)$ | `heapify` takes $O(N)$. Each of the $N-1$ smashes involves `heappop` and `heappush`, both taking $O(\log N)$. |

- **Time Complexity**: We perform at most $N-1$ iterations. In each iteration, we perform heap operations that take logarithmic time relative to the number of stones. Thus, $O(N \log N)$.
- **Space Complexity**: $O(N)$ to store the stones within the heap structure.

---

## 5. Real-World Applications

The pattern used in this problem—**continuously processing the highest-priority item and updating the state**—is fundamental in many software systems:

1. **Task Scheduling**: Operating systems use priority queues to manage process scheduling. The process with the highest priority is executed first; if its priority changes (or it's interrupted), it is re-inserted into the queue.
2. **Load Balancing**: In distributed systems, a "Least Connections" or "Highest Capacity" algorithm can use a heap to track which server is currently best equipped to handle an incoming request.
3. **Huffman Coding**: The algorithm used for lossless data compression builds a tree by repeatedly extracting the two symbols with the lowest frequencies (a Min Heap version of this problem) and merging them.
4. **Dijkstra's Shortest Path Algorithm**: Uses a priority queue to always expand the node with the smallest current distance from the source.
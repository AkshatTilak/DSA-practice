# Kth Largest Element in a Stream

## 📌 Overview & Problem Explanation

The **Kth Largest Element in a Stream** problem asks us to design a system that can track the $k$-th largest element in a continuous flow of numbers. Unlike a static array where we can simply sort the elements once, a "stream" implies that new data arrives dynamically, and we must efficiently update our answer.

### The Goal
We need to maintain a data structure such that at any given moment, we can retrieve the element that would be at the $k$-th position if all elements received so far were sorted in descending order.

### Input/Output
- **Initialization**: 
    - `k`: An integer representing the rank we are tracking.
    - `nums`: An initial list of integers.
- **`add(val)`**: 
    - `val`: A new integer being added to the stream.
    - **Returns**: The current $k$-th largest element after the addition.

### Constraints & Edge Cases
- **Constraints**: Typically $k \le \text{nums.length} \le 10^4$.
- **Negative Numbers**: The stream can contain negative integers, so the solution must not rely on values being positive.
- **Stream Size**: The stream grows over time; we cannot afford to re-sort the entire history for every new element.
- **Duplicates**: The system must handle duplicate values correctly (e.g., in `[3, 3, 3]`, the 2nd largest is `3`).

---

## ⚙️ Core Concepts & Data Structures

### The Min-Heap Pattern
The most efficient way to solve "K-th Largest" problems is using a **Min-Heap**. 

At first glance, it seems counterintuitive to use a **Min**-Heap to find a **Largest** element. However, the strategy is to maintain a heap that contains **only the $k$ largest elements seen so far**.

#### Why a Min-Heap?
1. If we keep exactly $k$ elements in a Min-Heap, the **root** (the smallest element in the heap) is the "smallest of the top $k$."
2. By definition, the smallest of the top $k$ largest elements is the **$k$-th largest overall**.
3. When a new element arrives:
   - If it is larger than the root, it belongs in our "top $k$" set. We remove the current root and insert the new element.
   - If it is smaller than the root, it cannot possibly be among the top $k$ largest elements, so we ignore it (or push and immediately pop it).

### Time & Space Complexity Logic
- **Heap Push/Pop**: Both operations take $O(\log k)$ time.
- **Space**: We only ever store $k$ elements, regardless of how many millions of numbers pass through the stream.

---

## 🚀 Step-by-Step Logic

### 1. Brute Force (Naive) Approach
1. Maintain a list of all elements.
2. Every time `add(val)` is called, append `val` to the list.
3. Sort the list in descending order.
4. Return the element at index $k-1$.
- **Downside**: Sorting takes $O(N \log N)$ per addition, which is prohibitively slow for a stream.

### 2. Optimal Approach (Min-Heap)
#### Initialization Phase:
1. Create a Min-Heap.
2. Add all elements from the initial `nums` array into the heap.
3. While the heap size is greater than $k$, pop the smallest element.
4. Now, the heap contains only the $k$ largest elements from the initial set.

#### Addition Phase (`add` method):
1. Push the new `val` onto the Min-Heap.
2. If the heap size now exceeds $k$, pop the smallest element.
3. The element at the root (`heap[0]`) is the current $k$-th largest element.

### Dry Run Example
**Input**: `k = 3`, `nums = [4, 5, 8, 2]`

1. **Init**: 
   - Push 4 $\rightarrow$ `[4]`
   - Push 5 $\rightarrow$ `[4, 5]`
   - Push 8 $\rightarrow$ `[4, 5, 8]`
   - Push 2 $\rightarrow$ `[2, 4, 5, 8]`
   - Size > 3? Yes. Pop `2`. Heap: `[4, 5, 8]`.
   - **Current 3rd Largest**: `4` (Root).

2. **`add(3)`**:
   - Push 3 $\rightarrow$ `[3, 4, 5, 8]`
   - Size > 3? Yes. Pop `3`. Heap: `[4, 5, 8]`.
   - **Return**: `4`.

3. **`add(10)`**:
   - Push 10 $\rightarrow$ `[4, 5, 8, 10]`
   - Size > 3? Yes. Pop `4`. Heap: `[5, 8, 10]`.
   - **Return**: `5`.

---

## 💻 Implementation

```python
import heapq

class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        """
        Initializes the object with integer k and the stream of integers nums.
        """
        self.k = k
        self.min_heap = []
        
        # Add all initial numbers into the heap
        for num in nums:
            self.add(num)

    def add(self, val: int) -> int:
        """
        Adds a value to the stream and returns the kth largest element.
        """
        # Push the new value into the min-heap
        heapq.heappush(self.min_heap, val)
        
        # Maintain the heap size to exactly k
        # If we have more than k elements, the smallest among them 
        # cannot be the kth largest element overall.
        if len(self.min_heap) > self.k:
            heapq.heappop(self.min_heap)
            
        # The root of the min-heap is the smallest of the k largest elements,
        # which is exactly the kth largest element in the stream.
        return self.min_heap[0]

# --- Complexity Analysis Implementation ---
def solve_optimal():
    # Example usage:
    k = 3
    nums = [4, 5, 8, 2]
    obj = KthLargest(k, nums)
    print(obj.add(3))   # Expected: 4
    print(obj.add(5))   # Expected: 5
    print(obj.add(10))  # Expected: 5
    print(obj.add(9))   # Expected: 8
    print(obj.add(4))   # Expected: 8
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity (Init) | Time Complexity (`add`) | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Brute Force** | $O(1)$ | $O(N \log N)$ | $O(N)$ | Sorting the entire list every time a new element arrives. |
| **Optimal (Heap)** | $O(N \log k)$ | $O(\log k)$ | $O(k)$ | Maintaining a fixed-size heap of $k$ elements. |

- **Init Time**: We process $N$ elements, each taking $\log k$ time to be pushed/popped from the heap.
- **Add Time**: Each `add` operation involves one push and potentially one pop, both $O(\log k)$.
- **Space**: The heap only stores $k$ elements, making it highly space-efficient for massive streams.

---

## 🌍 Real-World Applications

This pattern is widely used in systems where we need to maintain "Top-K" statistics in real-time:

1. **Real-Time Leaderboards**: In online gaming, tracking the Top 10 players globally without re-sorting millions of players every time a score changes.
2. **Trending Topics**: Social media platforms (like X/Twitter) use similar logic to track the most mentioned hashtags over a sliding window of time.
3. **Network Traffic Monitoring**: Identifying the top $K$ IP addresses generating the most traffic to detect potential DDoS attacks.
4. **Financial Systems**: Monitoring the highest $K$ price spikes in a stock ticker stream to trigger algorithmic trading alerts.
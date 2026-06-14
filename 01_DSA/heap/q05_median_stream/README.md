# Median Stream (q05_median_stream)

## 📌 Overview & Problem Explanation

The **Median Stream** problem asks us to design a data structure that supports two operations: adding a number from a continuous stream of data and finding the current median of all elements seen so far.

### What is a Median?
The median is the middle value in a sorted list of numbers.
- **Odd number of elements**: The median is the exact middle element.
- **Even number of elements**: The median is the average of the two middle elements.

### Problem Constraints & Edge Cases
- **Dynamic Input**: Numbers are not provided all at once; they arrive one by one.
- **Constraints**: The number of calls to `addNum` and `findMedian` can be up to $5 \times 10^4$.
- **Edge Cases**:
    - **Single Element**: The first element added is automatically the median.
    - **Duplicate Values**: The system must handle multiple instances of the same number correctly.
    - **Negative Numbers**: The logic must remain consistent regardless of the sign of the input.

---

## 🧠 Core Concepts & Data Structures

To solve this problem optimally, we use a **Two-Heap Pattern**. 

### Why Heaps?
A sorted array would allow $O(1)$ access to the median but would require $O(N)$ time to insert a new element to maintain order. A standard heap allows $O(\log N)$ insertion but only provides access to the extreme (min or max) element. By combining two heaps, we can track the "middle" of the dataset without sorting the entire collection.

### The Two-Heap Strategy
We split the data into two halves:
1. **Max-Heap (Left Half)**: Stores the smaller half of the numbers. The root is the **maximum** of the smaller half.
2. **Min-Heap (Right Half)**: Stores the larger half of the numbers. The root is the **minimum** of the larger half.

**The Key Property:**
If we keep the heaps balanced (size difference $\le 1$), the median will always be at the root of one or both heaps.

- If `len(max_heap) > len(min_heap)`, the median is the root of the max-heap.
- If `len(min_heap) > len(max_heap)`, the median is the root of the min-heap.
- If `len(max_heap) == len(min_heap)`, the median is the average of both roots.

---

## ⚙️ Step-by-Step Logic

### 1. The Insertion Process (`addNum`)
To ensure the heaps stay balanced and the elements are correctly partitioned, we follow these steps:

1. **Initial Push**: Push the new number into the `max_heap` (the smaller half). Since Python's `heapq` is a min-heap, we store values as **negative** to simulate a max-heap.
2. **Filtering**: To ensure the `max_heap` only contains values smaller than those in the `min_heap`, we pop the largest value from the `max_heap` and push it into the `min_heap`.
3. **Balancing**: If the `min_heap` now has more elements than the `max_heap`, we pop the smallest value from the `min_heap` and push it back into the `max_heap`.
   - *Result*: The `max_heap` will always be equal to or one element larger than the `min_heap`.

### 2. The Median Calculation (`findMedian`)
1. Check the sizes of the heaps.
2. If `max_heap` is larger, return its root (remember to flip the sign back to positive).
3. If they are equal in size, return the average of the roots of both heaps.

### 📝 Dry Run Example
Stream: `[1, 2, 3]`

1. **Add 1**: 
   - Push to `max_heap`: `[-1]`
   - Move to `min_heap`: `max_heap: [], min_heap: [1]`
   - Balance: `max_heap: [-1], min_heap: []`
   - **Median**: `-(-1) = 1`
2. **Add 2**: 
   - Push to `max_heap`: `[-2, -1]`
   - Move to `min_heap`: `max_heap: [-1], min_heap: [2]`
   - Balance: Sizes equal.
   - **Median**: `(-(-1) + 2) / 2 = 1.5`
3. **Add 3**: 
   - Push to `max_heap`: `[-3, -1]`
   - Move to `min_heap`: `max_heap: [-1], min_heap: [2, 3]`
   - Balance: `min_heap` is larger $\rightarrow$ move `2` to `max_heap`.
   - Result: `max_heap: [-2, -1], min_heap: [3]`
   - **Median**: `-(-2) = 2`

---

## 💻 Implementation

```python
import heapq

class MedianFinder:
    def __init__(self):
        # max_heap stores the smaller half of the numbers
        # We use negative values because heapq is a min-heap by default
        self.small_half = [] 
        # min_heap stores the larger half of the numbers
        self.large_half = []

    def addNum(self, num: int) -> None:
        # 1. Add to max_heap (small_half)
        heapq.heappush(self.small_half, -num)
        
        # 2. Ensure every element in small_half <= every element in large_half
        # Move the largest of the small_half to the large_half
        val = -heapq.heappop(self.small_half)
        heapq.heappush(self.large_half, val)
        
        # 3. Balance the sizes: small_half can have at most 1 more element than large_half
        if len(self.large_half) > len(self.small_half):
            val = heapq.heappop(self.large_half)
            heapq.heappush(self.small_half, -val)

    def findMedian(self) -> float:
        if len(self.small_half) > len(self.large_half):
            # Small half is larger, root of small_half is the median
            return float(-self.small_half[0])
        else:
            # Sizes are equal, average of the two roots
            return (-self.small_half[0] + self.large_half[0]) / 2.0

def solve():
    # Example usage
    mf = MedianFinder()
    mf.addNum(1)
    print(mf.findMedian()) # 1.0
    mf.addNum(2)
    print(mf.findMedian()) # 1.5
    mf.addNum(3)
    print(mf.findMedian()) # 2.0
```

---

## 📊 Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| `addNum` | $O(\log N)$ | $O(1)$ | Each `heappush` and `heappop` takes logarithmic time relative to the number of elements. |
| `findMedian` | $O(1)$ | $O(1)$ | Accessing the root of a heap (`heap[0]`) is a constant time operation. |
| **Overall** | **$O(N \log N)$** | **$O(N)$** | To process $N$ numbers, we perform $N$ additions. We store all $N$ numbers across two heaps. |

---

## 🌍 Real-World Applications

The **Two-Heap Median** pattern is widely used in systems requiring real-time statistics on fluctuating data:

1. **Network Traffic Monitoring**: Calculating the median latency of packets arriving at a router to detect network congestion without storing and sorting millions of packets.
2. **Financial Trading Systems**: Monitoring the median price of a stock ticker in real-time to identify price trends or anomalies.
3. **System Resource Telemetry**: Tracking the median CPU or Memory usage of a distributed cluster over a sliding window of time to set alerting thresholds.
4. **Game Server Matchmaking**: Dynamically calculating the median skill level (MMR) of players in a queue to create balanced matches.
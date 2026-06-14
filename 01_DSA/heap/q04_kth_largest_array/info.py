INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/kth-largest-element-in-an-array/',
    'description': 'Kth largest array.',
    'groups': ['Heap / Priority Queue', 'Array'],
    'readme_content': """# Kth Largest Array

## 1. Overview & Problem Explanation

The **Kth Largest Array** problem asks us to find the $k$-th largest element in an unsorted array. It is crucial to distinguish this from finding the $k$-th *distinct* element; if the array contains duplicates, they are counted as separate positions in the sorted order.

**Example:**
- **Input:** `nums = [3, 2, 1, 5, 6, 4]`, `k = 2`
- **Sorted Order (Descending):** `[6, 5, 4, 3, 2, 1]`
- **2nd Largest:** `5`
- **Output:** `5`

### Constraints & Edge Cases
- **Array Size:** The array can contain up to $10^5$ elements. A naive sorting approach might be acceptable, but for very large streams of data, it becomes inefficient.
- **Values:** Integers can be positive or negative.
- **K-Value:** $1 \le k \le \text{nums.length}$. This ensures $k$ is always within the bounds of the array.
- **Duplicates:** The array may contain duplicate values (e.g., `[3, 2, 3, 1, 2, 4, 5, 5, 6]`, $k=4 \rightarrow$ result is `4`).

---

## 2. Core Concepts & Data Structures

To solve this problem efficiently, we move beyond simple sorting and utilize specialized algorithmic patterns.

### A. The Min-Heap (Priority Queue)
A **Heap** is a specialized tree-based data structure that satisfies the heap property. In a **Min-Heap**, the parent node is always smaller than or equal to its children, meaning the root is always the minimum element of the heap.

**Why use a Min-Heap?**
To find the $k$-th largest element, we don't need to keep track of all $N$ elements in sorted order. We only need to maintain a "VIP list" of the **top $k$ largest elements** seen so far.
- By using a Min-Heap of size $k$, the root of the heap represents the "smallest of the best." 
- If we encounter a new number larger than the root, we discard the root and add the new number.
- After processing the entire array, the root of the heap is the $k$-th largest element.

### B. Quickselect (Divide and Conquer)
Quickselect is based on the **QuickSort** algorithm. Instead of sorting the entire array, Quickselect partitions the array around a pivot. 
- After one partition, the pivot is in its final sorted position.
- If the pivot's index is exactly the position of the $k$-th largest element, we return it.
- Otherwise, we only recurse into the half of the array where the $k$-th element must reside.

---

## 3. Step-by-Step Logic

### Approach 1: Sorting (Naive)
1. Sort the array in descending order.
2. Return the element at index $k-1$.
*This is simple but inefficient for very large datasets.*

### Approach 2: Min-Heap (Optimal for Streaming)
1. Initialize an empty **Min-Heap**.
2. Iterate through every number `num` in the `nums` array:
   - Push `num` onto the heap.
   - If the heap size exceeds $k$, pop the smallest element (the root).
3. Once the loop finishes, the heap contains exactly the $k$ largest elements of the array.
4. The root of the heap is the smallest among those $k$ largest elements, which is by definition the **$k$-th largest element**.

**Dry Run Example:** `nums = [3, 2, 1, 5, 6, 4], k = 2`
- `num = 3`: Heap `[3]`
- `num = 2`: Heap `[2, 3]`
- `num = 1`: Heap `[1, 2, 3]` $\rightarrow$ Size $> 2$, pop `1`. Heap: `[2, 3]`
- `num = 5`: Heap `[2, 3, 5]` $\rightarrow$ Size $> 2$, pop `2`. Heap: `[3, 5]`
- `num = 6`: Heap `[3, 5, 6]` $\rightarrow$ Size $> 2$, pop `3`. Heap: `[5, 6]`
- `num = 4`: Heap `[4, 5, 6]` $\rightarrow$ Size $> 2$, pop `4`. Heap: `[5, 6]`
- **Result:** Root is `5`.

### Approach 3: Quickselect (Optimal Average Time)
1. Pick a random `pivot` from the array.
2. Partition the array into three groups:
   - `left`: Elements greater than the pivot.
   - `mid`: Elements equal to the pivot.
   - `right`: Elements smaller than the pivot.
3. Compare $k$ to the size of these groups:
   - If $k \le \text{length(left)}$, the $k$-th largest is in the `left` group. Recurse there.
   - If $k > \text{length(left)} + \text{length(mid)}$, the $k$-th largest is in the `right` group. Recurse there, adjusting $k$ by subtracting the sizes of `left` and `mid`.
   - Otherwise, the $k$-th largest is the `pivot` itself.

---

## 4. Complexity Analysis

| Approach | Time Complexity (Avg) | Time Complexity (Worst) | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Sorting** | $O(N \log N)$ | $O(N \log N)$ | $O(1)$ or $O(N)$ | Depends on sorting implementation (Timsort/Heapsort). |
| **Min-Heap** | $O(N \log k)$ | $O(N \log k)$ | $O(k)$ | We iterate $N$ times, and each heap operation takes $\log k$. |
| **Quickselect**| $O(N)$ | $O(N^2)$ | $O(N)$ | Average case is linear; worst case occurs with poor pivot selection. |

---

## 5. Implementation

```python
import heapq

def solve_optimal(nums, k):
    \"\"\"
    Optimal solution using a Min-Heap.
    Time Complexity: O(N log k)
    Space Complexity: O(k)
    \"\"\"
    # Python's heapq implements a Min-Heap by default
    min_heap = []
    
    for num in nums:
        heapq.heappush(min_heap, num)
        # Keep the heap size limited to k
        if len(min_heap) > k:
            heapq.heappop(min_heap)
            
    # The root of the heap is the k-th largest element
    return min_heap[0]

# Example Usage:
# print(solve_optimal([3,2,3,1,2,4,5,5,6], 4)) # Output: 4
```

---

## 6. Real-World Applications

The pattern of finding the "Top-K" elements is ubiquitous in professional software engineering:

1. **Leaderboards:** In gaming or competitive platforms, maintaining a real-time top 100 leaderboard. Using a Min-Heap allows the system to process millions of scores without sorting the entire database.
2. **Recommendation Systems:** When a system needs to suggest the "Top 5 most relevant articles" based on a similarity score.
3. **Network Traffic Monitoring:** Identifying the "Top K" IP addresses consuming the most bandwidth to detect potential DDoS attacks.
4. **Priority Scheduling:** Operating systems use priority queues to manage processes, ensuring that the most critical tasks (highest priority) are handled first.
5. **Search Engines:** Returning the top $k$ results based on the ranking algorithm's score (PageRank).""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N log N)
# Space Complexity: O(1) or O(N) depending on the sorting algorithm implementation (Timsort in Python is O(N))
# The simplest approach is to sort the entire array in descending order and retrieve the element at index k-1.
def solve_naive(nums, k):
    if not nums or k > len(nums):
        return None
    
    # Sort the array in descending order
    sorted_nums = sorted(nums, reverse=True)
    
    # Return the kth element
    return sorted_nums[k - 1]

# --- APPROACH 2: Optimal (Min-Heap) ---
# Time Complexity: O(N log k)
# Space Complexity: O(k)
# A min-heap of size k is maintained. As we iterate through the array, we keep the k largest elements seen so far in the heap.
# The smallest element among these k largest elements (the root of the min-heap) will be the kth largest element overall.
# This is optimal because it reduces the time complexity from O(N log N) to O(N log k), which is significantly faster when k << N.
import heapq

def solve_optimal(nums, k):
    if not nums or k > len(nums):
        return None
    
    # Create a min-heap to store the k largest elements
    min_heap = []
    
    for num in nums:
        # Push current element onto the heap
        heapq.heappush(min_heap, num)
        
        # If heap size exceeds k, remove the smallest element
        if len(min_heap) > k:
            heapq.heappop(min_heap)
            
    # The root of the min-heap is the kth largest element
    return min_heap[0]

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package heap;

import java.util.PriorityQueue;

public class KthLargestArray {
    /**
     * Finds the kth largest element in an array using a Min-Heap.
     * 
     * @param nums The input array of integers.
     * @param k    The rank of the element to find.
     * @return     The kth largest element.
     * @throws IllegalArgumentException if the array is null or k is out of bounds.
     */
    public static int findKthLargest(int[] nums, int k) {
        if (nums == null || k <= 0 || k > nums.length) {
            throw new IllegalArgumentException("Invalid input array or k value.");
        }

        // PriorityQueue in Java is a min-heap by default
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();

        for (int num : nums) {
            minHeap.add(num);
            
            // Maintain only k elements in the heap
            if (minHeap.size() > k) {
                minHeap.poll();
            }
        }

        // The head of the heap is the kth largest element
        return minHeap.peek();
    }

    public static void main(String[] args) {
        int[] nums = {3, 2, 3, 1, 2, 4, 5, 5, 6};
        int k = 4;
        System.out.println("Kth largest element is: " + findKthLargest(nums, k)); 
        // Output: 4
    }
}
\"\"\"""",
}

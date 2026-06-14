"""
Challenge: q01_kth_largest
Difficulty: Easy
Link: https://leetcode.com/problems/kth-largest-element-in-a-stream/

Problem:
Kth largest element in stream.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N log N) per add operation, where N is the current size of the stream.
# Space Complexity: O(N) to store all elements of the stream.
# This approach stores every element received in a list. Every time a new element is added, 
# it sorts the entire list in descending order and retrieves the element at index k-1.

class KthLargestNaive:
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.nums = nums

    def add(self, val: int) -> int:
        self.nums.append(val)
        self.nums.sort(reverse=True)
        return self.nums[self.k - 1]

# --- APPROACH 2: Optimal (Min-Heap) ---
# Time Complexity: O(N log k) for initialization and O(log k) for each add operation.
# Space Complexity: O(k) to store only the k largest elements.
# This approach is optimal because it maintains a min-heap of size k. The root of the heap 
# always represents the smallest of the k largest elements, which is exactly the k-th 
# largest element. By keeping the heap size at k, we minimize space and ensure logarithmic 
# time complexity for insertions.

import heapq

class KthLargestOptimal:
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.min_heap = nums
        # Transform the list into a heap in-place: O(N)
        heapq.heapify(self.min_heap)
        # Remove elements until only the k largest remain: O((N-k) log N)
        while len(self.min_heap) > k:
            heapq.heappop(self.min_heap)

    def add(self, val: int) -> int:
        # Push the new value onto the heap: O(log k)
        heapq.heappush(self.min_heap, val)
        # If heap exceeds size k, remove the smallest: O(log k)
        if len(self.min_heap) > self.k:
            heapq.heappop(self.min_heap)
        # The root of the min-heap is the k-th largest element
        return self.min_heap[0]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package heap;

import java.util.PriorityQueue;
import java.util.List;
import java.util.ArrayList;

public class KthLargest {
    private final PriorityQueue<Integer> minHeap;
    private final int k;

    public KthLargest(int k, int[] nums) {
        this.k = k;
        this.minHeap = new PriorityQueue<>(k);
        
        for (int num : nums) {
            add(num);
        }
    }

    public int add(int val) {
        minHeap.offer(val);
        if (minHeap.size() > k) {
            minHeap.poll();
        }
        return minHeap.peek();
    }

    public static void main(String[] args) {
        int[] nums = {4, 5, 8, 2};
        KthLargest kthLargest = new KthLargest(3, nums);
        System.out.println(kthLargest.add(3));  // Returns 4
        System.out.println(kthLargest.add(5));  // Returns 5
        System.out.println(kthLargest.add(10)); // Returns 5
        System.out.println(kthLargest.add(9));  // Returns 8
        System.out.println(kthLargest.add(4));  // Returns 8
    }
}
"""

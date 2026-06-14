"""
Challenge: q05_median_stream
Difficulty: Hard
Link: https://leetcode.com/problems/find-median-from-data-stream/

Problem:
Find median from dynamic stream.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N) per addNum, O(1) per findMedian
# Space Complexity: O(N)
# This approach maintains a sorted list using binary search for insertion (bisect.insort). 
# While finding the median is constant time, inserting each new element takes linear time 
# because shifting elements in a Python list is O(N).
import bisect

class MedianFinderNaive:
    def __init__(self):
        self.data = []

    def addNum(self, num: int) -> None:
        # Maintain sorted order using bisect.insort
        bisect.insort(self.data, num)

    def findMedian(self) -> float:
        n = len(self.data)
        if n % 2 == 1:
            return float(self.data[n // 2])
        else:
            return (self.data[n // 2 - 1] + self.data[n // 2]) / 2.0

def solve_naive(nums):
    mf = MedianFinderNaive()
    results = []
    for n in nums:
        mf.addNum(n)
        results.append(mf.findMedian())
    return results

# --- APPROACH 2: Optimal (Two Heaps) ---
# Time Complexity: O(log N) per addNum, O(1) per findMedian
# Space Complexity: O(N)
# This approach uses two heaps: a max-heap to store the smaller half of the numbers 
# and a min-heap to store the larger half. By keeping the heaps balanced (size difference <= 1), 
# the median is always at the root of one or both heaps. This is optimal because it reduces 
# the insertion cost from linear to logarithmic.
import heapq

class MedianFinder:
    def __init__(self):
        # max_heap stores the smaller half (inverted values for heapq min-heap)
        self.small = [] 
        # min_heap stores the larger half
        self.large = []

    def addNum(self, num: int) -> None:
        # Step 1: Add to small heap (max-heap)
        heapq.heappush(self.small, -num)
        
        # Step 2: Ensure every element in small <= every element in large
        # Move the largest of the small half to the large half
        val = -heapq.heappop(self.small)
        heapq.heappush(self.large, val)
        
        # Step 3: Maintain size balance: len(small) >= len(large)
        if len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        else:
            return (-self.small[0] + self.large[0]) / 2.0

def solve_optimal(nums):
    mf = MedianFinder()
    results = []
    for n in nums:
        mf.addNum(n)
        results.append(mf.findMedian())
    return results

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package heap;

import java.util.PriorityQueue;
import java.util.Collections;

public class MedianStream {
    private PriorityQueue<Integer> small; // Max-heap
    private PriorityQueue<Integer> large; // Min-heap

    public MedianStream() {
        // Max-heap for the smaller half
        small = new PriorityQueue<>(Collections.reverseOrder());
        // Min-heap for the larger half
        large = new PriorityQueue<>();
    }

    public void addNum(int num) {
        // Always add to small heap first
        small.offer(num);
        
        // Balance: move largest of small to large
        large.offer(small.poll());
        
        // Maintain size property: small.size() >= large.size()
        if (large.size() > small.size()) {
            small.offer(large.poll());
        }
    }

    public double findMedian() {
        if (small.size() > large.size()) {
            return (double) small.peek();
        } else {
            return (small.peek() + large.peek()) / 2.0;
        }
    }

    public static void main(String[] args) {
        MedianStream ms = new MedianStream();
        ms.addNum(1);
        System.out.println(ms.findMedian()); // 1.0
        ms.addNum(2);
        System.out.println(ms.findMedian()); // 1.5
        ms.addNum(3);
        System.out.println(ms.findMedian()); // 2.0
    }
}
"""

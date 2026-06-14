"""
Challenge: q04_kth_largest_array
Difficulty: Medium
Link: https://leetcode.com/problems/kth-largest-element-in-an-array/

Problem:
Kth largest array.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

"""
Challenge: q04_find_minimum_in_rotated_sorted_array
Difficulty: Medium
Link: https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/

Problem:
Find minimum element in a sorted array that was rotated.
"""

# --- STARTER TEMPLATE FOR USER ---
def find_min(nums: list[int]) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# The naive approach iterates through the entire array once to find the minimum element.
def find_min_naive(nums: list[int]) -> int:
    if not nums:
        raise ValueError("Input array cannot be empty")
    
    min_val = nums[0]
    for i in range(1, len(nums)):
        if nums[i] < min_val:
            min_val = nums[i]
    return min_val

# --- APPROACH 2: Optimal (Binary Search) ---
# Time Complexity: O(log n)
# Space Complexity: O(1)
# Since the array is sorted and then rotated, it consists of two sorted subarrays. 
# We use binary search to identify the "pivot" point where the rotation occurred.
# If nums[mid] > nums[right], the minimum element must be in the right half (mid + 1 to right).
# If nums[mid] <= nums[right], the minimum element is either at mid or in the left half (left to mid).
# This reduces the search space by half in each iteration, making it O(log n).
def find_min(nums: list[int]) -> int:
    if not nums:
        raise ValueError("Input array cannot be empty")
    
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = left + (right - left) // 2
        
        # If mid element is greater than the rightmost element, 
        # the minimum must be in the right part of the array.
        if nums[mid] > nums[right]:
            left = mid + 1
        # Otherwise, the minimum is in the left part, including mid.
        else:
            right = mid
            
    return nums[left]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package binary_search;

public class FindMinimumInRotatedSortedArray {
    /**
     * Finds the minimum element in a rotated sorted array.
     * Time Complexity: O(log n)
     * Space Complexity: O(1)
     */
    public int findMin(int[] nums) {
        if (nums == null || nums.length == 0) {
            throw new IllegalArgumentException("Input array cannot be empty");
        }
        
        int left = 0;
        int right = nums.length - 1;
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] > nums[right]) {
                // The minimum is in the right half
                left = mid + 1;
            } else {
                // The minimum is in the left half, including mid
                right = mid;
            }
        }
        
        return nums[left];
    }

    public static void main(String[] args) {
        FindMinimumInRotatedSortedArray solver = new FindMinimumInRotatedSortedArray();
        int[] nums = {4, 5, 6, 7, 0, 1, 2};
        System.out.println("Minimum element: " + solver.findMin(nums)); // Output: 0
    }
}
"""

"""
Challenge: q01_binary_search
Difficulty: Easy
Link: https://leetcode.com/problems/binary-search/

Problem:
Search for a target value in a sorted array, returning index or -1.
"""

# --- STARTER TEMPLATE FOR USER ---
def search(nums: list[int], target: int) -> int:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach performs a linear search through the array, checking each element one by one. 
# It does not take advantage of the fact that the array is sorted.
def search_naive(nums: list[int], target: int) -> int:
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1

# --- APPROACH 2: Optimal (Binary Search) ---
# Time Complexity: O(log n)
# Space Complexity: O(1)
# This approach uses the Binary Search algorithm. Since the input array is sorted, 
# we can repeatedly divide the search interval in half. If the value of the search key 
# is less than the item in the middle of the interval, we narrow the interval to the 
# lower half. Otherwise, we narrow it to the upper half. This logarithmic time 
# complexity is optimal for searching in a sorted array.
def search_optimal(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    
    while left <= right:
        # Use (left + right) // 2, or left + (right - left) // 2 to prevent overflow in some languages
        mid = left + (right - left) // 2
        
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package binary_search;

public class BinarySearch {
    /**
     * Searches for a target value in a sorted integer array.
     * @param nums Sorted array of integers.
     * @param target The value to search for.
     * @return The index of the target if found, otherwise -1.
     */
    public static int search(int[] nums, int target) {
        if (nums == null || nums.length == 0) {
            return -1;
        }

        int left = 0;
        int right = nums.length - 1;

        while (left <= right) {
            // Prevent potential integer overflow for very large arrays
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return -1;
    }

    public static void main(String[] args) {
        int[] nums = {-1, 0, 3, 5, 9, 12};
        int target = 9;
        System.out.println("Index of target: " + search(nums, target)); // Output: 4
    }
}
"""

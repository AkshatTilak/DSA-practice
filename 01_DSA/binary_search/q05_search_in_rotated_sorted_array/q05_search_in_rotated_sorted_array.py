"""
Challenge: q05_search_in_rotated_sorted_array
Difficulty: Medium
Link: https://leetcode.com/problems/search-in-rotated-sorted-array/

Problem:
Find index of target in rotated sorted array.
"""

# --- STARTER TEMPLATE FOR USER ---
def search_rotated(nums: list[int], target: int) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach performs a linear scan of the array to find the target element.
# It does not leverage the sorted (though rotated) property of the array.
def search_rotated_naive(nums: list[int], target: int) -> int:
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1

# --- APPROACH 2: Optimal (Modified Binary Search) ---
# Time Complexity: O(log n)
# Space Complexity: O(1)
# This approach uses binary search. In a rotated sorted array, at least one half 
# (left or right of the midpoint) is always sorted. By identifying the sorted 
# half, we can determine if the target lies within its range. If it does, we 
# search that half; otherwise, we search the other half. This reduces the search 
# space by half in each iteration, making it optimal.
def search_rotated_optimal(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        
        # Identify which half is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
                
    return -1

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package binary_search;

public class SearchInRotatedSortedArray {
    /**
     * Searches for a target value in a rotated sorted array.
     * @param nums The rotated sorted array of integers.
     * @param target The integer value to search for.
     * @return The index of target if found, otherwise -1.
     */
    public int search(int[] nums, int target) {
        if (nums == null || nums.length == 0) {
            return -1;
        }
        
        int left = 0;
        int right = nums.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) {
                return mid;
            }
            
            // Check if the left half [left...mid] is sorted
            if (nums[left] <= nums[mid]) {
                // Target is within the sorted left half
                if (target >= nums[left] && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                // Right half [mid...right] must be sorted
                // Target is within the sorted right half
                if (target > nums[mid] && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        
        return -1;
    }

    public static void main(String[] args) {
        SearchInRotatedSortedArray solution = new SearchInRotatedSortedArray();
        int[] nums = {4, 5, 6, 7, 0, 1, 2};
        int target = 0;
        System.out.println("Index: " + solution.search(nums, target)); // Output: 4
    }
}
"""

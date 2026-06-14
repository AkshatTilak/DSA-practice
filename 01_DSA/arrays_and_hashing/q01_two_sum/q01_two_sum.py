"""
LeetCode 1: Two Sum
Difficulty: Easy
Category: Arrays & Hashing

Problem:
Given an array of integers `nums` and an integer `target`, return indices of the two numbers 
such that they add up to `target`.
You may assume that each input would have exactly one solution, and you may not use the 
same element twice. You can return the answer in any order.

Curriculum Link: https://leetcode.com/problems/two-sum/
"""

# --- STARTER TEMPLATE FOR USER ---
# You can implement your solution here. When testing, the system will run tests against this definition.
def two_sum(nums: list[int], target: int) -> list[int]:
    """
    Find two numbers in `nums` that add up to `target` and return their indices.
    """
    # Write your solution here
    pass


# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach uses nested loops to check every possible pair of numbers in the array to see if they sum up to the target.
def two_sum_naive(nums: list[int], target: int) -> list[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# --- APPROACH 2: Optimal (Hash Map) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach is optimal because it reduces the search time for the complement (target - current_value) from O(n) to O(1) 
# using a hash map, allowing us to find the result in a single pass through the array.
def two_sum_optimal(nums: list[int], target: int) -> list[int]:
    prev_map = {}  # val : index
    for i, n in enumerate(nums):
        diff = target - n
        if diff in prev_map:
            return [prev_map[diff], i]
        prev_map[n] = i
    return []

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.HashMap;
import java.util.Map;

public class TwoSum {
    /**
     * Returns the indices of two numbers such that they add up to the target.
     * Time Complexity: O(n)
     * Space Complexity: O(n)
     */
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> prevMap = new HashMap<>();
        
        for (int i = 0; i < nums.length; i++) {
            int diff = target - nums[i];
            if (prevMap.containsKey(diff)) {
                return new int[] { prevMap.get(diff), i };
            }
            prevMap.put(nums[i], i);
        }
        
        // Based on problem constraints, a solution is always guaranteed.
        // Returning an empty array or throwing an exception as a fallback.
        return new int[] {};
    }
}
"""

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

# --- APPROACH 1: Naive Brute Force ---
# Time Complexity: O(N^2)
# Space Complexity: O(1)
def two_sum_brute_force(nums: list[int], target: int) -> list[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


# --- APPROACH 2: Optimal Pythonic (Hash Map) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# Exploits Python's fast dictionary hashing for constant-time lookups.
def two_sum_optimal(nums: list[int], target: int) -> list[int]:
    num_to_idx = {}
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in num_to_idx:
            return [num_to_idx[complement], idx]
        num_to_idx[num] = idx
    return []


# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.HashMap;
import java.util.Map;

public class TwoSum {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> numMap = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (numMap.containsKey(complement)) {
                return new int[] { numMap.get(complement), i };
            }
            numMap.put(nums[i], i);
        }
        throw new IllegalArgumentException("No two sum solution");
    }
}
"""

"""
Challenge: q02_contains_duplicate
Difficulty: Easy
Link: https://leetcode.com/problems/contains-duplicate/

Problem:
Given an integer array `nums`, return `true` if any value appears at least twice in the array, and return `false` if every element is distinct.
"""

# --- STARTER TEMPLATE FOR USER ---
def contains_duplicate(nums: list[int]) -> bool:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach uses nested loops to compare every pair of elements in the array. 
# It is inefficient for large datasets but requires no additional memory.
def contains_duplicate_naive(nums: list[int]) -> bool:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] == nums[j]:
                return True
    return False

# --- APPROACH 2: Optimal (Hash Set) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach uses a hash set to keep track of the elements encountered so far.
# Checking for existence in a set takes O(1) on average, and we traverse the list once.
# This is optimal because we must examine each element at least once in the worst case, 
# and the hash set provides the fastest possible lookup time.
def contains_duplicate_optimal(nums: list[int]) -> bool:
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.HashSet;
import java.util.Set;

public class ContainsDuplicate {
    /**
     * Checks if any value appears at least twice in the array.
     * Time Complexity: O(n)
     * Space Complexity: O(n)
     */
    public boolean containsDuplicate(int[] nums) {
        if (nums == null || nums.length == 0) {
            return false;
        }
        
        Set<Integer> seen = new HashSet<>();
        for (int num : nums) {
            if (seen.contains(num)) {
                return true;
            }
            seen.add(num);
        }
        return false;
    }

    public static void main(String[] args) {
        ContainsDuplicate solution = new ContainsDuplicate();
        System.out.println(solution.containsDuplicate(new int[]{1, 2, 3, 1})); // true
        System.out.println(solution.containsDuplicate(new int[]{1, 2, 3, 4})); // false
    }
}
"""

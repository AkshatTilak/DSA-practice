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

# Approach 1: Naive (Sort) O(N log N)
def contains_duplicate_naive(nums: list[int]) -> bool:
    nums.sort()
    for i in range(len(nums) - 1):
        if nums[i] == nums[i+1]:
            return True
    return False

# Approach 2: Optimal (Hash Set) O(N)
def contains_duplicate_optimal(nums: list[int]) -> bool:
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# Approach 3: Java
'''
public boolean containsDuplicate(int[] nums) {
    Set<Integer> set = new HashSet<>();
    for (int n : nums) {
        if (!set.add(n)) return true;
    }
    return false;
}
'''

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

# Approach 1: Naive (Linear search) O(N)
def search_naive(nums: list[int], target: int) -> int:
    for i in range(len(nums)):
        if nums[i] == target: return i
    return -1

# Approach 2: Optimal (Split-interval) O(log N)
def search_optimal(nums: list[int], target: int) -> int:
    l, r = 0, len(nums) - 1
    while l <= r:
        m = l + (r - l) // 2
        if nums[m] == target: return m
        elif nums[m] < target: l = m + 1
        else: r = m - 1
    return -1

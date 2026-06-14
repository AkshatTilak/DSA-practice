"""
Challenge: q03_house_robber
Difficulty: Medium
Link: https://leetcode.com/problems/house-robber/

Problem:
Rob non-adjacent houses.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(2^n)
# Space Complexity: O(n)
# This approach uses recursion to explore all possible combinations of robbing or skipping houses.
# For every house, we have two choices: rob it (and move to index i+2) or skip it (and move to index i+1).
def solve_naive(nums):
    def rob_from(i):
        if i >= len(nums):
            return 0
        # Choice 1: Rob current house and move to house i+2
        rob = nums[i] + rob_from(i + 2)
        # Choice 2: Skip current house and move to house i+1
        skip = rob_from(i + 1)
        return max(rob, skip)
    
    return rob_from(0)

# --- APPROACH 2: Optimal (Dynamic Programming with Space Optimization) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses dynamic programming. We maintain two variables to keep track of the 
# maximum amount robbed up to the previous house and the house before that.
# The recurrence relation is: dp[i] = max(dp[i-1], dp[i-2] + nums[i]).
# This is optimal because it processes the array in a single pass and uses constant extra space.
def solve_optimal(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]
    
    # prev2 represents dp[i-2], prev1 represents dp[i-1]
    prev2 = 0
    prev1 = 0
    
    for amount in nums:
        # Current max is the maximum of:
        # 1. Robbing current house + max from 2 houses ago
        # 2. Skipping current house and taking max from 1 house ago
        current = max(prev1, prev2 + amount)
        prev2 = prev1
        prev1 = current
        
    return prev1

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

public class HouseRobber {
    /**
     * Calculates the maximum amount of money that can be robbed without
     * robbing two adjacent houses.
     *
     * @param nums Array of money in each house
     * @return Maximum money robbed
     */
    public int rob(int[] nums) {
        if (nums == null || nums.length == 0) {
            return 0;
        }
        if (nums.length == 1) {
            return nums[0];
        }

        int prev2 = 0; // Max robbed up to i-2
        int prev1 = 0; // Max robbed up to i-1

        for (int amount : nums) {
            int current = Math.max(prev1, prev2 + amount);
            prev2 = prev1;
            prev1 = current;
        }

        return prev1;
    }

    public static void main(String[] args) {
        HouseRobber solver = new HouseRobber();
        int[] test1 = {1, 2, 3, 1};
        int[] test2 = {2, 7, 9, 3, 1};
        System.out.println("Test 1: " + solver.rob(test1)); // Expected: 4
        System.out.println("Test 2: " + solver.rob(test2)); // Expected: 12
    }
}
"""

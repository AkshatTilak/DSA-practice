"""
Challenge: q04_house_robber_ii
Difficulty: Medium
Link: https://leetcode.com/problems/house-robber-ii/

Problem:
Circular robber.
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
# The naive approach uses recursion to explore all possible combinations of houses to rob.
# Since the houses are in a circle, we split the problem into two linear sub-problems:
# one where the first house is excluded and one where the last house is excluded.
def solve_naive(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    def rob_linear(houses):
        def helper(i):
            if i < 0:
                return 0
            # Option 1: Don't rob current house, move to previous
            # Option 2: Rob current house, move to house i-2
            return max(helper(i - 1), houses[i] + helper(i - 2))
        return helper(len(houses) - 1)

    # Case 1: Exclude the last house
    # Case 2: Exclude the first house
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))

# --- APPROACH 2: Optimal (Dynamic Programming with Space Optimization) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# The problem is reduced to the linear House Robber problem. Because the houses are circular,
# we cannot rob both the first and the last house. Therefore, the result is the maximum of:
# 1. Robbing houses from index 0 to n-2.
# 2. Robbing houses from index 1 to n-1.
# We use two variables to track the maximum profit up to the previous house and the one before that,
# reducing space complexity from O(n) to O(1).
def solve_optimal(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    def rob_linear(houses):
        prev_max = 0  # dp[i-2]
        curr_max = 0  # dp[i-1]
        for amount in houses:
            # The new maximum is either the previous maximum or 
            # the maximum from two houses ago plus the current house amount.
            temp = curr_max
            curr_max = max(curr_max, prev_max + amount)
            prev_max = temp
        return curr_max

    # Solve for the two possible linear ranges and return the maximum.
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

public class HouseRobberIi {
    /**
     * Computes the maximum amount of money that can be robbed from circular houses.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int rob(int[] nums) {
        if (nums == null || nums.length == 0) {
            return 0;
        }
        if (nums.length == 1) {
            return nums[0];
        }

        // The result is the maximum of robbing houses 0 to n-2 OR houses 1 to n-1.
        return Math.max(robLinear(nums, 0, nums.length - 2), 
                        robLinear(nums, 1, nums.length - 1));
    }

    private int robLinear(int[] nums, int start, int end) {
        int prevMax = 0;
        int currMax = 0;

        for (int i = start; i <= end; i++) {
            int temp = currMax;
            currMax = Math.max(currMax, prevMax + nums[i]);
            prevMax = temp;
        }

        return currMax;
    }

    public static void main(String[] args) {
        HouseRobberIi solution = new HouseRobberIi();
        int[] test1 = {2, 3, 2};
        int[] test2 = {1, 2, 3, 1};
        System.out.println(solution.rob(test1)); // Output: 3
        System.out.println(solution.rob(test2)); // Output: 4
    }
}
"""

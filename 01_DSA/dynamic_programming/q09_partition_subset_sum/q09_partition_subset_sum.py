"""
Challenge: q09_partition_subset_sum
Difficulty: Medium
Link: https://leetcode.com/problems/partition-equal-subset-sum/

Problem:
Partition equal sum check.
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
# This approach uses recursion to explore all possible subsets. For each element, we decide
# whether to include it in the target sum or not. This results in an exponential time complexity.
def can_partition_naive(nums):
    total_sum = sum(nums)
    if total_sum % 2 != 0:
        return False
    
    target = total_sum // 2
    n = len(nums)
    
    def solve(index, current_sum):
        # Base case: target sum reached
        if current_sum == target:
            return True
        # Base case: index out of bounds or sum exceeded
        if index >= n or current_sum > target:
            return False
        
        # Option 1: Include nums[index] in the subset
        if solve(index + 1, current_sum + nums[index]):
            return True
        
        # Option 2: Exclude nums[index] from the subset
        if solve(index + 1, current_sum):
            return True
            
        return False

    return solve(0, 0)

# --- APPROACH 2: Optimal (Dynamic Programming) ---
# Time Complexity: O(n * S) where n is the number of elements and S is the target sum (total_sum / 2).
# Space Complexity: O(S)
# This approach uses a 1D DP array to track reachable sums. We iterate through each number
# and update the DP table from right to left to ensure each number is used only once per subset.
# This is optimal because it reduces the state space from exponential to pseudo-polynomial
# and minimizes space by utilizing the property that the current state only depends on the previous state.
def can_partition_optimal(nums):
    total_sum = sum(nums)
    
    # If the total sum is odd, it's impossible to partition it into two equal integer subsets.
    if total_sum % 2 != 0:
        return False
    
    target = total_sum // 2
    n = len(nums)
    
    # dp[i] will be True if a subset sum of i is possible
    dp = [False] * (target + 1)
    dp[0] = True # Sum of 0 is always possible (empty subset)
    
    for num in nums:
        # Iterate backwards to prevent using the same element multiple times for the same target sum
        for j in range(target, num - 1, -1):
            if dp[j - num]:
                dp[j] = True
        
        # Early exit if we've already found a way to reach the target sum
        if dp[target]:
            return True
            
    return dp[target]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

import java.util.*;

public class PartitionSubsetSum {
    /**
     * Checks if the array can be partitioned into two subsets with equal sums.
     * Time Complexity: O(n * S)
     * Space Complexity: O(S)
     */
    public boolean canPartition(int[] nums) {
        if (nums == null || nums.length == 0) {
            return false;
        }
        
        int totalSum = 0;
        for (int num : nums) {
            totalSum += num;
        }
        
        // If total sum is odd, cannot be partitioned into two equal halves
        if (totalSum % 2 != 0) {
            return false;
        }
        
        int target = totalSum / 2;
        boolean[] dp = new boolean[target + 1];
        dp[0] = true;
        
        for (int num : nums) {
            // Traverse backwards to ensure we use the 'previous' state of the DP array
            for (int j = target; j >= num; j--) {
                if (dp[j - num]) {
                    dp[j] = true;
                }
            }
            // Optimization: Return true immediately if target is reached
            if (dp[target]) {
                return true;
            }
        }
        
        return dp[target];
    }

    public static void main(String[] args) {
        PartitionSubsetSum solver = new PartitionSubsetSum();
        int[] nums1 = {1, 5, 11, 5};
        System.out.println("Input: [1, 5, 11, 5] | Result: " + solver.canPartition(nums1)); // Expected: true
        
        int[] nums2 = {1, 2, 3, 5};
        System.out.println("Input: [1, 2, 3, 5] | Result: " + solver.canPartition(nums2)); // Expected: false
    }
}
"""

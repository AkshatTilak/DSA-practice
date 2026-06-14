"""
Challenge: q08_longest_increasing_subsequence
Difficulty: Medium
Link: https://leetcode.com/problems/longest-increasing-subsequence/

Problem:
LIS length.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(n)
# This approach uses dynamic programming. We maintain an array 'dp' where dp[i] represents the length of the longest increasing subsequence ending at index i. For each element, we look back at all previous elements to find the maximum LIS length that can be extended.
def solve_naive(nums):
    if not nums:
        return 0
    
    n = len(nums)
    # Initialize DP table with 1 since each element is an LIS of length 1
    dp = [1] * n
    
    for i in range(1, n):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
                
    return max(dp)

# --- APPROACH 2: Optimal (Binary Search / Patience Sorting) ---
# Time Complexity: O(n log n)
# Space Complexity: O(n)
# This approach uses the concept of Patience Sorting. We maintain a list 'tails', where tails[i] is the smallest tail of all increasing subsequences of length i+1. For each number x in the input, we use binary search to find the smallest element in 'tails' that is greater than or equal to x and replace it. If x is larger than all elements in 'tails', we append it. This ensures that 'tails' remains sorted and represents the most optimistic potential for future extensions.
import bisect

def solve_optimal(nums):
    if not nums:
        return 0
    
    # tails[i] will store the smallest tail of all increasing subsequences of length i+1
    tails = []
    
    for x in nums:
        # Binary search to find the insertion point for x in tails
        # bisect_left finds the leftmost index to insert x while maintaining order
        idx = bisect.bisect_left(tails, x)
        
        if idx == len(tails):
            # x is larger than any current tail, extending the longest subsequence
            tails.append(x)
        else:
            # x can replace an existing tail to potentially allow longer subsequences later
            tails[idx] = x
            
    return len(tails)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class LongestIncreasingSubsequence {
    /**
     * Computes the length of the Longest Increasing Subsequence using Binary Search.
     * Time Complexity: O(n log n)
     * Space Complexity: O(n)
     */
    public int solveOptimal(int[] nums) {
        if (nums == null || nums.length == 0) {
            return 0;
        }

        // Using a list to act as the 'tails' array for binary search
        List<Integer> tails = new ArrayList<>();

        for (int x : nums) {
            int idx = Collections.binarySearch(tails, x);
            
            // binarySearch returns (-(insertion point) - 1) if the element is not found
            if (idx < 0) {
                idx = -(idx + 1);
            }

            if (idx == tails.size()) {
                tails.add(x);
            } else {
                tails.set(idx, x);
            }
        }

        return tails.size();
    }

    public static void main(String[] args) {
        LongestIncreasingSubsequence lis = new LongestIncreasingSubsequence();
        int[] nums = {10, 9, 2, 5, 3, 7, 101, 18};
        System.out.println("Length of LIS: " + lis.solveOptimal(nums)); // Output: 4
    }
}
"""

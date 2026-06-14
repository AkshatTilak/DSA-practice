"""
Challenge: q01_climbing_stairs
Difficulty: Easy
Link: https://leetcode.com/problems/climbing-stairs/

Problem:
Calculate distinct ways to climb n steps if you take 1 or 2 steps each time.
"""

# --- STARTER TEMPLATE FOR USER ---
def climb_stairs(n: int) -> int:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(2^n)
# Space Complexity: O(n)
# This approach uses simple recursion to explore all possible paths. It recalculates 
# the same subproblems multiple times, leading to exponential time complexity.
def climb_stairs_naive(n: int) -> int:
    if n <= 2:
        return n
    return climb_stairs_naive(n - 1) + climb_stairs_naive(n - 2)

# --- APPROACH 2: Optimal (Iterative DP with Space Optimization) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach recognizes that the number of ways to reach step n is the sum of the 
# ways to reach (n-1) and (n-2), which is the Fibonacci sequence. Instead of using 
# an array to store all values (O(n) space), we only keep track of the last two 
# computed values, reducing space complexity to constant.
def climb_stairs_optimal(n: int) -> int:
    if n <= 2:
        return n
    
    # Base cases: ways to reach step 1 and step 2
    first = 1
    second = 2
    
    for i in range(3, n + 1):
        current = first + second
        first = second
        second = current
        
    return second

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

public class ClimbingStairs {
    /**
     * Calculates the number of distinct ways to climb n steps.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int climbStairs(int n) {
        if (n <= 2) {
            return n;
        }
        
        int first = 1;
        int second = 2;
        
        for (int i = 3; i <= n; i++) {
            int current = first + second;
            first = second;
            second = current;
        }
        
        return second;
    }

    public static void main(String[] args) {
        ClimbingStairs solution = new ClimbingStairs();
        System.out.println(solution.climbStairs(5)); // Output: 8
    }
}
"""

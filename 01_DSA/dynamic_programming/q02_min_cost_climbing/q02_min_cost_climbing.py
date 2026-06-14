"""
Challenge: q02_min_cost_climbing
Difficulty: Easy
Link: https://leetcode.com/problems/min-cost-climbing-stairs/

Problem:
Min cost stairs.
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
# This approach uses simple recursion to find the minimum cost to reach each step. 
# It recalculates the cost for the same step multiple times, leading to exponential time complexity.
def solve_naive(cost):
    def calculate_min_cost(i):
        # Base case: if we are at the first or second step, the cost is just the cost of that step.
        if i <= 1:
            return cost[i]
        # Recurrence: cost to reach step i is cost[i] plus the minimum of the two previous steps.
        return cost[i] + min(calculate_min_cost(i - 1), calculate_min_cost(i - 2))

    n = len(cost)
    # The goal is to reach the top, which is one step beyond the last index.
    # We can reach the top from either the last step or the second-to-last step.
    return min(calculate_min_cost(n - 1), calculate_min_cost(n - 2))

# --- APPROACH 2: Optimal (Dynamic Programming with Space Optimization) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses Dynamic Programming. Instead of maintaining a full DP table, 
# we only track the costs of the two most recent steps since each step only depends on them.
# It is optimal because it visits each element exactly once and uses constant extra space.
def solve_optimal(cost):
    n = len(cost)
    if n == 0:
        return 0
    if n == 1:
        return cost[0]
    
    # prev2 represents the cost to reach step i-2
    # prev1 represents the cost to reach step i-1
    prev2 = cost[0]
    prev1 = cost[1]
    
    for i in range(2, n):
        # The cost to reach the current step is its own cost plus the cheaper of the two paths.
        current = cost[i] + min(prev1, prev2)
        prev2 = prev1
        prev1 = current
        
    # The top can be reached from either of the last two calculated steps.
    return min(prev1, prev2)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

public class MinCostClimbing {
    /**
     * Calculates the minimum cost to reach the top of the stairs.
     * 
     * @param cost An array where cost[i] is the cost of the ith step.
     * @return The minimum cost to reach the top.
     */
    public int solve(int[] cost) {
        if (cost == null || cost.length == 0) {
            return 0;
        }
        int n = cost.length;
        if (n == 1) {
            return cost[0];
        }

        int prev2 = cost[0];
        int prev1 = cost[1];

        for (int i = 2; i < n; i++) {
            int current = cost[i] + Math.min(prev1, prev2);
            prev2 = prev1;
            prev1 = current;
        }

        return Math.min(prev1, prev2);
    }

    public static void main(String[] args) {
        MinCostClimbing solver = new MinCostClimbing();
        int[] cost1 = {10, 15, 20};
        System.out.println("Test 1: " + solver.solve(cost1)); // Expected: 15

        int[] cost2 = {1, 100, 1, 1, 1, 100, 1, 1, 100, 1};
        System.out.println("Test 2: " + solver.solve(cost2)); // Expected: 6
    }
}
"""

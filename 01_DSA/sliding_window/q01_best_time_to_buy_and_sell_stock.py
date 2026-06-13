"""
Challenge: q01_best_time_to_buy_and_sell_stock
Difficulty: Easy
Link: https://leetcode.com/problems/best-time-to-buy-and-sell-stock/

Problem:
Find the maximum profit you can achieve buying one day and selling another.
"""

# --- STARTER TEMPLATE FOR USER ---
def max_profit(prices: list[int]) -> int:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Approach 1: Naive (O(N^2))
def max_profit_naive(prices: list[int]) -> int:
    max_p = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            max_p = max(max_p, prices[j] - prices[i])
    return max_p

# Approach 2: Optimal (Sliding Window / Min Tracker) O(N)
def max_profit_optimal(prices: list[int]) -> int:
    min_p = float('inf')
    max_p = 0
    for p in prices:
        if p < min_p: min_p = p
        elif p - min_p > max_p: max_p = p - min_p
    return max_p

# Approach 3: Java
'''
public int maxProfit(int[] prices) {
    int min = Integer.MAX_VALUE, max = 0;
    for(int p : prices) {
        if(p < min) min = p;
        else if(p - min > max) max = p - min;
    }
    return max;
}
'''

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

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach iterates through every possible pair of buying and selling days, 
# calculating the profit for each valid pair (where sell day > buy day) and 
# keeping track of the maximum value found.
def max_profit_naive(prices: list[int]) -> int:
    if not prices or len(prices) < 2:
        return 0
    
    max_p = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            profit = prices[j] - prices[i]
            if profit > max_p:
                max_p = profit
    return max_p

# --- APPROACH 2: Optimal (One-Pass / Two-Pointer) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach is optimal because it traverses the list exactly once. 
# It maintains the minimum price encountered so far and calculates the potential 
# profit at every step. By updating the minimum price and the maximum profit 
# greedily, we find the global maximum in linear time without redundant calculations.
def max_profit_optimal(prices: list[int]) -> int:
    if not prices:
        return 0
    
    min_price = float('inf')
    max_p = 0
    
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_p:
            max_p = price - min_price
            
    return max_p

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package sliding_window;

public class BestTimeToBuyAndSellStock {
    /**
     * Calculates the maximum profit from buying and selling a stock.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int maxProfit(int[] prices) {
        if (prices == null || prices.length < 2) {
            return 0;
        }

        int minPrice = Integer.MAX_VALUE;
        int maxProfit = 0;

        for (int price : prices) {
            if (price < minPrice) {
                minPrice = price;
            } else if (price - minPrice > maxProfit) {
                maxProfit = price - minPrice;
            }
        }

        return maxProfit;
    }

    public static void main(String[] args) {
        BestTimeToBuyAndSellStock solution = new BestTimeToBuyAndSellStock();
        int[] prices = {7, 1, 5, 3, 6, 4};
        System.out.println("Max Profit: " + solution.maxProfit(prices)); // Output: 5
    }
}
"""

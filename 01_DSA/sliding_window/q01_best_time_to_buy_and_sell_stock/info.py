INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/',
    'description': 'Find the maximum profit you can achieve buying one day and selling another.',
    'groups': ['Array', 'Sliding Window'],
    'starter_code': """def max_profit(prices: list[int]) -> int:
    # Write your solution here
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_stock():
    assert max_profit([7,1,5,3,6,4]) == 5
    assert max_profit([7,6,4,3,1]) == 0""",
    'readme_content': """# Best Time To Buy And Sell Stock

## 📌 Overview & Problem Explanation

The **Best Time To Buy And Sell Stock** problem is a classic introductory challenge that tests your ability to optimize a search over a linear sequence. 

### The Goal
You are given an array `prices` where `prices[i]` represents the price of a given stock on the $i^{th}$ day. You want to maximize your profit by choosing a **single day** to buy one stock and choosing a **different day in the future** to sell that stock.

### Constraints & Requirements
- **Sequential Order**: You must buy the stock before you can sell it (you cannot sell on day 1 and buy on day 2).
- **Single Transaction**: You are only allowed one purchase and one sale.
- **Profit Calculation**: $\text{Profit} = \text{Price}_{\text{sell}} - \text{Price}_{\text{buy}}$.
- **No Profit Scenario**: If no profit can be achieved (e.g., the price drops every single day), the function should return `0`.

### Edge Cases
- **Empty or Single Element Array**: If there are fewer than two prices, no transaction is possible. Profit = `0`.
- **Strictly Decreasing Prices**: If the stock price only goes down, you can never sell for more than you bought. Profit = `0`.
- **Strictly Increasing Prices**: The best strategy is to buy on day 0 and sell on the last day.
- **Large Price Volatility**: Prices may fluctuate wildly; the algorithm must track the global minimum and the maximum gap.

---

## 💡 Core Concepts & Algorithmic Patterns

### 1. The Brute Force Approach (Nested Loops)
The simplest way to solve this is to simulate every possible pair of buy and sell days. By checking every combination where the sell date comes after the buy date, we guarantee finding the maximum. However, this leads to quadratic time complexity.

### 2. The Optimal Approach: Sliding Window / One-Pass Greedy
The key insight is that to maximize profit, we need to find the **lowest possible price** to buy and the **highest possible price** that occurs *after* that buy date.

Instead of re-scanning the array for every buy date, we can maintain a "running minimum" as we iterate through the list once. This is a variation of the **Sliding Window** pattern (where the window expands to track the gap between the minimum seen so far and the current price) or a **Greedy** approach.

**Why this is optimal:**
- We only visit each element once.
- We only store two variables (`min_price` and `max_profit`), regardless of the input size.
- It eliminates redundant calculations by remembering the best "buy" opportunity encountered up to the current point.

---

## 🛠️ Step-by-Step Logic

### Naive Logic ($\mathcal{O}(N^2)$)
1. Initialize `max_profit = 0`.
2. Use a loop (index `i`) to pick a buying day.
3. Use a second nested loop (index `j`, starting from `i + 1`) to pick a selling day.
4. Calculate `prices[j] - prices[i]`.
5. If this value is greater than `max_profit`, update `max_profit`.
6. Return `max_profit`.

### Optimal Logic ($\mathcal{O}(N)$)
1. Initialize `min_price` to infinity ($\infty$) to ensure the first price encountered becomes the initial minimum.
2. Initialize `max_profit` to `0`.
3. Iterate through each price `p` in the `prices` array:
    - **Update Minimum**: If the current price `p` is lower than `min_price`, update `min_price = p`. (We found a better day to buy).
    - **Calculate Potential Profit**: If the current price is NOT a new minimum, check how much profit we would make if we sold today: $\text{current\_profit} = p - \text{min\_price}$.
    - **Update Maximum**: If `current_profit` is greater than `max_profit`, update `max_profit`.
4. Return `max_profit`.

### 🔍 Dry Run Example
**Input**: `prices = [7, 1, 5, 3, 6, 4]`

| Day | Price | `min_price` | Calculation ($p - \text{min\_price}$) | `max_profit` | Note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 7 | 7 | $7 - 7 = 0$ | 0 | First element sets min |
| 2 | 1 | 1 | $1 - 1 = 0$ | 0 | New minimum found |
| 3 | 5 | 1 | $5 - 1 = 4$ | 4 | Profit increased to 4 |
| 4 | 3 | 1 | $3 - 1 = 2$ | 4 | 2 < 4, no update |
| 5 | 6 | 1 | $6 - 1 = 5$ | 5 | Profit increased to 5 |
| 6 | 4 | 1 | $4 - 1 = 3$ | 5 | 3 < 5, no update |

**Final Result**: `5`

---

## 💻 Implementation

```python
def max_profit(prices: list[int]) -> int:
    \"\"\"
    Finds the maximum profit possible from one buy and one sell transaction.
    Time Complexity: O(N)
    Space Complexity: O(1)
    \"\"\"
    # Initialize min_price to infinity so the first element always updates it
    min_price = float('inf')
    max_profit = 0
    
    for p in prices:
        # Update the minimum price encountered so far
        if p < min_price:
            min_price = p
        # If current price is higher than min_price, calculate potential profit
        elif p - min_price > max_profit:
            max_profit = p - min_price
            
    return max_profit
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Naive** | $\mathcal{O}(N^2)$ | $\mathcal{O}(1)$ | Nested loops iterate through almost all pairs of elements. |
| **Optimal** | $\mathcal{O}(N)$ | $\mathcal{O}(1)$ | Single pass through the array; only two scalar variables used. |

---

## 🚀 Real-World Applications

The pattern used here—**tracking a running minimum/maximum to find the optimal gap**—is used extensively in software engineering:

1. **Financial Analysis**: Calculating the "Maximum Drawdown" in a portfolio (the maximum loss from a peak to a trough).
2. **Signal Processing**: Peak-to-peak detection in waveforms to identify the range of a signal.
3. **System Monitoring**: Detecting the largest spike in memory usage or CPU load over a specific time window.
4. **Telemetry Data**: Finding the largest temperature swing in a set of sensor readings over 24 hours.""",
}

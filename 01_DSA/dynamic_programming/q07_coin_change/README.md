# Coin Change (q07_coin_change)

## 1. Overview & Problem Explanation

The **Coin Change** problem is a classic optimization puzzle. You are given an integer array `coins` representing different denominations of coins and an integer `amount` representing a total sum of money. The goal is to find the **fewest number of coins** that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.

### Problem Breakdown
- **Input**: 
    - `coins`: A list of integers (e.g., `[1, 2, 5]`).
    - `amount`: A non-negative integer (e.g., `11`).
- **Output**: 
    - An integer representing the minimum number of coins (e.g., `3`, because $5+5+1=11$).
    - `-1` if the amount is unreachable.

### Constraints & Edge Cases
- **Unreachable Amounts**: If the coins provided cannot sum to the target (e.g., `coins = [2]`, `amount = 3`), the algorithm must return `-1`.
- **Amount = 0**: The minimum coins required to make an amount of 0 is always `0`.
- **Large Coin Values**: Coins can be very large, potentially exceeding the target amount immediately.
- **Non-Greedy Nature**: A common mistake is assuming a **Greedy Approach** (always taking the largest coin first) works. 
    - *Example*: `coins = [1, 3, 4]`, `amount = 6`.
    - *Greedy*: 4 + 1 + 1 = 3 coins.
    - *Optimal*: 3 + 3 = 2 coins.
    - Because the greedy approach fails, we must use **Dynamic Programming**.

---

## 2. Core Concepts & Algorithms

### Dynamic Programming (DP)
This problem exhibits two key properties that make it a perfect candidate for DP:
1. **Overlapping Subproblems**: To find the minimum coins for `amount = 11`, you first need to know the minimum coins for `11 - 1`, `11 - 2`, and `11 - 5`. These smaller calculations are repeated many times.
2. **Optimal Substructure**: The optimal solution for `amount` can be constructed from the optimal solutions of its sub-amounts.

### Why Bottom-Up DP?
While Top-Down (Recursion + Memoization) works, **Bottom-Up (Iterative)** DP is often preferred here because it avoids recursion limit issues and typically has better constant-time performance. We build a table from `0` up to the target `amount`, ensuring that when we calculate `dp[i]`, all previous values `dp[0...i-1]` are already optimized.

---

## 3. Step-by-Step Logic

### The Naive Approach (Recursive)
The brute force method would be to try every single coin for the current amount, subtract its value, and recurse. This results in an exponential time complexity $O(C^A)$ (where $C$ is number of coins and $A$ is amount), which is unusable for $A=10,000$.

### The Optimal Approach (Bottom-Up DP)

#### 1. State Definition
Let `dp[i]` be the **minimum number of coins needed to make up amount `i`**.

#### 2. Base Case
- `dp[0] = 0`: Zero coins are needed to make the amount 0.

#### 3. Initialization
We initialize the `dp` array with a value larger than any possible answer. Since the smallest coin is 1, the maximum number of coins needed for `amount` is `amount`. Thus, `amount + 1` serves as a perfect "infinity" marker.

#### 4. State Transition Equation
For every amount `i` from `1` to `amount`, and for every coin `c` in `coins`:
If $i - c \ge 0$:
$$\text{dp}[i] = \min(\text{dp}[i], \text{dp}[i - c] + 1)$$
*Explanation: If we use coin `c`, the total number of coins is 1 (the current coin) plus however many coins were needed to make the remaining amount (`dp[i - c]`).*

### Dry Run Example
`coins = [1, 2, 5]`, `amount = 5`

| Amount (i) | Calculation | `dp[i]` |
| :--- | :--- | :--- |
| 0 | Base case | 0 |
| 1 | $\min(\infty, dp[1-1]+1) = \min(\infty, 0+1)$ | 1 |
| 2 | $\min(\infty, dp[2-1]+1, dp[2-2]+1) = \min(\infty, 1+1, 0+1)$ | 1 |
| 3 | $\min(\infty, dp[3-1]+1, dp[3-2]+1) = \min(\infty, 1+1, 1+1)$ | 2 |
| 4 | $\min(\infty, dp[4-1]+1, dp[4-2]+1) = \min(\infty, 2+1, 1+1)$ | 2 |
| 5 | $\min(\infty, dp[5-1]+1, dp[5-2]+1, dp[5-5]+1) = \min(\infty, 2+1, 2+1, 0+1)$ | 1 |

**Result**: `dp[5] = 1`.

---

## 4. Implementation

```python
def solve_optimal(coins, amount):
    # Initialize DP table with a value greater than any possible answer
    # amount + 1 is a safe 'infinity' because the most coins we could use is 'amount' (all 1s)
    dp = [amount + 1] * (amount + 1)
    
    # Base case: 0 coins to make amount 0
    dp[0] = 0
    
    # Iterate through every amount from 1 to target
    for i in range(1, amount + 1):
        # Try every available coin denomination
        for coin in coins:
            if i - coin >= 0:
                # The transition: take the minimum of current value or 
                # 1 (the current coin) + coins needed for the remainder
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    # If dp[amount] is still amount + 1, it means the amount is unreachable
    return dp[amount] if dp[amount] != amount + 1 else -1
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(C^A)$ | $O(A)$ | Exponential growth based on coin choices per amount. |
| **Optimal DP** | $O(A \cdot C)$ | $O(A)$ | We iterate through the amount $A$ and for each, check $C$ coins. |

- **Time Complexity $O(A \cdot C)$**: Where $A$ is the amount and $C$ is the number of denominations. We use a nested loop structure: the outer loop runs $A$ times, and the inner loop runs $C$ times.
- **Space Complexity $O(A)$**: We maintain a 1D array of size $A+1$ to store the minimum coins for every sub-amount.

---

## 6. Real-World Applications

The "Coin Change" pattern is a specific instance of the **Unbounded Knapsack Problem**. This logic is utilized in various software systems:

1. **Financial Systems**: Vending machines or automated teller machines (ATMs) calculating the fewest bills/coins to dispense for a requested withdrawal.
2. **Resource Allocation**: In cloud computing, determining the minimum number of virtual machine "instances" of different sizes (Small, Medium, Large) required to meet a specific CPU/RAM capacity requirement.
3. **Cutting Stock Problem**: In manufacturing, finding the minimum number of standard-length rolls of material (like paper or steel) needed to produce a set of smaller, custom-length pieces.
4. **Change-making Algorithms**: Used in legacy POS (Point of Sale) software to suggest the most efficient way to give change to a customer.
INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/min-cost-climbing-stairs/',
    'description': 'Min cost stairs.',
    'groups': ['Dynamic Programming', 'Array'],
    'readme_content': """## 🧗‍♂️ Min Cost Climbing Stairs

### 🚀 Overview & Problem Explanation

The "Min Cost Climbing Stairs" problem is a classic dynamic programming challenge that asks us to find the least expensive way to ascend a staircase.

Imagine you're at the bottom of a staircase, and each step has a certain non-negative cost associated with it. You can choose to climb either one or two steps at a time. Your goal is to reach the "top of the floor" (which is one step beyond the last actual stair) with the minimum possible total cost. A crucial detail is that you can start climbing from either the first step (index 0) or the second step (index 1) **without incurring any initial cost** for that starting position.

**Problem Statement:**
Given an integer array `cost` where `cost[i]` is the cost to climb the `i`-th step. You can either climb one or two steps. You can start from step `0` or step `1`. Return the minimum cost to reach the top of the floor.

**Example:**
`cost = [10, 15, 20]`

*   If you start at step 0: pay 10. You are now on step 0.
    *   From step 0, take 2 steps to step 2: pay 20. Total cost: 10 + 20 = 30. (You are now at the top, after step 2).
*   If you start at step 1: pay 15. You are now on step 1.
    *   From step 1, take 1 step to step 2: pay 20. Total cost: 15 + 20 = 35. (You are now at the top, after step 2).
*   The minimum cost is 30.

Let's re-evaluate the interpretation based on typical solutions, where `dp[i]` is the minimum cost to reach *the position just before step `i`* or *the top after step `i-1`*.

**Revised Example Trace:** `cost = [10, 15, 20]`
*   There are 3 steps (indices 0, 1, 2). The "top of the floor" is effectively after step 2, which we can consider as "index 3" in a conceptual `dp` array.
*   Option 1: Start at step 0 (cost `cost[0]=10`).
    *   From step 0, jump to step 2 (cost `cost[2]=20`). Total: `10 + 20 = 30`.
*   Option 2: Start at step 1 (cost `cost[1]=15`).
    *   From step 1, jump to step 2 (cost `cost[2]=20`). Total: `15 + 20 = 35`.
*   Wait, the "top of the floor" means we have *passed* the last step.
    *   If `cost = [10, 15, 20]`
        *   Path 1: Start at 0, pay `cost[0]=10`. Now at step 0.
            *   From step 0, take 2 steps to land on step 2, pay `cost[2]=20`. Now at step 2.
            *   From step 2, take 1 step to reach the top. Total cost: `10 + 20 = 30`.
        *   Path 2: Start at 1, pay `cost[1]=15`. Now at step 1.
            *   From step 1, take 1 step to land on step 2, pay `cost[2]=20`. Now at step 2.
            *   From step 2, take 1 step to reach the top. Total cost: `15 + 20 = 35`.
        *   The path 1 is indeed `10 + 20 = 30`.

The provided example in LeetCode `cost = [10, 15, 20]` gives `15`. How?
*   Start at index 1 (cost 15).
*   From index 1, take 1 step to land at index 2 (cost 20). This would be `15 + 20 = 35`.
*   From index 1, take 2 steps to land at index *beyond* index 2 (the top). Cost `15`.
This implies that `cost[i]` is the cost *to step on* step `i`. Once you are on step `i`, you can move. And the "top" is past the last step.

Let's use the standard LeetCode DP formulation: `dp[i]` is the minimum cost to reach the *`i`-th position*, where `i` represents the position *after* step `i-1`. The "top of the floor" for an array of `N` steps is position `N`.

**Input:**
*   `cost`: A list of integers representing the cost for each step.

**Output:**
*   An integer, the minimum total cost to reach the top.

**Constraints:**
*   `2 <= cost.length <= 1000`
*   `0 <= cost[i] <= 999`

**Edge Cases:**
*   The minimum length is 2, so `cost` will never be empty or have only one element.
*   Costs are non-negative.

### 🧠 Core Concepts & Data Structures/Algorithms

This problem is a quintessential example of **Dynamic Programming (DP)**.

**Dynamic Programming (DP):**
DP is an algorithmic technique for solving optimization problems by breaking them down into simpler subproblems. It's applicable when a problem has two key properties:

1.  **Optimal Substructure:** The optimal solution to the overall problem can be constructed from optimal solutions to its subproblems. In our case, the minimum cost to reach step `i` depends on the minimum cost to reach step `i-1` or step `i-2`.
2.  **Overlapping Subproblems:** The same subproblems are encountered multiple times. A naive recursive solution would recompute these subproblems repeatedly, leading to inefficiency. DP solves this by storing the results of subproblems (memoization) or by solving them in a bottom-up fashion (tabulation).

**Why DP is suitable here:**
To find the minimum cost to reach the "top" (position `N`), we need to know the minimum cost to reach position `N-1` (after step `N-2`) and position `N-2` (after step `N-3`), because we can arrive at `N` from either `N-1` (taking one step) or `N-2` (taking two steps). This clearly shows the optimal substructure. If we were to use simple recursion, the calculation for `N-1` would involve subproblems, and `N-2` would involve similar subproblems, leading to overlapping calculations.

We will use **tabulation (bottom-up DP)**, building up our solution from the base cases.

### 🧩 Step-by-Step Logic

#### Approach 1: Dynamic Programming (Tabulation)

Let `dp[i]` represent the minimum cost to reach the `i`-th position. The "top of the floor" is at position `n`, where `n` is the length of the `cost` array.

1.  **Define DP State:**
    *   `dp[i]` = minimum cost to reach the `i`-th position.
    *   The `cost` array has `n` steps, indexed `0` to `n-1`.
    *   The "top of the floor" is conceptually at index `n`. So, our `dp` array will have size `n + 1`.

2.  **Base Cases:**
    *   `dp[0] = 0`: The cost to reach position 0 (before the first step) is 0. This accounts for starting from step 0.
    *   `dp[1] = 0`: The cost to reach position 1 (before the second step) is 0. This accounts for starting from step 1.
    *   These base cases implicitly cover the ability to start at either step 0 or step 1 "for free" in terms of current position. The cost is incurred when you *climb* a step.

3.  **Recurrence Relation:**
    For `i` from `2` to `n`:
    `dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])`

    *   To reach position `i`, you must have come from either position `i-1` (by taking one step from `i-1` and paying `cost[i-1]`) or from position `i-2` (by taking two steps from `i-2` and paying `cost[i-2]`).
    *   `cost[i-1]` is the cost of the step that gets you *to* position `i` from `i-1`.
    *   `cost[i-2]` is the cost of the step that gets you *to* position `i` from `i-2`.

4.  **Final Answer:**
    The minimum cost to reach the top of the floor is `dp[n]`.

---

**Example Walkthrough: `cost = [10, 15, 20]`**
*   `n = 3`
*   Initialize `dp` array of size `n+1 = 4`: `dp = [0, 0, ?, ?]`

1.  **Base Cases:**
    *   `dp[0] = 0`
    *   `dp[1] = 0`

2.  **Iterate `i` from 2 to 3:**
    *   **`i = 2`:** (Min cost to reach position 2)
        *   `dp[2] = min(dp[2-1] + cost[2-1], dp[2-2] + cost[2-2])`
        *   `dp[2] = min(dp[1] + cost[1], dp[0] + cost[0])`
        *   `dp[2] = min(0 + 15, 0 + 10)`
        *   `dp[2] = min(15, 10) = 10`
        *   (This means the minimum cost to reach position 2 is 10, by starting at position 0 and paying `cost[0] = 10` to climb step 0).
    *   **`i = 3`:** (Min cost to reach position 3, which is the top)
        *   `dp[3] = min(dp[3-1] + cost[3-1], dp[3-2] + cost[3-2])`
        *   `dp[3] = min(dp[2] + cost[2], dp[1] + cost[1])`
        *   `dp[3] = min(10 + 20, 0 + 15)`
        *   `dp[3] = min(30, 15) = 15`
        *   (This means the minimum cost to reach position 3 is 15, by starting at position 1 and paying `cost[1]=15` to climb step 1. From there, we take 2 steps to reach the top).

3.  **Result:** `dp[n] = dp[3] = 15`.

```python
def solve_dp_tabulation(cost: list[int]) -> int:
    n = len(cost)
    
    # dp[i] represents the minimum cost to reach position i
    # The 'top' is considered position n
    dp = [0] * (n + 1)
    
    # Base cases: cost to reach position 0 or 1 is 0
    # (can start from step 0 or step 1 without initial cost)
    dp[0] = 0
    dp[1] = 0
    
    # Fill dp array using the recurrence relation
    # For each position i from 2 to n:
    #   dp[i] is the minimum of
    #     (cost to reach i-1) + (cost to climb step i-1)
    #     (cost to reach i-2) + (cost to climb step i-2)
    for i in range(2, n + 1):
        dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
        
    return dp[n]

# Example usage (for internal testing)
# print(solve_dp_tabulation([10, 15, 20])) # Expected: 15
# print(solve_dp_tabulation([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])) # Expected: 6
```

---

#### Approach 2: Space-Optimized Dynamic Programming

Notice that in the recurrence relation `dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])`, `dp[i]` only depends on the two previous `dp` values (`dp[i-1]` and `dp[i-2]`). This means we don't need to store the entire `dp` array. We can use just two variables to keep track of the necessary previous values.

1.  **Variables:**
    *   `prev2`: Minimum cost to reach position `i-2`.
    *   `prev1`: Minimum cost to reach position `i-1`.
    *   `current`: Minimum cost to reach position `i`.

2.  **Initialization:**
    *   `prev2 = 0` (equivalent to `dp[0]`)
    *   `prev1 = 0` (equivalent to `dp[1]`)

3.  **Iteration:**
    For `i` from `2` to `n`:
    *   Calculate `current = min(prev1 + cost[i-1], prev2 + cost[i-2])`
    *   Update `prev2 = prev1` (The old `prev1` becomes the new `prev2`)
    *   Update `prev1 = current` (The `current` value becomes the new `prev1`)

4.  **Final Answer:**
    After the loop finishes, `prev1` will hold the minimum cost to reach position `n` (the top).

```python
# --- APPROACH 1: Optimal (Space Optimized) ---
def solve_optimal(cost: list[int]) -> int:
    n = len(cost)
    
    # Base cases for n=2. The problem constraints state n >= 2.
    # If n=2, cost = [c0, c1].
    # Options: start at 0, pay c0. Top reached. Cost: c0.
    #          start at 1, pay c1. Top reached. Cost: c1.
    # Result: min(c0, c1)
    # Our DP handles this correctly:
    # prev2 = 0 (dp[0])
    # prev1 = 0 (dp[1])
    # i = 2:
    # current = min(prev1 + cost[1], prev2 + cost[0])
    # current = min(0 + cost[1], 0 + cost[0]) = min(cost[1], cost[0])
    # prev2 = prev1 (0)
    # prev1 = current (min(cost[1], cost[0]))
    # Loop ends. Return prev1. Correct.

    # prev2 stores dp[i-2]
    # prev1 stores dp[i-1]
    prev2 = 0  # Represents dp[0]
    prev1 = 0  # Represents dp[1]
    
    for i in range(2, n + 1):
        # current represents dp[i]
        # To reach position i, we either come from i-1 (paying cost[i-1])
        # or from i-2 (paying cost[i-2])
        current = min(prev1 + cost[i-1], prev2 + cost[i-2])
        
        # Update for the next iteration
        prev2 = prev1
        prev1 = current
        
    return prev1

# Note: The problem asks for `solve()` which implies one solution.
# The provided template shows `solve_optimal()`.
# Let's align with the template.
def solve():
    # This function should wrap the solution
    # For a real system, it would likely take 'cost' as an argument.
    # For the study guide context, let's assume it gets 'cost' from some context
    # or takes it as an argument if refactoring the starter template.
    # Assuming 'cost' is available in context or passed as an argument based on how it's called
    # For the purpose of the guide, the internal functions are defined above.
    pass # Placeholder if the actual `solve()` needs a specific implementation.
```

### 📊 Complexity Analysis

| Approach                         | Time Complexity | Space Complexity | Explanation                                                                                                                                                                                                                                                                                                                                                                                                                     |
| :------------------------------- | :-------------- | :--------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dynamic Programming (Tabulation)** | O(N)            | O(N)             | The algorithm iterates through the `cost` array once, from index 2 to `N`. Each step involves constant time operations (arithmetic, min comparison). Therefore, the time complexity is linear with respect to the number of steps, `N`. <br><br> An array `dp` of size `N+1` is used to store the minimum costs for each position. This array consumes space proportional to `N`.                                                                |
| **Space-Optimized DP**           | O(N)            | O(1)             | The algorithm still iterates through the `cost` array once, performing constant time operations at each step. Thus, the time complexity remains linear, O(N). <br><br> Instead of an entire `dp` array, only a constant number of variables (`prev1`, `prev2`, `current`) are used to store the necessary previous states. The amount of space used does not grow with the input size `N`, making it constant space. |

### 🌐 Real-World Applications

The "Min Cost Climbing Stairs" problem, or the underlying dynamic programming pattern, appears in various real-world scenarios:

1.  **Shortest Path Problems:** This problem is a simplified version of finding the shortest path in a directed acyclic graph (DAG). More complex shortest path algorithms like Dijkstra's or Bellman-Ford often use DP principles for optimization.
    *   **Examples:** Network routing protocols, GPS navigation systems determining the shortest route, optimizing data packet flow in telecommunications.

2.  **Resource Optimization:** When there are multiple ways to achieve a goal, each with associated costs, DP can find the optimal path.
    *   **Examples:** Manufacturing scheduling (minimizing production costs or time), project management (finding the critical path to minimize project duration), financial modeling (optimizing investment strategies over time).

3.  **Bioinformatics:** Sequence alignment (e.g., Needleman-Wunsch algorithm) uses dynamic programming to find the best possible alignment between two DNA or protein sequences, minimizing "cost" (mutations, insertions, deletions).

4.  **Speech Recognition:** The Viterbi algorithm, a dynamic programming algorithm, is used to find the most likely sequence of hidden states (e.g., phonetic units) in a Hidden Markov Model (HMM), which is fundamental to many speech recognition systems.

5.  **Compiler Optimization:** Dynamic programming can be used to optimize code generation, for instance, by finding the minimum cost instruction sequence to compute a value or by optimizing register allocation.

6.  **Image Processing:** Certain image segmentation or image stitching algorithms can leverage DP to find optimal cuts or seam lines that minimize a given cost function.

This problem serves as an excellent entry point to understanding how breaking down a problem into interconnected optimal decisions can lead to highly efficient solutions.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

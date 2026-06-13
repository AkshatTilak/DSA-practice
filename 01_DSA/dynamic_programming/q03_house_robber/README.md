# House Robber (q03_house_robber)

## 🎯 Overview & Problem Explanation

The "House Robber" problem is a classic dynamic programming challenge. Imagine you are a professional robber planning to rob houses along a street. Each house has a certain amount of money. The only constraint stopping you from robbing all of them is that **adjacent houses have security systems connected**. If you rob two adjacent houses, the system will automatically call the police.

Your goal is to determine the maximum amount of money you can rob tonight without alerting the police.

**Input:**
*   `nums`: An integer array representing the amount of money in each house. `nums[i]` is the amount of money in the i-th house.

**Output:**
*   An integer representing the maximum amount of money you can rob.

**Constraints (Commonly found on LeetCode):**
*   `1 <= nums.length <= 100` (The number of houses can range from 1 to 100)
*   `0 <= nums[i] <= 400` (The money in each house is non-negative and capped at 400)

**Edge Cases:**
*   **Empty input array**: If `nums` is empty, no houses can be robbed, so the result is `0`. (Note: Given `nums.length >= 1`, this specific case might not occur based on constraints, but it's good to consider for robustness).
*   **Single house**: If there's only one house, you rob it for `nums[0]`.
*   **Two houses**: You pick the house with the maximum money, i.e., `max(nums[0], nums[1])`.
*   **All houses have zero money**: The total robbed will be `0`.

---

## 💡 Core Concepts & Data Structures/Algorithms: Dynamic Programming

This problem is a perfect candidate for **Dynamic Programming (DP)** because it exhibits two key properties:

1.  **Optimal Substructure**: The optimal solution to the problem can be constructed from optimal solutions to its subproblems. The maximum money from `n` houses depends on the maximum money from `n-1` or `n-2` houses.
2.  **Overlapping Subproblems**: When solving recursively, the same subproblems are computed multiple times. DP allows us to store the results of these subproblems to avoid redundant calculations.

The core idea is to build up the solution from the smallest subproblems. For each house `i`, we have two choices:

*   **Rob house `i`**: If we rob house `i`, we cannot rob house `i-1`. Therefore, the total money would be `nums[i]` plus the maximum money robbed from houses up to `i-2`.
*   **Don't rob house `i`**: If we don't rob house `i`, the total money would be the maximum money robbed from houses up to `i-1`.

We pick the maximum of these two options.

### DP State Definition
Let `dp[i]` be the maximum amount of money that can be robbed from houses `0` through `i` (inclusive), adhering to the non-adjacent constraint.

### DP Recurrence Relation
For `i >= 2`:
`dp[i] = max(nums[i] + dp[i-2], dp[i-1])`

### Base Cases
*   `dp[0] = nums[0]` (If only one house, rob it)
*   `dp[1] = max(nums[0], nums[1])` (If two houses, rob the one with more money)

---

## 🚶 Step-by-Step Logic

We'll explore a couple of approaches, moving from a conceptual recursive solution to an optimal iterative one.

### 1. Naive Recursive Approach (Brute Force with Memoization Potential)

A direct translation of the recurrence relation leads to a recursive solution.

```python
def rob_recursive(nums, i):
    if i < 0:
        return 0
    if i == 0:
        return nums[0]
    if i == 1:
        return max(nums[0], nums[1])
    
    # Option 1: Rob current house i
    rob_current = nums[i] + rob_recursive(nums, i-2)
    
    # Option 2: Don't rob current house i
    skip_current = rob_recursive(nums, i-1)
    
    return max(rob_current, skip_current)

# To call it: rob_recursive(nums, len(nums) - 1)
```

This recursive solution without memoization will re-calculate the same subproblems many times, leading to an exponential time complexity. Adding memoization (caching results in a dictionary or array) would bring its time complexity down to O(N).

### 2. Optimal Approach: Iterative Dynamic Programming (Bottom-Up)

This approach builds the `dp` array from the base cases up to the final solution.

#### Step-by-step Dry Run Example: `nums = [2, 7, 9, 3, 1]`

1.  **Initialization**:
    *   `n = 5`
    *   Handle base cases:
        *   `nums = []`: return 0
        *   `nums = [2]`: `dp[0] = 2`
        *   `nums = [2, 7]`: `dp[1] = max(2, 7) = 7`
    *   Initialize `dp` array: `dp = [0, 0, 0, 0, 0]` (size `n`)
    *   `dp[0] = nums[0] = 2`
    *   `dp[1] = max(nums[0], nums[1]) = max(2, 7) = 7`
    *   Current `dp` array: `[2, 7, 0, 0, 0]`

2.  **Iteration `i = 2` (House with 9 money)**:
    *   `nums[2] = 9`
    *   `dp[2] = max(nums[2] + dp[0], dp[1])`
    *   `dp[2] = max(9 + 2, 7)`
    *   `dp[2] = max(11, 7) = 11`
    *   Current `dp` array: `[2, 7, 11, 0, 0]`

3.  **Iteration `i = 3` (House with 3 money)**:
    *   `nums[3] = 3`
    *   `dp[3] = max(nums[3] + dp[1], dp[2])`
    *   `dp[3] = max(3 + 7, 11)`
    *   `dp[3] = max(10, 11) = 11`
    *   Current `dp` array: `[2, 7, 11, 11, 0]`

4.  **Iteration `i = 4` (House with 1 money)**:
    *   `nums[4] = 1`
    *   `dp[4] = max(nums[4] + dp[2], dp[3])`
    *   `dp[4] = max(1 + 11, 11)`
    *   `dp[4] = max(12, 11) = 12`
    *   Current `dp` array: `[2, 7, 11, 11, 12]`

5.  **Result**: The maximum money that can be robbed is `dp[n-1] = dp[4] = 12`.

### 3. Most Optimal Approach: Iterative Dynamic Programming with Space Optimization (O(1) Space)

Notice that `dp[i]` only depends on `dp[i-1]` and `dp[i-2]`. This means we don't need to store the entire `dp` array. We only need to keep track of the two previous maximum values.

Let's rename `dp[i-2]` to `rob_prev_prev` and `dp[i-1]` to `rob_prev`.
Then, `dp[i]` becomes `current_rob`.

```python
# --- APPROACH 1: Optimal (Iterative DP with Space Optimization) ---
def solve_optimal(nums: list[int]) -> int:
    n = len(nums)

    # Edge cases
    if n == 0:
        return 0
    if n == 1:
        return nums[0]
    if n == 2:
        return max(nums[0], nums[1])

    # Initialize for the first two houses
    # rob_prev_prev represents dp[i-2]
    # rob_prev represents dp[i-1]
    rob_prev_prev = nums[0]
    rob_prev = max(nums[0], nums[1])

    # Iterate from the third house onwards
    for i in range(2, n):
        # Calculate current_rob (which would be dp[i])
        # Option 1: Rob current house nums[i]. Cannot rob nums[i-1].
        # Max money would be nums[i] + max money from houses up to i-2 (rob_prev_prev).
        # Option 2: Don't rob current house nums[i].
        # Max money would be max money from houses up to i-1 (rob_prev).
        current_rob = max(nums[i] + rob_prev_prev, rob_prev)

        # Update for the next iteration:
        # The previous 'rob_prev' now becomes 'rob_prev_prev' for the next step.
        rob_prev_prev = rob_prev
        # The 'current_rob' now becomes 'rob_prev' for the next step.
        rob_prev = current_rob
    
    # After the loop, rob_prev holds the maximum money robbed for all houses.
    return rob_prev

```

#### Dry Run with Space Optimization: `nums = [2, 7, 9, 3, 1]`

1.  **Initialization**:
    *   `n = 5`
    *   Edge cases handled.
    *   `rob_prev_prev = nums[0] = 2`
    *   `rob_prev = max(nums[0], nums[1]) = max(2, 7) = 7`

2.  **Iteration `i = 2` (House with 9 money)**:
    *   `nums[2] = 9`
    *   `current_rob = max(nums[2] + rob_prev_prev, rob_prev)`
    *   `current_rob = max(9 + 2, 7) = max(11, 7) = 11`
    *   Update:
        *   `rob_prev_prev = rob_prev` (which was 7) => `rob_prev_prev = 7`
        *   `rob_prev = current_rob` (which was 11) => `rob_prev = 11`

3.  **Iteration `i = 3` (House with 3 money)**:
    *   `nums[3] = 3`
    *   `current_rob = max(nums[3] + rob_prev_prev, rob_prev)`
    *   `current_rob = max(3 + 7, 11) = max(10, 11) = 11`
    *   Update:
        *   `rob_prev_prev = rob_prev` (which was 11) => `rob_prev_prev = 11`
        *   `rob_prev = current_rob` (which was 11) => `rob_prev = 11`

4.  **Iteration `i = 4` (House with 1 money)**:
    *   `nums[4] = 1`
    *   `current_rob = max(nums[4] + rob_prev_prev, rob_prev)`
    *   `current_rob = max(1 + 11, 11) = max(12, 11) = 12`
    *   Update:
        *   `rob_prev_prev = rob_prev` (which was 11) => `rob_prev_prev = 11`
        *   `rob_prev = current_rob` (which was 12) => `rob_prev = 12`

5.  **Result**: Loop finishes. Return `rob_prev`, which is `12`.

---

## ⏱️ Complexity Analysis

| Approach                         | Time Complexity | Space Complexity | Reasoning                                                                                                                                                                             |
| :------------------------------- | :-------------- | :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Naive Recursive (Brute Force)** | O(2^N)          | O(N)             | Each function call can branch into two recursive calls, leading to an exponential number of computations. Space is for the recursion stack depth.                                      |
| **Recursive with Memoization**   | O(N)            | O(N)             | Each subproblem `rob(i)` is computed only once and its result stored. There are `N` distinct subproblems. Space is for the memoization table and recursion stack.                     |
| **Iterative DP (Bottom-Up)**     | O(N)            | O(N)             | A single pass is made through the `nums` array to fill the `dp` array. Space is used to store the `dp` array of size `N`.                                                               |
| **Iterative DP (Space Optimized)**| O(N)            | O(1)             | A single pass is made through the `nums` array. Only a constant number of variables (`rob_prev_prev`, `rob_prev`, `current_rob`) are used, regardless of the input array size. |

---

## 🚀 Real-World Applications

The "House Robber" problem is a classic example of dynamic programming that teaches a fundamental pattern applicable in various real-world scenarios:

1.  **Resource Allocation/Scheduling**: Imagine scheduling tasks where some tasks cannot run concurrently or consecutively. This pattern helps maximize the total value or output while respecting such constraints. For instance, in manufacturing, scheduling jobs on a machine where certain jobs require a cool-down period.
2.  **Financial Trading**: Deciding when to buy or sell stocks or assets to maximize profit, where transactions might have associated "cooldown" periods or dependencies (e.g., if you sell today, you cannot buy the same asset tomorrow to prevent wash sales).
3.  **Job Sequencing with Deadlines**: A more complex variant might involve jobs with deadlines and profits, where picking one job might preclude picking another in an adjacent time slot.
4.  **Optimal Pathfinding with Constraints**: In networks or graphs, finding an optimal path where certain "nodes" or "edges" cannot be traversed consecutively due to restrictions (e.g., a road might be closed the day after maintenance).
5.  **Advertising Campaign Optimization**: Choosing which advertising slots to purchase to maximize reach or impact, given that some slots might be in adjacent time intervals or publications and have diminished returns or higher costs when chosen together.
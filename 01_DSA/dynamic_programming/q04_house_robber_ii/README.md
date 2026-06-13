# House Robber II (q04_house_robber_ii)

## 🎯 Overview & Problem Explanation

The **House Robber II** problem is a classic dynamic programming challenge that builds upon the foundational "House Robber I" problem. Imagine you are a professional robber planning to rob houses along a street. Each house has a certain amount of money. The only constraint preventing you from robbing adjacent houses is a security system: if two adjacent houses are robbed on the same night, the alarm will go off.

### The Twist: A Circular Street

In House Robber II, the houses are arranged in a **circle**. This means the first house and the last house are considered adjacent. This introduces a critical new constraint: **you cannot rob both the first house and the last house simultaneously.**

Your goal is to determine the maximum amount of money you can rob tonight without alerting the police.

### Inputs

*   `nums`: An integer array representing the amount of money in each house.
    *   Each `nums[i]` is a non-negative integer.

### Outputs

*   An integer representing the maximum amount of money you can rob.

### Constraints

*   `1 <= nums.length <= 100`
*   `0 <= nums[i] <= 1000`

### Edge Cases

*   **Single House (`n = 1`):** If there's only one house, you can rob it. The maximum is `nums[0]`.
*   **Two Houses (`n = 2`):** If there are two houses, you can rob either one, but not both. The maximum is `max(nums[0], nums[1])`.
*   **Empty Array:** The constraints state `nums.length >= 1`, so an empty array is not an input.

## 💡 Core Concepts & Data Structures/Algorithms

This problem is a prime example of applying **Dynamic Programming** combined with a clever **problem decomposition** strategy.

### 1. Dynamic Programming (DP)

*   **Optimal Substructure**: The optimal solution to the overall problem can be constructed from optimal solutions to its subproblems. If we know the maximum money we can rob up to a certain house `i`, we can use this information to find the maximum for house `i+1`.
*   **Overlapping Subproblems**: When we break down the problem, we notice that the same subproblems are solved repeatedly. DP efficiently stores the results of these subproblems to avoid re-computation.

The core DP recurrence for the linear (non-circular) "House Robber I" problem is:
`dp[i] = max(money_at_house[i] + dp[i-2], dp[i-1])`
This means, for the current house `i`, you have two choices:
    1.  Rob house `i`: In this case, you cannot rob house `i-1`. So, the total money would be `money_at_house[i]` plus the maximum money you could rob up to house `i-2`.
    2.  Don't rob house `i`: In this case, the total money would be the same as the maximum money you could rob up to house `i-1`.

### 2. Problem Decomposition for Circular Arrays

The critical challenge in House Robber II is the circular arrangement. The adjacency between the first and last houses (`nums[0]` and `nums[n-1]`) means we cannot rob both. This immediately suggests a strategy to transform the circular problem into standard linear problems:

*   **Case 1: Rob `nums[0]` (the first house).** If we rob the first house, we *cannot* rob the last house (`nums[n-1]`). This effectively means we are solving the "House Robber I" problem on the subarray `nums[0 ... n-2]`.
*   **Case 2: Don't rob `nums[0]` (the first house).** If we don't rob the first house, the restriction on `nums[n-1]` is lifted (relative to `nums[0]`). This means we are solving the "House Robber I" problem on the subarray `nums[1 ... n-1]`.

The maximum money you can rob in the circular arrangement will be the maximum of the results from these two independent linear subproblems.

## Walkthrough: Step-by-Step Logic

We'll define a helper function `rob_linear(arr)` that solves the original "House Robber I" problem (i.e., finding the maximum money that can be robbed from a *linear* array of houses). Then, we'll apply this helper to our decomposed subproblems.

### 1. `rob_linear(arr)` Helper Function (House Robber I)

This function finds the maximum amount of money that can be robbed from a linear list of houses, ensuring no two adjacent houses are robbed. We use a space-optimized DP approach.

*   **Inputs:** `arr` (a list of non-negative integers representing money in houses).
*   **Outputs:** Maximum money that can be robbed from `arr`.

**Logic:**
Initialize two variables to keep track of the maximum money robbed:
*   `prev1`: Maximum money robbed up to the *previous* house (`i-1`).
*   `prev2`: Maximum money robbed up to the house *before the previous one* (`i-2`).

Iterate through each house's money `x` in `arr`:
1.  Calculate `current_max`: This is the maximum of two choices:
    *   Don't rob the current house: The max money is `prev1`.
    *   Rob the current house `x`: The max money is `x + prev2` (since we cannot rob `prev1`'s house).
    2.  Update `prev2` to `prev1`.
    3.  Update `prev1` to `current_max`.

After iterating through all houses, `prev1` will hold the maximum money robbed from `arr`.

**Base Cases for `rob_linear`:**
*   If `arr` is empty: return `0`.
*   If `arr` has one house: return `arr[0]`.

### 2. Main `solve_optimal` Function (House Robber II)

*   **Inputs:** `nums` (the original circular array).
*   **Outputs:** Maximum money robbed from `nums`.

**Logic:**
1.  **Handle Edge Cases:**
    *   If `n == 1` (only one house), return `nums[0]`. This is crucial because `nums[0:n-1]` would be `nums[0:0]` which is empty, and `nums[1:n]` would be `nums[1:1]` which is also empty. `rob_linear([])` would return 0, which is incorrect.

2.  **Decompose and Solve:**
    *   Calculate `max1 = rob_linear(nums[0 : n-1])`: This represents the case where `nums[n-1]` (the last house) is NOT robbed. The houses considered are `nums[0]` through `nums[n-2]`.
    *   Calculate `max2 = rob_linear(nums[1 : n])`: This represents the case where `nums[0]` (the first house) is NOT robbed. The houses considered are `nums[1]` through `nums[n-1]`.

3.  **Return the Maximum:**
    *   The overall maximum money is `max(max1, max2)`.

### Example Walkthrough: `nums = [2,3,2]`

Let `n = 3`.

1.  **Edge Case Check:** `n` is not 1, so proceed.

2.  **Subproblem 1: Robbing `nums[0 ... n-2]` (excluding `nums[n-1]`)**
    *   We call `rob_linear([2, 3])`.
    *   Inside `rob_linear([2, 3])`:
        *   `prev2 = 0`, `prev1 = 0`
        *   For `x = 2`:
            *   `current_max = max(prev1, x + prev2) = max(0, 2 + 0) = 2`
            *   `prev2 = 0`, `prev1 = 2`
        *   For `x = 3`:
            *   `current_max = max(prev1, x + prev2) = max(2, 3 + 0) = 3`
            *   `prev2 = 2`, `prev1 = 3`
        *   `rob_linear` returns `3`. So, `max1 = 3`.

3.  **Subproblem 2: Robbing `nums[1 ... n-1]` (excluding `nums[0]`)**
    *   We call `rob_linear([3, 2])`.
    *   Inside `rob_linear([3, 2])`:
        *   `prev2 = 0`, `prev1 = 0`
        *   For `x = 3`:
            *   `current_max = max(prev1, x + prev2) = max(0, 3 + 0) = 3`
            *   `prev2 = 0`, `prev1 = 3`
        *   For `x = 2`:
            *   `current_max = max(prev1, x + prev2) = max(3, 2 + 0) = 3`
            *   `prev2 = 3`, `prev1 = 3`
        *   `rob_linear` returns `3`. So, `max2 = 3`.

4.  **Final Result:**
    *   `max(max1, max2) = max(3, 3) = 3`.

The maximum money you can rob from `[2,3,2]` is `3` (by robbing either house 1 or house 2).

## 💻 Solutions Implemented in Codebase

```python
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Optimal ---
def solve_optimal(nums: list[int]) -> int:
    def rob_linear(arr: list[int]) -> int:
        # Base cases for the linear problem
        if not arr:
            return 0
        if len(arr) == 1:
            return arr[0]

        prev2 = 0  # Max money up to house i-2
        prev1 = 0  # Max money up to house i-1 (initially, from house -1, which is 0)

        for x in arr:
            # Current max is either:
            # 1. Don't rob current house (take prev1's max)
            # 2. Rob current house (take current money + prev2's max)
            current_max = max(prev1, x + prev2)
            prev2 = prev1
            prev1 = current_max
        return prev1

    n = len(nums)
    if n == 0:
        return 0 # Per constraints, n >= 1, but good practice
    if n == 1:
        return nums[0]

    # Case 1: Rob houses from 0 to n-2 (exclude last house)
    # This implies nums[0] might be robbed, but nums[n-1] cannot be.
    result_excluding_last = rob_linear(nums[0 : n - 1])

    # Case 2: Rob houses from 1 to n-1 (exclude first house)
    # This implies nums[0] cannot be robbed, so nums[n-1] can be.
    result_excluding_first = rob_linear(nums[1 : n])

    return max(result_excluding_last, result_excluding_first)

# Placeholder for the starter template
def solve():
    # Example usage:
    # nums = [2, 3, 2]
    # print(solve_optimal(nums))
    # nums = [1, 2, 3, 1]
    # print(solve_optimal(nums))
    # nums = [1]
    # print(solve_optimal(nums))
    pass

```

## ⏱️ Complexity Analysis

| Approach        | Time Complexity | Space Complexity | Reasoning                                                                                                                                                                             |
| :-------------- | :-------------- | :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Optimal (DP)** | `O(N)`          | `O(1)`           | The `rob_linear` function iterates through its input array once, taking `O(N)` time. We call `rob_linear` twice on subarrays of size `N-1`, leading to `O(N) + O(N)` = `O(N)` total time. <br> The `rob_linear` function uses a constant number of variables (`prev1`, `prev2`, `current_max`), resulting in `O(1)` auxiliary space. Python's list slicing `nums[0:n-1]` and `nums[1:n]` creates new lists, which would technically take `O(N)` space for the copies. However, when discussing algorithmic space complexity, we often refer to the *auxiliary* space used by the algorithm itself, excluding input/output or intermediate data structures created by language features if they are not integral to the DP state storage. For competitive programming, this is generally considered `O(1)` extra space beyond input. |

## 🌍 Real-World Applications

The House Robber problem, and its variations, illustrate a common pattern in **optimization problems** where sequential decisions have dependencies:

1.  **Resource Allocation with Mutual Exclusion:** Imagine scheduling tasks where certain tasks cannot run concurrently (e.g., using the same limited resource). This pattern can help optimize the selection of non-conflicting tasks to maximize throughput or value.
2.  **Financial Portfolio Optimization:** Selecting investments where some investments are mutually exclusive due to risk profiles or regulatory constraints.
3.  **Job Scheduling:** In manufacturing or IT, scheduling jobs on a machine where some jobs cannot follow each other directly due to setup times or resource conflicts. The goal is to maximize the number of jobs completed or total value generated.
4.  **Network Routing:** Determining optimal paths in a network where certain nodes or links cannot be used consecutively due to congestion or security policies.
5.  **Dynamic Pricing Strategies:** In e-commerce, deciding which promotions to offer on consecutive days, where certain promotions might invalidate others, to maximize long-term revenue.
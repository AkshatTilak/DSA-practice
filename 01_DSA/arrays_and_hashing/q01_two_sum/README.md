# Two Sum (q01_two_sum)

## Overview & Problem Explanation

The "Two Sum" problem is a foundational challenge in data structures and algorithms, frequently encountered in technical interviews. Given an array of integers, `nums`, and a target integer, `target`, the goal is to find two distinct numbers within the array whose sum equals `target`. The task is to return the **indices** of these two numbers.

### Problem Statement

You are given:
*   An array of integers, `nums`.
*   An integer, `target`.

Your function should:
*   Return a list (or array) of two integers, representing the **indices** of the two numbers in `nums` that add up to `target`.

### Constraints

The problem comes with specific constraints that define the characteristics of the input and the expected behavior:
*   The length of the `nums` array will be between 2 and 10^4 elements, inclusive (`2 <= nums.length <= 10^4`).
*   Each element `nums[i]` in the array will be between -10^9 and 10^9, inclusive (`-10^9 <= nums[i] <= 10^9`).
*   The `target` value will also be between -10^9 and 10^9, inclusive (`-10^9 <= target <= 10^9`).
*   Crucially, there is exactly one valid solution for each input. This means you don't need to worry about multiple pairs summing to the target or no solution existing.
*   You may not use the same element twice. This implies that the two indices you return must be different (`i != j`).

### Example

Let's illustrate with an example:

**Input:**
`nums = [2, 7, 11, 15]`
`target = 9`

**Output:**
`[0, 1]`

**Explanation:**
Because `nums[0]` (which is 2) + `nums[1]` (which is 7) equals 9, we return their indices `[0, 1]`.

## Core Concepts & Data Structures/Algorithms

The "Two Sum" problem can be approached with different strategies, but understanding the trade-offs in terms of efficiency often leads to the use of a key data structure: the **Hash Map** (also known as a Hash Table, dictionary in Python, or `HashMap` in Java).

### 1. Brute Force (Naive Approach)

This approach involves checking every possible pair of numbers in the array to see if their sum matches the target. It's straightforward to understand but generally not the most efficient for larger datasets.

### 2. Hash Map (Optimal Approach)

The optimal solution leverages a **Hash Map** to significantly reduce the time complexity.

*   **What is a Hash Map?**
    A hash map is a data structure that implements an associative array abstract data type, mapping keys to values. It uses a hash function to compute an index into an array of buckets or slots, from which the desired value can be found.
*   **Why choose a Hash Map for Two Sum?**
    The primary advantage of hash maps is their ability to perform **average O(1) time complexity** for insertion, deletion, and, most importantly for this problem, **lookup** operations (checking if a key exists).
*   **How it works (theoretically):**
    When looking for two numbers that sum to `target`, if we have `num1 + num2 = target`, then `num2 = target - num1`. If we iterate through the array and for each `num1`, we can quickly check if `target - num1` (its "complement") has been seen before and stored, we can find the pair efficiently. The hash map allows this quick check.

## Step-by-Step Logic

Let's break down the logic for both the brute force and the optimal hash map approaches.

### Approach 1: Naive Brute Force

This method exhaustively checks every unique pair of numbers.

1.  **Outer Loop**: Iterate through the array `nums` with an index `i` from the first element up to the second-to-last element.
2.  **Inner Loop**: For each `nums[i]`, iterate with a second index `j` from `i + 1` to the end of the array. This ensures that:
    *   We consider distinct elements (`j` is always greater than `i`).
    *   We don't use the same element twice (since `j` starts after `i`).
3.  **Check Sum**: Inside the inner loop, check if `nums[i] + nums[j]` is equal to `target`.
4.  **Return Indices**: If the sum matches the `target`, return the list `[i, j]`.
5.  **No Solution (Theoretical)**: According to the problem constraints, a solution always exists, so the loops will always find and return a pair.

**Dry Run Example:**
`nums = [2, 7, 11, 15]`, `target = 9`

*   `i = 0`, `nums[0] = 2`
    *   `j = 1`, `nums[1] = 7`
        *   `nums[0] + nums[1] = 2 + 7 = 9`. This equals `target`.
        *   **Return `[0, 1]`**.

### Approach 2: Optimal Pythonic (Hash Map / One-Pass)

This approach makes a single pass through the array, using a hash map to store previously encountered numbers and their indices.

1.  **Initialize Hash Map**: Create an empty hash map (e.g., a Python dictionary `num_to_idx`). This map will store `(number: index)` pairs.
2.  **Iterate and Process**: Loop through `nums` using both the index (`idx`) and the value (`num`) of each element.
3.  **Calculate Complement**: For the current `num`, calculate the `complement` needed to reach the `target`: `complement = target - num`.
4.  **Check in Hash Map**: Check if this `complement` already exists as a key in `num_to_idx`.
    *   **If `complement` is in `num_to_idx`**: This means we have found the two numbers. The index of the `complement` is `num_to_idx[complement]`, and the index of the current `num` is `idx`. Return `[num_to_idx[complement], idx]`.
    *   **If `complement` is NOT in `num_to_idx`**: The current `num` is not the second part of a pair found so far. Store the current `num` and its `idx` in the hash map for future lookups: `num_to_idx[num] = idx`.
5.  **No Solution (Theoretical)**: Due to the problem constraints, a solution is guaranteed to be found and returned within the loop.

**Dry Run Example:**
`nums = [2, 7, 11, 15]`, `target = 9`
`num_to_idx = {}`

*   `idx = 0`, `num = 2`
    *   `complement = 9 - 2 = 7`.
    *   Is `7` in `num_to_idx`? No.
    *   Add `(2: 0)` to `num_to_idx`. `num_to_idx = {2: 0}`.
*   `idx = 1`, `num = 7`
    *   `complement = 9 - 7 = 2`.
    *   Is `2` in `num_to_idx`? Yes, `num_to_idx[2]` is `0`.
    *   **Return `[num_to_idx[2], 1]` which is `[0, 1]`**.

## Complexity Analysis

Let `N` be the number of elements in the `nums` array.

| Approach                  | Time Complexity | Space Complexity | Reasoning                                                                                                                                                                                                                            |
| :------------------------ | :-------------- | :--------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Naive Brute Force**  | O(N^2)          | O(1)             | The solution involves nested loops. The outer loop runs `N-1` times, and the inner loop runs approximately `N` times in the worst case (from `i+1` to `N-1`). This leads to `N * N` operations, which is quadratic. No additional data structures are used, only a few variables. |
| **2. Optimal (Hash Map)** | O(N)            | O(N)             | We iterate through the array once. For each element, calculating the complement and performing a hash map lookup (or insertion) takes **average O(1)** time. Thus, the total time complexity is linear. In the worst case, the hash map may store all `N` elements if no pair is found until the very end, requiring space proportional to `N`.           |

## Real-World Applications

The "Two Sum" problem, or the underlying pattern it represents, is highly relevant in various real-world software systems:

1.  **Transaction Matching/Financial Systems**: Identifying two transactions that, when combined, meet a specific value (e.g., balancing debits and credits, finding two payments that sum to an invoice total).
2.  **Data Filtering and Search**: In large datasets, quickly finding two data points that satisfy a certain numerical relationship. For instance, finding two products whose prices add up to a promotional discount value.
3.  **Cryptography and Hashing**: While Two Sum is simpler, the concept of efficiently checking for the existence of a "complement" is fundamental to collision detection in hash functions and other cryptographic algorithms.
4.  **Compiler Design / Symbol Tables**: Compilers use symbol tables (often implemented with hash maps) for fast lookups of variable names, function names, and other identifiers. The efficiency of hash map lookups is critical for overall compilation speed.
5.  **Network Routing**: In some routing algorithms, finding pairs of network nodes or path costs that sum to a certain latency or capacity could leverage similar principles.
6.  **E-commerce Recommendations**: While more complex, recommending items that complement a user's existing choices or basket value could conceptually involve summing values.
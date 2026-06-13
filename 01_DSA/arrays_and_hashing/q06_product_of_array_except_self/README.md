# Product Of Array Except Self (q06_product_of_array_except_self)

## Overview & Problem Explanation

The "Product Of Array Except Self" challenge is a classic array manipulation problem that requires you to compute an array where each element `answer[i]` is the product of all elements in the input array `nums` *except* for the element at index `i`. The key constraints are to solve this **without using the division operation** and within **O(N) time complexity**.

**Inputs**:
*   `nums`: A list (or array) of integers.

**Outputs**:
*   An array `answer` of the same length as `nums`, where `answer[i]` is the product of all elements in `nums` except `nums[i]`.

**Constraints**:
*   The length of `nums` (`n`) is between 2 and 10^5 (inclusive).
*   Each element `nums[i]` is between -30 and 30 (inclusive).
*   The product of any prefix or suffix of `nums` is guaranteed to fit within a 32-bit integer.
*   The overall product `answer[i]` for any index `i` is also guaranteed to fit within a 32-bit integer.
*   You **must not use the division operator**.
*   Your algorithm must run in **O(N) time complexity**.
*   The follow-up asks to solve it in **O(1) extra space complexity**, where the output array itself **does not count as extra space**.

**Example 1**:
Input: `nums = [1, 2, 3, 4]`
Output: `[24, 12, 8, 6]`
Explanation:
*   `answer[0]` = 2 * 3 * 4 = 24
*   `answer[1]` = 1 * 3 * 4 = 12
*   `answer[2]` = 1 * 2 * 4 = 8
*   `answer[3]` = 1 * 2 * 3 = 6

**Example 2**:
Input: `nums = [-1, 1, 0, -3, 3]`
Output: `[0, 0, 9, 0, 0]`
Explanation:
*   `answer[0]` = 1 * 0 * -3 * 3 = 0
*   `answer[1]` = -1 * 0 * -3 * 3 = 0
*   `answer[2]` = -1 * 1 * -3 * 3 = 9 (Product of all elements except 0)
*   `answer[3]` = -1 * 1 * 0 * 3 = 0
*   `answer[4]` = -1 * 1 * 0 * -3 = 0

**Edge Cases**:
*   **Zeroes in the array**: If there's one zero, `answer[i]` will be 0 for all `i` except the index of the zero, which will be the product of all non-zero elements. If there are two or more zeroes, all elements in the `answer` array will be 0.
*   **Negative numbers**: Handled naturally by multiplication.
*   **Smallest array size**: `n` is at least 2.

## Core Concepts & Data Structures/Algorithms

The primary conceptual insight for solving this problem efficiently and without division is to leverage **prefix products** and **suffix products**.

**Why Prefix and Suffix Products?**
The product of all elements except `nums[i]` can be thought of as:
(Product of all elements to the *left* of `nums[i]`) * (Product of all elements to the *right* of `nums[i]`).

*   **Prefix Product**: For any index `i`, the prefix product is the cumulative product of all elements from the beginning of the array up to `nums[i-1]`.
*   **Suffix Product**: For any index `i`, the suffix product is the cumulative product of all elements from the end of the array down to `nums[i+1]`.

By calculating these two separate products for each index and then multiplying them, we effectively exclude `nums[i]` from the total product without ever needing to perform division. This strategy naturally leads to an O(N) time complexity solution.

## Step-by-Step Logic

### Naive/Brute Force Approach (Conceptual)

A straightforward, but inefficient, approach would be to iterate through the array for each index `i`. For each `i`, iterate through the entire array again, multiplying all elements where the index is not `i`.

```python
def product_except_self_naive(nums: list[int]) -> list[int]:
    n = len(nums)
    answer = [0] * n
    for i in range(n):
        current_product = 1
        for j in range(n):
            if i != j:
                current_product *= nums[j]
        answer[i] = current_product
    return answer
```
This approach involves nested loops, leading to O(N^2) time complexity, which violates the O(N) requirement.

### Optimal Solution: Prefix and Suffix Products (Two-Pass Approach)

The optimal solution utilizes two passes over the array to build the `answer` array directly, achieving O(N) time and O(1) extra space (excluding the output array).

**Algorithm Steps**:

1.  **Initialize Result Array**: Create an `answer` array of the same size as `nums`, and initialize all its elements to 1. This array will store our final results.
    `answer = [1, 1, 1, ..., 1]` (length `n`)
2.  **First Pass (Calculate Prefix Products)**:
    *   Iterate through the `nums` array from left to right, starting from index 0.
    *   Maintain a `prefix_product` variable, initialized to 1.
    *   For each index `i`:
        *   Set `answer[i]` to the current `prefix_product`. At this point, `answer[i]` stores the product of all elements *before* `nums[i]`.
        *   Update `prefix_product` by multiplying it with `nums[i]`.
    *   After this pass, `answer[i]` contains the product of `nums[0] * ... * nums[i-1]`. For `answer[0]`, it will be 1 (as there are no elements to its left).

    **Dry Run (First Pass) with `nums = [1, 2, 3, 4]`**:
    *   `n = 4`
    *   `answer = [1, 1, 1, 1]`
    *   `prefix_product = 1`

    | `i` | `nums[i]` | `answer` (before update) | `answer[i]` = `prefix_product` | `prefix_product` = `prefix_product` * `nums[i]` | `answer` (after update) |
    | :-- | :-------- | :----------------------- | :----------------------------- | :---------------------------------------------- | :------------------------ |
    | 0   | 1         | `[1, 1, 1, 1]`           | `answer[0] = 1`                | `prefix_product = 1 * 1 = 1`                    | `[1, 1, 1, 1]`            |
    | 1   | 2         | `[1, 1, 1, 1]`           | `answer[1] = 1`                | `prefix_product = 1 * 2 = 2`                    | `[1, 1, 1, 1]`            |
    | 2   | 3         | `[1, 1, 1, 1]`           | `answer[2] = 2`                | `prefix_product = 2 * 3 = 6`                    | `[1, 1, 2, 1]`            |
    | 3   | 4         | `[1, 1, 2, 1]`           | `answer[3] = 6`                | `prefix_product = 6 * 4 = 24`                   | `[1, 1, 2, 6]`            |

    After the first pass, `answer` is `[1, 1, 2, 6]`. This represents the prefix products (product of elements to the left).

3.  **Second Pass (Calculate Suffix Products and Final Result)**:
    *   Iterate through the `nums` array from right to left, starting from index `n-1`.
    *   Maintain a `suffix_product` variable, initialized to 1.
    *   For each index `i`:
        *   Multiply `answer[i]` (which currently holds the prefix product) by the current `suffix_product`. This combines the product of elements to the left and to the right of `nums[i]`.
        *   Update `suffix_product` by multiplying it with `nums[i]`.
    *   After this pass, `answer[i]` will hold the desired result.

    **Dry Run (Second Pass) with `nums = [1, 2, 3, 4]` and `answer = [1, 1, 2, 6]` (from first pass)**:
    *   `n = 4`
    *   `suffix_product = 1`

    | `i` | `nums[i]` | `answer` (before update) | `answer[i]` = `answer[i]` * `suffix_product` | `suffix_product` = `suffix_product` * `nums[i]` | `answer` (after update) |
    | :-- | :-------- | :----------------------- | :--------------------------------------------- | :---------------------------------------------- | :------------------------ |
    | 3   | 4         | `[1, 1, 2, 6]`           | `answer[3] = 6 * 1 = 6`                        | `suffix_product = 1 * 4 = 4`                    | `[1, 1, 2, 6]`            |
    | 2   | 3         | `[1, 1, 2, 6]`           | `answer[2] = 2 * 4 = 8`                        | `suffix_product = 4 * 3 = 12`                   | `[1, 1, 8, 6]`            |
    | 1   | 2         | `[1, 1, 8, 6]`           | `answer[1] = 1 * 12 = 12`                      | `suffix_product = 12 * 2 = 24`                  | `[1, 12, 8, 6]`           |
    | 0   | 1         | `[1, 12, 8, 6]`          | `answer[0] = 1 * 24 = 24`                      | `suffix_product = 24 * 1 = 24`                  | `[24, 12, 8, 6]`          |

    The final `answer` array is `[24, 12, 8, 6]`, which is the correct output.

```python
def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    answer = [1] * n

    # First pass: Calculate prefix products
    # answer[i] will contain product of nums[0...i-1]
    prefix_product = 1
    for i in range(n):
        answer[i] = prefix_product
        prefix_product *= nums[i]
    
    # Second pass: Calculate suffix products and combine with prefix products
    # answer[i] is now product of nums[0...i-1]
    # We multiply it by product of nums[i+1...n-1]
    suffix_product = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix_product
        suffix_product *= nums[i]
        
    return answer
```

## Complexity Analysis

| Approach                       | Time Complexity | Space Complexity | Reasoning                                                                                                                                                                                                                                                                                                 |
| :----------------------------- | :-------------- | :--------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Naive (Brute Force)**        | O(N^2)          | O(1)             | The outer loop runs `N` times. The inner loop runs `N` times for each iteration of the outer loop, resulting in `N * N` operations. Only a few extra variables are used. The output array is excluded per problem guidelines.                                                               |
| **Optimal (Two-Pass)**         | O(N)            | O(1)             | The algorithm performs two separate passes over the input array, each iterating `N` times. This results in `O(N) + O(N) = O(2N)`, which simplifies to `O(N)`. Only a few extra variables (`prefix_product`, `suffix_product`) are used, which is constant space. The output array is excluded per problem guidelines. |

## Real-World Applications

While "Product of Array Except Self" might seem like a specific algorithmic puzzle, the underlying patterns (prefix sums/products, dynamic programming, efficient array manipulation) are common in various software systems:

1.  **Data Stream Processing**: In scenarios where you need to calculate aggregates (sums, products, averages) over a sliding window or for specific sub-sections of a continuous data stream, without re-calculating everything from scratch.
2.  **Financial Analysis**: Calculating rolling products for stock returns, or analyzing performance metrics where the contribution of a specific asset or period needs to be isolated without direct division (e.g., if a value could be zero).
3.  **Signal Processing/Image Processing**: Computing convolutions or transformations that involve products or sums of neighboring elements, where optimizing calculations for overlapping windows is crucial.
4.  **Database Query Optimization**: Similar to prefix sums, prefix/suffix products can be conceptually applied in optimizing queries that involve cumulative calculations, allowing pre-computation to speed up subsequent requests.
5.  **Compiler Optimization**: In certain arithmetic expression evaluations, identifying and optimizing common sub-expressions or patterns that resemble prefix/suffix calculations can lead to more efficient code generation.
6.  **Cryptography and Hashing (Conceptual)**: While not directly this algorithm, the idea of combining values in a non-linear way (like products) without relying on division might appear in more complex hash functions or cryptographic primitives, where performance and specific mathematical properties are essential.
7.  **Resource Management/Load Balancing**: In distributed systems, understanding the "impact" of removing a single node or resource can sometimes be modeled using similar logic, where the overall system's capacity/throughput is the "product" of individual components.
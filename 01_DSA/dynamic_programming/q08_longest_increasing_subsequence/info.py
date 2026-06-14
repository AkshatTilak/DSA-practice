INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/longest-increasing-subsequence/',
    'description': 'LIS length.',
    'groups': ['Dynamic Programming', 'Array', 'Binary Search'],
    'readme_content': """# Longest Increasing Subsequence (LIS)

## 1. Overview & Problem Explanation

The **Longest Increasing Subsequence (LIS)** problem is a classic algorithmic challenge that asks us to find the length of the longest subsequence in a given array of integers such that all elements of the subsequence are sorted in **strictly increasing** order.

### Key Definitions
- **Subsequence**: A sequence that can be derived from another sequence by deleting zero or more elements without changing the order of the remaining elements. (Unlike a *subarray*, a subsequence does not need to be contiguous).
- **Strictly Increasing**: For any two consecutive elements in the subsequence $a_i$ and $a_{i+1}$, the condition $a_i < a_{i+1}$ must hold.

### Input/Output Example
- **Input**: `nums = [10, 9, 2, 5, 3, 7, 101, 18]`
- **Possible Increasing Subsequences**: `[10, 101]`, `[2, 5, 7, 101]`, `[2, 3, 7, 18]`
- **Output**: `4` (The length of `[2, 3, 7, 18]` or `[2, 5, 7, 18]`)

### Constraints & Edge Cases
- **Empty Input**: If `nums` is empty, the LIS length is $0$.
- **All Identical Elements**: For `[7, 7, 7, 7]`, the LIS length is $1$ because it must be *strictly* increasing.
- **Strictly Decreasing**: For `[5, 4, 3, 2, 1]`, the LIS length is $1$.
- **Negative Numbers**: The logic remains the same regardless of whether numbers are positive or negative.
- **Complexity Limits**: For an input size of $N = 10^5$, an $O(N^2)$ approach will time out (TLE), necessitating an $O(N \log N)$ solution.

---

## 2. Core Concepts & Algorithmic Patterns

### Dynamic Programming (DP)
The problem exhibits **Optimal Substructure**. The LIS ending at index $i$ depends on the LIS ending at some index $j < i$. By storing the results of smaller subproblems (the LIS length for every index), we avoid redundant calculations.

### Patience Sorting (The $O(N \log N)$ Intuition)
The optimal solution is based on a technique called **Patience Sorting**. Imagine you are dealing cards into piles:
1. You place a card on a pile if the card's value is $\le$ the top card of that pile.
2. If the card is larger than all current pile-top cards, you create a new pile to the right.
3. You always place a card on the **leftmost** possible pile.

The number of piles formed at the end is exactly the length of the Longest Increasing Subsequence.

### Binary Search
In the Patience Sorting approach, since the top cards of the piles are always sorted, we can use **Binary Search** to find the leftmost pile where a card can be placed, reducing the search time from $O(N)$ to $O(\log N)$.

---

## 3. Step-by-Step Logic

### Approach 1: Standard Dynamic Programming ($O(N^2)$)

1. **State Definition**: Let `dp[i]` be the length of the LIS that ends with the element at index `i`.
2. **Initialization**: Initialize an array `dp` of size $N$ with $1$ (since every single element is an increasing subsequence of length 1).
3. **Transition**: For every index `i` from $1$ to $N-1$:
    - Iterate through all indices `j` from $0$ to $i-1$.
    - If `nums[i] > nums[j]`, then `nums[i]` can extend the sequence ending at `j`.
    - Update: `dp[i] = max(dp[i], dp[j] + 1)`.
4. **Result**: The final answer is the maximum value found in the `dp` array.

**Dry Run `[10, 9, 2, 5, 3]`**:
- `i=0`: `dp=[1, 1, 1, 1, 1]`
- `i=1` (9): $9 \ngtr 10 \rightarrow$ `dp[1]=1`
- `i=2` (2): $2 \ngtr 10, 2 \ngtr 9 \rightarrow$ `dp[2]=1`
- `i=3` (5): $5 \ngtr 10, 5 \ngtr 9, 5 > 2 \rightarrow$ `dp[3] = max(1, 1+1) = 2`
- `i=4` (3): $3 \ngtr 10, 3 \ngtr 9, 3 > 2 \rightarrow$ `dp[4] = max(1, 1+1) = 2`
- **Max**: $2$

---

### Approach 2: Binary Search / Patience Sorting ($O(N \log N)$)

1. **The `tails` Array**: Maintain an array `tails` where `tails[i]` stores the **smallest ending element** of all increasing subsequences of length $i+1$.
2. **Iteration**: For each number `x` in `nums`:
    - If `x` is larger than all elements in `tails`, append `x` to the end (this increases the LIS length).
    - If `x` is not the largest, find the smallest element in `tails` that is $\ge x$ using binary search and replace it with `x`.
3. **Why replace?** Replacing a larger tail with a smaller one doesn't change the current LIS length, but it makes it **easier** for future numbers to be appended, potentially increasing the length later.
4. **Result**: The length of the `tails` array is the LIS.

**Dry Run `[10, 9, 2, 5, 3, 7]`**:
- `x=10`: `tails = [10]`
- `x=9`: Replace 10 $\rightarrow$ `tails = [9]`
- `x=2`: Replace 9 $\rightarrow$ `tails = [2]`
- `x=5`: Append $\rightarrow$ `tails = [2, 5]`
- `x=3`: Replace 5 $\rightarrow$ `tails = [2, 3]`
- `x=7`: Append $\rightarrow$ `tails = [2, 3, 7]`
- **Length**: $3$

---

## 4. Implementation

```python
import bisect

def solve_optimal(nums):
    if not nums:
        return 0
    
    # tails[i] will store the smallest tail of all increasing subsequences of length i+1
    tails = []
    
    for x in nums:
        # Find the insertion point to maintain sorted order
        # bisect_left finds the first index where tails[i] >= x
        idx = bisect.bisect_left(tails, x)
        
        if idx == len(tails):
            # x is larger than any current tail, so it extends the LIS
            tails.append(x)
        else:
            # x can replace an existing tail to make it smaller and more flexible
            tails[idx] = x
            
    return len(tails)
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Standard DP** | $O(N^2)$ | $O(N)$ | Nested loops: outer loop runs $N$ times, inner loop runs up to $N$ times. |
| **Binary Search** | $O(N \log N)$ | $O(N)$ | We iterate through the array once ($N$) and perform a binary search ($\log N$) at each step. |

---

## 6. Real-World Applications

The Longest Increasing Subsequence pattern is used in several high-level computing domains:

1. **Version Control Systems (Diff Tools)**: Algorithms like the Myers Diff algorithm use concepts similar to LIS to find the minimum number of edits (insertions/deletions) to transform one file into another.
2. **Bioinformatics**: Used in comparing DNA or protein sequences to find common patterns or evolutionary similarities (though often modified into Longest Common Subsequence).
3. **Database Query Optimization**: Used in certain join-order optimizations and indexing strategies where sequential access patterns are analyzed.
4. **Scheduling**: Determining the maximum number of tasks that can be performed in a specific order given their constraints.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(n)
# This approach uses dynamic programming. We maintain an array 'dp' where dp[i] represents the length of the longest increasing subsequence ending at index i. For each element, we look back at all previous elements to find the maximum LIS length that can be extended.
def solve_naive(nums):
    if not nums:
        return 0
    
    n = len(nums)
    # Initialize DP table with 1 since each element is an LIS of length 1
    dp = [1] * n
    
    for i in range(1, n):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
                
    return max(dp)

# --- APPROACH 2: Optimal (Binary Search / Patience Sorting) ---
# Time Complexity: O(n log n)
# Space Complexity: O(n)
# This approach uses the concept of Patience Sorting. We maintain a list 'tails', where tails[i] is the smallest tail of all increasing subsequences of length i+1. For each number x in the input, we use binary search to find the smallest element in 'tails' that is greater than or equal to x and replace it. If x is larger than all elements in 'tails', we append it. This ensures that 'tails' remains sorted and represents the most optimistic potential for future extensions.
import bisect

def solve_optimal(nums):
    if not nums:
        return 0
    
    # tails[i] will store the smallest tail of all increasing subsequences of length i+1
    tails = []
    
    for x in nums:
        # Binary search to find the insertion point for x in tails
        # bisect_left finds the leftmost index to insert x while maintaining order
        idx = bisect.bisect_left(tails, x)
        
        if idx == len(tails):
            # x is larger than any current tail, extending the longest subsequence
            tails.append(x)
        else:
            # x can replace an existing tail to potentially allow longer subsequences later
            tails[idx] = x
            
    return len(tails)

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package dynamic_programming;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class LongestIncreasingSubsequence {
    /**
     * Computes the length of the Longest Increasing Subsequence using Binary Search.
     * Time Complexity: O(n log n)
     * Space Complexity: O(n)
     */
    public int solveOptimal(int[] nums) {
        if (nums == null || nums.length == 0) {
            return 0;
        }

        // Using a list to act as the 'tails' array for binary search
        List<Integer> tails = new ArrayList<>();

        for (int x : nums) {
            int idx = Collections.binarySearch(tails, x);
            
            // binarySearch returns (-(insertion point) - 1) if the element is not found
            if (idx < 0) {
                idx = -(idx + 1);
            }

            if (idx == tails.size()) {
                tails.add(x);
            } else {
                tails.set(idx, x);
            }
        }

        return tails.size();
    }

    public static void main(String[] args) {
        LongestIncreasingSubsequence lis = new LongestIncreasingSubsequence();
        int[] nums = {10, 9, 2, 5, 3, 7, 101, 18};
        System.out.println("Length of LIS: " + lis.solveOptimal(nums)); // Output: 4
    }
}
\"\"\"""",
}

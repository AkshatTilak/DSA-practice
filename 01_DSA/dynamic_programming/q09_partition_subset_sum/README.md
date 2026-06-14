# Partition Subset Sum (q09_partition_subset_sum)

## 📌 Overview & Problem Explanation

The **Partition Subset Sum** problem asks whether a given set of positive integers can be divided into two subsets such that the sum of elements in both subsets is exactly equal.

### The Core Intuition
If we can split an array into two subsets with equal sums, it implies that:
1. The total sum of all elements in the array must be **even**. If the total sum is odd, it is mathematically impossible to divide it into two equal integer parts.
2. If the total sum is $S$, we are essentially looking for a subset whose sum is exactly $T = S / 2$. If we find a subset that sums to $T$, the remaining elements will automatically sum to $T$ as well.

**Example:**
- **Input:** `nums = [1, 5, 11, 5]`
- **Total Sum:** $1 + 5 + 11 + 5 = 22$
- **Target:** $22 / 2 = 11$
- **Check:** Can we find a subset that sums to $11$? Yes, $\{11\}$ or $\{1, 5, 5\}$.
- **Output:** `True`

### Constraints & Edge Cases
- **Empty Input:** While the problem usually specifies a non-empty array, an empty array typically cannot be partitioned.
- **Odd Total Sum:** Immediately return `False`.
- **Single Element:** A single element cannot be partitioned into two non-empty subsets.
- **Large Target Sum:** If the target sum is very large, the time complexity $O(N \cdot \text{Target})$ might become a bottleneck (though usually acceptable for "Medium" constraints).

---

## 🧠 Core Concepts & Algorithms

### 1. The 0/1 Knapsack Pattern
This is a classic variation of the **0/1 Knapsack Problem**. In a 0/1 Knapsack, for every item, you have a binary choice: either you **include** the item in your subset or you **exclude** it. You cannot use the same element multiple times.

### 2. Dynamic Programming (DP)
We use DP because the problem exhibits:
- **Overlapping Subproblems:** Calculating if sum $X$ is possible often requires knowing if sum $X - \text{current\_num}$ was possible.
- **Optimal Substructure:** The solution to the problem for $N$ elements can be built from the solutions for $N-1$ elements.

### 3. Why DP over Recursion?
A naive recursive approach would explore every possible subset, leading to a time complexity of $O(2^n)$, which is exponential. DP reduces this to pseudo-polynomial time by storing the results of previously computed sub-problems.

---

## 🚶 Step-by-Step Logic

### Approach 1: Recursive Brute Force (Naive)
1. Start from the first element.
2. For each element, you have two choices:
   - Add it to the subset sum.
   - Ignore it and move to the next element.
3. If the current sum equals the target, return `True`.
4. If you reach the end of the array without hitting the target, return `False`.

### Approach 2: Top-Down DP (Memoization)
To optimize the recursion, we use a hash map or a 2D array `memo[index][current_sum]` to store whether we have already checked if the `current_sum` is achievable starting from `index`.

### Approach 3: Bottom-Up DP (Tabulation)
1. Create a boolean array `dp` of size `target + 1`.
2. `dp[i]` will be `True` if a sum of `i` can be formed using a subset of the numbers processed so far.
3. **Base Case:** `dp[0] = True` (a sum of 0 is always possible with an empty subset).
4. For every number `num` in `nums`:
   - Update the `dp` table from **right to left** (from `target` down to `num`).
   - `dp[i] = dp[i] or dp[i - num]`
   - *Crucial:* We iterate backward to ensure that each number is used only once. If we iterated forward, we might use the same number multiple times to reach the target (which would solve the "Unbounded Knapsack" problem instead).

### Dry Run Example: `nums = [1, 5, 11, 5]`, `Target = 11`
- Initialize `dp = [True, F, F, F, F, F, F, F, F, F, F, True]` (indices 0 to 11)
- **Processing 1:** `dp[1] = dp[1] or dp[0]` $\rightarrow$ `dp[1] = True`
- **Processing 5:** `dp[6] = dp[6] or dp[1]`, `dp[5] = dp[5] or dp[0]` $\rightarrow$ `dp[6]=T, dp[5]=T`
- **Processing 11:** `dp[11] = dp[11] or dp[0]` $\rightarrow$ `dp[11] = True`
- **Result:** `dp[11]` is `True`.

---

## 💻 Implementation

```python
def solve_optimal(nums):
    total_sum = sum(nums)
    
    # If the total sum is odd, it cannot be partitioned into two equal subsets
    if total_sum % 2 != 0:
        return False
    
    target = total_sum // 2
    
    # dp[i] represents whether a subset sum of i is possible
    # We only need a 1D array to optimize space
    dp = [False] * (target + 1)
    
    # Base case: A sum of 0 is always possible (empty subset)
    dp[0] = True
    
    for num in nums:
        # Iterate backwards to ensure each element is used only once
        # We stop at 'num' because we can't form a sum smaller than the number itself
        for i in range(target, num - 1, -1):
            if dp[i - num]:
                dp[i] = True
        
        # Early exit: if we've already found the target sum, we can stop
        if dp[target]:
            return True
            
    return dp[target]
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(2^N)$ | $O(N)$ | Explores every possible subset combination. |
| **Top-Down DP** | $O(N \cdot T)$ | $O(N \cdot T)$ | State is defined by (index, current\_sum). |
| **Bottom-Up DP** | $O(N \cdot T)$ | $O(T)$ | Space optimized to a 1D array of size Target. |

*Where $N$ is the number of elements in the array and $T$ is the target sum ($\sum nums / 2$).*

---

## 🌍 Real-World Applications

The "Partition Subset Sum" pattern is widely used in optimization and resource management:

1. **Load Balancing:** In distributed systems, if you have two servers with equal capacity, you can use this logic to determine if a set of tasks (with varying weights/resource requirements) can be split perfectly between them to prevent one server from being overloaded.
2. **Cryptography:** Problems related to the "Subset Sum" are the foundation of some early public-key cryptosystems (e.g., the Merkle-Hellman knapsack cryptosystem).
3. **Bin Packing (Simplified):** Determining if items can fit into a fixed number of bins is a generalization of the partition problem.
4. **Financial Auditing:** Detecting if a specific transaction amount was composed of a certain subset of smaller invoices or payments.
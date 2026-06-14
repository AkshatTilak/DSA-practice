INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/partition-equal-subset-sum/',
    'description': 'Partition equal sum check.',
    'groups': ['Dynamic Programming', 'Array'],
    'readme_content': """# Partition Subset Sum (q09_partition_subset_sum)

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
4. **Financial Auditing:** Detecting if a specific transaction amount was composed of a certain subset of smaller invoices or payments.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(2^n)
# Space Complexity: O(n)
# This approach uses recursion to explore all possible subsets. For each element, we decide
# whether to include it in the target sum or not. This results in an exponential time complexity.
def can_partition_naive(nums):
    total_sum = sum(nums)
    if total_sum % 2 != 0:
        return False
    
    target = total_sum // 2
    n = len(nums)
    
    def solve(index, current_sum):
        # Base case: target sum reached
        if current_sum == target:
            return True
        # Base case: index out of bounds or sum exceeded
        if index >= n or current_sum > target:
            return False
        
        # Option 1: Include nums[index] in the subset
        if solve(index + 1, current_sum + nums[index]):
            return True
        
        # Option 2: Exclude nums[index] from the subset
        if solve(index + 1, current_sum):
            return True
            
        return False

    return solve(0, 0)

# --- APPROACH 2: Optimal (Dynamic Programming) ---
# Time Complexity: O(n * S) where n is the number of elements and S is the target sum (total_sum / 2).
# Space Complexity: O(S)
# This approach uses a 1D DP array to track reachable sums. We iterate through each number
# and update the DP table from right to left to ensure each number is used only once per subset.
# This is optimal because it reduces the state space from exponential to pseudo-polynomial
# and minimizes space by utilizing the property that the current state only depends on the previous state.
def can_partition_optimal(nums):
    total_sum = sum(nums)
    
    # If the total sum is odd, it's impossible to partition it into two equal integer subsets.
    if total_sum % 2 != 0:
        return False
    
    target = total_sum // 2
    n = len(nums)
    
    # dp[i] will be True if a subset sum of i is possible
    dp = [False] * (target + 1)
    dp[0] = True # Sum of 0 is always possible (empty subset)
    
    for num in nums:
        # Iterate backwards to prevent using the same element multiple times for the same target sum
        for j in range(target, num - 1, -1):
            if dp[j - num]:
                dp[j] = True
        
        # Early exit if we've already found a way to reach the target sum
        if dp[target]:
            return True
            
    return dp[target]

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package dynamic_programming;

import java.util.*;

public class PartitionSubsetSum {
    /**
     * Checks if the array can be partitioned into two subsets with equal sums.
     * Time Complexity: O(n * S)
     * Space Complexity: O(S)
     */
    public boolean canPartition(int[] nums) {
        if (nums == null || nums.length == 0) {
            return false;
        }
        
        int totalSum = 0;
        for (int num : nums) {
            totalSum += num;
        }
        
        // If total sum is odd, cannot be partitioned into two equal halves
        if (totalSum % 2 != 0) {
            return false;
        }
        
        int target = totalSum / 2;
        boolean[] dp = new boolean[target + 1];
        dp[0] = true;
        
        for (int num : nums) {
            // Traverse backwards to ensure we use the 'previous' state of the DP array
            for (int j = target; j >= num; j--) {
                if (dp[j - num]) {
                    dp[j] = true;
                }
            }
            // Optimization: Return true immediately if target is reached
            if (dp[target]) {
                return true;
            }
        }
        
        return dp[target];
    }

    public static void main(String[] args) {
        PartitionSubsetSum solver = new PartitionSubsetSum();
        int[] nums1 = {1, 5, 11, 5};
        System.out.println("Input: [1, 5, 11, 5] | Result: " + solver.canPartition(nums1)); // Expected: true
        
        int[] nums2 = {1, 2, 3, 5};
        System.out.println("Input: [1, 2, 3, 5] | Result: " + solver.canPartition(nums2)); // Expected: false
    }
}
\"\"\"""",
}

INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/3sum/',
    'description': 'Find all unique triplets that sum to zero.',
    'groups': ['Array', 'Two Pointers'],
    'starter_code': """def three_sum(nums: list[int]) -> list[list[int]]:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^3)
# Space Complexity: O(M) where M is the number of unique triplets
# This approach uses three nested loops to check every possible combination of three elements. 
# To ensure uniqueness of triplets, we sort each found triplet and store it in a set.
def three_sum_naive(nums: list[int]) -> list[list[int]]:
    res = set()
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    # Sort the triplet to handle duplicates via the set
                    triplet = tuple(sorted([nums[i], nums[j], nums[k]]))
                    res.add(triplet)
    return [list(t) for t in res]

# --- APPROACH 2: Optimal (Sorting + Two Pointers) ---
# Time Complexity: O(N^2)
# Space Complexity: O(1) or O(N) depending on the sorting implementation
# This approach is optimal because it reduces the search space from O(N^3) to O(N^2). 
# By sorting the array, we can use two pointers (left and right) to find the target sum 
# for a fixed element nums[i]. Skipping identical elements ensures that no duplicate 
# triplets are added to the result without needing a costly set operation.
def three_sum_optimal(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res = []
    n = len(nums)
    
    for i in range(n - 2):
        # Skip duplicate values for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        # Optimization: Since the array is sorted, if nums[i] > 0, 
        # no three numbers can sum to 0
        if nums[i] > 0:
            break
            
        left, right = i + 1, n - 1
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            if current_sum == 0:
                res.append([nums[i], nums[left], nums[right]])
                # Skip duplicate values for the second and third elements
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1
                
    return res

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package two_pointers;

import java.util.*;

public class ThreeSum {
    /**
     * Finds all unique triplets that sum to zero.
     * Time Complexity: O(N^2)
     * Space Complexity: O(1) (excluding the space for the output list)
     */
    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        if (nums == null || nums.length < 3) {
            return result;
        }

        Arrays.sort(nums);

        for (int i = 0; i < nums.length - 2; i++) {
            // Avoid duplicates for the first element
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }

            // Optimization: If the smallest number is > 0, sum cannot be 0
            if (nums[i] > 0) {
                break;
            }

            int left = i + 1;
            int right = nums.length - 1;

            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];

                if (sum == 0) {
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));

                    // Avoid duplicates for left and right pointers
                    while (left < right && nums[left] == nums[left + 1]) {
                        left++;
                    }
                    while (left < right && nums[right] == nums[right - 1]) {
                        right--;
                    }
                    left++;
                    right--;
                } else if (sum < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return result;
    }
}
\"\"\"""",
    'test_code': """def test_3sum():
    assert len(three_sum([-1,0,1,2,-1,-4])) > 0""",
    'readme_content': """# 3Sum (q03_3sum)

## 📌 Overview & Problem Explanation

The **3Sum** problem is a classic extension of the "Two Sum" problem. The goal is to find all unique triplets in an integer array that sum up to exactly zero.

### Problem Statement
Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that:
1. $i \neq j, i \neq k,$ and $j \neq k$ (The indices must be distinct).
2. $nums[i] + nums[j] + nums[k] = 0$.
3. The solution set **must not contain duplicate triplets**.

### Inputs & Outputs
- **Input**: A list of integers `nums` (e.g., `[-1, 0, 1, 2, -1, -4]`).
- **Output**: A list of lists containing the triplets (e.g., `[[-1, -1, 2], [-1, 0, 1]]`).

### Constraints & Edge Cases
- **Array Size**: Can range from $0$ to $3000$ elements.
- **Value Range**: Integers can be negative, zero, or positive.
- **Empty/Small Inputs**: If the array has fewer than 3 elements, no triplet can exist.
- **Duplicates**: The input array may contain duplicate numbers, but the output must only contain unique triplets.
- **All Zeros**: An input like `[0, 0, 0, 0]` should result in `[[0, 0, 0]]`.

---

## 💡 Core Concepts & Algorithms

To solve this problem efficiently, we combine **Sorting** with the **Two-Pointer Technique**.

### 1. Why Sorting?
Sorting the array serves two critical purposes:
- **Duplicate Handling**: Once the array is sorted, duplicate elements are adjacent. This allows us to skip them easily using a simple `while` loop or an `if` check, ensuring our result set contains only unique triplets.
- **Directional Movement**: In a sorted array, if our current sum is too low, we know exactly which direction to move to increase it (move the left pointer right). If the sum is too high, we move the right pointer left.

### 2. The Two-Pointer Pattern
The 3Sum problem can be viewed as: for every element $nums[i]$, find two other elements $nums[left]$ and $nums[right]$ such that:
$$nums[left] + nums[right] = -nums[i]$$
By fixing one number and using two pointers to find the remaining two, we reduce the search space from a cubic complexity to a quadratic one.

---

## 🛠️ Step-by-Step Logic

### Naive Approach (Brute Force)
The simplest way is to use three nested loops to check every possible combination of three numbers.
1. Loop $i$ from $0$ to $n-1$.
2. Loop $j$ from $i+1$ to $n-1$.
3. Loop $k$ from $j+1$ to $n-1$.
4. If $nums[i] + nums[j] + nums[k] == 0$, add the triplet to a **Set** (to handle uniqueness).
- **Complexity**: $O(n^3)$ time.

### Optimal Approach (Sort + Two Pointers)

#### Logical Steps:
1. **Sort** the input array `nums`.
2. **Iterate** through the array with a pointer $i$. This is our "fixed" element.
   - If $nums[i] > 0$, break the loop immediately (since the array is sorted, no three positive numbers can sum to zero).
   - If $i > 0$ and $nums[i] == nums[i-1]$, skip this iteration to avoid duplicate triplets.
3. **Initialize Two Pointers**:
   - `left = i + 1`
   - `right = len(nums) - 1`
4. **While `left < right`**:
   - Calculate `current_sum = nums[i] + nums[left] + nums[right]`.
   - **Case 1: `current_sum == 0`**: 
     - We found a triplet! Append `[nums[i], nums[left], nums[right]]` to the results.
     - Move `left` forward and `right` backward.
     - **Crucial**: Skip any identical values for `nums[left]` and `nums[right]` to avoid duplicates.
   - **Case 2: `current_sum < 0`**: 
     - The sum is too small. To increase it, move the `left` pointer to the right (`left += 1`).
   - **Case 3: `current_sum > 0`**: 
     - The sum is too large. To decrease it, move the `right` pointer to the left (`right -= 1`).

### Dry Run Example
`nums = [-1, 0, 1, 2, -1, -4]`

1. **Sort**: `[-4, -1, -1, 0, 1, 2]`
2. **$i = 0$ (val: -4)**:
   - `left = -1`, `right = 2`. Sum = $-4 + (-1) + 2 = -3$. (Too small $\rightarrow$ `left++`)
   - `left = -1`, `right = 2`. Sum = $-4 + (-1) + 2 = -3$. (Too small $\rightarrow$ `left++`)
   - ... no triplets found for -4.
3. **$i = 1$ (val: -1)**:
   - `left = -1`, `right = 2`. Sum = $-1 + (-1) + 2 = 0$. **Found: [-1, -1, 2]**.
   - Move pointers: `left` becomes $0$, `right` becomes $1$.
   - `left = 0`, `right = 1`. Sum = $-1 + 0 + 1 = 0$. **Found: [-1, 0, 1]**.
4. **$i = 2$ (val: -1)**:
   - $nums[2] == nums[1]$. **Skip** to avoid duplicate triplets.
5. **End of loop**. Final Result: `[[-1, -1, 2], [-1, 0, 1]]`.

---

## 🚀 Implementation

```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res = []
    n = len(nums)
    
    for i in range(n):
        # Optimization: If the fixed number is > 0, 
        # the remaining numbers must also be > 0, so sum cannot be 0.
        if nums[i] > 0:
            break
            
        # Skip duplicate values for the fixed pointer 'i'
        if i > 0 and nums[i] == nums[i-1]:
            continue
            
        left, right = i + 1, n - 1
        
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                # Found a triplet
                res.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates for the left and right pointers
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                
                # Move pointers inward after finding a valid triplet
                left += 1
                right -= 1
                
    return res
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(n^3)$ | $O(1)$ or $O(k)$ | Triple nested loop; space for results. |
| **Optimal** | $O(n^2)$ | $O(1)$ to $O(n)$ | $O(n \log n)$ for sorting + $O(n^2)$ for the loop/pointer search. Space depends on the sorting algorithm implementation. |

- **Time**: The outer loop runs $n$ times. Inside, the `while` loop with two pointers traverses the remaining array once ($O(n)$). Total = $O(n \times n) = O(n^2)$.
- **Space**: If we ignore the space required for the output list, the space complexity is $O(1)$ (constant extra space) or $O(\log n)$ to $O(n)$ depending on the sorting algorithm used by the language (e.g., Timsort in Python).

---

## 🌍 Real-World Applications

The "3Sum" pattern (searching for a target sum within a sorted dataset) is highly applicable in various domains:

1. **Financial Auditing**: Identifying "Wash Trades" or balanced transactions where a series of credits and debits sum to zero to detect fraudulent accounting.
2. **Signal Processing**: Finding specific frequency combinations that cancel each other out (destructive interference).
3. **Computational Geometry**: Finding if three points are collinear (though this usually involves slopes, the underlying search for triplets is similar).
4. **Resource Allocation**: In cloud computing, finding a combination of three virtual machine sizes that exactly fit a physical server's total capacity.""",
}

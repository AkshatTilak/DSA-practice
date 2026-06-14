INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/',
    'description': 'Find two numbers in a sorted array that add up to target.',
    'groups': ['Array', 'Two Pointers'],
    'starter_code': """def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach uses nested loops to check every possible pair of numbers in the array.
# Although simple, it is inefficient for large arrays as it does not leverage the sorted property of the input.
def two_sum_sorted_naive(numbers: list[int], target: int) -> list[int]:
    n = len(numbers)
    for i in range(n):
        for j in range(i + 1, n):
            if numbers[i] + numbers[j] == target:
                # Returning 1-based indices as per standard Two Sum II specifications
                return [i + 1, j + 1]
    return []

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# Since the input array is already sorted, we can use two pointers: one at the beginning and one at the end.
# If the sum is too small, we move the left pointer forward to increase the sum.
# If the sum is too large, we move the right pointer backward to decrease the sum.
# This is optimal because it processes the array in a single pass and requires no additional memory.
def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    left = 0
    right = len(numbers) - 1
    
    while left < right:
        current_sum = numbers[left] + numbers[right]
        
        if current_sum == target:
            return [left + 1, right + 1]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
            
    return []

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package two_pointers;

public class TwoSumIi {
    /**
     * Finds two numbers in a sorted array that add up to a specific target.
     * Returns the 1-based indices of the two numbers.
     * 
     * @param numbers Sorted array of integers
     * @param target The target sum
     * @return int array containing 1-based indices [index1, index2]
     */
    public int[] twoSum(int[] numbers, int target) {
        int left = 0;
        int right = numbers.length - 1;
        
        while (left < right) {
            int currentSum = numbers[left] + numbers[right];
            
            if (currentSum == target) {
                return new int[]{left + 1, right + 1};
            } else if (currentSum < target) {
                left++;
            } else {
                right--;
            }
        }
        
        // Return an empty array if no solution is found, although problem 
        // constraints typically guarantee exactly one solution.
        return new int[0];
    }

    public static void main(String[] args) {
        TwoSumIi solution = new TwoSumIi();
        int[] nums = {2, 7, 11, 15};
        int target = 9;
        int[] result = solution.twoSum(nums, target);
        System.out.println("[" + result[0] + ", " + result[1] + "]"); // Expected: [1, 2]
    }
}
\"\"\"""",
    'test_code': """def test_two_sum_ii():
    assert two_sum_sorted([2,7,11,15], 9) == [1, 2]""",
    'readme_content': """# Two Sum II - Input Array Is Sorted

## 📌 Overview & Problem Explanation

The **Two Sum II** challenge is a variation of the classic "Two Sum" problem. The critical difference here is that the input array is **already sorted in non-decreasing order**. 

### Problem Statement
Given a 1-indexed array of integers `numbers` that is already sorted in non-decreasing order, you need to find two numbers such that they add up to a specific `target` number.

### Constraints & Requirements
- **Sorted Input**: The array is guaranteed to be sorted. This is the most important hint for choosing an optimal algorithm.
- **Exactly One Solution**: The problem guarantees that there is exactly one solution, and you may not use the same element twice.
- **1-Indexed Output**: The resulting indices must be 1-indexed (e.g., index `0` in Python becomes index `1` in the output).
- **Space Complexity Goal**: The challenge encourages finding a solution with $O(1)$ extra space.

### Edge Cases to Consider
- **Negative Numbers**: The array can contain negative integers (e.g., `[-5, -2, 1, 4]`).
- **Large Values**: The target or the numbers in the array could be very large, though Python handles arbitrary-precision integers automatically.
- **Minimum Array Size**: The smallest possible input is an array of length 2.

---

## 🧠 Core Concepts & Algorithmic Pattern

### The Two Pointers Technique
The optimal way to solve this problem is using the **Two Pointers** pattern, specifically the **Opposite Ends** approach.

#### Why Two Pointers?
In an unsorted array, we typically use a **Hash Map** to store seen values to achieve $O(n)$ time complexity, but that costs $O(n)$ space. However, because this array is **sorted**, we can leverage the mathematical property of the sequence:
1. Increasing the left index $\rightarrow$ **Increases** the total sum.
2. Decreasing the right index $\rightarrow$ **Decreases** the total sum.

By placing one pointer at the very start (smallest value) and one at the very end (largest value), we can "squeeze" the search space based on whether our current sum is too high or too low.

---

## 🚶 Step-by-Step Logic

### 1. Brute Force Approach (Naive)
The naive approach involves checking every possible pair using nested loops.
- Iterate through each element $i$.
- For each $i$, iterate through all subsequent elements $j$.
- If `numbers[i] + numbers[j] == target`, return indices.
- **Downside**: This results in $O(n^2)$ time complexity, which is inefficient for large arrays.

### 2. Optimal Two Pointers Approach
1. **Initialize**: Place a `left` pointer at index `0` and a `right` pointer at index `len(numbers) - 1`.
2. **Evaluate**: Calculate the current sum: `current_sum = numbers[left] + numbers[right]`.
3. **Compare**:
   - **Case A: `current_sum == target`**: You found the pair! Return `[left + 1, right + 1]`.
   - **Case B: `current_sum < target`**: The sum is too small. To increase the sum, move the `left` pointer one step to the right (`left += 1`).
   - **Case C: `current_sum > target`**: The sum is too large. To decrease the sum, move the `right` pointer one step to the left (`right -= 1`).
4. **Repeat**: Continue steps 2 and 3 until the pointers meet.

### 🔍 Dry Run Example
**Input**: `numbers = [2, 7, 11, 15]`, `target = 9`

| Step | Left Index | Right Index | Values | Sum | Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 0 | 3 | $2 + 15$ | 17 | $17 > 9 \rightarrow$ Move Right pointer left |
| 2 | 0 | 2 | $2 + 11$ | 13 | $13 > 9 \rightarrow$ Move Right pointer left |
| 3 | 0 | 1 | $2 + 7$ | 9 | **Match!** Return `[0+1, 1+1]` |

**Result**: `[1, 2]`

---

## 💻 Implementation

```python
def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    \"\"\"
    Finds two numbers in a sorted array that add up to target using 
    the two-pointer approach.
    \"\"\"
    # Initialize two pointers at the opposite ends of the array
    left = 0
    right = len(numbers) - 1
    
    while left < right:
        current_sum = numbers[left] + numbers[right]
        
        if current_sum == target:
            # Return 1-indexed positions
            return [left + 1, right + 1]
        
        elif current_sum < target:
            # Sum is too small, move left pointer to a larger value
            left += 1
            
        else:
            # Sum is too large, move right pointer to a smaller value
            right -= 1
            
    # The problem guarantees exactly one solution, 
    # so we don't strictly need a return here, but it's good practice.
    return []
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(n^2)$ | $O(1)$ | Nested loops iterate through almost all pairs. |
| **Hash Map** | $O(n)$ | $O(n)$ | Single pass, but requires a map to store seen values. |
| **Two Pointers** | $O(n)$ | $O(1)$ | Single pass through the array; no extra data structures used. |

- **Time Complexity $O(n)$**: In the worst case, we visit each element in the array at most once.
- **Space Complexity $O(1)$**: We only use two integer variables (`left` and `right`) regardless of the input size.

---

## 🌍 Real-World Applications

The Two Pointers pattern is a fundamental building block in software engineering:

1. **Search Optimization**: Used in database query optimizers to find pairs of records that meet specific criteria in sorted indexes.
2. **Data Deduplication**: Used when merging two sorted lists (like in **Merge Sort**) to identify duplicate entries efficiently.
3. **Signal Processing**: In audio or image processing, two pointers are often used to find specific "windows" or peaks in sorted signal data.
4. **Network Routing**: Some routing table lookups use similar "shrinking window" logic to find the longest prefix match in sorted IP ranges.""",
}

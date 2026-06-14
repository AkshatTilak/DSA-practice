INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/',
    'description': 'Find minimum element in a sorted array that was rotated.',
    'groups': ['Array', 'Binary Search'],
    'starter_code': """def find_min(nums: list[int]) -> int:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# The naive approach iterates through the entire array once to find the minimum element.
def find_min_naive(nums: list[int]) -> int:
    if not nums:
        raise ValueError("Input array cannot be empty")
    
    min_val = nums[0]
    for i in range(1, len(nums)):
        if nums[i] < min_val:
            min_val = nums[i]
    return min_val

# --- APPROACH 2: Optimal (Binary Search) ---
# Time Complexity: O(log n)
# Space Complexity: O(1)
# Since the array is sorted and then rotated, it consists of two sorted subarrays. 
# We use binary search to identify the "pivot" point where the rotation occurred.
# If nums[mid] > nums[right], the minimum element must be in the right half (mid + 1 to right).
# If nums[mid] <= nums[right], the minimum element is either at mid or in the left half (left to mid).
# This reduces the search space by half in each iteration, making it O(log n).
def find_min(nums: list[int]) -> int:
    if not nums:
        raise ValueError("Input array cannot be empty")
    
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = left + (right - left) // 2
        
        # If mid element is greater than the rightmost element, 
        # the minimum must be in the right part of the array.
        if nums[mid] > nums[right]:
            left = mid + 1
        # Otherwise, the minimum is in the left part, including mid.
        else:
            right = mid
            
    return nums[left]

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package binary_search;

public class FindMinimumInRotatedSortedArray {
    /**
     * Finds the minimum element in a rotated sorted array.
     * Time Complexity: O(log n)
     * Space Complexity: O(1)
     */
    public int findMin(int[] nums) {
        if (nums == null || nums.length == 0) {
            throw new IllegalArgumentException("Input array cannot be empty");
        }
        
        int left = 0;
        int right = nums.length - 1;
        
        while (left < right) {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] > nums[right]) {
                // The minimum is in the right half
                left = mid + 1;
            } else {
                // The minimum is in the left half, including mid
                right = mid;
            }
        }
        
        return nums[left];
    }

    public static void main(String[] args) {
        FindMinimumInRotatedSortedArray solver = new FindMinimumInRotatedSortedArray();
        int[] nums = {4, 5, 6, 7, 0, 1, 2};
        System.out.println("Minimum element: " + solver.findMin(nums)); // Output: 0
    }
}
\"\"\"""",
    'test_code': """def test_min_rotated():
    assert find_min([3,4,5,1,2]) == 1""",
    'readme_content': """# Find Minimum In Rotated Sorted Array

## Overview & Problem Explanation

This challenge asks us to find the minimum element in an array that was originally sorted in ascending order but has been rotated at some unknown pivot point.

Imagine an array `[0, 1, 2, 4, 5, 6, 7]`. If it's rotated 4 times, it might become `[4, 5, 6, 7, 0, 1, 2]`. Notice that the array is no longer fully sorted, but it consists of two sorted sub-arrays. The minimum element will always be at the "break" or "inflection point" between these two sorted parts.

Our goal is to efficiently locate this minimum element.

**Inputs:**
*   `nums`: A list of integers (`list[int]`).
    *   It's guaranteed that `nums` was originally sorted in ascending order.
    *   It's guaranteed that `nums` has been rotated `k` times, where `1 <= k <= n` (meaning it's *always* rotated, not just potentially).
    *   All integers in `nums` are **unique**. (This is a crucial constraint that simplifies the problem compared to its variant allowing duplicates).

**Outputs:**
*   An integer, representing the minimum value in the rotated sorted array.

**Constraints:**
*   `n == nums.length`
*   `1 <= n <= 5000`
*   `-5000 <= nums[i] <= 5000`
*   All the integers of `nums` are unique.

**Edge Cases & Considerations:**
*   **Array with a single element:** If `n=1`, the array is `[x]`. The minimum is `x`. Our algorithm should handle this.
*   **Array already "sorted":** If the array is rotated `n` times, it effectively returns to its original sorted state (e.g., `[1,2,3,4,5]` rotated 5 times remains `[1,2,3,4,5]`). The problem statement `1 <= k <= n` ensures it's always rotated, but if `k=n`, it's equivalent to `k=0`. The minimum will still be `nums[0]`.
*   **Unique elements:** This constraint significantly simplifies the binary search logic, as we don't have to deal with `nums[mid] == nums[left]` or `nums[mid] == nums[right]` ambiguities that arise with duplicates.

## Core Concepts & Data Structures/Algorithms

The most efficient approach to solve this problem is **Binary Search**.

### Why Binary Search?
Even though the array is "rotated," it retains a crucial property: it is composed of **two sorted sub-arrays**. For example, in `[4, 5, 6, 7, 0, 1, 2]`, `[4, 5, 6, 7]` is sorted, and `[0, 1, 2]` is sorted. The minimum element (`0`) is the pivot or inflection point where the order "breaks."

Binary search is ideal for problems where:
1.  The search space is ordered (or partially ordered).
2.  We can eliminate a significant portion (typically half) of the search space in each step.

In a rotated sorted array with unique elements, we can always determine which half contains the minimum by comparing the middle element with the elements at the boundaries of our current search space. This allows us to repeatedly narrow down the search interval logarithmically.

### How it Works (Theoretically)
1.  Initialize `left` and `right` pointers to the start and end of the array.
2.  In each iteration, calculate the `mid` element.
3.  **Crucial Logic**: Compare `nums[mid]` with `nums[right]` (or `nums[left]`).
    *   If `nums[mid] > nums[right]`: This means `mid` is in the "larger" sorted segment (e.g., `mid` is `7` in `[4,5,6,7,0,1,2]`). The minimum must therefore be in the right half, after `mid`. So, we update `left = mid + 1`.
    *   If `nums[mid] < nums[right]`: This means `mid` is in the "smaller" sorted segment (e.g., `mid` is `0` in `[4,5,6,7,0,1,2]`, or `mid` is `5` in `[4,5,1,2,3]`). The minimum could be `mid` itself, or it could be to the left of `mid`. So, we update `right = mid`.
4.  There's also an important optimization: If at any point `nums[left] < nums[right]`, it means the current segment `[left...right]` is fully sorted. In this case, `nums[left]` is guaranteed to be the minimum within this segment (and possibly the overall minimum if this is the first such occurrence or the entire array).

The loop continues until `left` and `right` pointers converge, at which point they both point to the minimum element.

## Step-by-Step Logic

### 1. Brute Force (Linear Scan)

**Logic:**
The simplest way to find the minimum element is to iterate through the entire array and keep track of the smallest value encountered.

**Steps:**
1.  Initialize a variable `min_val` to the first element of the array (or positive infinity).
2.  Iterate from the second element (or first, if `min_val` is infinity) to the end of the array.
3.  In each step, compare the current element with `min_val`. If the current element is smaller, update `min_val`.
4.  After iterating through all elements, `min_val` will hold the minimum element.

**Example Trace (`nums = [3, 4, 5, 1, 2]`):**
1.  `min_val = 3`
2.  `num = 4`: `4 < 3` is false. `min_val` remains `3`.
3.  `num = 5`: `5 < 3` is false. `min_val` remains `3`.
4.  `num = 1`: `1 < 3` is true. `min_val` becomes `1`.
5.  `num = 2`: `2 < 1` is false. `min_val` remains `1`.
6.  Return `1`.

### 2. Optimal Solution (Binary Search)

**Logic:**
Utilize the properties of a rotated sorted array to narrow down the search space by half in each step until the minimum is found.

**Steps:**
1.  Initialize `left` pointer to `0` and `right` pointer to `len(nums) - 1`.
2.  Enter a `while` loop that continues as long as `left < right`.
    *   **Optimization/Base Case**: Check if the sub-array `nums[left...right]` is already sorted. This happens if `nums[left] < nums[right]`. If it is, `nums[left]` is the minimum in this segment, and since we are always narrowing down to the segment containing the minimum, `nums[left]` must be the overall minimum. Return `nums[left]`.
    *   Calculate the middle index: `mid = left + (right - left) // 2`.
    *   **Decision**: Compare `nums[mid]` with `nums[right]`.
        *   If `nums[mid] > nums[right]`: This means the elements from `left` to `mid` are in the "larger" sorted segment. The minimum element must be in the right half, *after* `mid`. So, update `left = mid + 1`.
        *   If `nums[mid] < nums[right]`: This means the elements from `mid` to `right` are in the "smaller" sorted segment (or `mid` itself is the minimum). The minimum element could be `mid` or to its left. So, update `right = mid`.
3.  When the loop terminates (`left == right`), both pointers will be pointing to the minimum element. Return `nums[left]` (or `nums[right]`).

**Python Implementation (Optimal):**

```python
def find_min(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1

    while left < right:
        # If the array segment is already sorted, nums[left] is the minimum.
        # This covers cases like [1, 2, 3, 4, 5] (k=n rotation) or
        # when we've narrowed down to a sorted sub-array.
        if nums[left] < nums[right]:
            return nums[left]

        mid = left + (right - left) // 2

        # Decide which half to discard.
        # If nums[mid] > nums[right], it means the minimum is in the right half
        # (the "break" point is to the right of mid).
        # Example: [3,4,5,1,2]. mid=5, right=2. 5 > 2. Min must be in [1,2]. left = mid + 1.
        if nums[mid] > nums[right]:
            left = mid + 1
        # If nums[mid] < nums[right], it means the minimum is in the left half,
        # potentially including mid. (the "break" point is at or to the left of mid).
        # Example: [4,5,1,2,3]. mid=1, right=3. 1 < 3. Min is 1. right = mid.
        else: # nums[mid] < nums[right] (since elements are unique, cannot be ==)
            right = mid
    
    # When the loop terminates (left == right), left (or right) points to the minimum element.
    return nums[left]

```

**Dry Run (`nums = [3, 4, 5, 1, 2]`):**

| Iteration | `left` | `right` | `nums[left]` | `nums[right]` | `nums[left] < nums[right]` | `mid` | `nums[mid]` | `nums[mid] > nums[right]` | Action          |
| :-------- | :----- | :------ | :----------- | :------------ | :-------------------------- | :---- | :---------- | :------------------------ | :-------------- |
| Initial   | 0      | 4       | 3            | 2             | False                       |       |             |                           |                 |
| 1         | 0      | 4       | 3            | 2             | False                       | 2     | 5           | True (5 > 2)              | `left = mid + 1` (`left` becomes `3`) |
| 2         | 3      | 4       | 1            | 2             | True (1 < 2)                |       |             |                           | Return `nums[left]` (`1`) |
| End       |        |         |              |               |                             |       |             |                           | Result: `1`     |

**Dry Run (`nums = [4, 5, 1, 2, 3]`):**

| Iteration | `left` | `right` | `nums[left]` | `nums[right]` | `nums[left] < nums[right]` | `mid` | `nums[mid]` | `nums[mid] > nums[right]` | Action          |
| :-------- | :----- | :------ | :----------- | :------------ | :-------------------------- | :---- | :---------- | :------------------------ | :-------------- |
| Initial   | 0      | 4       | 4            | 3             | False                       |       |             |                           |                 |
| 1         | 0      | 4       | 4            | 3             | False                       | 2     | 1           | False (1 < 3)             | `right = mid` (`right` becomes `2`) |
| 2         | 0      | 2       | 4            | 1             | False                       | 1     | 5           | True (5 > 1)              | `left = mid + 1` (`left` becomes `2`) |
| 3         | 2      | 2       |              |               |                             |       |             |                           | Loop terminates (`left == right`) |
| End       |        |         |              |               |                             |       |             |                           | Return `nums[left]` (`1`) |

## Complexity Analysis

| Approach        | Time Complexity | Space Complexity |
| :-------------- | :-------------- | :--------------- |
| Brute Force     | O(N)            | O(1)             |
| Binary Search   | O(log N)        | O(1)             |

**Explanation:**

*   **Brute Force (Linear Scan):**
    *   **Time Complexity: O(N)**
        *   We iterate through all `N` elements of the array exactly once to find the minimum. In the worst case, the minimum could be the last element.
    *   **Space Complexity: O(1)**
        *   We only use a few extra variables (`min_val`, loop counter) which consume a constant amount of space regardless of the input array size.

*   **Binary Search:**
    *   **Time Complexity: O(log N)**
        *   In each step of the binary search, we effectively divide the search space in half. This logarithmic reduction in search space is the hallmark of binary search. For an array of size `N`, it takes approximately `log₂N` steps to converge to a single element.
    *   **Space Complexity: O(1)**
        *   The algorithm uses a fixed number of pointers (`left`, `right`, `mid`) and variables, regardless of the input array's size. No auxiliary data structures are used.

## Real-World Applications

The "Find Minimum in Rotated Sorted Array" problem is a classic example of applying binary search to a subtly ordered data structure. This pattern and the underlying principles are applicable in various real-world scenarios:

1.  **Database Indexing and Search:** Similar logic can be applied in B-trees or other tree-based indexes where data blocks are sorted. If an index becomes "rotated" (e.g., due to rebalancing or specific update patterns), an efficient search for a boundary or specific value can leverage adapted binary search.
2.  **Version Control Systems (Git bisect):** When a bug is introduced in a software project, `git bisect` uses a binary search-like approach to find the commit that introduced the bug. You mark commits as "good" or "bad," and the system efficiently narrows down the culpable commit. This is analogous to finding an "inflection point" where behavior changes.
3.  **Network Routing Tables:** Routers often have sorted lists of IP address ranges to determine the next hop for a packet. If these tables are updated or dynamically reordered (conceptually "rotated"), an efficient search for the smallest matching range can use principles similar to this problem.
4.  **Optimizing Search in Cyclic Data:** In scenarios where data naturally forms a cycle but has an inherent sorted order (e.g., time-series data that wraps around, circular buffers), an adapted binary search can quickly find minimums, maximums, or specific values.
5.  **Resource Allocation:** In distributed systems, if resources (e.g., servers with processing capacity) are ordered by load, and this order can shift due to dynamic conditions, finding the minimum-loaded server can use a similar binary search approach to identify the "inflection point" where load starts to increase again.
6.  **Compiler Optimization:** Some compiler optimizations involve searching for specific patterns or minimum/maximum values within sorted (or partially sorted) instruction sequences to apply transformations.

The key takeaway is the ability to adapt binary search to structures that are not *perfectly* sorted but maintain enough order to allow for logarithmic search reduction.""",
}

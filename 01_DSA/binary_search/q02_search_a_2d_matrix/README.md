# Search A 2D Matrix (q02_search_a_2d_matrix)

## 📖 Overview & Problem Explanation

This challenge asks us to efficiently determine if a given `target` integer exists within an `m x n` 2D matrix. The matrix has two key properties that are crucial for optimization:

1.  **Row-wise Sorted**: Integers in each row are sorted in non-decreasing order from left to right.
2.  **Inter-row Sorted**: The first integer of each row is greater than the last integer of the previous row.

These properties imply that if we were to flatten the entire 2D matrix into a 1D array, that 1D array would also be perfectly sorted in non-decreasing order. This observation is the cornerstone for optimal solutions.

**Inputs**:
*   `matrix`: A list of lists of integers representing the `m x n` 2D matrix.
    *   `m` (number of rows) and `n` (number of columns) are at least 1.
    *   `matrix[i][j]` values range from -10^4 to 10^4.
*   `target`: An integer to search for, ranging from -10^4 to 10^4.

**Output**:
*   `bool`: `True` if the `target` is found in the matrix, `False` otherwise.

**Constraints**:
*   `m == matrix.length`
*   `n == matrix[i].length`
*   `1 <= m, n <= 100`
*   `-10^4 <= matrix[i][j], target <= 10^4`

**Edge Cases**:
*   **Empty Matrix**: The constraints specify `m, n >= 1`, so an entirely empty matrix (0x0) is not possible. However, if `m=1, n=1`, it's a single element matrix.
*   **Target out of range**: If the target is smaller than the smallest element (`matrix[0][0]`) or larger than the largest element (`matrix[m-1][n-1]`), it cannot be present.

**Example**:

```
Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
Output: true

Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 13
Output: false
```

## 🧠 Core Concepts & Data Structures/Algorithms

The problem's primary hints are the "sorted" properties of the matrix. Whenever we encounter sorted data, **Binary Search** immediately comes to mind as an efficient search algorithm.

### Binary Search (Logarithmic Search)
*   **Concept**: Binary search is an algorithm that finds the position of a target value within a sorted array. It repeatedly divides the search interval in half. If the value of the search key is less than the item in the middle of the interval, the algorithm narrows the interval to the lower half. Otherwise, it narrows it to the upper half.
*   **Why it's chosen**: The sorted nature of the rows and the inter-row relationship allow us to leverage binary search, reducing the search space exponentially with each step, leading to a much faster solution than linear scanning.
*   **Properties**:
    *   Requires the data to be sorted.
    *   Time complexity: O(log N) where N is the number of elements.
    *   Space complexity: O(1) (iterative) or O(log N) (recursive due to call stack).

### Treating a 2D Matrix as a Virtual 1D Array
This is the most crucial insight for the optimal solution. Given the two sorting properties:
1.  Each row is sorted: `matrix[i][0] <= matrix[i][1] <= ... <= matrix[i][n-1]`
2.  Rows are sorted relative to each other: `matrix[i][0] > matrix[i-1][n-1]`

These two conditions together guarantee that if you concatenate all rows, the resulting 1D array will also be perfectly sorted.

For an `m x n` matrix:
*   The total number of elements is `M = m * n`.
*   We can conceptually map a 1D index `k` (from `0` to `M-1`) to its corresponding 2D coordinates `(row, col)`:
    *   `row = k // n` (integer division gives the row index)
    *   `col = k % n` (modulo gives the column index)

This mapping allows us to perform a single binary search over the entire conceptual 1D sorted array, efficiently finding the target's potential location.

## 👣 Step-by-Step Logic

We'll explore a couple of approaches, moving from a brute-force idea to the optimal solution.

### Approach 1: Brute Force (Linear Scan)
A straightforward, though inefficient, approach is to simply iterate through every element of the matrix and check if it equals the target.

1.  Iterate through each row `r` from `0` to `m-1`.
2.  Within each row `r`, iterate through each column `c` from `0` to `n-1`.
3.  If `matrix[r][c] == target`, return `True`.
4.  If the loops complete without finding the target, return `False`.

*This approach does not leverage the sorted properties and will be slow for large matrices.*

### Approach 2: Two Binary Searches (Better)
This approach leverages the sorted properties by performing two separate binary searches: one to find the correct row, and another to find the target within that row.

1.  **Binary Search for the Row**:
    *   The goal is to find the row `r_idx` such that `matrix[r_idx][0] <= target` and (if `r_idx < m-1`) `matrix[r_idx + 1][0] > target`. This means the `target` can only be in `matrix[r_idx]`.
    *   Initialize `row_low = 0` and `row_high = m - 1`.
    *   While `row_low <= row_high`:
        *   Calculate `mid_row = row_low + (row_high - row_low) // 2`.
        *   If `matrix[mid_row][0] == target`, we found it, return `True`.
        *   If `matrix[mid_row][0] < target`: The target could be in this row or a later row. So, we try to go right, `row_low = mid_row + 1`.
        *   If `matrix[mid_row][0] > target`: The target must be in an earlier row (or not present). So, we go left, `row_high = mid_row - 1`.
    *   After the loop, `row_high` will point to the index of the row that potentially contains the target (or -1 if `target` is smaller than `matrix[0][0]`).
    *   If `row_high < 0`, the target is smaller than the smallest element in the matrix, so return `False`.

2.  **Binary Search within the Found Row**:
    *   Perform a standard binary search on `matrix[row_high]` for the `target`.
    *   Initialize `col_low = 0` and `col_high = n - 1`.
    *   While `col_low <= col_high`:
        *   Calculate `mid_col = col_low + (col_high - col_low) // 2`.
        *   If `matrix[row_high][mid_col] == target`, return `True`.
        *   If `matrix[row_high][mid_col] < target`, `col_low = mid_col + 1`.
        *   If `matrix[row_high][mid_col] > target`, `col_high = mid_col - 1`.
    *   If the inner loop finishes without finding the target, return `False`.

### Approach 3: Single Binary Search on Virtual 1D Array (Optimal)

This is the most elegant and common optimal solution. It treats the `m x n` matrix as a single sorted array of `m * n` elements and applies binary search directly.

1.  Get the dimensions: `m = len(matrix)` and `n = len(matrix[0])`.
2.  Define the search space for the virtual 1D array:
    *   `low = 0` (index of the first element in the virtual array)
    *   `high = (m * n) - 1` (index of the last element in the virtual array)
3.  Perform binary search:
    *   While `low <= high`:
        *   Calculate `mid = low + (high - low) // 2`. This is the 1D index.
        *   **Map `mid` to 2D coordinates**:
            *   `row = mid // n`
            *   `col = mid % n`
        *   **Compare `matrix[row][col]` with `target`**:
            *   If `matrix[row][col] == target`, we found it. Return `True`.
            *   If `matrix[row][col] < target`, the target must be in the right half of the virtual array. Update `low = mid + 1`.
            *   If `matrix[row][col] > target`, the target must be in the left half of the virtual array. Update `high = mid - 1`.
4.  If the loop finishes (meaning `low > high`), the target was not found. Return `False`.

#### Dry Run Example (Optimal Approach)

Let's trace `matrix = [[1, 3, 5], [10, 11, 13]], target = 11`

*   `m = 2`, `n = 3`
*   `low = 0`, `high = (2 * 3) - 1 = 5`

**Iteration 1:**
*   `mid = 0 + (5 - 0) // 2 = 2`
*   `row = 2 // 3 = 0`
*   `col = 2 % 3 = 2`
*   `matrix[0][2] = 5`
*   `5 < target (11)`, so `low = mid + 1 = 3`

**Iteration 2:**
*   `low = 3`, `high = 5`
*   `mid = 3 + (5 - 3) // 2 = 4`
*   `row = 4 // 3 = 1`
*   `col = 4 % 3 = 1`
*   `matrix[1][1] = 11`
*   `11 == target (11)`, so return `True`.

Target found!

## ⏱️ Complexity Analysis

| Approach                       | Time Complexity       | Space Complexity |
| :----------------------------- | :-------------------- | :--------------- |
| **Brute Force (Linear Scan)**  | O(M*N)                | O(1)             |
| **Two Binary Searches**        | O(log M + log N)      | O(1)             |
| **Single Binary Search (Optimal)** | O(log (M*N))          | O(1)             |

**Explanation**:

*   **Brute Force**: In the worst case, we might visit every element in the matrix. An `m x n` matrix has `m * n` elements.
*   **Two Binary Searches**:
    *   Finding the correct row takes `O(log M)` time because we are binary searching through `M` rows (specifically, the first elements of `M` rows).
    *   Searching within that row takes `O(log N)` time because we are binary searching through `N` columns.
    *   Total time: `O(log M + log N)`.
*   **Single Binary Search (Optimal)**:
    *   We are performing a single binary search over a conceptual 1D array of `M * N` elements.
    *   Each step divides the search space in half. Therefore, the time complexity is `O(log (M*N))`.
    *   **Note**: `log (M*N)` is mathematically equivalent to `log M + log N`. So, both optimal approaches have the same asymptotic time complexity. The single binary search might have slightly better constant factors in practice as it avoids nested function calls or separate loop structures.
*   **Space Complexity**: All approaches use a constant amount of extra space for variables (pointers, loop counters), making them `O(1)`.

## 🌐 Real-World Applications

The pattern of searching in a sorted 2D structure, or conceptually flattening it for efficient search, is quite common:

1.  **Database Indexing**: Many databases use multi-dimensional indexes (like B-trees or k-d trees) where data is sorted across multiple dimensions. Efficiently querying such data often involves logic similar to searching a 2D sorted matrix.
2.  **Geospatial Data**: In mapping applications or geographical information systems (GIS), data points (e.g., locations, sensor readings) might be stored in a grid-like structure, sorted by latitude and longitude. Searching for specific data points within a bounding box or near a coordinate can utilize these principles.
3.  **Configuration Tables/Lookup Tables**: Systems that rely on large lookup tables (e.g., tax rates based on income and deductions, pricing tiers based on quantity and customer type) might store this data in a sorted matrix format. Efficiently finding the correct value requires rapid lookups.
4.  **Game Development**: Pathfinding algorithms or collision detection in grid-based games can sometimes leverage sorted grid properties for faster lookups of terrain types or object positions.
5.  **Search Engines (Simplified)**: While real search engines are far more complex, the fundamental idea of quickly narrowing down results within vast, indexed (and thus sorted) datasets is at their core. Imagine searching a sorted index where keywords are rows and document IDs are columns.
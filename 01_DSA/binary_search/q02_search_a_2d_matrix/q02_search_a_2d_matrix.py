"""
Challenge: q02_search_a_2d_matrix
Difficulty: Medium
Link: https://leetcode.com/problems/search-a-2d-matrix/

Problem:
Search target in 2D sorted matrix.
"""

# --- STARTER TEMPLATE FOR USER ---
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---`
    *   `# Time Complexity: O(m * n)`
    *   `# Space Complexity: O(1)`
    *   `def search_matrix_naive(matrix: list[list[int]], target: int) -> bool:`
    *   `# --- APPROACH 2: Optimal (Binary Search) ---`
    *   `# Time Complexity: O(log(m * n))`
    *   `# Space Complexity: O(1)`
    *   `def search_matrix_optimal(matrix: list[list[int]], target: int) -> bool:`
    *   `# --- APPROACH 3: Secondary Language (Java Variant) ---`
    *   `""" ... """`

    *   Wait, does "Search target in 2D sorted matrix" mean LeetCode 74 (fully sorted) or LeetCode 240 (rows sorted, cols sorted)?
    *   The starter code name `search_matrix` and the prompt `binary_search` usually imply the fully sorted one (LeetCode 74), as that's the classic binary search application for 2D. If it were LeetCode 240, it's usually called `search_matrix_ii` and uses a "Staircase Search" $O(m+n)$. Given the topic `binary_search`, I will implement the $O(\log(m \times n))$ version.

    *   Naive: $O(m \times n)$.
    *   Optimal: $O(\log(m \times n))$.
    *   Java: Matching logic.# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(m * n)
# Space Complexity: O(1)
# This approach iterates through every element of the 2D matrix sequentially to check if the target exists.
def search_matrix_naive(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    
    rows = len(matrix)
    cols = len(matrix[0])
    
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == target:
                return True
    return False

# --- APPROACH 2: Optimal (Binary Search) ---
# Time Complexity: O(log(m * n))
# Space Complexity: O(1)
# Since the matrix is sorted such that the first integer of each row is greater than the last integer of the previous row, 
# the entire matrix can be treated as a single sorted 1D array. We map the 1D index 'mid' back to 2D coordinates 
# using row = mid // cols and col = mid % cols. This is optimal because it leverages the full sorting property 
# of the matrix to achieve logarithmic time complexity.
def search_matrix_optimal(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    
    rows = len(matrix)
    cols = len(matrix[0])
    
    low = 0
    high = (rows * cols) - 1
    
    while low <= high:
        mid = (low + high) // 2
        # Map 1D index to 2D coordinates
        mid_val = matrix[mid // cols][mid % cols]
        
        if mid_val == target:
            return True
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return False

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package binary_search;

public class SearchA2dMatrix {
    /**
     * Searches for a target value in a 2D sorted matrix.
     * Time Complexity: O(log(m * n))
     * Space Complexity: O(1)
     */
    public boolean searchMatrix(int[][] matrix, int target) {
        if (matrix == null || matrix.length == 0 || matrix[0].length == 0) {
            return false;
        }
        
        int rows = matrix.length;
        int cols = matrix[0].length;
        
        int low = 0;
        int high = (rows * cols) - 1;
        
        while (low <= high) {
            int mid = low + (high - low) / 2;
            // Coordinate mapping: 1D index to 2D [row][col]
            int midVal = matrix[mid / cols][mid % cols];
            
            if (midVal == target) {
                return true;
            } else if (midVal < target) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        
        return false;
    }

    public static void main(String[] args) {
        SearchA2dMatrix solution = new SearchA2dMatrix();
        int[][] matrix = {
            {1, 3, 5, 7},
            {10, 11, 16, 20},
            {23, 30, 34, 60}
        };
        System.out.println(solution.searchMatrix(matrix, 3));  // Output: true
        System.out.println(solution.searchMatrix(matrix, 13)); // Output: false
    }
}
"""

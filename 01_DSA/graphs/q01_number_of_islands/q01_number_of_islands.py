"""
Challenge: q01_number_of_islands
Difficulty: Medium
Link: https://leetcode.com/problems/number-of-islands/

Problem:
Given a 2D grid of '1's (land) and '0's (water), return the number of islands.
"""

# --- STARTER TEMPLATE FOR USER ---
def num_islands(grid: list[list[str]]) -> int:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---`
    *   `# Time Complexity: ...`
    *   `# Space Complexity: ...`
    *   `def num_islands_naive(grid: list[list[str]]) -> int:`
    *   `# --- APPROACH 2: Optimal (In-place DFS) ---`
    *   `# Time Complexity: ...`
    *   `# Space Complexity: ...`
    *   `def num_islands_optimal(grid: list[list[str]]) -> int:`
    *   `# --- APPROACH 3: Secondary Language (Java Variant) ---`
    *   `""" [Java Code] """`

    *   Recursive DFS for Approach 1 with `visited = set()`.
    *   Recursive DFS for Approach 2 with `grid[r][c] = '0'`.
    *   Java code needs to handle `char[][]`.

    *   Approach 1 Space: $O(M \times N)$ for visited set + $O(M \times N)$ for recursion.
    *   Approach 2 Space: $O(M \times N)$ for recursion.
    *   Wait, a "Naive" approach might be something like trying to find all connected components using a disjoint set union (DSU), but DSU is often considered an alternative, not necessarily naive. Or maybe just the explicit visited set. Let's go with the explicit visited set for Approach 1.# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(M * N)
# Space Complexity: O(M * N)
# This approach uses a recursive Depth-First Search (DFS) to traverse the grid. It utilizes an explicit 'visited' set to keep track of the coordinates already processed, ensuring that each cell is visited at most once. While functionally correct, it consumes additional memory for the set compared to an in-place modification.
def num_islands_naive(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    visited = set()
    island_count = 0

    def dfs(r, c):
        # Base case: boundary check, water check, or already visited
        if (r < 0 or r >= rows or c < 0 or c >= cols or 
            grid[r][c] == '0' or (r, c) in visited):
            return
        
        visited.add((r, c))
        # Visit 4-directional neighbors
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in visited:
                island_count += 1
                dfs(r, c)
                
    return island_count

# --- APPROACH 2: Optimal (In-place DFS) ---
# Time Complexity: O(M * N)
# Space Complexity: O(M * N)
# This approach is optimal because it achieves the theoretical lower bound for time complexity (visiting every cell once). It improves upon the naive approach by modifying the grid in-place (sinking the islands by changing '1' to '0'), which eliminates the need for an auxiliary 'visited' set. The space complexity remains O(M * N) in the worst case due to the recursion stack (e.g., in a grid full of land).
def num_islands_optimal(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    island_count = 0

    def dfs(r, c):
        # Base case: boundary check or water ('0')
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
            return
        
        # Mark current cell as visited by sinking it
        grid[r][c] = '0'
        
        # Traverse all 4 directions
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                island_count += 1
                dfs(r, c)
                
    return island_count

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

public class NumberOfIslands {
    /**
     * Computes the number of islands in a 2D grid.
     * Time Complexity: O(M * N) where M is rows and N is cols.
     * Space Complexity: O(M * N) due to recursion stack.
     */
    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) {
            return 0;
        }

        int rows = grid.length;
        int cols = grid[0].length;
        int islandCount = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == '1') {
                    islandCount++;
                    dfs(grid, r, c);
                }
            }
        }
        return islandCount;
    }

    private void dfs(char[][] grid, int r, int c) {
        int rows = grid.length;
        int cols = grid[0].length;

        // Boundary and water checks
        if (r < 0 || c < 0 || r >= rows || c >= cols || grid[r][c] == '0') {
            return;
        }

        // Mark as visited
        grid[r][c] = '0';

        // Recurse in 4 directions
        dfs(grid, r + 1, c);
        dfs(grid, r - 1, c);
        dfs(grid, r, c + 1);
        dfs(grid, r, c - 1);
    }

    public static void main(String[] args) {
        NumberOfIslands solution = new NumberOfIslands();
        char[][] grid = {
            {'1', '1', '0', '0', '0'},
            {'1', '1', '0', '0', '0'},
            {'0', '0', '1', '0', '0'},
            {'0', '0', '0', '1', '1'}
        };
        System.out.println("Number of islands: " + solution.numIslands(grid)); // Expected: 3
    }
}
"""

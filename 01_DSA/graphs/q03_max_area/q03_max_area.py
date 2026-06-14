"""
Challenge: q03_max_area
Difficulty: Medium
Link: https://leetcode.com/problems/max-area-of-island/

Problem:
Max area island.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(R * C)
# Space Complexity: O(R * C)
# This approach uses a separate 'visited' set to keep track of explored land cells, 
# ensuring the original input grid remains immutable. It uses Depth First Search (DFS) 
# to explore each island fully.
from typing import List

def solve_naive(grid: List[List[int]]) -> int:
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    visited = set()
    
    def dfs(r, c):
        # Boundary checks, water check, and visited check
        if (r < 0 or r >= rows or c < 0 or c >= cols or 
            grid[r][c] == 0 or (r, c) in visited):
            return 0
        
        visited.add((r, c))
        # Explore all 4 directions and sum the area
        return (1 + dfs(r + 1, c) + 
                    dfs(r - 1, c) + 
                    dfs(r, c + 1) + 
                    dfs(r, c - 1))

    max_area = 0
    for r in range(rows):
        for c in range(cols):
            # Start a DFS if we find land that hasn't been visited
            if grid[r][c] == 1 and (r, c) not in visited:
                max_area = max(max_area, dfs(r, c))
                
    return max_area

# --- APPROACH 2: Optimal (In-place DFS) ---
# Time Complexity: O(R * C)
# Space Complexity: O(R * C)
# This approach is optimal as it minimizes auxiliary space by modifying the input grid 
# directly (often called 'sinking' the island). By flipping 1s to 0s as we visit them, 
# we eliminate the need for a separate visited set. The time complexity remains linear 
# relative to the number of cells, and the space complexity is determined by the 
# recursion stack in the worst case (an island covering the entire grid).
from typing import List

def solve_optimal(grid: List[List[int]]) -> int:
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    
    def dfs(r, c):
        # Base case: boundary check or cell is water (0)
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
            return 0
        
        # Sink the land: mark as visited by changing 1 to 0
        grid[r][c] = 0
        
        # Sum the current cell and the result of recursive calls to neighbors
        return (1 + dfs(r + 1, c) + 
                    dfs(r - 1, c) + 
                    dfs(r, c + 1) + 
                    dfs(r, c - 1))

    max_area = 0
    for r in range(rows):
        for c in range(cols):
            # Only start DFS if the cell is land
            if grid[r][c] == 1:
                max_area = max(max_area, dfs(r, c))
                
    return max_area

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

public class MaxArea {
    /**
     * Computes the maximum area of an island in a 2D binary grid.
     * Time Complexity: O(R * C)
     * Space Complexity: O(R * C) due to recursion stack.
     */
    public int maxAreaOfIsland(int[][] grid) {
        if (grid == null || grid.length == 0) {
            return 0;
        }
        
        int rows = grid.length;
        int cols = grid[0].length;
        int maxArea = 0;
        
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == 1) {
                    maxArea = Math.max(maxArea, dfs(grid, r, c));
                }
            }
        }
        
        return maxArea;
    }
    
    private int dfs(int[][] grid, int r, int c) {
        // Boundary and water checks
        if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length || grid[r][c] == 0) {
            return 0;
        }
        
        // Mark as visited (sink the island)
        grid[r][c] = 0;
        
        // Recursively visit all 4 directions
        int area = 1;
        area += dfs(grid, r + 1, c);
        area += dfs(grid, r - 1, c);
        area += dfs(grid, r, c + 1);
        area += dfs(grid, r, c - 1);
        
        return area;
    }

    public static void main(String[] args) {
        MaxArea solver = new MaxArea();
        int[][] grid = {
            {0,0,1,0,0,0,0,1,0,0,0,0,0},
            {0,0,0,0,0,0,0,1,1,1,0,0,0},
            {0,1,1,0,1,0,0,1,0,0,0,0,0},
            {0,1,0,0,1,0,0,1,1,0,0,0,0},
            {0,1,0,0,1,0,0,1,0,0,0,0,0},
            {0,0,0,0,0,0,0,0,0,0,1,1,0},
            {0,0,0,0,0,0,0,0,0,0,1,1,0},
            {0,0,0,0,0,0,0,0,0,0,0,0,0}
        };
        System.out.println("Max Area: " + solver.maxAreaOfIsland(grid)); // Expected: 6
    }
}
"""

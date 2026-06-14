"""
Challenge: q04_pacific_atlantic
Difficulty: Medium
Link: https://leetcode.com/problems/pacific-atlantic-water-flow/

Problem:
Water flow maps.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O((M * N)^2)
# Space Complexity: O(M * N)
# This approach iterates through every single cell in the grid and performs two separate 
# Depth-First Searches (DFS) to check if the cell can reach both the Pacific and Atlantic oceans.
# For each cell, the worst-case scenario is visiting all other cells in the grid.
def solve_naive(heights):
    if not heights or not heights[0]:
        return []
    
    rows, cols = len(heights), len(heights[0])
    
    def can_reach(r, c, target_ocean):
        visited = set()
        stack = [(r, c)]
        visited.add((r, c))
        
        while stack:
            curr_r, curr_c = stack.pop()
            
            # Check if current cell touches the target ocean
            if target_ocean == 'Pacific':
                if curr_r == 0 or curr_c == 0:
                    return True
            else: # Atlantic
                if curr_r == rows - 1 or curr_c == cols - 1:
                    return True
            
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    # Water flows from higher/equal to lower/equal
                    if heights[nr][nc] <= heights[curr_r][curr_c]:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
        return False

    result = []
    for r in range(rows):
        for c in range(cols):
            if can_reach(r, c, 'Pacific') and can_reach(r, c, 'Atlantic'):
                result.append([r, c])
    return result

# --- APPROACH 2: Optimal (Multi-Source DFS/BFS) ---
# Time Complexity: O(M * N)
# Space Complexity: O(M * N)
# This approach reverses the problem: instead of checking if each cell can reach the ocean, 
# we start from the ocean borders and find all cells that can "flow" backwards (upwards) 
# from the ocean. We maintain two boolean matrices to track reachability for each ocean.
# The intersection of these two matrices gives the cells that can reach both.
# This is optimal because each cell is visited at most twice (once per ocean).
def solve_optimal(heights):
    if not heights or not heights[0]:
        return []
    
    rows, cols = len(heights), len(heights[0])
    pacific_reachable = [[False for _ in range(cols)] for _ in range(rows)]
    atlantic_reachable = [[False for _ in range(cols)] for _ in range(rows)]
    
    def dfs(r, c, reachable):
        reachable[r][c] = True
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            # Water flows "up" from ocean to mountain: height[nr][nc] >= height[r][c]
            if (0 <= nr < rows and 0 <= nc < cols and 
                not reachable[nr][nc] and heights[nr][nc] >= heights[r][c]):
                dfs(nr, nc, reachable)

    # Start DFS from Pacific borders (top row and left column)
    for c in range(cols):
        dfs(0, c, pacific_reachable)
    for r in range(rows):
        dfs(r, 0, pacific_reachable)
        
    # Start DFS from Atlantic borders (bottom row and right column)
    for c in range(cols):
        dfs(rows - 1, c, atlantic_reachable)
    for r in range(rows):
        dfs(r, cols - 1, atlantic_reachable)
        
    # Intersection of both reachable sets
    result = []
    for r in range(rows):
        for c in range(cols):
            if pacific_reachable[r][c] and atlantic_reachable[r][c]:
                result.append([r, c])
    return result

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

import java.util.*;

public class PacificAtlantic {
    public List<List<Integer>> pacificAtlantic(int[][] heights) {
        List<List<Integer>> result = new ArrayList<>();
        if (heights == null || heights.length == 0 || heights[0].length == 0) {
            return result;
        }

        int rows = heights.length;
        int cols = heights[0].length;
        boolean[][] pacific = new boolean[rows][cols];
        boolean[][] atlantic = new boolean[rows][cols];

        // Process left and right borders
        for (int r = 0; r < rows; r++) {
            dfs(heights, r, 0, pacific, heights[r][0]);
            dfs(heights, r, cols - 1, atlantic, heights[r][cols - 1]);
        }

        // Process top and bottom borders
        for (int c = 0; c < cols; c++) {
            dfs(heights, 0, c, pacific, heights[0][c]);
            dfs(heights, rows - 1, c, atlantic, heights[rows - 1][c]);
        }

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (pacific[r][c] && atlantic[r][c]) {
                    result.add(Arrays.asList(r, c));
                }
            }
        }

        return result;
    }

    private void dfs(int[][] heights, int r, int c, boolean[][] reachable, int prevHeight) {
        int rows = heights.length;
        int cols = heights[0].length;

        if (r < 0 || r >= rows || c < 0 || c >= cols || 
            reachable[r][c] || heights[r][c] < prevHeight) {
            return;
        }

        reachable[r][c] = true;
        dfs(heights, r + 1, c, reachable, heights[r][c]);
        dfs(heights, r - 1, c, reachable, heights[r][c]);
        dfs(heights, r, c + 1, reachable, heights[r][c]);
        dfs(heights, r, c - 1, reachable, heights[r][c]);
    }
}
"""

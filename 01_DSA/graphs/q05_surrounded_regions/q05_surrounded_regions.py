"""
Challenge: q05_surrounded_regions
Difficulty: Medium
Link: https://leetcode.com/problems/surrounded-regions/

Problem:
Capture border-trapped regions.
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
# This approach iterates through every cell in the grid. For every 'O' found, it performs a separate 
# Depth First Search (DFS) to determine if that specific 'O' can reach any cell on the border of the board.
# If the DFS completes without reaching the border, the cell is marked for flipping. 
# This is inefficient because it re-traverses the same connected components many times.
def solve_naive(board: list[list[str]]) -> None:
    if not board or not board[0]:
        return

    rows, cols = len(board), len(board[0])
    to_flip = []

    def can_reach_border(r, c, visited):
        # If we reached the border, this 'O' is not surrounded
        if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
            return True
        
        visited.add((r, c))
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == 'O' and (nr, nc) not in visited:
                if can_reach_border(nr, nc, visited):
                    return True
        return False

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'O':
                # Use a fresh visited set for every cell to check its connectivity to border
                if not can_reach_border(r, c, set()):
                    to_flip.append((r, c))

    for r, c in to_flip:
        board[r][c] = 'X'

# --- APPROACH 2: Optimal (Border-Based DFS/BFS) ---
# Time Complexity: O(M * N)
# Space Complexity: O(M * N)
# This approach identifies "safe" 'O' cells—those connected to the border—first. 
# We start a traversal from all 'O's located on the four boundaries. Any 'O' reachable 
# from the border is marked as 'S' (safe). 
# After marking all safe cells, any remaining 'O' must be surrounded by 'X's.
# Finally, we iterate through the board: 'O' becomes 'X', and 'S' reverts to 'O'.
# This is optimal because each cell is visited a constant number of times.
def solve_optimal(board: list[list[str]]) -> None:
    if not board or not board[0]:
        return

    rows, cols = len(board), len(board[0])

    def mark_safe(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != 'O':
            return
        # Mark as safe
        board[r][c] = 'S'
        # Explore neighbors
        mark_safe(r + 1, c)
        mark_safe(r - 1, c)
        mark_safe(r, c + 1)
        mark_safe(r, c - 1)

    # Step 1: Mark all 'O's on the top and bottom borders and their connected components
    for c in range(cols):
        mark_safe(0, c)
        mark_safe(rows - 1, c)

    # Step 2: Mark all 'O's on the left and right borders and their connected components
    for r in range(rows):
        mark_safe(r, 0)
        mark_safe(r, cols - 1)

    # Step 3: Process the board
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'O':
                board[r][c] = 'X'  # Surrounded
            elif board[r][c] == 'S':
                board[r][c] = 'O'  # Safe, revert back

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

import java.util.*;

public class SurroundedRegions {
    public void solve(char[][] board) {
        if (board == null || board.length == 0) {
            return;
        }
        
        int rows = board.length;
        int cols = board[0].length;
        
        // Mark boundary-connected 'O's
        for (int i = 0; i < rows; i++) {
            dfs(board, i, 0);
            dfs(board, i, cols - 1);
        }
        for (int j = 0; j < cols; j++) {
            dfs(board, 0, j);
            dfs(board, rows - 1, j);
        }
        
        // Final pass to flip cells
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (board[i][j] == 'O') {
                    board[i][j] = 'X';
                } else if (board[i][j] == 'S') {
                    board[i][j] = 'O';
                }
            }
        }
    }
    
    private void dfs(char[][] board, int r, int c) {
        if (r < 0 || r >= board.length || c < 0 || c >= board[0].length || board[r][c] != 'O') {
            return;
        }
        
        board[r][c] = 'S'; // Mark as safe
        dfs(board, r + 1, c);
        dfs(board, r - 1, c);
        dfs(board, r, c + 1);
        dfs(board, r, c - 1);
    }
}
"""

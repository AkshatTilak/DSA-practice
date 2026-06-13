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

def num_islands_optimal(grid):
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])
    visited = set()
    islands = 0
    
    def dfs(r, c):
        if r<0 or r>=rows or c<0 or c>=cols or grid[r][c]=='0' or (r,c) in visited:
            return
        visited.add((r,c))
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            dfs(r+dr, c+dc)
            
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r,c) not in visited:
                dfs(r, c)
                islands += 1
    return islands

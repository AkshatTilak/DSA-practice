"""
Challenge: q06_rotting_oranges
Difficulty: Medium
Link: https://leetcode.com/problems/rotting-oranges/

Problem:
Multi-source BFS decay.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O((R * C)^2)
# Space Complexity: O(R * C)
# The naive approach repeatedly scans the entire grid in each time step. 
# It identifies all fresh oranges adjacent to any rotten orange and marks them for rotting.
# This process repeats until no more oranges can rot.
from typing import List

def solve_naive(grid: List[List[int]]) -> int:
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    time = 0
    
    while True:
        # Find all fresh oranges that are adjacent to a rotten one
        to_rot = []
        fresh_count = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1:
                    fresh_count += 1
                    # Check neighbors
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 2:
                            to_rot.append((r, c))
                            break
        
        # If no fresh oranges are left, we are done
        if fresh_count == 0:
            return time
        
        # If no oranges can be rotted further but fresh ones still exist, return -1
        if not to_rot:
            return -1 if fresh_count > 0 else time
        
        # Rot the identified oranges
        for r, c in to_rot:
            grid[r][c] = 2
        
        time += 1

# --- APPROACH 2: Optimal (Multi-source BFS) ---
# Time Complexity: O(R * C)
# Space Complexity: O(R * C)
# This approach uses a Multi-source Breadth-First Search (BFS). 
# We start by adding all initially rotten oranges to a queue. 
# In each step, we process the current "layer" of rotten oranges, spreading the rot to 
# adjacent fresh oranges. This ensures that we find the minimum time required.
# BFS is optimal here because it explores all nodes at distance 't' before moving to 't+1'.
from collections import deque
from typing import List

def solve_optimal(grid: List[List[int]]) -> int:
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_oranges = 0
    
    # Step 1: Initialize queue with all rotten oranges and count fresh ones
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh_oranges += 1
                
    if fresh_oranges == 0:
        return 0
    
    minutes = 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    # Step 2: Multi-source BFS
    while queue and fresh_oranges > 0:
        minutes += 1
        # Process all oranges that rotted in the previous minute
        for _ in range(len(queue)):
            r, c = queue.popleft()
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                # If neighbor is within bounds and is a fresh orange
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2 # Mark as rotten
                    fresh_oranges -= 1
                    queue.append((nr, nc))
                    
    return minutes if fresh_oranges == 0 else -1

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

import java.util.*;

public class RottingOranges {
    public int orangesRotting(int[][] grid) {
        if (grid == null || grid.length == 0) return 0;
        
        int rows = grid.length;
        int cols = grid[0].length;
        Queue<int[]> queue = new LinkedList<>();
        int freshOranges = 0;
        
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == 2) {
                    queue.offer(new int[]{r, c});
                } else if (grid[r][c] == 1) {
                    freshOranges++;
                }
            }
        }
        
        if (freshOranges == 0) return 0;
        
        int minutes = 0;
        int[][] directions = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};
        
        while (!queue.isEmpty() && freshOranges > 0) {
            minutes++;
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                int[] curr = queue.poll();
                for (int[] dir : directions) {
                    int nr = curr[0] + dir[0];
                    int nc = curr[1] + dir[1];
                    
                    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 1) {
                        grid[nr][nc] = 2;
                        freshOranges--;
                        queue.offer(new int[]{nr, nc});
                    }
                }
            }
        }
        
        return freshOranges == 0 ? minutes : -1;
    }
}
"""

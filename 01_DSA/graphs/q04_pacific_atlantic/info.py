INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/pacific-atlantic-water-flow/',
    'description': 'Water flow maps.',
    'groups': ['Graph', 'Matrix'],
    'readme_content': """# Pacific Atlantic Water Flow

## 🌊 Overview & Problem Explanation

The **Pacific Atlantic Water Flow** problem asks us to identify all grid cells from which water can flow to **both** the Pacific Ocean and the Atlantic Ocean.

### The Scenario
Imagine a rectangular island represented by a 2D grid of heights. 
- The **Pacific Ocean** touches the **top edge** and the **left edge** of the island.
- The **Atlantic Ocean** touches the **bottom edge** and the **right edge** of the island.

### The Rule of Flow
Water flows from a cell to an adjacent cell (up, down, left, right) **if and only if** the adjacent cell's height is **less than or equal to** the current cell's height.

### Goal
Find all coordinates `(r, c)` such that water starting at that cell can reach both the Pacific and Atlantic oceans.

### Constraints & Edge Cases
- **Grid Dimensions:** $m \times n$ where $1 \le m, n \le 200$.
- **Height Values:** $0 \le \text{height} \le 10^5$.
- **Edge Cases:**
    - A $1 \times 1$ grid: The single cell touches both oceans.
    - A grid with uniform height: All cells can flow to both oceans.
    - A "mountain" in the center: Only the peak might reach both, or none if it's blocked.

---

## 🧠 Core Concepts & Data Structures

### 1. The "Reverse Thinking" Pattern
The naive approach is to start at every single cell and see if you can reach both oceans. However, this results in redundant calculations and poor performance.

The **optimal insight** is to reverse the flow: **Instead of asking "Can this cell reach the ocean?", we ask "Which cells can the ocean reach?"**
- We start from the ocean boundaries.
- We "flow" uphill (move to an adjacent cell only if its height is $\ge$ the current cell).
- Any cell reachable from the Pacific boundary is marked as `pacific_reachable`.
- Any cell reachable from the Atlantic boundary is marked as `atlantic_reachable`.

### 2. Depth-First Search (DFS) / Breadth-First Search (BFS)
Since we are traversing a graph (the grid), DFS or BFS is ideal. 
- **Why DFS?** It is often simpler to implement recursively for reachability problems on grids.
- **Why BFS?** It can be used if we need the shortest path, but here we only care about connectivity.

### 3. Visited Sets/Matrices
To prevent infinite loops (cycles) and redundant work, we maintain two boolean matrices (or sets) to track which cells have already been "claimed" by the Pacific or Atlantic oceans.

---

## 🛠️ Step-by-Step Logic

### Naive Approach (Brute Force)
1. For every cell $(r, c)$ in the grid:
   - Run a DFS to see if a path exists to the top/left edge.
   - Run a DFS to see if a path exists to the bottom/right edge.
2. If both are true, add $(r, c)$ to the result.
- **Complexity:** $O((m \cdot n)^2)$ — This is too slow for a $200 \times 200$ grid.

### Optimal Approach (Multi-Source Reachability)
1. **Initialize** two boolean matrices: `pacific_reachable` and `atlantic_reachable`, both of size $m \times n$, initialized to `False`.
2. **Pacific Start Points:** 
   - For every cell in the **top row** and **left column**, trigger a DFS.
   - During DFS, mark cells as `True` in `pacific_reachable` if they are $\ge$ the previous cell.
3. **Atlantic Start Points:**
   - For every cell in the **bottom row** and **right column**, trigger a DFS.
   - During DFS, mark cells as `True` in `atlantic_reachable` if they are $\ge$ the previous cell.
4. **Find Intersection:**
   - Iterate through every cell $(r, c)$. If `pacific_reachable[r][c]` AND `atlantic_reachable[r][c]` are both `True`, add that cell to the final list.

### Dry Run Example
**Input Grid:**
```
[1, 2]
[2, 1]
```
1. **Pacific DFS (Top/Left):**
   - Start (0,0) height 1 $\rightarrow$ Mark Pacific. Check neighbor (0,1) height 2 (2 $\ge$ 1) $\rightarrow$ Mark Pacific. Check neighbor (1,0) height 2 (2 $\ge$ 1) $\rightarrow$ Mark Pacific.
   - Result: All cells except (1,1) are Pacific reachable.
2. **Atlantic DFS (Bottom/Right):**
   - Start (1,1) height 1 $\rightarrow$ Mark Atlantic. Check neighbor (1,0) height 2 (2 $\ge$ 1) $\rightarrow$ Mark Atlantic. Check neighbor (0,1) height 2 (2 $\ge$ 1) $\rightarrow$ Mark Atlantic.
   - Result: All cells except (0,0) are Atlantic reachable.
3. **Intersection:**
   - (0,1) and (1,0) are marked in both.
   - **Output:** `[[0, 1], [1, 0]]`

---

## 💻 Implementation

```python
from typing import List

def solve_optimal(heights: List[List[int]]) -> List[List[int]]:
    if not heights or not heights[0]:
        return []

    rows, cols = len(heights), len(heights[0])
    pacific_reachable = [[False for _ in range(cols)] for _ in range(rows)]
    atlantic_reachable = [[False for _ in range(cols)] for _ in range(rows)]

    def dfs(r, c, reachable, prev_height):
        # 1. Bounds check
        # 2. Already visited check
        # 3. Height check (must be flowing "uphill" from ocean to peak)
        if (r < 0 or r >= rows or c < 0 or c >= cols or 
            reachable[r][c] or heights[r][c] < prev_height):
            return
        
        reachable[r][c] = True
        
        # Visit neighbors
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dfs(r + dr, c + dc, reachable, heights[r][c])

    # Step 1: Start DFS from Pacific boundaries (Top and Left)
    for i in range(rows):
        dfs(i, 0, pacific_reachable, heights[i][0]) # Left edge
    for j in range(cols):
        dfs(0, j, pacific_reachable, heights[0][j]) # Top edge

    # Step 2: Start DFS from Atlantic boundaries (Bottom and Right)
    for i in range(rows):
        dfs(i, cols - 1, atlantic_reachable, heights[i][cols-1]) # Right edge
    for j in range(cols):
        dfs(rows - 1, j, atlantic_reachable, heights[rows-1][j]) # Bottom edge

    # Step 3: Intersection of both reachability maps
    result = []
    for r in range(rows):
        for c in range(cols):
            if pacific_reachable[r][c] and atlantic_reachable[r][c]:
                result.append([r, c])
                
    return result
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O((M \cdot N)^2)$ | $O(M \cdot N)$ | Every cell starts a full traversal of the grid. |
| **Optimal (DFS)** | $O(M \cdot N)$ | $O(M \cdot N)$ | Each cell is visited a maximum of twice (once per ocean). Space is used by the reachability matrices and recursion stack. |

- **Time Complexity $O(M \cdot N)$**: We perform two passes of DFS. In the worst case, every cell is visited during the Pacific DFS and again during the Atlantic DFS.
- **Space Complexity $O(M \cdot N)$**: We maintain two $M \times N$ boolean grids. The recursion depth of DFS can also go up to $M \times N$ in the worst case (a long winding path).

---

## 🌍 Real-World Applications

This "Reverse Reachability" pattern on a grid is widely used in several domains:

1. **Hydrology & Geography**: Predicting flood zones. If you know where the sea level is, you can determine which low-lying land will be submerged based on elevation maps.
2. **Network Routing**: Determining if a node in a network can communicate with two different gateways or servers.
3. **Image Processing (Seed Fill/Flood Fill)**: The logic is identical to the "Bucket Fill" tool in paint applications, where a color spreads to all connected pixels of the same color.
4. **Game AI**: Pathfinding and "Influence Maps" where an entity needs to know if a location is accessible from multiple strategic points (e.g., can a unit be flanked by two different army bases?).""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

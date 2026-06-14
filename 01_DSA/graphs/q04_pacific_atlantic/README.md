# Pacific Atlantic Water Flow

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
4. **Game AI**: Pathfinding and "Influence Maps" where an entity needs to know if a location is accessible from multiple strategic points (e.g., can a unit be flanked by two different army bases?).
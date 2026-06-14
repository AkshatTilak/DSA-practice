INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/rotting-oranges/',
    'description': 'Multi-source BFS decay.',
    'groups': ['Graph', 'Matrix'],
    'readme_content': """# Rotting Oranges

## 1. Overview & Problem Explanation

The **Rotting Oranges** problem is a classic grid-based simulation that tests your ability to handle simultaneous propagation. 

### The Scenario
You are given a 2D grid representing a warehouse of oranges:
- `0`: Empty cell.
- `1`: A fresh orange.
- `2`: A rotten orange.

Every minute, any fresh orange that is **4-directionally adjacent** (up, down, left, right) to a rotten orange becomes rotten itself. We need to determine the **minimum number of minutes** that must elapse until no fresh oranges remain. If it is impossible to rot all fresh oranges (e.g., some are blocked by empty spaces), the function should return `-1`.

### Inputs & Outputs
- **Input**: A 2D integer array `grid` of size $m \times n$.
- **Output**: An integer representing the total minutes elapsed, or `-1` if impossible.

### Constraints & Edge Cases
- **Grid Size**: Typically up to $10 \times 10$ in basic versions, but can be larger. The algorithm must be efficient.
- **No Fresh Oranges**: If there are no fresh oranges at $t=0$, the time taken is `0`.
- **Impossible Reach**: If a fresh orange is surrounded by empty cells (`0`), it can never rot.
- **All Empty**: A grid containing only `0`s should return `0`.

---

## 2. Core Concepts & Data Structures

### Multi-Source Breadth-First Search (BFS)
The core of this problem is finding the "shortest time" for a state to spread. In graph theory, the shortest path in an unweighted graph is best found using **Breadth-First Search (BFS)**.

**Why BFS instead of DFS?**
- **DFS (Depth-First Search)** explores one path as deep as possible. In this problem, DFS would find *one* way for the rot to spread, but not necessarily the *fastest* way.
- **BFS** explores in "waves" or "layers." Every node at distance 1 is visited, then every node at distance 2, and so on. This mirrors the minute-by-minute spread of the rot perfectly.

**The "Multi-Source" Twist**
Standard BFS starts from a single source. However, in this problem, multiple oranges can be rotten simultaneously at the start. If we ran a separate BFS for every rotten orange, we would be doing redundant work. Instead, we use **Multi-Source BFS**:
1. Initialize the queue with **all** initially rotten oranges.
2. Process them all as "Layer 0."
3. The spread from all these sources happens concurrently, ensuring we find the global minimum time.

---

## 3. Step-by-Step Logic

### The Optimal Strategy

#### Step 1: Initialization
- Create a `queue` to hold the coordinates $(r, c)$ of rotten oranges.
- Initialize a `fresh_count` variable to keep track of how many fresh oranges exist.
- Iterate through the entire grid:
    - If `grid[r][c] == 2`, add $(r, c)$ to the queue.
    - If `grid[r][c] == 1`, increment `fresh_count`.

#### Step 2: The BFS Process
While the queue is not empty and `fresh_count > 0`:
1. **Level Processing**: Capture the current size of the queue. This represents all oranges that turned rotten in the *previous* minute.
2. **Expansion**: For each rotten orange in the current level:
    - Check its 4 neighbors (Up, Down, Left, Right).
    - If a neighbor is within bounds AND is a fresh orange (`1`):
        - Mark the neighbor as rotten (`grid[r][c] = 2`).
        - Decrement `fresh_count`.
        - Add the neighbor's coordinates to the queue for the next minute's expansion.
3. **Time Increment**: After processing the entire level, increment the `minutes` counter.

#### Step 3: Final Verification
- Once the queue is empty, check `fresh_count`.
- If `fresh_count == 0`, return the total `minutes`.
- If `fresh_count > 0`, it means some oranges were unreachable; return `-1`.

### Dry Run Example
**Input Grid:**
```
[[2, 1, 1],
 [1, 1, 0],
 [0, 1, 1]]
```
1. **Start**: Queue: `[(0,0)]`, Fresh: `6`, Time: `0`.
2. **Minute 1**: 
   - Pop `(0,0)`. Rots `(0,1)` and `(1,0)`.
   - Queue: `[(0,1), (1,0)]`, Fresh: `4`, Time: `1`.
3. **Minute 2**: 
   - Pop `(0,1)` $\rightarrow$ rots `(0,2)`.
   - Pop `(1,0)` $\rightarrow$ rots `(1,1)`.
   - Queue: `[(0,2), (1,1)]`, Fresh: `2`, Time: `2`.
4. **Minute 3**:
   - Pop `(0,2)` $\rightarrow$ no fresh neighbors.
   - Pop `(1,1)` $\rightarrow$ rots `(2,1)`.
   - Queue: `[(2,1)]`, Fresh: `1`, Time: `3`.
5. **Minute 4**:
   - Pop `(2,1)` $\rightarrow$ rots `(2,2)`.
   - Queue: `[(2,2)]`, Fresh: `0`, Time: `4`.
6. **End**: `fresh_count == 0`. Return `4`.

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Multi-Source BFS** | $O(M \times N)$ | $O(M \times N)$ | We visit each cell at most once. The queue can hold up to $M \times N$ elements in the worst case. |

- **Time Complexity**: $O(M \times N)$. We perform one initial pass to count fresh oranges and populate the queue, and then each cell is processed at most once during the BFS expansion.
- **Space Complexity**: $O(M \times N)$. In the worst case (e.g., all oranges start rotten), the queue will store all cells of the grid.

---

## 5. Real-World Applications

The "Multi-Source Decay/Spread" pattern is widely used in software engineering beyond simple coding challenges:

1. **Epidemiology & Viral Modeling**: Simulating how a virus spreads through a population. Each "infected" person acts as a source that can infect neighbors.
2. **Forest Fire Simulation**: Predicting the spread of fire across a terrain based on wind direction and fuel (trees) availability.
3. **Network Broadcasts**: When a router sends a packet to all other nodes in a network (Flooding Algorithm), the packet spreads in a BFS manner from the source.
4. **Image Processing (Flood Fill)**: The "Paint Bucket" tool in Photoshop uses a similar logic to find all connected pixels of the same color and change them to a new color.
5. **Game AI (Pathfinding/Influence Maps)**: Calculating the "influence" or "danger zone" of multiple enemy units on a game map simultaneously.

---

## 6. Implementation

```python
from collections import deque

def solve(grid):
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_count = 0
    
    # 1. Initialize: Find all rotten oranges and count fresh ones
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh_count += 1
    
    # If there are no fresh oranges, return 0 immediately
    if fresh_count == 0:
        return 0
    
    minutes = 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    # 2. Multi-source BFS
    while queue and fresh_count > 0:
        minutes += 1
        # Process current level (current minute)
        for _ in range(len(queue)):
            r, c = queue.popleft()
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                
                # Check bounds and if orange is fresh
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    # Rot the orange
                    grid[nr][nc] = 2
                    fresh_count -= 1
                    queue.append((nr, nc))
    
    # 3. Final check: if fresh oranges remain, return -1
    return minutes if fresh_count == 0 else -1
```""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

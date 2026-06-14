# Number Of Islands

## 1. Overview & Problem Explanation

The **Number of Islands** problem is a classic graph traversal challenge that tests your ability to navigate a 2D grid and identify "connected components."

### The Problem Statement
You are given an `m x n` 2D binary grid which represents a map of `'1'`s (land) and `'0'`s (water). An **island** is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You are tasked with returning the total number of islands present in the grid.

### Visualizing the Problem
Imagine a top-down map of an archipelago. 
- A group of `'1's` touching each other (up, down, left, right) forms a single landmass.
- If a group of `'1's` is completely separated from another group by `'0's`, they are distinct islands.

### Inputs & Outputs
- **Input**: `grid` $\rightarrow$ A list of lists of strings (`list[list[str]]`), where each element is either `'1'` or `'0'`.
- **Output**: `int` $\rightarrow$ The total count of isolated islands.

### Constraints & Edge Cases
- **Grid Dimensions**: The grid can be empty or have dimensions up to $300 \times 300$.
- **Empty Grid**: If the input grid is `[]` or `[[]]`, the result should be `0`.
- **No Land**: A grid consisting entirely of `'0's` should return `0`.
- **All Land**: A grid consisting entirely of `'1's` should return `1` (one giant island).
- **Single Cell Islands**: A single `'1'` surrounded by `'0's` counts as one island.

---

## 2. Core Concepts & Data Structures

### Graph Theory: Connected Components
At its heart, this is a problem of finding the number of **Connected Components** in an undirected graph.
- **Nodes**: Each cell `(r, c)` in the grid is a node.
- **Edges**: An edge exists between two nodes if they are adjacent (North, South, East, West) and both contain the value `'1'`.

### Algorithmic Choice: Depth-First Search (DFS)
To solve this, we use **Depth-First Search (DFS)**. 

**Why DFS?**
When we encounter a piece of land (`'1'`), we want to explore every single connected piece of land associated with that island before we stop. DFS is ideal for this "deep dive" exploration. Once the DFS completes, we know we have visited every cell of that specific island, allowing us to increment our island counter and move on to find the next one.

**Alternative Approaches:**
- **BFS (Breadth-First Search)**: Uses a queue to explore layer-by-layer. It achieves the same time/space complexity.
- **Union-Find (Disjoint Set Union)**: Useful for dynamic connectivity problems, though slightly more complex to implement for a static grid.

---

## 3. Step-by-Step Logic

### The Optimal Strategy
The goal is to iterate through every cell in the grid. When we find a `'1'` that hasn't been visited, we trigger a DFS to "consume" the entire island.

#### Detailed Walkthrough:
1. **Initialize**: Create a `visited` set to keep track of coordinates we have already processed. Initialize an `islands` counter to `0`.
2. **Iterate**: Use a nested loop to visit every cell `(r, c)` in the $M \times N$ grid.
3. **Island Detection**: If `grid[r][c] == '1'` AND `(r, c)` is NOT in the `visited` set:
   - We have found the start of a new island.
   - Increment the `islands` counter by 1.
   - Launch a **DFS** starting from this cell to mark all connected land as visited.
4. **DFS Exploration**:
   - **Base Case**: If the current cell is out of bounds, is water (`'0'`), or has already been visited, stop the recursion.
   - **Marking**: Add the current cell `(r, c)` to the `visited` set.
   - **Recursive Step**: Call the DFS function for the four neighboring directions:
     - Up: `(r - 1, c)`
     - Down: `(r + 1, c)`
     - Left: `(r, c - 1)`
     - Right: `(r, c + 1)`

### Dry Run Example
**Input Grid:**
```text
1 1 0
1 0 0
0 0 1
```
1. Start at `(0,0)`. It's a `'1'`. `islands = 1`.
2. DFS from `(0,0)` $\rightarrow$ visits `(0,1)` and `(1,0)`.
3. All connected `'1's` for the first island are now in `visited`.
4. Loop continues... skips `(0,1)`, `(1,0)`, `(0,2)`, `(1,1)`, `(1,2)`, `(2,0)`, `(2,1)`.
5. Reach `(2,2)`. It's a `'1'` and not visited. `islands = 2`.
6. DFS from `(2,2)` $\rightarrow$ no neighbors are `'1'`.
7. **Final Result: 2**

---

## 4. Implementation

```python
def num_islands(grid: list[list[str]]) -> int:
    if not grid: 
        return 0
    
    rows, cols = len(grid), len(grid[0])
    visited = set()
    islands = 0
    
    def dfs(r, c):
        # 1. Boundary and Validity Checks
        if (r < 0 or r >= rows or 
            c < 0 or c >= cols or 
            grid[r][c] == '0' or 
            (r, c) in visited):
            return
        
        # 2. Mark the current cell as visited
        visited.add((r, c))
        
        # 3. Explore all 4 adjacent directions
        # Directions: Up, Down, Left, Right
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dfs(r + dr, c + dc)
            
    # Traverse the entire grid
    for r in range(rows):
        for c in range(cols):
            # If we find land that hasn't been visited, it's a new island
            if grid[r][c] == '1' and (r, c) not in visited:
                dfs(r, c)
                islands += 1
                
    return islands
```

---

## 5. Complexity Analysis

| Complexity | Notation | Reasoning |
| :--- | :--- | :--- |
| **Time Complexity** | $O(M \times N)$ | We visit every cell in the grid exactly once. Even with DFS, the `visited` set ensures we never process the same cell twice. |
| **Space Complexity** | $O(M \times N)$ | In the worst case (a grid full of land), the `visited` set stores every cell. Additionally, the recursion stack for DFS can go as deep as $M \times N$. |

---

## 6. Real-World Applications

The pattern used to solve "Number of Islands" (Connected Component Labeling) is used extensively in software engineering:

1. **Computer Vision (Blob Detection)**: 
   Used in image processing to detect distinct objects in a binary image (e.g., identifying separate cells in a medical scan or counting components on a circuit board).
   
2. **Social Network Analysis**: 
   Finding "communities" or isolated groups of people in a social graph where an edge represents a friendship.

3. **Network Routing**: 
   Identifying isolated sub-networks (partitions) in a distributed system to detect network failures or split-brain scenarios.

4. **Game Development**: 
   Procedural map generation (e.g., ensuring a generated game world has a main landmass and several smaller islands) or determining reachable areas for a character.
# Surrounded Regions

## 1. Overview & Problem Explanation

The **Surrounded Regions** problem asks us to modify a matrix consisting of characters `'X'` and `'O'`. The goal is to "capture" all regions that are completely surrounded by `'X'`. 

### What does "captured" mean?
A region is captured if it consists of one or more `'O'`s connected 4-directionally (up, down, left, right) that **cannot** reach the boundary of the matrix. If an `'O'` is on the border, or is connected to an `'O'` that is on the border, it is considered "safe" and should not be flipped.

**Input:**
- A 2D grid `board` of size $m \times n$ containing characters `'X'` and `'O'`.

**Output:**
- The same `board` modified in-place where all captured `'O'`s are replaced by `'X'`.

### Constraints & Edge Cases
- **Grid Dimensions:** $m, n$ can range from 1 to 200.
- **Empty Grid:** A grid with 0 rows or columns (though constraints usually guarantee at least 1).
- **No 'O's:** The board consists entirely of `'X'`.
- **All 'O's:** The board consists entirely of `'O'`.
- **Single Row/Column:** In a $1 \times n$ or $m \times 1$ grid, any `'O'` present is technically on the boundary and cannot be captured.

---

## 2. Core Concepts & Data Structures

The fundamental challenge is that it's easier to identify which regions are **not** surrounded than to identify which ones are.

### Algorithmic Pattern: Boundary-First Traversal
Instead of checking every single `'O'` to see if it hits a border (which would be redundant and slow), we use a **Reverse Thinking** approach:
1. **Start at the edges**: Any `'O'` on the border is automatically "safe."
2. **Propagate safety**: Any `'O'` connected to a safe `'O'` is also safe.
3. **Flip the rest**: Any `'O'` that was not marked as safe during the propagation phase must be surrounded.

### Data Structures Used
- **Depth-First Search (DFS) or Breadth-First Search (BFS)**: Used to traverse the connected components of `'O'`s starting from the boundaries.
- **In-place Marking**: To save space, we can temporarily change safe `'O'`s to a placeholder character (like `'#'` or `'T'`) to distinguish them from surrounded `'O'`s.

### Why this is optimal?
By starting from the boundary, we only visit the cells that are guaranteed to survive. This avoids the need to perform a full search for every single cell in the grid, ensuring we visit each cell a constant number of times.

---

## 3. Step-by-Step Logic

### The Optimal Strategy (Boundary DFS)

#### Step 1: Identify Boundary Seeds
Iterate through the first row, last row, first column, and last column. Whenever an `'O'` is encountered, trigger a DFS/BFS to mark it and all its connected `'O'` neighbors as "Safe."

#### Step 2: Propagate Safety (The DFS)
For a given cell `(r, c)`:
1. Check if it is within bounds and is an `'O'`.
2. Change `'O'` $\rightarrow$ `'#'` (marking it as safe).
3. Recursively visit the neighbors (Up, Down, Left, Right).

#### Step 3: Final Transformation
Traverse the entire grid one last time:
- If the cell is `'O'`, it means it was never reached by the boundary DFS $\rightarrow$ **Change to `'X'`**.
- If the cell is `'#'`, it was marked safe $\rightarrow$ **Change back to `'O'`**.

### Dry Run Example
**Input:**
```text
X X X X
X O O X
X X O X
X O X X
```

1. **Boundary Check:** 
   - Bottom row has an `'O'` at `(3, 1)`. Start DFS.
   - `(3, 1)` becomes `'#'`. It has no `'O'` neighbors.
2. **Internal Grid:**
   - The `'O'`s at `(1, 1), (1, 2), (2, 2)` are not connected to any boundary `'O'`. They remain `'O'`.
3. **Final Pass:**
   - `(1, 1), (1, 2), (2, 2)` $\rightarrow$ flipped to `'X'`.
   - `(3, 1)` $\rightarrow$ flipped from `'#'` back to `'O'`.

**Result:**
```text
X X X X
X X X X
X X X X
X O X X
```

---

## 4. Implementation

```python
def solve(board):
    """
    Do not return anything, modify board in-place instead.
    """
    if not board or not board[0]:
        return

    rows, cols = len(board), len(board[0])

    def dfs(r, c):
        # Base case: Out of bounds or not an 'O'
        if r < 0 or c < 0 or r >= rows or c >= cols or board[r][c] != 'O':
            return
        
        # Mark as safe
        board[r][c] = '#'
        
        # Visit 4-directional neighbors
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    # 1. Start DFS from the left and right boundaries
    for r in range(rows):
        dfs(r, 0)
        dfs(r, cols - 1)

    # 2. Start DFS from the top and bottom boundaries
    for c in range(cols):
        dfs(0, c)
        dfs(rows - 1, c)

    # 3. Final pass to flip cells
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'O':
                board[r][c] = 'X'  # Captured
            elif board[r][c] == '#':
                board[r][c] = 'O'  # Restored safe region
```

---

## 5. Complexity Analysis

| Complexity | Time | Space | Reasoning |
| :--- | :--- | :--- | :--- |
| **Optimal (DFS/BFS)** | $O(M \times N)$ | $O(M \times N)$ | We visit every cell in the grid a maximum of 3 times (Boundary check, DFS, Final pass). Space is used by the recursion stack in the worst case (e.g., the grid is all `'O'`). |

- **Time Complexity**: $O(M \times N)$. Each cell is processed a constant number of times.
- **Space Complexity**: $O(M \times N)$. In the worst case, the DFS recursion depth can go up to $M \times N$ if the grid is filled with connected `'O'`s.

---

## 6. Real-World Applications

The pattern used in "Surrounded Regions" is known as **Connected Component Labeling** or **Flood Fill**. It is widely used in various software systems:

1. **Image Processing (Magic Wand Tool):** In software like Photoshop, the "Magic Wand" selects a contiguous area of pixels of the same color. This is exactly a BFS/DFS on a 2D grid.
2. **Game Development:** Determining if a player is "trapped" in a game (e.g., Go or Othello) where pieces are captured if they have no liberties (paths to open space).
3. **GIS (Geographic Information Systems):** Identifying "enclaves" (territories completely surrounded by another territory) or calculating drainage basins in topography maps.
4. **Network Analysis:** Identifying isolated clusters of nodes in a network that have no connection to a central gateway or external internet boundary.
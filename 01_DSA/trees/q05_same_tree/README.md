# Same Tree (q05_same_tree)

## 1. Overview & Problem Explanation
The **Same Tree** problem asks us to determine if two binary trees are identical. Two binary trees are considered the same if:
1. They have the **exact same structure**.
2. Every corresponding node in both trees has the **same value**.

### Input/Output
- **Input**: Two root nodes of binary trees, `p` and `q`.
- **Output**: A boolean value (`True` if the trees are identical, `False` otherwise).

### Constraints & Edge Cases
- **Empty Trees**: If both `p` and `q` are `null`, they are identical.
- **Structural Mismatch**: If one tree has a node where the other has `null`, they are not identical.
- **Value Mismatch**: If both have nodes at the same position but the values differ, they are not identical.
- **Constraints**: The number of nodes is typically small (up to 100), meaning an $O(N)$ solution is highly efficient.

---

## 2. Core Concepts & Data Structures
The most effective way to solve this problem is using **Depth-First Search (DFS)** via **Recursion**.

### Why Recursion?
Binary trees are recursive data structures by nature (a tree consists of a root node and two sub-trees, which are themselves trees). Therefore, a recursive approach allows us to break the problem down into the smallest possible sub-problems:
- "Are these two current nodes the same?"
- "Are their left children the same?"
- "Are their right children the same?"

### Algorithmic Pattern: Divide and Conquer
We divide the problem by checking the root and then delegating the check for the left and right subtrees to recursive calls. If all three conditions (root, left, right) are true, the trees are identical.

---

## 3. Step-by-Step Logic

### The Recursive Strategy
To determine if two trees are the same, we follow these logical steps at every node:

1. **Base Case 1: Both are Null**
   If both `p` and `q` are `None`, we have reached the leaf ends of both trees simultaneously. This is a match. Return `True`.
   
2. **Base Case 2: One is Null, One is Not**
   If one node is `None` but the other is not, the structures differ. Return `False`.

3. **Base Case 3: Value Mismatch**
   If both nodes exist but `p.val != q.val`, the trees are not identical. Return `False`.

4. **Recursive Step: Check Subtrees**
   If the current nodes are identical, we must ensure their children are also identical. We recursively call the function for:
   - The left child of `p` and the left child of `q`.
   - The right child of `p` and the right child of `q`.
   - Both must return `True` for the current subtree to be considered identical.

### Dry Run Example
**Input**: `p = [1, 2, 3]`, `q = [1, 2, 3]`
1. `solve(p, q)`: Both are not null, values are `1 == 1`. Proceed to children.
2. `solve(p.left, q.left)`: Both are not null, values are `2 == 2`. Proceed to children.
   - `solve(p.left.left, q.left.left)`: Both are `None` $\rightarrow$ **True**.
   - `solve(p.left.right, q.left.right)`: Both are `None` $\rightarrow$ **True**.
   - Result for node `2`: `True && True` $\rightarrow$ **True**.
3. `solve(p.right, q.right)`: Both are not null, values are `3 == 3`. Proceed to children.
   - `solve(p.right.left, q.right.left)`: Both are `None` $\rightarrow$ **True**.
   - `solve(p.right.right, q.right.right)`: Both are `None` $\rightarrow$ **True**.
   - Result for node `3`: `True && True` $\rightarrow$ **True**.
4. Final Result: `True (Root) && True (Left) && True (Right)` $\rightarrow$ **True**.

---

## 4. Implementation

```python
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isSameTree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    """
    Optimal solution using recursive DFS to verify if two binary trees are identical.
    """
    # 1. Both nodes are null: they are identical at this position
    if not p and not q:
        return True
    
    # 2. One node is null or values differ: they are not identical
    if not p or not q or p.val != q.val:
        return False
    
    # 3. Recursively check left and right subtrees
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)

# Wrapper for the challenge format
def solve():
    # Example usage
    p = TreeNode(1, TreeNode(2), TreeNode(3))
    q = TreeNode(1, TreeNode(2), TreeNode(3))
    print(f"Are trees same? {isSameTree(p, q)}") # Expected: True

if __name__ == "__main__":
    solve()
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive DFS** | $O(N)$ | $O(H)$ | Time is $O(N)$ because we visit every node exactly once. Space is $O(H)$ due to the recursion stack, where $H$ is the height of the tree. |

- **Time Complexity $O(N)$**: In the worst case (where the trees are identical), we must traverse every single node in both trees to verify equality.
- **Space Complexity $O(H)$**: The space used is proportional to the depth of the recursion. In a balanced tree, $H = \log N$. In a skewed tree (like a linked list), $H = N$.

---

## 6. Real-World Applications

The "Same Tree" pattern—comparing structural integrity and data across hierarchical models—is used in several critical software systems:

1. **Merkle Trees (Blockchain & Git)**: 
   Git uses a similar concept to compare directory structures. Instead of comparing every file, it compares hashes of tree nodes. If the root hashes are the same, the entire directory tree is identical.
   
2. **Virtual DOM Diffing (React.js)**: 
   Modern UI frameworks like React compare a "Virtual DOM" (a tree structure) with a previous version to determine exactly which parts of the UI need to be updated, minimizing expensive browser repaints.

3. **Compiler Optimization**: 
   Compilers often represent code as an **Abstract Syntax Tree (AST)**. To detect redundant code or perform "common subexpression elimination," the compiler checks if two AST sub-trees are identical.

4. **File System Synchronization**: 
   Tools like `rsync` or cloud backup services compare directory trees to identify which folders are identical and which need to be synchronized.
# Subtree of Another Tree (q06_subtree)

## 1. Overview & Problem Explanation

The **Subtree of Another Tree** challenge asks us to determine if a given binary tree (`subRoot`) is a subtree of another binary tree (`root`). 

### What defines a "Subtree"?
In the context of this problem, a **subtree** of a binary tree `root` is defined as a tree consisting of a node in `root` and **all of its descendants**. 

This is a critical distinction: you cannot simply find a "pattern" of nodes; the structure must be identical from the chosen node all the way down to the leaves.

### Input & Output
- **Input**: Two binary tree roots, `root` and `subRoot`.
- **Output**: A boolean (`True` or `False`).

### Constraints & Edge Cases
- **Node Count**: Both trees can have between 1 and 200 nodes.
- **Node Values**: Values range from $-10^4$ to $10^4$.
- **Edge Cases to Consider**:
    - `subRoot` is exactly the same as `root`.
    - `root` is empty, but `subRoot` is not (Return `False`).
    - `subRoot` is empty (Technically a subtree of any tree, though constraints usually specify at least 1 node).
    - Trees have the same values but different structural shapes.
    - `subRoot` exists in the middle of `root` but has extra children in `root` that are not in `subRoot` (Return `False`).

---

## 2. Core Concepts & Algorithms

### Depth-First Search (DFS)
The primary algorithmic pattern here is **DFS**. Since we need to explore the `root` tree to find a potential starting point for the `subRoot`, and then explore the structure of both trees deeply to verify equality, recursion (the hallmark of DFS) is the most natural fit.

### The "Two-Step" Recursive Pattern
This problem requires two distinct recursive processes:
1. **The Search Process**: Traverse the main tree (`root`) to find a node that matches the root of `subRoot`.
2. **The Comparison Process**: Once a potential match is found, verify if the tree starting at that node is **identical** in structure and value to `subRoot`.

### Why this approach?
We use a helper function `isSameTree` because the logic for "Are these two trees identical?" is different from "Does this tree contain another tree?". Separating these concerns keeps the code clean and reduces the cognitive load.

---

## 3. Step-by-Step Logic

### Approach: Recursive DFS (Optimal for constraints)

#### Step 1: The `isSameTree` Helper
To check if two trees `p` and `q` are identical:
1. If both `p` and `q` are `None`, they are identical $\rightarrow$ `True`.
2. If only one is `None`, or their values differ $\rightarrow$ `False`.
3. Recursively check if `p.left` is same as `q.left` **AND** `p.right` is same as `q.right`.

#### Step 2: The `isSubtree` Main Logic
To check if `subRoot` is a subtree of `root`:
1. If `root` is `None`, it cannot contain `subRoot` (since `subRoot` is non-empty) $\rightarrow$ `False`.
2. Check if the current `root` and `subRoot` are identical using `isSameTree(root, subRoot)`. If yes $\rightarrow$ `True`.
3. If not identical at the current node, recursively search in the left child: `isSubtree(root.left, subRoot)`.
4. Recursively search in the right child: `isSubtree(root.right, subRoot)`.
5. Return `True` if either the left or right subtree search returns `True`.

### Dry Run Example
**Input**: `root = [3,4,5,1,2]`, `subRoot = [4,1,2]`

1. `isSubtree(node(3), subRoot)` $\rightarrow$ `isSameTree(3, 4)` is `False`.
2. Move to `root.left` $\rightarrow$ `isSubtree(node(4), subRoot)`.
3. Inside this call: `isSameTree(node(4), subRoot)`:
    - `4 == 4` (Match!)
    - `isSameTree(node(1), node(1))` $\rightarrow$ `True`.
    - `isSameTree(node(2), node(2))` $\rightarrow$ `True`.
4. `isSameTree` returns `True`.
5. `isSubtree` returns `True`.

---

## 4. Implementation

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isSameTree(p: TreeNode, q: TreeNode) -> bool:
    # If both nodes are null, they are identical
    if not p and not q:
        return True
    # If one is null or values differ, they are not identical
    if not p or not q or p.val != q.val:
        return False
    # Recurse for left and right children
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)

def solve_optimal(root: TreeNode, subRoot: TreeNode) -> bool:
    # Base case: if root is null, it cannot contain subRoot
    if not root:
        return False
    
    # 1. Check if the tree starting at current root is identical to subRoot
    if isSameTree(root, subRoot):
        return True
    
    # 2. Otherwise, search for subRoot in the left and right children
    return solve_optimal(root.left, subRoot) or solve_optimal(root.right, subRoot)
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive DFS** | $O(N \times M)$ | $O(\max(H_N, H_M))$ | In the worst case, we call `isSameTree` (which takes $O(M)$) for every node in `root` ($O(N)$). Space is determined by the recursion stack height. |

- **$N$**: Number of nodes in the main tree (`root`).
- **$M$**: Number of nodes in the subtree (`subRoot`).
- **$H$**: Height of the tree.

---

## 6. Real-World Applications

The logic used in "Subtree of Another Tree" is a fundamental building block for several complex software systems:

1. **Abstract Syntax Trees (AST)**: Compilers and linters use this pattern to find specific code smells or patterns. For example, searching for a specific nested function call structure within a large source code tree.
2. **DOM Manipulation**: In web browsers, searching for a specific HTML structure (a `div` containing a specific set of nested `span` and `p` tags) is essentially a subtree matching problem.
3. **File System Analysis**: Searching for a specific directory structure (e.g., "find every folder that contains a `src` folder and a `package.json` file") mimics the subtree search logic.
4. **XML/JSON Validation**: Validating that a specific required schema subtree exists within a larger data document.
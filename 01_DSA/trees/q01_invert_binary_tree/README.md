# Invert Binary Tree (q01_invert_binary_tree)

## 1. Overview & Problem Explanation

The **Invert Binary Tree** problem is a classic technical interview question that tests a developer's understanding of tree traversal and recursion. To "invert" a binary tree means to create a mirror image of the original tree. For every single node in the tree, its left child must become its right child, and its right child must become its left child.

### Problem Statement
Given the `root` of a binary tree, invert the tree and return its root.

### Visual Representation
**Input:**
```text
     4
   /   \
  2     7
 / \   / \
1   3 6   9
```

**Output (Inverted):**
```text
     4
   /   \
  7     2
 / \   / \
9   6 3   1
```

### Constraints & Edge Cases
- **Empty Tree**: If the `root` is `None`, the function should return `None` immediately.
- **Single Node**: If the tree consists of only one node, it is technically already inverted.
- **Skewed Tree**: A tree where every node has only one child (essentially a linked list). The logic must still hold.
- **Constraints**: Usually, the number of nodes ranges from $0$ to $100$, meaning an $O(n)$ solution is highly efficient and well within limits.

---

## 2. Core Concepts & Data Structures

### Binary Trees
A **Binary Tree** is a hierarchical data structure in which each node has at most two children, referred to as the left child and the right child.

### Recursion & Depth-First Search (DFS)
The most intuitive way to solve this problem is using **Recursion**, which is a specific implementation of **Depth-First Search (DFS)**. 

**Why Recursion?**
Trees are recursive data structures by nature—every child of a node is itself the root of a smaller subtree. Therefore, the problem of inverting a large tree can be broken down into:
1. Inverting the left subtree.
2. Inverting the right subtree.
3. Swapping the two inverted subtrees.

This "bottom-up" approach ensures that by the time we swap the children of the root, the children themselves have already been perfectly mirrored.

---

## 3. Step-by-Step Logic

### Optimal Recursive Approach
The goal is to visit every node and swap its children.

#### Logical Steps:
1. **Base Case**: Check if the current node (`root`) is `None`. If it is, we have reached the end of a branch; return `None`.
2. **Recursive Call (Left)**: Call the function on the left child. This will dive deep into the leftmost leaf first.
3. **Recursive Call (Right)**: Call the function on the right child.
4. **The Swap**: Once the recursive calls return (meaning the subtrees below the current node are already inverted), swap the current node's `left` and `right` pointers.
5. **Return**: Return the `root` node to the previous caller in the stack.

#### Dry Run Example
Input: `[2, 1, 3]` (Root: 2, Left: 1, Right: 3)

1. `invert_tree(Node 2)` is called.
2. It calls `invert_tree(Node 1)`.
   - `Node 1` calls `invert_tree(None)` $\rightarrow$ returns `None`.
   - `Node 1` calls `invert_tree(None)` $\rightarrow$ returns `None`.
   - `Node 1` swaps its children (None $\leftrightarrow$ None).
   - Returns `Node 1`.
3. It calls `invert_tree(Node 3)`.
   - `Node 3` calls `invert_tree(None)` $\rightarrow$ returns `None`.
   - `Node 3` calls `invert_tree(None)` $\rightarrow$ returns `None`.
   - `Node 3` swaps its children (None $\leftrightarrow$ None).
   - Returns `Node 3`.
4. `Node 2` now swaps its `left` (Node 1) with its `right` (Node 3).
5. Returns `Node 2` with new children: Left: 3, Right: 1.

### Implementation
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def invert_tree_optimal(root: TreeNode) -> TreeNode:
    # Base Case: If the node is null, we've reached the end of a branch
    if not root: 
        return None
    
    # Recursively invert the subtrees and swap them in one line
    # We store the results of the recursive calls and assign them to the opposite side
    root.left, root.right = invert_tree_optimal(root.right), invert_tree_optimal(root.left)
    
    return root
```

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive DFS** | $O(n)$ | $O(h)$ | **Time**: We must visit every node exactly once. **Space**: The recursion stack depth equals the height of the tree ($h$). |

- **Time Complexity $O(n)$**: Where $n$ is the number of nodes in the tree. Each node is processed exactly once.
- **Space Complexity $O(h)$**: Where $h$ is the height of the tree. 
    - In the **best case** (perfectly balanced tree), $h = \log n$.
    - In the **worst case** (completely skewed tree), $h = n$, making the space complexity $O(n)$.

---

## 5. Real-World Applications

While "inverting a binary tree" seems like a puzzle, the underlying patterns are used extensively in software engineering:

1. **Mirroring and UI Layouts**: In graphical user interfaces (GUIs) or game development, mirroring a coordinate-based tree structure is used to create mirrored layouts (e.g., Right-to-Left (RTL) language support for Arabic or Hebrew).
2. **Compiler Design**: Abstract Syntax Trees (ASTs) are used by compilers to represent code. Certain optimization passes involve transforming or rearranging these trees to simplify expressions.
3. **Search Normalization**: In certain specialized search indexes or decision trees, mirroring the tree can be used to test symmetry or to implement specific types of "opposite" logic searches.
4. **Data Transformation**: Whenever a hierarchical data structure needs to be reversed or flipped for a specific API requirement or data visualization (like a flipped organizational chart), this pattern is applied.
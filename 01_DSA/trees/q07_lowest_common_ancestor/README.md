# Lowest Common Ancestor of a Binary Search Tree

## 1. Overview & Problem Explanation

The goal of this challenge is to find the **Lowest Common Ancestor (LCA)** of two given nodes, `p` and `q`, in a **Binary Search Tree (BST)**.

### What is the Lowest Common Ancestor?
The Lowest Common Ancestor of two nodes $p$ and $q$ is defined as the lowest node in the tree that has both $p$ and $q$ as descendants. Crucially, a node can be a descendant of itself. Therefore, if node $p$ is the parent of node $q$, then $p$ is the LCA.

### The BST Advantage
While finding the LCA in a general Binary Tree requires traversing the tree to locate both nodes, a **Binary Search Tree (BST)** provides a specific property we can exploit:
- For any given node, all values in its **left subtree** are smaller than the node's value.
- All values in its **right subtree** are larger than the node's value.

### Input/Output
- **Input**: The `root` of a BST, and two nodes `p` and `q`.
- **Output**: The node that represents the LCA of `p` and `q`.

### Constraints & Edge Cases
- The nodes `p` and `q` are guaranteed to exist in the BST.
- The BST contains unique values.
- **Edge Case**: One of the nodes is the ancestor of the other (e.g., $p$ is the root and $q$ is a leaf). In this case, $p$ is the LCA.

---

## 2. Core Concepts & Data Structures

### Binary Search Tree (BST) Property
The core of this problem is the **Binary Search Property**. Because the tree is sorted, we don't need to "search" for the nodes in the traditional sense. Instead, we can use the values of $p$ and $q$ to decide which direction to move.

### Algorithmic Pattern: Binary Search on Trees
Just as binary search on an array halves the search space at each step, navigating a BST allows us to discard an entire subtree at each decision point. This transforms a potentially $O(N)$ search into an $O(H)$ search, where $H$ is the height of the tree.

### Why this approach?
- **Efficiency**: We only visit nodes on the path from the root to the LCA.
- **Simplicity**: The decision logic is based on simple numerical comparisons.

---

## 3. Step-by-Step Logic

### The Intuition
Imagine you are at the root. You want to find where $p$ and $q$ "split" apart.
1. If both $p$ and $q$ are **smaller** than the current node, they both must reside in the **left subtree**.
2. If both $p$ and $q$ are **larger** than the current node, they both must reside in the **right subtree**.
3. If one is smaller and the other is larger (or the current node equals either $p$ or $q$), you have found the **split point**. This split point is the LCA.

### Iterative Approach (Optimal)
1. Start at the `root`.
2. While the current node is not null:
    - Check if `p.val` and `q.val` are both greater than `root.val`. If yes, move `root` to `root.right`.
    - Check if `p.val` and `q.val` are both smaller than `root.val`. If yes, move `root` to `root.left`.
    - Otherwise, the current `root` is the LCA. Return it.

### Dry Run Example
**Input**: Root = [6, 2, 8, 0, 4, 7, 9], $p = 2, q = 8$
1. **Current Node = 6**:
   - Is $2 > 6$ and $8 > 6$? No.
   - Is $2 < 6$ and $8 < 6$? No.
   - **Split found!** Return node 6.

**Input**: Root = [6, 2, 8, 0, 4, 7, 9], $p = 2, q = 4$
1. **Current Node = 6**:
   - Is $2 < 6$ and $4 < 6$? **Yes**. Move to `root.left` (Node 2).
2. **Current Node = 2**:
   - Is $2 > 2$ and $4 > 2$? No.
   - Is $2 < 2$ and $4 < 2$? No.
   - **Split found!** (Note: current node is $p$). Return node 2.

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive** | $O(H)$ | $O(H)$ | We visit one node per level. The recursion stack takes space proportional to the height. |
| **Iterative** | $O(H)$ | $O(1)$ | We visit one node per level. No extra space is used beyond a single pointer. |

- **$N$**: Number of nodes in the tree.
- **$H$**: Height of the tree. In a balanced BST, $H = \log N$. In a skewed BST (like a linked list), $H = N$.

---

## 5. Implementation

```python
# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def solve_optimal(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """
    Iterative approach to find the LCA in a BST.
    Time Complexity: O(H)
    Space Complexity: O(1)
    """
    current = root
    
    while current:
        # If both p and q are greater than parent, LCA is in the right subtree
        if p.val > current.val and q.val > current.val:
            current = current.right
        # If both p and q are smaller than parent, LCA is in the left subtree
        elif p.val < current.val and q.val < current.val:
            current = current.left
        else:
            # We have found the split point, or current is either p or q
            return current
```

---

## 6. Real-World Applications

The concept of the Lowest Common Ancestor is widely used in computer science and software engineering:

1. **Version Control Systems (Git)**: When merging two branches, Git needs to find the "merge base," which is the Lowest Common Ancestor of the two commit hashes in the commit graph. This determines which changes are new and which are shared.
2. **Organizational Hierarchies**: In an HR system representing a corporate hierarchy, finding the LCA of two employees identifies their immediate common manager.
3. **File Systems**: Finding the LCA of two file paths (e.g., `/home/user/docs/file1.txt` and `/home/user/pics/img1.jpg`) determines the deepest common directory (`/home/user`), which is essential for calculating relative paths.
4. **Taxonomy & Biology**: In phylogenetic trees (evolutionary trees), the LCA of two species represents their most recent common ancestor.
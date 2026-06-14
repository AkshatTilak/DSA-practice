# Balanced Binary Tree (q04_balanced_tree)

## 📌 Overview & Problem Explanation

The goal of this challenge is to determine if a given binary tree is **height-balanced**. 

### What is a Height-Balanced Binary Tree?
A binary tree is considered height-balanced if, for **every** node in the tree, the absolute difference between the height of its left subtree and the height of its right subtree is **no more than 1**.

**Mathematically:** 
A node is balanced if: $| \text{height}(\text{left\_child}) - \text{height}(\text{right\_child}) | \le 1$

### Input/Output
- **Input**: The root of a binary tree.
- **Output**: A boolean value (`True` if the tree is balanced, `False` otherwise).

### Constraints & Edge Cases
- **Empty Tree**: An empty tree (root is `None`) is considered balanced.
- **Single Node**: A tree with only one node is balanced.
- **Skewed Tree**: A tree where every node has only one child (like a linked list) is generally unbalanced unless it has very few nodes.
- **Large Trees**: The solution must be efficient enough to handle trees with thousands of nodes without hitting recursion limits or timing out.

---

## 🧠 Core Concepts & Data Structures

### 1. Binary Tree Height
The **height** of a node is the number of edges on the longest path from that node to a leaf. A leaf node has a height of 0.

### 2. Depth-First Search (DFS)
To determine if a tree is balanced, we must visit the nodes. Since the balance of a parent depends on the heights of its children, a **Post-Order Traversal** (Left $\rightarrow$ Right $\rightarrow$ Root) is the most logical choice. We calculate the height of the subtrees first and then use those values to evaluate the current node.

### 3. Bottom-Up vs. Top-Down
- **Top-Down (Naive)**: Check the root, then recursively check the children. This results in redundant calculations because the height of the same nodes is calculated multiple times.
- **Bottom-Up (Optimal)**: Calculate height from the leaves upward. If a subtree is found to be unbalanced, we "bubble up" that information immediately to avoid unnecessary further calculations.

---

## 🛠️ Step-by-Step Logic

### Approach 1: Top-Down (Naive)
1. Create a helper function `getHeight(node)` that recursively calculates the height of a tree.
2. For the current root:
   - Get the height of the left subtree.
   - Get the height of the right subtree.
   - Check if the absolute difference is $\le 1$.
3. Recursively call the same check for the left and right children.
4. **The Flaw**: For every node, we call `getHeight`, which visits all descendants. This leads to an $O(N^2)$ time complexity in the worst case.

### Approach 2: Bottom-Up (Optimal)
Instead of calling a separate height function, we integrate the balance check into the height calculation.

1. **Recursive Base Case**: If the node is `None`, its height is $0$.
2. **Recurse Left**: Call the function on the left child. If the left child returns `-1` (indicating it is unbalanced), immediately return `-1` to the parent.
3. **Recurse Right**: Call the function on the right child. If the right child returns `-1`, immediately return `-1`.
4. **Balance Check**: 
   - Calculate the difference: `abs(left_height - right_height)`.
   - If the difference is $> 1$, this node is unbalanced $\rightarrow$ return `-1`.
5. **Return Height**: If the node is balanced, return its actual height: `1 + max(left_height, right_height)`.

#### Dry Run Example:
Consider a tree: `[3, 9, 20, None, None, 15, 7]`
- Node `15`: Left=0, Right=0 $\rightarrow$ Balanced, height = 1.
- Node `7`: Left=0, Right=0 $\rightarrow$ Balanced, height = 1.
- Node `20`: Left=1, Right=1 $\rightarrow$ Balanced, height = 2.
- Node `9`: Left=0, Right=0 $\rightarrow$ Balanced, height = 1.
- Node `3`: Left=1 (from 9), Right=2 (from 20) $\rightarrow$ $|1-2| = 1$ $\rightarrow$ Balanced, height = 3.
- **Result**: `True`.

---

## 💻 Implementation

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve(root: TreeNode) -> bool:
    """
    Determines if a binary tree is height-balanced.
    Using the optimal Bottom-Up DFS approach.
    """
    
    def check_height(node):
        # Base case: an empty node has height 0
        if not node:
            return 0
        
        # Check left subtree
        left_height = check_height(node.left)
        if left_height == -1: 
            return -1  # Propagate unbalance upward
        
        # Check right subtree
        right_height = check_height(node.right)
        if right_height == -1: 
            return -1  # Propagate unbalance upward
        
        # Check if current node is balanced
        if abs(left_height - right_height) > 1:
            return -1  # Current node is unbalanced
        
        # Return the actual height of the node
        return 1 + max(left_height, right_height)

    # If the helper returns -1, the tree is unbalanced
    return check_height(root) != -1
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Top-Down** | $O(N^2)$ | $O(N)$ | Each node is visited multiple times by the `getHeight` function. |
| **Bottom-Up** | $O(N)$ | $O(N)$ | Each node is visited exactly once. Space is used by the recursion stack. |

- **Time Complexity $O(N)$**: We visit each node in the tree exactly once during the post-order traversal.
- **Space Complexity $O(N)$**: In the worst case (a completely skewed tree), the recursion stack will grow to the size of the number of nodes $N$. For a balanced tree, it would be $O(\log N)$.

---

## 🌍 Real-World Applications

The concept of maintaining a balanced tree is critical in software engineering to ensure predictable performance:

1. **Database Indexing (B-Trees / AVL Trees)**: Databases use balanced trees (like B-Trees) to ensure that searching for a record takes $O(\log N)$ time. If the tree becomes unbalanced, search performance degrades to $O(N)$.
2. **File Systems**: Many file systems use balanced tree structures to manage directory hierarchies and file metadata, ensuring fast access times regardless of how many files are created.
3. **Network Routing**: Certain routing algorithms use balanced trees to maintain efficient look-up tables for IP prefixes.
4. **Memory Management**: Some memory allocation algorithms use balanced binary search trees to track free blocks of memory for efficient allocation and merging.
INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/kth-smallest-element-in-a-bst/',
    'description': 'Find Kth smallest.',
    'groups': ['Tree', 'Binary Search'],
    'readme_content': """# Kth Smallest Element in a BST

## 1. Overview & Problem Explanation
The objective of this challenge is to identify the $k$-th smallest value in a **Binary Search Tree (BST)**. 

In a standard binary tree, elements are placed without a specific order. However, a **Binary Search Tree (BST)** follows a strict ordering property:
- The **left subtree** of a node contains only nodes with keys **less than** the node's key.
- The **right subtree** of a node contains only nodes with keys **greater than** the node's key.

Given the root of a BST and an integer $k$, we need to return the value of the $k$-th smallest element.

### Inputs & Outputs
- **Input**: 
    - `root`: The root node of the Binary Search Tree.
    - `k`: An integer representing the rank (1-indexed) of the element to retrieve.
- **Output**: 
    - An integer representing the value of the $k$-th smallest node.

### Constraints & Edge Cases
- **Constraints**: 
    - $1 \le k \le \text{number of nodes in the tree}$.
    - The tree contains at least one node.
    - All node values are unique.
- **Edge Cases**:
    - **$k = 1$**: The leftmost leaf node (the absolute minimum).
    - **$k = N$ (Total Nodes)**: The rightmost leaf node (the absolute maximum).
    - **Skewed Tree**: A tree that looks like a linked list (height $H = N$), which tests the efficiency of the stack/recursion.

---

## 2. Core Concepts & Data Structures

### The Power of In-Order Traversal
The most critical property of a BST is that an **In-order Traversal** (Left $\rightarrow$ Root $\rightarrow$ Right) visits the nodes in **non-decreasing sorted order**.

**Why this works:**
By always visiting the leftmost child first, we ensure we reach the smallest possible value. Then, we visit the parent (which is slightly larger), and finally the right subtree (which contains values larger than the parent).

### Algorithmic Patterns
1. **Depth First Search (DFS)**: We use DFS to dive deep into the left subtree before processing any values.
2. **Iterative Stack**: While recursion is intuitive, an iterative approach using a `stack` allows for **early termination**. As soon as we encounter the $k$-th element, we can stop traversing and return the result immediately, rather than visiting every single node in the tree.

---

## 3. Step-by-Step Logic

### Approach 1: Full In-Order Traversal (Naive/Simple)
1. Perform a full recursive in-order traversal of the entire tree.
2. Store every visited node's value into a list.
3. Return the element at index `k - 1`.

**Dry Run**:
- Tree: `[3, 1, 4, null, 2]` | $k = 1$
- In-order sequence: `[1, 2, 3, 4]`
- Result: `list[0] = 1`

### Approach 2: Iterative In-Order with Early Exit (Optimal)
Instead of storing all elements, we maintain a counter and stop the moment the counter reaches $k$.

1. Initialize an empty **stack** and set the current node to `root`.
2. **Traverse Left**: While the current node is not null, push the current node onto the stack and move to its left child. This ensures we reach the smallest element first.
3. **Process Node**: 
    - Pop the top node from the stack.
    - Increment the counter (we have visited one more smallest element).
    - If the counter equals $k$, **return this node's value**.
4. **Traverse Right**: Move the current node to the popped node's right child and repeat from Step 2.

**Example Trace**:
- Tree: `root(3)`, `left(1)`, `right(4)`, `1.right(2)` | $k = 2$
- **Step 1**: Push `3`, Push `1`. (Stack: `[3, 1]`)
- **Step 2**: Pop `1`. Count = 1. (Not $k$)
- **Step 3**: Move to `1.right` $\rightarrow$ node `2`.
- **Step 4**: Push `2`. (Stack: `[3, 2]`)
- **Step 5**: Pop `2`. Count = 2. (**Matches $k$!**)
- **Return**: `2`.

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Full In-Order** | $O(N)$ | $O(N)$ | We visit every node and store all $N$ nodes in a list. |
| **Iterative (Optimal)** | $O(H + k)$ | $O(H)$ | We descend to the leftmost leaf ($H$) and then visit $k$ nodes. Space is used by the stack for tree height $H$. |

- **$N$**: Total number of nodes in the BST.
- **$H$**: Height of the tree. In a balanced tree, $H = \log N$. In a skewed tree, $H = N$.

---

## 5. Implementation

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_optimal(root: TreeNode, k: int) -> int:
    \"\"\"
    Finds the kth smallest element in a BST using an iterative 
    in-order traversal to allow for early termination.
    \"\"\"
    stack = []
    curr = root
    n = 0  # Counter to keep track of visited nodes
    
    while curr or stack:
        # 1. Reach the leftmost node of the current subtree
        while curr:
            stack.append(curr)
            curr = curr.left
        
        # 2. Process the node
        curr = stack.pop()
        n += 1
        
        if n == k:
            return curr.val
        
        # 3. Move to the right subtree
        curr = curr.right
        
    return -1 # Should not be reached given problem constraints
```

---

## 6. Real-World Applications

1. **Order Statistics in Databases**: 
   Many database indexing systems (like B-Trees, a generalization of BSTs) use similar logic to implement "Find the $k$-th record" or "Range queries" (e.g., `SELECT * FROM users ORDER BY age LIMIT 1 OFFSET 10`).
   
2. **Priority Queues & Scheduling**: 
   In systems where you need to retrieve the $k$-th highest priority task rather than just the top one, augmented BSTs (where nodes store the size of their subtree) are used to achieve $O(\log N)$ lookup.

3. **File System Navigation**: 
   When listing files in a directory sorted by name, the OS effectively performs a traversal of the directory structure, similar to how we traverse the BST to find a specific rank.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach performs a full in-order traversal of the Binary Search Tree (BST), 
# storing all elements in a list. Since in-order traversal of a BST yields elements 
# in sorted order, the kth smallest element is simply the element at index k-1.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_naive(root: TreeNode, k: int) -> int:
    nodes = []
    
    def inorder(node):
        if not node:
            return
        inorder(node.left)
        nodes.append(node.val)
        inorder(node.right)
        
    inorder(root)
    return nodes[k - 1]

# --- APPROACH 2: Optimal (Iterative In-Order Traversal) ---
# Time Complexity: O(H + k)
# Space Complexity: O(H)
# This approach is optimal because it uses an iterative in-order traversal with a stack.
# Instead of traversing the entire tree, it stops immediately when the kth element is reached.
# H is the height of the tree; in the worst case (skewed tree), H = N, but for a balanced tree, H = log N.
# It optimizes space by only storing the path from the root to the current leftmost leaf.

def solve_optimal(root: TreeNode, k: int) -> int:
    stack = []
    curr = root
    
    while stack or curr:
        # Reach the leftmost node of the current subtree
        while curr:
            stack.append(curr)
            curr = curr.left
        
        # Process the node
        curr = stack.pop()
        k -= 1
        if k == 0:
            return curr.val
        
        # Move to the right subtree
        curr = curr.right
    
    return -1 # Should not be reached if k is valid

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package trees;

import java.util.Stack;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode(int x) { val = x; }
}

public class KthSmallest {
    /**
     * Finds the kth smallest element in a BST using an iterative in-order traversal.
     * Time Complexity: O(H + k)
     * Space Complexity: O(H)
     */
    public int kthSmallest(TreeNode root, int k) {
        Stack<TreeNode> stack = new Stack<>();
        TreeNode curr = root;
        
        while (curr != null || !stack.isEmpty()) {
            // Go to the leftmost leaf
            while (curr != null) {
                stack.push(curr);
                curr = curr.left;
            }
            
            // Visit the node
            curr = stack.pop();
            k--;
            if (k == 0) {
                return curr.val;
            }
            
            // Move to right subtree
            curr = curr.right;
        }
        
        return -1; // Case where k is greater than the number of nodes
    }

    public static void main(String[] args) {
        KthSmallest solver = new KthSmallest();
        // Example Construction:
        //      3
        //     / \
        //    1   4
        //     \
        //      2
        TreeNode root = new TreeNode(3);
        root.left = new TreeNode(1);
        root.right = new TreeNode(4);
        root.left.right = new TreeNode(2);
        
        System.out.println(solver.kthSmallest(root, 1)); // Output: 1
    }
}
\"\"\"""",
}

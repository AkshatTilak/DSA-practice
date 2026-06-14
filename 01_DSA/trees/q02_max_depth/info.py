INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/maximum-depth-of-binary-tree/',
    'description': 'Max depth.',
    'groups': ['Tree'],
    'readme_content': """# Max Depth of Binary Tree (q02_max_depth)

## 1. Overview & Problem Explanation

The goal of this challenge is to find the **Maximum Depth** of a binary tree. In tree terminology, the maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.

### Understanding the Input/Output
- **Input**: The `root` node of a binary tree. Each node contains a value and pointers to its `left` and `right` children.
- **Output**: An integer representing the maximum depth.

### Key Constraints & Edge Cases
- **Empty Tree**: If the root is `None`, the depth is $0$.
- **Single Node**: If the tree consists of only the root, the depth is $1$.
- **Skewed Tree**: A tree where every node has only one child (effectively a linked list). The depth equals the total number of nodes $N$.
- **Balanced Tree**: A tree where left and right subtrees are roughly equal in height.
- **Constraints**: Typically, the number of nodes ranges from $0$ to $10^4$, meaning an $O(N)$ solution is required.

---

## 2. Core Concepts & Data Structures

To solve this problem, we rely on the fundamental properties of **Binary Trees** and **Tree Traversal** algorithms.

### The Recursive Nature of Trees
A binary tree is a recursive data structure. The maximum depth of a tree rooted at `node` is simply:
$$\text{depth}(\text{node}) = 1 + \max(\text{depth}(\text{node.left}), \text{depth}(\text{node.right}))$$
This relationship makes the problem a perfect candidate for **Depth-First Search (DFS)**.

### Algorithmic Choices
1. **Recursive DFS (Bottom-Up)**: We dive to the leaves and propagate the height back up to the root. This is the most concise approach.
2. **Iterative BFS (Level Order Traversal)**: We traverse the tree level by level. The number of levels we traverse before the queue becomes empty is the maximum depth. This is intuitive for visualizing "depth" as "layers."
3. **Iterative DFS**: Using an explicit stack to simulate recursion, keeping track of the current depth for each node.

---

## 3. Step-by-Step Logic

### Approach 1: Recursive DFS (Optimal & Elegant)
This approach uses a **Post-Order Traversal** pattern (Left $\rightarrow$ Right $\rightarrow$ Root).

1. **Base Case**: If the current node is `None`, we have reached beyond a leaf. Return $0$.
2. **Recursive Step**:
    - Recursively calculate the depth of the **left subtree**.
    - Recursively calculate the depth of the **right subtree**.
3. **Aggregation**: The depth of the current node is the maximum of the two subtree depths, plus $1$ (to account for the current node itself).

**Dry Run Example**:
Tree: `[3, 9, 20, null, null, 15, 7]`
- `depth(15) = 1 + max(0, 0) = 1`
- `depth(7) = 1 + max(0, 0) = 1`
- `depth(20) = 1 + max(depth(15), depth(7)) = 1 + max(1, 1) = 2`
- `depth(9) = 1 + max(0, 0) = 1`
- `depth(3) = 1 + max(depth(9), depth(20)) = 1 + max(1, 2) = 3`
- **Result**: 3

### Approach 2: Iterative BFS (The "Layer" Method)
1. Initialize a `queue` containing the `root` and a `depth` counter at $0$.
2. While the queue is not empty:
    - Increment the `depth` counter.
    - Determine the number of nodes currently in the queue (this represents one full level).
    - Pop all nodes of the current level and push their children into the queue.
3. Once the queue is empty, the `depth` counter holds the total levels.

---

## 4. Implementation

```python
from collections import deque
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    # --- APPROACH 1: Recursive DFS (Optimal) ---
    def maxDepth_Recursive(self, root: Optional[TreeNode]) -> int:
        # Base Case: If node is None, depth is 0
        if not root:
            return 0
        
        # Recursive call to find depth of subtrees
        left_depth = self.maxDepth_Recursive(root.left)
        right_depth = self.maxDepth_Recursive(root.right)
        
        # Current depth is 1 + the maximum of the two children
        return 1 + max(left_depth, right_depth)

    # --- APPROACH 2: Iterative BFS ---
    def maxDepth_BFS(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        
        queue = deque([root])
        depth = 0
        
        while queue:
            # Number of nodes at the current level
            level_size = len(queue)
            depth += 1
            
            for _ in range(level_size):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
                    
        return depth

def solve():
    # Example Usage
    root = TreeNode(3)
    root.left = TreeNode(9)
    root.right = TreeNode(20)
    root.right.left = TreeNode(15)
    root.right.right = TreeNode(7)
    
    sol = Solution()
    print(f"Max Depth (Recursive): {sol.maxDepth_Recursive(root)}") # Expected: 3
    print(f"Max Depth (BFS): {sol.maxDepth_BFS(root)}")             # Expected: 3

if __name__ == "__main__":
    solve()
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive DFS** | $O(N)$ | $O(H)$ | Time: Every node is visited once. Space: The recursion stack depth equals the height of the tree $H$. |
| **Iterative BFS** | $O(N)$ | $O(W)$ | Time: Every node is visited once. Space: The queue stores the maximum width $W$ of the tree. |

- **$N$**: Total number of nodes in the tree.
- **$H$**: Height of the tree (Worst case $O(N)$ for skewed trees, Best case $O(\log N)$ for balanced trees).
- **$W$**: Maximum width of the tree (In a perfect binary tree, $W \approx N/2$).

---

## 6. Real-World Applications

The concept of calculating tree depth is fundamental in several software engineering domains:

1. **File System Analysis**: Calculating the nesting level of directories in a file system to prevent path-length overflow (e.g., Windows MAX_PATH).
2. **DOM Tree Depth**: Web browsers analyze the depth of the Document Object Model (DOM). Extremely deep DOM trees can lead to performance degradation in rendering and CSS selector matching.
3. **Compiler Design**: Abstract Syntax Trees (ASTs) are used to represent code structure. The depth of an AST can influence the recursion limit needed for the compiler's optimization passes.
4. **Organizational Hierarchies**: In HR systems or corporate directory software, calculating the "reporting distance" from a junior employee to the CEO.
5. **JSON/XML Parsing**: Validating the nesting depth of data formats to prevent **Stack Overflow** attacks (Recursive Descent Parsing vulnerabilities).""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach uses an iterative Breadth-First Search (BFS) using a queue. 
# It traverses the tree level by level, incrementing the depth counter for each level processed.
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_naive(root: TreeNode) -> int:
    if not root:
        return 0
    
    queue = deque([root])
    depth = 0
    
    while queue:
        depth += 1
        # Process all nodes at the current level
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
                
    return depth

# --- APPROACH 2: Optimal (Recursive DFS) ---
# Time Complexity: O(N)
# Space Complexity: O(H) where H is the height of the tree.
# This approach uses Depth-First Search (DFS) via recursion. 
# The maximum depth of a node is 1 plus the maximum of the depths of its left and right children.
# It is optimal because it visits each node exactly once and minimizes the auxiliary space 
# required to O(H) for the call stack, which is O(log N) for a balanced tree.
def solve_optimal(root: TreeNode) -> int:
    if not root:
        return 0
    
    # The depth of the current node is 1 + the depth of its deepest subtree
    return 1 + max(solve_optimal(root.left), solve_optimal(root.right))

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package trees;

public class MaxDepth {
    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int val) { this.val = val; }
        TreeNode(int val, TreeNode left, TreeNode right) {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }

    /**
     * Computes the maximum depth of a binary tree.
     * Time Complexity: O(N)
     * Space Complexity: O(H)
     */
    public int solveOptimal(TreeNode root) {
        if (root == null) {
            return 0;
        }
        
        int leftDepth = solveOptimal(root.left);
        int rightDepth = solveOptimal(root.right);
        
        return 1 + Math.max(leftDepth, rightDepth);
    }

    public static void main(String[] args) {
        MaxDepth solution = new MaxDepth();
        // Example: [3, 9, 20, null, null, 15, 7]
        TreeNode root = new TreeNode(3);
        root.left = new TreeNode(9);
        root.right = new TreeNode(20, new TreeNode(15), new TreeNode(7));
        
        System.out.println("Max Depth: " + solution.solveOptimal(root)); // Expected: 3
    }
}
\"\"\"""",
}

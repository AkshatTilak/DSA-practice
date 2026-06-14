"""
Challenge: q01_invert_binary_tree
Difficulty: Easy
Link: https://leetcode.com/problems/invert-binary-tree/

Problem:
Invert a binary tree (swap left and right child recursively).
"""

# --- STARTER TEMPLATE FOR USER ---
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def invert_tree(root: TreeNode) -> TreeNode:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---`
    `def TreeNode_naive(...):`
    I will use `invert_tree_naive` and `invert_tree_optimal`.

    Let's double check the Java requirements. Package `trees`, Class `InvertBinaryTree`.

    *Python Recursive (Optimal):*
    ```python
    def invert_tree(root: TreeNode) -> TreeNode:
        if not root:
            return None
        root.left, root.right = invert_tree(root.right), invert_tree(root.left)
        return root
    ```

    *Python Iterative (Naive/Alternative):*
    ```python
    from collections import deque
    def invert_tree_naive(root: TreeNode) -> TreeNode:
        if not root:
            return None
        queue = deque([root])
        while queue:
            node = queue.popleft()
            node.left, node.right = node.right, node.left
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        return root
    ```

    Wait, the prompt asks for `TreeNode_naive` and `TreeNode_optimal` in the template. I'll use those names if it's a strict requirement for "MUST be exactly like this", but usually, "signatures... match... starter code" takes precedence. I'll name them `invert_tree_naive` and `invert_tree_optimal` but follow the header format exactly.

    *Refining Java code:*
    ```java
    package trees;

    public class InvertBinaryTree {
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

        public TreeNode invertTree(TreeNode root) {
            if (root == null) {
                return null;
            }
            TreeNode temp = root.left;
            root.left = invertTree(root.right);
            root.right = invertTree(temp);
            return root;
        }
    }
    ```

    Final check on complexities:
    Recursive: Time O(N), Space O(H).
    Iterative: Time O(N), Space O(W).

    Wait, is Iterative "Naive"? No, but the prompt asks for "brute-force / naive / alternative". BFS is an alternative.

    Let's execute the final raw output.

    *Self-Correction on naming again:* The prompt says "The format... MUST be exactly like this", and the example shows `def TreeNode_naive(...)`. However, it also says "Ensure the signatures... match... starter code". Starter code is `invert_tree`. If I name it `TreeNode_naive`, I violate the starter code signature. If I name it `invert_tree`, I violate the "MUST be exactly like this" format. Usually, "signatures match starter code" is the functional requirement for the test runner. I will name them `invert_tree_naive` and `invert_tree_optimal`.

    Actually, let's look at the prompt's example again:
    `# --- APPROACH 1: Naive (Brute Force) ---`
    `def TreeNode_naive(...):`
    This is likely just a placeholder. I'll use the correct function name.

    Final polish:
    Approach 1 (Iterative BFS):
    Time Complexity: O(N)
    Space Complexity: O(N)
    Explanation: Uses a queue to traverse the tree level by level, swapping children at each node.

    Approach 2 (Recursive DFS):
    Time Complexity: O(N)
    Space Complexity: O(H)
    Explanation: The most elegant and direct approach using recursion to swap child pointers from the bottom up. Optimal because it minimizes overhead and has a better average space complexity than BFS on balanced trees.

    Wait, "optimal" usually refers to the best possible time and space. DFS is O(N) time and O(H) space. BFS is O(N) time and O(W) space. In a skewed tree, H=N, W=1. In a balanced tree, H=logN, W=N/2. Both are O(N) worst case. But DFS is generally considered the "standard" optimal for this problem.

    One last check: "Return ONLY the raw Python code." "Do NOT wrap it in markdown block formatting".

    Let's go.class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach uses an iterative Breadth-First Search (BFS) with a queue to traverse the tree level by level. 
# While not "brute force" in terms of time complexity, it is an alternative to the standard recursive method.
from collections import deque

def invert_tree_naive(root: TreeNode) -> TreeNode:
    if not root:
        return None
    
    queue = deque([root])
    while queue:
        current = queue.popleft()
        
        # Swap the children
        current.left, current.right = current.right, current.left
        
        # Add non-null children to the queue for further processing
        if current.left:
            queue.append(current.left)
        if current.right:
            queue.append(current.right)
            
    return root

# --- APPROACH 2: Optimal (Recursive DFS) ---
# Time Complexity: O(N)
# Space Complexity: O(H)
# This approach uses a recursive Depth-First Search (DFS). It is optimal because it visits each node exactly once 
# and utilizes the call stack for traversal, resulting in a space complexity proportional to the height of the tree (H), 
# which is O(log N) for balanced trees and O(N) for skewed trees.
def invert_tree(root: TreeNode) -> TreeNode:
    # Base case: if the node is None, we've reached a leaf's child
    if not root:
        return None
    
    # Swap the left and right children
    # We recursively call invert_tree on the children before or during the swap
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    
    return root

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

import java.util.*;

public class InvertBinaryTree {
    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        
        TreeNode() {}
        TreeNode(int val) { this.val = val; }
        TreeNode(int val, TreeNode left, TreeNode right) {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }

    /**
     * Inverts a binary tree by swapping left and right children recursively.
     * Time Complexity: O(N) - where N is the number of nodes in the tree.
     * Space Complexity: O(H) - where H is the height of the tree.
     */
    public TreeNode invertTree(TreeNode root) {
        if (root == null) {
            return null;
        }
        
        // Store left child in a temporary variable to avoid losing reference
        TreeNode tempLeft = root.left;
        
        // Swap and recurse
        root.left = invertTree(root.right);
        root.right = invertTree(tempLeft);
        
        return root;
    }
}
"""

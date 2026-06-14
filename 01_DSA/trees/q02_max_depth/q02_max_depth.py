"""
Challenge: q02_max_depth
Difficulty: Easy
Link: https://leetcode.com/problems/maximum-depth-of-binary-tree/

Problem:
Max depth.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

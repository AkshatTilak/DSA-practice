"""
Challenge: q10_kth_smallest
Difficulty: Medium
Link: https://leetcode.com/problems/kth-smallest-element-in-a-bst/

Problem:
Find Kth smallest.
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
"""
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
"""

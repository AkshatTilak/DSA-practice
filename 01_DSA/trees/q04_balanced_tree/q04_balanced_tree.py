"""
Challenge: q04_balanced_tree
Difficulty: Easy
Link: https://leetcode.com/problems/balanced-binary-tree/

Problem:
Check balance.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2)
# Space Complexity: O(H) where H is the height of the tree (recursion stack).
# This approach calculates the height of left and right subtrees for every single node. 
# In the worst case (a skewed tree), the height function is called repeatedly on the same nodes, 
# leading to quadratic time complexity.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_naive(root: TreeNode) -> bool:
    def get_height(node):
        if not node:
            return 0
        return 1 + max(get_height(node.left), get_height(node.right))

    if not root:
        return True
    
    left_h = get_height(root.left)
    right_h = get_height(root.right)
    
    # Check current node balance and recursively check child nodes
    if abs(left_h - right_h) <= 1 and solve_naive(root.left) and solve_naive(root.right):
        return True
    
    return False

# --- APPROACH 2: Optimal (Bottom-Up DFS) ---
# Time Complexity: O(N)
# Space Complexity: O(H) where H is the height of the tree.
# This approach uses a post-order traversal to calculate height and balance status simultaneously.
# Instead of calling a separate height function for every node, it passes the height up the 
# recursion tree. If any subtree is found to be unbalanced, it returns a sentinel value (-1), 
# allowing the failure to propagate immediately to the root. This ensures each node is visited exactly once.

def solve_optimal(root: TreeNode) -> bool:
    def check_balance(node):
        if not node:
            return 0
        
        # Post-order: check left subtree
        left_height = check_balance(node.left)
        if left_height == -1:
            return -1
        
        # Post-order: check right subtree
        right_height = check_balance(node.right)
        if right_height == -1:
            return -1
        
        # Check balance of current node
        if abs(left_height - right_height) > 1:
            return -1
        
        # Return height of current node if balanced
        return max(left_height, right_height) + 1

    return check_balance(root) != -1

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode(int x) { val = x; }
}

public class BalancedTree {
    /**
     * Checks if a binary tree is height-balanced.
     * Time Complexity: O(N)
     * Space Complexity: O(H)
     */
    public boolean isBalanced(TreeNode root) {
        return checkHeight(root) != -1;
    }

    private int checkHeight(TreeNode node) {
        if (node == null) {
            return 0;
        }

        int leftHeight = checkHeight(node.left);
        if (leftHeight == -1) return -1;

        int rightHeight = checkHeight(node.right);
        if (rightHeight == -1) return -1;

        if (Math.abs(leftHeight - rightHeight) > 1) {
            return -1;
        }

        return Math.max(leftHeight, rightHeight) + 1;
    }

    public static void main(String[] args) {
        BalancedTree solution = new BalancedTree();
        
        // Example: Balanced Tree
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        System.out.println("Is balanced: " + solution.isBalanced(root)); // Expected: true
    }
}
"""

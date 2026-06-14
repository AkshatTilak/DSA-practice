"""
Challenge: q09_validate_bst
Difficulty: Medium
Link: https://leetcode.com/problems/validate-binary-search-tree/

Problem:
Validate BST values.
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
# This approach performs an in-order traversal of the tree and stores the result in a list. 
# Since an in-order traversal of a valid BST must yield a strictly increasing sequence, 
# we simply check if the resulting list is sorted and contains no duplicates.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_naive(root: TreeNode) -> bool:
    inorder_list = []
    
    def traverse(node):
        if not node:
            return
        traverse(node.left)
        inorder_list.append(node.val)
        traverse(node.right)
        
    traverse(root)
    
    for i in range(1, len(inorder_list)):
        if inorder_list[i] <= inorder_list[i-1]:
            return False
            
    return True

# --- APPROACH 2: Optimal (Recursive Range Validation) ---
# Time Complexity: O(N)
# Space Complexity: O(H)
# This approach is optimal because it validates each node exactly once and uses space 
# proportional only to the height of the tree (H) for the recursion stack, rather than 
# storing all node values in a separate list. It maintains a dynamic range (low, high) 
# that every node's value must fall within, ensuring that all descendants of a node 
# satisfy the BST property relative to all their ancestors.

def solve_optimal(root: TreeNode) -> bool:
    def validate(node, low, high):
        # An empty node is valid
        if not node:
            return True
        
        # The current node's value must be strictly between low and high
        if not (low < node.val < high):
            return False
        
        # For the left child, the upper bound becomes the current node's value
        # For the right child, the lower bound becomes the current node's value
        return validate(node.left, low, node.val) and validate(node.right, node.val, high)
    
    # Start with the full range of possible values
    return validate(root, float('-inf'), float('inf'))

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

public class ValidateBst {
    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int val) { this.val = val; }
    }

    public boolean isValidBST(TreeNode root) {
        return validate(root, null, null);
    }

    private boolean validate(TreeNode node, Integer low, Integer high) {
        // Base case: an empty tree is a valid BST
        if (node == null) {
            return true;
        }

        // If a lower bound is set, node value must be strictly greater than it
        if (low != null && node.val <= low) {
            return false;
        }

        // If an upper bound is set, node value must be strictly less than it
        if (high != null && node.val >= high) {
            return false;
        }

        // Recursively check left subtree with updated high bound
        // and right subtree with updated low bound
        return validate(node.left, low, node.val) && validate(node.right, node.val, high);
    }

    public static void main(String[] args) {
        ValidateBst solver = new ValidateBst();
        TreeNode root = new TreeNode(2);
        root.left = new TreeNode(1);
        root.right = new TreeNode(3);
        System.out.println(solver.isValidBST(root)); // Output: true
    }
}
"""

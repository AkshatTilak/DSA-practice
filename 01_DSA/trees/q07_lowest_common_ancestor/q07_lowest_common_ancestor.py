"""
Challenge: q07_lowest_common_ancestor
Difficulty: Easy
Link: https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/

Problem:
LCA BST.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
    # Time Complexity: ...
    # Space Complexity: ...
    # [Explanation]
    def solve_naive(...):
        ...

    # --- APPROACH 2: Optimal ([Algorithm/Data Structure used]) ---
    # Time Complexity: ...
    # Space Complexity: ...
    # [Explanation]
    def solve_optimal(...):
        ...

    # --- APPROACH 3: Secondary Language (Java Variant) ---
    """
    ...
    """

    Final check on logic:
    If `p.val` and `q.val` are both smaller than `root.val`, the LCA must be in the left subtree.
    If both are larger, the LCA must be in the right subtree.
    If one is smaller and one is larger, or if `root` is either `p` or `q`, the current `root` is the LCA.
    Correct.

    Complexity:
    Time: $O(H)$ - we traverse down one path from root to LCA.
    Space: $O(1)$ - iterative.

    Naive (General Binary Tree) Complexity:
    Time: $O(N)$ - must potentially visit all nodes.
    Space: $O(H)$ - recursive call stack.

    Let's write it.class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(H)
# This approach treats the BST as a general binary tree, ignoring the sorted property. 
# It recursively searches for p and q in the left and right subtrees. 
# If a node receives non-null returns from both children, it is the Lowest Common Ancestor.
def solve_naive(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    if not root or root == p or root == q:
        return root

    left = solve_naive(root.left, p, q)
    right = solve_naive(root.right, p, q)

    if left and right:
        return root
    
    return left if left else right

# --- APPROACH 2: Optimal (BST Iterative Traversal) ---
# Time Complexity: O(H)
# Space Complexity: O(1)
# This approach leverages the Binary Search Tree (BST) property: for any node, 
# values in the left subtree are smaller and values in the right subtree are larger.
# We traverse from the root: if both p and q are smaller than the current node, the LCA must be in the left subtree.
# If both are larger, the LCA must be in the right subtree.
# The first node we encounter that splits the paths to p and q (or is equal to either) is the LCA.
# This is optimal because it avoids unnecessary visits to subtrees and uses constant extra space.
def solve_optimal(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    current = root
    while current:
        if p.val < current.val and q.val < current.val:
            current = current.left
        elif p.val > current.val and q.val > current.val:
            current = current.right
        else:
            # We have found the split point or one of the nodes is the ancestor of the other
            return current
    return None

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode(int x) { val = x; }
}

public class LowestCommonAncestor {
    /**
     * Finds the lowest common ancestor of two nodes in a BST.
     * Time Complexity: O(H) where H is the height of the tree.
     * Space Complexity: O(1).
     */
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        TreeNode current = root;
        
        while (current != null) {
            if (p.val < current.val && q.val < current.val) {
                // Both nodes are in the left subtree
                current = current.left;
            } else if (p.val > current.val && q.val > current.val) {
                // Both nodes are in the right subtree
                current = current.right;
            } else {
                // This is the split point, or current is either p or q
                return current;
            }
        }
        return null;
    }
}
"""

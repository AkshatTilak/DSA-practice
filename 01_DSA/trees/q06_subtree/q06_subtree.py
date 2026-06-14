"""
Challenge: q06_subtree
Difficulty: Easy
Link: https://leetcode.com/problems/subtree-of-another-tree/

Problem:
Subtree match.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N * M)
# Space Complexity: O(max(H_N, H_M))
# This approach iterates through every node in the main tree (root) and, for each node, 
# checks if the subtree rooted at that node is identical to the target subtree (subRoot) 
# using a helper function `is_same_tree`. N is the number of nodes in the root tree, 
# M is the number of nodes in the subRoot tree, and H is the height of the trees.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_naive(root: TreeNode, subRoot: TreeNode) -> bool:
    def is_same_tree(p: TreeNode, q: TreeNode) -> bool:
        if not p and not q:
            return True
        if not p or not q:
            return False
        if p.val != q.val:
            return False
        return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)

    if not subRoot:
        return True
    if not root:
        return False
    
    if is_same_tree(root, subRoot):
        return True
    
    return solve_naive(root.left, subRoot) or solve_naive(root.right, subRoot)

# --- APPROACH 2: Optimal (Tree Serialization) ---
# Time Complexity: O(N + M)
# Space Complexity: O(N + M)
# This approach converts both the main tree and the subtree into unique string 
# representations using a preorder traversal. By including markers for null nodes 
# and delimiters for node values, each tree structure is uniquely mapped to a string. 
# We then simply check if the subRoot's serialized string is a substring of the root's 
# serialized string. This is optimal because it reduces the problem to a linear 
# string search, visiting each node exactly once.

def solve_optimal(root: TreeNode, subRoot: TreeNode) -> bool:
    def serialize(node: TreeNode) -> str:
        if not node:
            return ",#,"
        # Wrap value in commas to ensure unique matching (e.g., avoiding "1" matching "11")
        return f",{node.val},{serialize(node.left)}{serialize(node.right)}"

    # A null subtree is technically a subtree of any tree
    if not subRoot:
        return True
    if not root:
        return False

    s_root = serialize(root)
    s_sub = serialize(subRoot)
    
    return s_sub in s_root

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

class TreeNode {
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

public class Subtree {
    /**
     * Optimal approach using Serialization.
     * Time Complexity: O(N + M)
     * Space Complexity: O(N + M)
     */
    public boolean isSubtree(TreeNode root, TreeNode subRoot) {
        if (subRoot == null) return true;
        if (root == null) return false;

        StringBuilder sbRoot = new StringBuilder();
        StringBuilder sbSub = new StringBuilder();
        
        serialize(root, sbRoot);
        serialize(subRoot, sbSub);
        
        return sbRoot.toString().contains(sbSub.toString());
    }

    private void serialize(TreeNode node, StringBuilder sb) {
        if (node == null) {
            sb.append(",#,");
            return;
        }
        // Use delimiters to prevent partial value matching (e.g., 1 matching 11)
        sb.append(",").append(node.val).append(",");
        serialize(node.left, sb);
        serialize(node.right, sb);
    }

    public static void main(String[] args) {
        Subtree sol = new Subtree();
        TreeNode root = new TreeNode(3, new TreeNode(4, new TreeNode(1), new TreeNode(2)), new TreeNode(5));
        TreeNode subRoot = new TreeNode(4, new TreeNode(1), new TreeNode(2));
        System.out.println(sol.isSubtree(root, subRoot)); // Expected: true
    }
}
"""

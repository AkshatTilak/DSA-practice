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

def invert_tree_optimal(root):
    if not root: return None
    root.left, root.right = invert_tree_optimal(root.right), invert_tree_optimal(root.left)
    return root

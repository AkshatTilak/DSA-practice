INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/invert-binary-tree/',
    'description': 'Invert a binary tree (swap left and right child recursively).',
    'groups': ['Tree'],
    'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef invert_tree(root: TreeNode) -> TreeNode:\n    # Write your solution here\n    pass',
    'solutions': 'def invert_tree_optimal(root):\n    if not root: return None\n    root.left, root.right = invert_tree_optimal(root.right), invert_tree_optimal(root.left)\n    return root',
    'test_code': 'def test_invert():\n    pass',
    'readme_content': '# Invert Binary Tree\nRecursive traversal swaps.',
}

"""
Challenge: q08_level_order
Difficulty: Medium
Link: https://leetcode.com/problems/binary-tree-level-order-traversal/

Problem:
BFS traversal.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N * H) where N is the number of nodes and H is the height of the tree.
# Space Complexity: O(H) for the recursion stack.
# This approach uses a recursive method to traverse the tree multiple times. 
# It first calculates the height of the tree and then iterates from level 1 to height, 
# performing a DFS to find all nodes at that specific level.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_naive(root):
    if not root:
        return []

    def get_height(node):
        if not node:
            return 0
        return 1 + max(get_height(node.left), get_height(node.right))

    def get_nodes_at_level(node, level, current_level_list):
        if not node:
            return
        if level == 1:
            current_level_list.append(node.val)
        elif level > 1:
            get_nodes_at_level(node.left, level - 1, current_level_list)
            get_nodes_at_level(node.right, level - 1, current_level_list)

    height = get_height(root)
    result = []
    for i in range(1, height + 1):
        level_list = []
        get_nodes_at_level(root, i, level_list)
        result.append(level_list)
    
    return result

# --- APPROACH 2: Optimal (Queue-based BFS) ---
# Time Complexity: O(N) where N is the number of nodes. Each node is visited exactly once.
# Space Complexity: O(W) where W is the maximum width of the tree. In a perfect binary tree, W ≈ N/2.
# This approach is optimal because it uses a queue to process the tree level-by-level in a single pass.
# By tracking the queue size at the start of each level, we can separate nodes into their respective levels.
from collections import deque

def solve_optimal(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
        
    return result

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

import java.util.*;

public class LevelOrder {
    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int val) { this.val = val; }
    }

    public List<List<Integer>> solveOptimal(TreeNode root) {
        if (root == null) {
            return new ArrayList<>();
        }

        List<List<Integer>> result = new ArrayList<>();
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<Integer> currentLevel = new ArrayList<>();

            for (int i = 0; i < levelSize; i++) {
                TreeNode currentNode = queue.poll();
                currentLevel.add(currentNode.val);

                if (currentNode.left != null) {
                    queue.add(currentNode.left);
                }
                if (currentNode.right != null) {
                    queue.add(currentNode.right);
                }
            }
            result.add(currentLevel);
        }

        return result;
    }

    public static void main(String[] args) {
        LevelOrder sol = new LevelOrder();
        TreeNode root = new TreeNode(3);
        root.left = new TreeNode(9);
        root.right = new TreeNode(20);
        root.right.left = new TreeNode(15);
        root.right.right = new TreeNode(7);

        System.out.println(sol.solveOptimal(root)); // Expected: [[3], [9, 20], [15, 7]]
    }
}
"""

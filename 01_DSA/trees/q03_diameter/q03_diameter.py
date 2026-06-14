"""
Challenge: q03_diameter
Difficulty: Easy
Link: https://leetcode.com/problems/diameter-of-binary-tree/

Problem:
Tree diameter.
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
# Space Complexity: O(H) where H is the height of the tree.
# This approach calculates the height of the left and right subtrees for every single node 
# in the tree independently. For each node, it computes the diameter passing through it 
# and recursively finds the maximum diameter in its subtrees.

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def get_height(node):
    if not node:
        return 0
    return 1 + max(get_height(node.left), get_height(node.right))

def solve_naive(root):
    if not root:
        return 0
    
    # Diameter passing through the current root
    current_diameter = get_height(root.left) + get_height(root.right)
    
    # Maximum diameter found in left or right subtrees
    left_diameter = solve_naive(root.left)
    right_diameter = solve_naive(root.right)
    
    return max(current_diameter, left_diameter, right_diameter)

# --- APPROACH 2: Optimal (Bottom-Up DFS) ---
# Time Complexity: O(N)
# Space Complexity: O(H) where H is the height of the tree.
# This approach is optimal because it visits each node exactly once. Instead of 
# recomputing heights, it uses a bottom-up recursion (Post-order traversal) that 
# returns the height of the current subtree to its parent while simultaneously 
# updating the global diameter. This reduces the time complexity from quadratic to linear.

def solve_optimal(root):
    max_diameter = 0

    def calculate_height(node):
        nonlocal max_diameter
        if not node:
            return 0
        
        # Recursively find the height of left and right subtrees
        left_height = calculate_height(node.left)
        right_height = calculate_height(node.right)
        
        # The diameter at the current node is the sum of heights of its children
        max_diameter = max(max_diameter, left_height + right_height)
        
        # Return the height of the current node to the parent
        return 1 + max(left_height, right_height)

    calculate_height(root)
    return max_diameter

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

public class Diameter {
    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int val) { this.val = val; }
    }

    private int maxDiameter = 0;

    public int solveOptimal(TreeNode root) {
        maxDiameter = 0;
        calculateHeight(root);
        return maxDiameter;
    }

    private int calculateHeight(TreeNode node) {
        if (node == null) {
            return 0;
        }

        int leftHeight = calculateHeight(node.left);
        int rightHeight = calculateHeight(node.right);

        // Update the global maximum diameter found so far
        maxDiameter = Math.max(maxDiameter, leftHeight + rightHeight);

        // Return height of the current node
        return 1 + Math.max(leftHeight, rightHeight);
    }

    public static void main(String[] args) {
        Diameter solver = new Diameter();
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        root.left.left = new TreeNode(4);
        root.left.right = new TreeNode(5);
        
        System.out.println("Diameter: " + solver.solveOptimal(root)); // Output: 3
    }
}
"""

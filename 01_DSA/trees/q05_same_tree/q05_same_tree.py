"""
Challenge: q05_same_tree
Difficulty: Easy
Link: https://leetcode.com/problems/same-tree/

Problem:
Verify same tree.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---`
    - `# Time Complexity: O(...)`
    - `# Space Complexity: O(...)`
    - `def solve_naive(p, q):`
    - `# --- APPROACH 2: Optimal ([Algorithm/Data Structure used]) ---`
    - `# Time Complexity: O(...)`
    - `# Space Complexity: O(...)`
    - `def solve_optimal(p, q):`
    - `# --- APPROACH 3: Secondary Language (Java Variant) ---`
    - `""" ... """`

    Let's make sure the Java code includes the `TreeNode` class.

    *Java code structure:*
    ```java
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

    public class SameTree {
        public boolean isSameTree(TreeNode p, TreeNode q) {
            if (p == null && q == null) return true;
            if (p == null || q == null || p.val != q.val) return false;
            return isSameTree(p.left, q.left) && isSameTree(p.right, q.right);
        }
    }
    ```

    *Wait, Python `solve_naive` memory:* Using `+` for lists in recursion creates many intermediate lists. To be slightly more "production grade" while remaining "naive", I'll use a helper with a list passed by reference.

    ```python
    def solve_naive(p, q):
        def get_structure(node, res):
            if not node:
                res.append(None)
                return
            res.append(node.val)
            get_structure(node.left, res)
            get_structure(node.right, res)
        
        list_p, list_q = [], []
        get_structure(p, list_p)
        get_structure(q, list_q)
        return list_p == list_q
    ```
    This is still $O(N)$ time and $O(N)$ space, but more efficient than the `+` operator.

    *Refining Optimal:*
    Standard recursion is optimal for this problem.

    *Final check on instructions:* "Return ONLY the raw Python code. Do NOT wrap it in markdown block formatting... and do NOT write any conversational text".

    One last check on the Python `TreeNode` definition. I'll define it before the functions to make the code snippet self-contained and valid.

    Wait, should I include `TreeNode` class in Python? Usually, these tests expect the functions to be defined. If I define the class, it's safer.

    ```python
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right
    ```

    Okay, let's assemble.class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach serializes both binary trees into lists using a pre-order traversal, including markers for None children.
# It then compares the two resulting lists for equality. While it works, it requires O(N) auxiliary space regardless of tree height.
def solve_naive(p, q):
    def serialize(node, result):
        if not node:
            result.append(None)
            return
        result.append(node.val)
        serialize(node.left, result)
        serialize(node.right, result)
    
    list_p, list_q = [], []
    serialize(p, list_p)
    serialize(q, list_q)
    return list_p == list_q

# --- APPROACH 2: Optimal (Recursive DFS) ---
# Time Complexity: O(N)
# Space Complexity: O(H)
# This approach uses a recursive Depth-First Search (DFS) to compare the trees node by node.
# It is optimal because it visits each node at most once and short-circuits (returns False) immediately upon finding a mismatch.
# The space complexity is proportional to the height of the tree (H) due to the recursion stack, which is O(log N) for balanced trees and O(N) for skewed trees.
def solve_optimal(p, q):
    # If both nodes are None, the trees are identical at this position
    if not p and not q:
        return True
    # If one node is None or the values differ, the trees are not identical
    if not p or not q or p.val != q.val:
        return False
    # Recursively check left and right subtrees
    return solve_optimal(p.left, q.left) and solve_optimal(p.right, q.right)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package trees;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

public class SameTree {
    /**
     * Verifies if two binary trees are the same.
     * Time Complexity: O(N)
     * Space Complexity: O(H)
     */
    public boolean isSameTree(TreeNode p, TreeNode q) {
        // If both nodes are null, they are identical
        if (p == null && q == null) {
            return true;
        }
        // If one is null or values differ, they are not identical
        if (p == null || q == null || p.val != q.val) {
            return false;
        }
        // Recurse for left and right children
        return isSameTree(p.left, q.left) && isSameTree(p.right, q.right);
    }
}
"""

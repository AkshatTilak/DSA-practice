INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/same-tree/',
    'description': 'Verify same tree.',
    'groups': ['Tree'],
    'readme_content': """# Same Tree (q05_same_tree)

## 1. Overview & Problem Explanation
The **Same Tree** problem asks us to determine if two binary trees are identical. Two binary trees are considered the same if:
1. They have the **exact same structure**.
2. Every corresponding node in both trees has the **same value**.

### Input/Output
- **Input**: Two root nodes of binary trees, `p` and `q`.
- **Output**: A boolean value (`True` if the trees are identical, `False` otherwise).

### Constraints & Edge Cases
- **Empty Trees**: If both `p` and `q` are `null`, they are identical.
- **Structural Mismatch**: If one tree has a node where the other has `null`, they are not identical.
- **Value Mismatch**: If both have nodes at the same position but the values differ, they are not identical.
- **Constraints**: The number of nodes is typically small (up to 100), meaning an $O(N)$ solution is highly efficient.

---

## 2. Core Concepts & Data Structures
The most effective way to solve this problem is using **Depth-First Search (DFS)** via **Recursion**.

### Why Recursion?
Binary trees are recursive data structures by nature (a tree consists of a root node and two sub-trees, which are themselves trees). Therefore, a recursive approach allows us to break the problem down into the smallest possible sub-problems:
- "Are these two current nodes the same?"
- "Are their left children the same?"
- "Are their right children the same?"

### Algorithmic Pattern: Divide and Conquer
We divide the problem by checking the root and then delegating the check for the left and right subtrees to recursive calls. If all three conditions (root, left, right) are true, the trees are identical.

---

## 3. Step-by-Step Logic

### The Recursive Strategy
To determine if two trees are the same, we follow these logical steps at every node:

1. **Base Case 1: Both are Null**
   If both `p` and `q` are `None`, we have reached the leaf ends of both trees simultaneously. This is a match. Return `True`.
   
2. **Base Case 2: One is Null, One is Not**
   If one node is `None` but the other is not, the structures differ. Return `False`.

3. **Base Case 3: Value Mismatch**
   If both nodes exist but `p.val != q.val`, the trees are not identical. Return `False`.

4. **Recursive Step: Check Subtrees**
   If the current nodes are identical, we must ensure their children are also identical. We recursively call the function for:
   - The left child of `p` and the left child of `q`.
   - The right child of `p` and the right child of `q`.
   - Both must return `True` for the current subtree to be considered identical.

### Dry Run Example
**Input**: `p = [1, 2, 3]`, `q = [1, 2, 3]`
1. `solve(p, q)`: Both are not null, values are `1 == 1`. Proceed to children.
2. `solve(p.left, q.left)`: Both are not null, values are `2 == 2`. Proceed to children.
   - `solve(p.left.left, q.left.left)`: Both are `None` $\rightarrow$ **True**.
   - `solve(p.left.right, q.left.right)`: Both are `None` $\rightarrow$ **True**.
   - Result for node `2`: `True && True` $\rightarrow$ **True**.
3. `solve(p.right, q.right)`: Both are not null, values are `3 == 3`. Proceed to children.
   - `solve(p.right.left, q.right.left)`: Both are `None` $\rightarrow$ **True**.
   - `solve(p.right.right, q.right.right)`: Both are `None` $\rightarrow$ **True**.
   - Result for node `3`: `True && True` $\rightarrow$ **True**.
4. Final Result: `True (Root) && True (Left) && True (Right)` $\rightarrow$ **True**.

---

## 4. Implementation

```python
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isSameTree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    \"\"\"
    Optimal solution using recursive DFS to verify if two binary trees are identical.
    \"\"\"
    # 1. Both nodes are null: they are identical at this position
    if not p and not q:
        return True
    
    # 2. One node is null or values differ: they are not identical
    if not p or not q or p.val != q.val:
        return False
    
    # 3. Recursively check left and right subtrees
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)

# Wrapper for the challenge format
def solve():
    # Example usage
    p = TreeNode(1, TreeNode(2), TreeNode(3))
    q = TreeNode(1, TreeNode(2), TreeNode(3))
    print(f"Are trees same? {isSameTree(p, q)}") # Expected: True

if __name__ == "__main__":
    solve()
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive DFS** | $O(N)$ | $O(H)$ | Time is $O(N)$ because we visit every node exactly once. Space is $O(H)$ due to the recursion stack, where $H$ is the height of the tree. |

- **Time Complexity $O(N)$**: In the worst case (where the trees are identical), we must traverse every single node in both trees to verify equality.
- **Space Complexity $O(H)$**: The space used is proportional to the depth of the recursion. In a balanced tree, $H = \log N$. In a skewed tree (like a linked list), $H = N$.

---

## 6. Real-World Applications

The "Same Tree" pattern—comparing structural integrity and data across hierarchical models—is used in several critical software systems:

1. **Merkle Trees (Blockchain & Git)**: 
   Git uses a similar concept to compare directory structures. Instead of comparing every file, it compares hashes of tree nodes. If the root hashes are the same, the entire directory tree is identical.
   
2. **Virtual DOM Diffing (React.js)**: 
   Modern UI frameworks like React compare a "Virtual DOM" (a tree structure) with a previous version to determine exactly which parts of the UI need to be updated, minimizing expensive browser repaints.

3. **Compiler Optimization**: 
   Compilers often represent code as an **Abstract Syntax Tree (AST)**. To detect redundant code or perform "common subexpression elimination," the compiler checks if two AST sub-trees are identical.

4. **File System Synchronization**: 
   Tools like `rsync` or cloud backup services compare directory trees to identify which folders are identical and which need to be synchronized.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---`
    - `# Time Complexity: O(...)`
    - `# Space Complexity: O(...)`
    - `def solve_naive(p, q):`
    - `# --- APPROACH 2: Optimal ([Algorithm/Data Structure used]) ---`
    - `# Time Complexity: O(...)`
    - `# Space Complexity: O(...)`
    - `def solve_optimal(p, q):`
    - `# --- APPROACH 3: Secondary Language (Java Variant) ---`
    - `\"\"\" ... \"\"\"`

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
\"\"\"
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
\"\"\"""",
}

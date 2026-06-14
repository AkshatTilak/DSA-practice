INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/validate-binary-search-tree/',
    'description': 'Validate BST values.',
    'groups': ['Tree', 'Binary Search'],
    'readme_content': """# Validate BST

## 1. Overview & Problem Explanation

The objective of this challenge is to determine whether a given binary tree is a valid **Binary Search Tree (BST)**. 

### What is a Binary Search Tree?
A binary tree is defined as a BST if it satisfies the following properties for **every** node in the tree:
1. The **left subtree** of a node contains only nodes with keys **strictly less than** the node's key.
2. The **right subtree** of a node contains only nodes with keys **strictly greater than** the node's key.
3. Both the left and right subtrees must also be binary search trees.

### The Common Pitfall
A frequent mistake beginners make is simply checking if a node's value is greater than its immediate left child and smaller than its immediate right child. **This is insufficient.** 

**Example of an Invalid BST that passes the "immediate child" check:**
```text
      10
     /  \
    5    15
        /  \
       6    20
```
In this case, the node `6` is indeed smaller than its parent `15`, but it is located in the right subtree of the root `10`. Since $6 < 10$, this violates the BST property (all nodes in the right subtree of `10` must be $> 10$).

### Inputs, Outputs, and Constraints
- **Input**: The root of a binary tree.
- **Output**: A boolean value (`True` if it is a valid BST, `False` otherwise).
- **Constraints**:
    - The number of nodes can range from $0$ to $10^4$.
    - Node values can be anywhere between $-2^{31}$ and $2^{31}-1$.
    - Edge cases include:
        - Empty tree (usually considered a valid BST).
        - A single node tree (valid).
        - Trees with duplicate values (invalid, as the property requires *strictly* less/greater).

---

## 2. Core Concepts & Data Structures

### Recursive Range Constraints (Top-Down DFS)
To solve the "pitfall" mentioned above, we must pass down a **valid range** (a minimum and a maximum bound) that every node in a specific subtree must fall within.
- As we move to the **left child**, we update the **upper bound** to the current node's value.
- As we move to the **right child**, we update the **lower bound** to the current node's value.

### In-Order Traversal Property
One of the most powerful properties of a BST is that an **In-Order Traversal** (Left $\rightarrow$ Root $\rightarrow$ Right) visits the nodes in **strictly increasing order**.
- If we perform an in-order traversal and find that the current node's value is less than or equal to the previously visited node's value, the tree is not a valid BST.

### Why these choices?
- **DFS (Depth First Search)** is the natural choice for tree validation because the BST property is hierarchical.
- **Range Constraints** allow us to validate the tree in a single pass without needing extra space to store the traversal.
- **In-Order Traversal** transforms a structural tree problem into a linear sequence problem, which is conceptually simpler to verify.

---

## 3. Step-by-Step Logic

### Approach 1: Recursive Range Validation (Optimal)
This approach uses a helper function that carries the `low` and `high` boundaries.

1. **Initialization**: Start the recursion at the root with the range $(-\infty, +\infty)$.
2. **Base Case**: If the current node is `None`, we have reached a leaf's child. Return `True`.
3. **Validation**: Check if the current node's value $V$ satisfies: $\text{low} < V < \text{high}$.
    - If $V \le \text{low}$ or $V \ge \text{high}$, return `False`.
4. **Recursive Step**:
    - For the **left child**, the new range is $(\text{low}, V)$.
    - For the **right child**, the new range is $(V, \text{high})$.
5. **Aggregation**: The tree is valid only if both the left and right subtrees are valid.

### Approach 2: In-Order Traversal
1. **State Tracking**: Maintain a variable `prev` initialized to $-\infty$.
2. **Traversal**: Perform a standard recursive In-Order traversal.
3. **Comparison**:
    - Visit Left subtree.
    - Compare current node value with `prev`. If $\text{current} \le \text{prev}$, return `False`.
    - Update `prev` to the current node value.
    - Visit Right subtree.

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

def solve_optimal(root: Optional[TreeNode]) -> bool:
    \"\"\"
    Validates a BST using the recursive range constraint method.
    Time Complexity: O(N)
    Space Complexity: O(H) where H is tree height.
    \"\"\"
    def validate(node, low=-float('inf'), high=float('inf')):
        # An empty node is technically a valid BST
        if not node:
            return True
        
        # The current node's value must be strictly between low and high
        if not (low < node.val < high):
            return False
        
        # Left subtree: values must be < node.val
        # Right subtree: values must be > node.val
        return (validate(node.left, low, node.val) and 
                validate(node.right, node.val, high))

    return validate(root)

def solve_inorder(root: Optional[TreeNode]) -> bool:
    \"\"\"
    Validates a BST using the In-Order Traversal property.
    Time Complexity: O(N)
    Space Complexity: O(H)
    \"\"\"
    prev = -float('inf')
    
    def inorder(node):
        nonlocal prev
        if not node:
            return True
        
        # Visit Left
        if not inorder(node.left):
            return False
        
        # Visit Root: must be strictly increasing
        if node.val <= prev:
            return False
        prev = node.val
        
        # Visit Right
        return inorder(node.right)

    return inorder(root)
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Recursive Range** | $O(N)$ | $O(H)$ | We visit every node exactly once. Space is used by the recursion stack, which is proportional to the height $H$. |
| **In-Order Traversal** | $O(N)$ | $O(H)$ | Every node is visited once. Space is used by the recursion stack. |

- **Note on $H$**: In a balanced tree, $H = \log N$. In a skewed tree (worst case), $H = N$.

---

## 6. Real-World Applications

The logic of validating and maintaining a BST is foundational to several high-performance systems:

1. **Database Indexing**: Many databases use B-Trees (a generalization of BSTs) to index data. Validating the BST property is similar to ensuring that index pages are correctly sorted for $O(\log N)$ lookups.
2. **Filesystems**: Directory structures in some operating systems use tree-like structures to organize files and metadata, ensuring fast retrieval of file paths.
3. **Set and Map Implementations**: In languages like Java (`TreeSet`, `TreeMap`) or C++ (`std::set`, `std::map`), the underlying data structure is typically a Red-Black Tree (a self-balancing BST). The BST property is what allows these collections to stay sorted.
4. **Compiler Optimization**: Abstract Syntax Trees (ASTs) are used by compilers to represent the structure of program code. While not always BSTs, the recursive validation pattern used here is exactly how compilers check for semantic errors or type consistency across a code tree.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

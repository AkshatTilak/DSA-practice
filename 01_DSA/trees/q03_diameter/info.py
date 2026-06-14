INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/diameter-of-binary-tree/',
    'description': 'Tree diameter.',
    'groups': ['Tree'],
    'readme_content': """# Diameter of Binary Tree (q03_diameter)

## 📌 Overview & Problem Explanation

The **Diameter of a Binary Tree** is defined as the length of the longest path between any two nodes in a tree. This path may or may not pass through the root of the tree. 

The "length" of a path is represented by the **number of edges** between the nodes, not the number of nodes themselves.

### Key Constraints & Considerations:
- **Input**: The root of a binary tree.
- **Output**: An integer representing the length of the diameter.
- **Constraint**: The number of nodes can range from $0$ to $10^4$.
- **Edge Cases**:
    - **Empty Tree**: If the root is `None`, the diameter is $0$.
    - **Single Node**: A tree with only one node has a diameter of $0$.
    - **Skewed Tree**: A tree where every node has only one child (essentially a linked list).
    - **Non-Root Diameter**: The longest path might exist entirely within a subtree, never crossing the actual root of the whole tree.

---

## 🧠 Core Concepts & Algorithms

### 1. Depth First Search (DFS)
To find the diameter, we need to know the maximum depth of the left and right subtrees for every single node in the tree. This naturally suggests a **Post-Order Traversal** (Left $\rightarrow$ Right $\rightarrow$ Node). We process the children first to determine their heights before calculating the result for the current node.

### 2. The Height-Diameter Relationship
For any specific node $N$, the longest path that **passes through** $N$ as the highest point (the peak) is:
$$\text{Path through } N = \text{Height}(\text{left child}) + \text{Height}(\text{right child})$$

The diameter of the entire tree is simply the **maximum** of these values calculated across all nodes in the tree.

### 3. Why this approach?
A naive approach would be to call a `height()` function for every node in the tree. Since `height()` takes $O(N)$ and we call it $N$ times, the complexity would be $O(N^2)$. By using a bottom-up DFS, we calculate the height and update the diameter in a **single pass**, reducing the complexity to $O(N)$.

---

## ⚙️ Step-by-Step Logic

### The Optimal Strategy: Bottom-Up Recursion

1. **Initialize a Global Variable**: Create a variable `max_diameter` (or use a class member) to keep track of the longest path found so far.
2. **Define a Recursive Helper (`depth`)**:
    - **Base Case**: If the current node is `None`, its depth is $0$.
    - **Recursive Step**: 
        - Calculate the depth of the left subtree: `left_depth = depth(node.left)`.
        - Calculate the depth of the right subtree: `right_depth = depth(node.right)`.
    - **Update Diameter**: The diameter passing through the current node is `left_depth + right_depth`. Compare this to `max_diameter` and update it if the current path is longer.
    - **Return Height**: Return the height of the current node to its parent: `1 + max(left_depth, right_depth)`.

### Dry Run Example
Consider this tree:
```
      1
     / \
    2   3
   / \
  4   5
```
- Node **4**: `left=0, right=0`. Path = $0$. Returns height $1$.
- Node **5**: `left=0, right=0`. Path = $0$. Returns height $1$.
- Node **2**: `left=1, right=1`. Path = $1+1 = 2$. `max_diameter` becomes $2$. Returns height $1 + \max(1,1) = 2$.
- Node **3**: `left=0, right=0`. Path = $0$. Returns height $1$.
- Node **1**: `left=2, right=1`. Path = $2+1 = 3$. `max_diameter` becomes $3$. Returns height $1 + \max(2,1) = 3$.

**Final Diameter: 3** (Path: 4 $\rightarrow$ 2 $\rightarrow$ 1 $\rightarrow$ 3 or 5 $\rightarrow$ 2 $\rightarrow$ 1 $\rightarrow$ 3).

---

## 💻 Implementation

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_optimal(root: TreeNode) -> int:
    # We use a list or a nonlocal variable to track the max diameter 
    # across recursive calls.
    max_diameter = 0

    def get_height(node):
        nonlocal max_diameter
        
        # Base case: an empty node has height 0
        if not node:
            return 0
        
        # Recursively find the height of left and right subtrees
        left_h = get_height(node.left)
        right_h = get_height(node.right)
        
        # The diameter at the current node is the sum of heights of its children
        # Update the global maximum diameter found so far
        max_diameter = max(max_diameter, left_h + right_h)
        
        # Return the height of the current node to the parent caller
        return 1 + max(left_h, right_h)

    get_height(root)
    return max_diameter

# Starter template format
def solve():
    # Example usage:
    # root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
    # print(solve_optimal(root))
    pass
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Naive** | $O(N^2)$ | $O(H)$ | Calculating height separately for every node. |
| **Optimal (DFS)** | $O(N)$ | $O(H)$ | Every node is visited exactly once. Space is used by the recursion stack. |

- **Time $O(N)$**: We traverse each node in the binary tree exactly once.
- **Space $O(H)$**: In the worst case (a skewed tree), the recursion stack will go as deep as the number of nodes $N$. In a balanced tree, this is $O(\log N)$.

---

## 🌍 Real-World Applications

While calculating the diameter of a binary tree seems academic, the underlying pattern (**aggregating subtree information to solve a global problem**) is used extensively in:

1. **Network Routing**: Finding the "longest path" or maximum latency between two nodes in a hierarchical network topology.
2. **Compiler Design**: In Abstract Syntax Trees (AST), identifying the depth or complexity of nested expressions to optimize register allocation.
3. **Social Network Analysis**: Determining the "eccentricity" of a node (the distance to the farthest node), which is a key component in calculating the **Graph Center**.
4. **File System Analysis**: Calculating the maximum depth of a directory structure to prevent stack overflow during recursive file searches.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

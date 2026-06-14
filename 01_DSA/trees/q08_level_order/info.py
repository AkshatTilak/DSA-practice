INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/binary-tree-level-order-traversal/',
    'description': 'BFS traversal.',
    'groups': ['Tree', 'Graph'],
    'readme_content': """# Level Order Traversal

## 📌 Overview & Problem Explanation

The **Level Order Traversal** problem asks us to visit every node in a binary tree level by level, from top to bottom and left to right. Instead of diving deep into a branch (like Depth-First Search), we "scan" the tree horizontally.

### Problem Statement
Given the `root` of a binary tree, return the *level order traversal* of its nodes' values. This means we must group the values of each level into separate lists.

**Example:**
Input: `root = [3, 9, 20, null, null, 15, 7]`
Output: `[[3], [9, 20], [15, 7]]`

### Inputs & Outputs
- **Input**: A reference to the `root` node of a binary tree.
- **Output**: A list of lists (`List[List[int]]`), where each inner list contains the values of nodes at that specific depth.

### Constraints & Edge Cases
- **Empty Tree**: If the root is `null`, the result should be an empty list `[]`.
- **Single Node**: If the tree only has one node, the result is `[[val]]`.
- **Skewed Tree**: A tree that looks like a linked list (only left or only right children) should still be processed level by level.
- **Balanced Tree**: A full binary tree where the number of nodes grows exponentially per level.

---

## 💡 Core Concepts & Data Structures

### Breadth-First Search (BFS)
The fundamental algorithmic pattern used here is **Breadth-First Search (BFS)**. While Depth-First Search (DFS) uses a **Stack** (often via recursion), BFS uses a **Queue**.

### Why a Queue?
A Queue follows the **First-In-First-Out (FIFO)** principle. This is critical for level order traversal because:
1. We visit the root first.
2. We "schedule" its children to be visited next.
3. Because children are added to the back of the queue, we are guaranteed to finish processing all nodes at level $i$ before we move on to any nodes at level $i+1$.

### The "Level-Size" Technique
To distinguish between different levels in the output, we don't just pop nodes one by one. Instead, we capture the **size of the queue** at the start of each level. This tells us exactly how many nodes belong to the current depth, allowing us to bundle them into a single list before moving to the next depth.

---

## 🛠️ Step-by-Step Logic

### Optimal Approach: Queue-based BFS

1. **Handle Edge Case**: If the `root` is `None`, return `[]` immediately.
2. **Initialize Queue**: Create a queue (using `collections.deque` for $O(1)$ pops) and enqueue the `root`.
3. **Outer Loop**: While the queue is not empty, a new level has started.
    - **Determine Level Width**: Store the current length of the queue (`level_size = len(queue)`).
    - **Inner Loop**: Iterate exactly `level_size` times to process all nodes of the current level.
        - **Dequeue**: Remove the node from the front of the queue.
        - **Record Value**: Append the node's value to a temporary list `current_level`.
        - **Enqueue Children**: 
            - If the node has a **left child**, add it to the queue.
            - If the node has a **right child**, add it to the queue.
    - **Store Level**: Append the `current_level` list to the final `result` list.
4. **Return Result**: Once the queue is empty, return the `result`.

### Dry Run Example
**Input**: `[3, 9, 20, null, null, 15, 7]`

| Step | Queue State | Level Size | Current Level List | Action |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `[3]` | 1 | `[]` | Pop 3, add children [9, 20] |
| 2 | `[9, 20]` | 1 | `[3]` | Level 0 Complete. |
| 3 | `[9, 20]` | 2 | `[]` | Pop 9, no children. |
| 4 | `[20]` | 2 | `[9]` | Pop 20, add children [15, 7]. |
| 5 | `[15, 7]` | 2 | `[9, 20]` | Level 1 Complete. |
| 6 | `[15, 7]` | 2 | `[]` | Pop 15, no children. |
| 7 | `[7]` | 2 | `[15]` | Pop 7, no children. |
| 8 | `[]` | 2 | `[15, 7]` | Level 2 Complete. |

**Final Result**: `[[3], [9, 20], [15, 7]]`

---

## 💻 Implementation

```python
from collections import deque

def solve(root):
    \"\"\"
    Performs a level order traversal of a binary tree.
    \"\"\"
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue) # Number of elements at the current level
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft() # FIFO
            current_level.append(node.val)
            
            # Add children to the queue for the next level
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
        
    return result
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **BFS (Optimal)** | $O(N)$ | $O(N)$ | **Time**: Every node is visited and processed exactly once. **Space**: In a perfect binary tree, the last level contains $N/2$ nodes, meaning the queue grows to $O(N)$. |

---

## 🚀 Real-World Applications

1. **DOM Tree Rendering**: Browsers often use BFS-like logic when calculating layout or searching for elements in the Document Object Model (DOM) based on depth.
2. **Networking (Broadcasting)**: When a packet is broadcast in a network, it spreads level-by-level from the source to all neighbors, then to neighbors' neighbors.
3. **Social Networks**: Finding "1st-degree", "2nd-degree", and "3rd-degree" connections on LinkedIn or Facebook is a direct application of level order traversal.
4. **Garbage Collection**: Some memory management algorithms (like Cheney's algorithm) use BFS to copy reachable objects from one memory region to another.
5. **Shortest Path in Unweighted Graphs**: BFS is the gold standard for finding the shortest path between two nodes in an unweighted graph because it explores all nodes at distance $d$ before moving to distance $d+1$.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

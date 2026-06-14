# Clone Graph

## 📌 Overview & Problem Explanation

The **Clone Graph** challenge asks us to create a **deep copy** of a connected undirected graph. 

### What is a Deep Copy?
In software engineering, a **shallow copy** merely copies the reference to an object, meaning both the original and the copy point to the same memory address. A **deep copy**, however, creates entirely new instances of every object in the structure. If you modify a node in a deep copy, the original graph remains untouched.

### The Challenge
We are given a reference to a single node in a graph. This node has a value and a list of its neighbors. Because graphs can contain **cycles** (e.g., Node A $\rightarrow$ Node B $\rightarrow$ Node A), a naive recursive approach would lead to an infinite loop. We must ensure that each node is instantiated exactly once and that all original edges are replicated in the new graph.

### Input & Output
- **Input**: A reference to a `Node` object.
- **Output**: A reference to the root of the newly cloned graph.
- **Constraints**:
    - The number of nodes is between $0$ and $100$.
    - Node values are unique.
    - The graph is connected.

### Edge Cases
- **Empty Graph**: If the input node is `None`, the output should be `None`.
- **Single Node**: A graph with one node and no edges.
- **Self-Loops**: A node that has an edge pointing to itself.
- **Cyclic Graphs**: Multiple paths leading back to the same node.

---

## ⚙️ Core Concepts & Data Structures

To solve this problem optimally, we rely on two primary pillars: **Graph Traversal** and **Hashing**.

### 1. Hashing (The Mapping Registry)
The most critical component is a **Hash Map** (Python `dict`). We use this map to store the relationship:
`Original Node` $\rightarrow$ `Cloned Node`

**Why a Hash Map?**
- **Avoids Redundancy**: Before creating a new node, we check if it already exists in the map.
- **Prevents Infinite Loops**: When we encounter a neighbor that has already been cloned, we simply retrieve the reference from the map instead of initiating a new recursive call.

### 2. Traversal Algorithms
We can traverse the graph using either **Depth-First Search (DFS)** or **Breadth-First Search (BFS)**.

- **DFS (Recursive)**: Naturally handles the "deep" exploration of paths. It is often more concise to implement.
- **BFS (Iterative)**: Uses a queue to process nodes level-by-level. It is often preferred in systems where recursion depth might hit a limit (though not an issue with $N=100$).

---

## 🚀 Step-by-Step Logic

### Approach 1: Depth-First Search (DFS) - Optimal
This approach uses recursion to visit every node and its neighbors.

1. **Base Case**: If the current node is `None`, return `None`.
2. **Check Registry**: If the current node is already in our `visited` hash map, return the cloned version from the map.
3. **Clone Node**: Create a new node instance with the same value as the original.
4. **Register**: Store the mapping `original_node: cloned_node` in the hash map immediately.
5. **Recursive Step**: Iterate through the `neighbors` of the original node. For each neighbor, recursively call the DFS function and append the returned cloned neighbor to the cloned node's neighbor list.
6. **Return**: Return the cloned node.

### Approach 2: Breadth-First Search (BFS) - Optimal
This approach uses a queue to clone the graph iteratively.

1. **Initialization**: Create a `visited` hash map and a `queue`.
2. **Start Node**: Clone the start node, add it to the map, and push the original start node into the queue.
3. **Processing**: While the queue is not empty:
    - Pop the `current_node`.
    - For each `neighbor` of the `current_node`:
        - **If neighbor not cloned**: Create the clone, add it to the map, and push the original neighbor into the queue.
        - **Edge Linkage**: Add the cloned neighbor (retrieved from the map) to the `neighbors` list of the cloned `current_node`.
4. **Return**: Return the cloned version of the start node.

### Dry Run Example
**Graph**: `1 - 2`, `2 - 3`, `3 - 1` (A triangle cycle)
1. Start at `Node 1`. Map: `{1: 1'}`. Queue: `[1]`.
2. Pop `1`. Neighbors are `2` and `3`.
3. Clone `2`. Map: `{1: 1', 2: 2'}`. Queue: `[2]`. Link `1' -> 2'`.
4. Clone `3`. Map: `{1: 1', 2: 2', 3: 3'}`. Queue: `[2, 3]`. Link `1' -> 3'`.
5. Pop `2`. Neighbors are `1` and `3`. 
   - `1` is in map $\rightarrow$ Link `2' -> 1'`.
   - `3` is in map $\rightarrow$ Link `2' -> 3'`.
6. Pop `3`. Neighbors are `1` and `2`.
   - `1` is in map $\rightarrow$ Link `3' -> 1'`.
   - `2` is in map $\rightarrow$ Link `3' -> 2'`.
7. Queue empty. Return `1'`.

---

## 💻 Implementation

```python
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def solve_dfs(node):
    """
    Optimal Solution using Depth First Search.
    """
    if not node:
        return None
    
    # Map to keep track of already cloned nodes
    visited = {}

    def clone(node):
        # If the node was already cloned, return the clone
        if node in visited:
            return visited[node]
        
        # Create the clone
        clone_node = Node(node.val)
        # Map original to clone BEFORE recursing to handle cycles
        visited[node] = clone_node
        
        # Recursively clone neighbors
        for neighbor in node.neighbors:
            clone_node.neighbors.append(clone(neighbor))
            
        return clone_node

    return clone(node)

def solve_bfs(node):
    """
    Optimal Solution using Breadth First Search.
    """
    if not node:
        return None
    
    visited = {node: Node(node.val)}
    queue = [node]
    
    while queue:
        curr = queue.pop(0)
        
        for neighbor in curr.neighbors:
            if neighbor not in visited:
                # Clone and add to map
                visited[neighbor] = Node(neighbor.val)
                # Add original to queue for further exploration
                queue.append(neighbor)
            
            # Link the cloned current node to the cloned neighbor
            visited[curr].neighbors.append(visited[neighbor])
            
    return visited[node]
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **DFS** | $O(V + E)$ | $O(V)$ | We visit every vertex once and every edge once. Space is used by the hash map and recursion stack. |
| **BFS** | $O(V + E)$ | $O(V)$ | We visit every vertex once and every edge once. Space is used by the hash map and the queue. |

- **$V$**: Number of vertices (nodes).
- **$E$**: Number of edges.

---

## 🌍 Real-World Applications

The pattern of "Deep Cloning" a graph is prevalent in several high-level software engineering scenarios:

1. **Undo/Redo Mechanisms**: In complex software (like Figma or Photoshop), the state of the document is often represented as a graph of objects. To implement a "Snapshot" or "Undo" feature, the system may deep-clone the current state graph to preserve it before applying changes.
2. **Game State Serialization**: In game development, cloning a game world or a specific set of interconnected entities (e.g., a squad of NPCs with shared references) is necessary for creating save points or simulating "what-if" scenarios in AI.
3. **Compiler Design**: Abstract Syntax Trees (ASTs) are essentially graphs. Compilers often need to clone parts of an AST to perform optimizations or transformations without destroying the original source representation.
4. **Dependency Injection Containers**: When creating isolated scopes for different requests in a web server, the container may clone a graph of service dependencies to ensure that one request's state does not leak into another.
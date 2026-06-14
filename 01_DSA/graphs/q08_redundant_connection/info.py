INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/redundant-connection/',
    'description': 'Union-find cycle detection.',
    'groups': ['Graph'],
    'readme_content': """# Redundant Connection

## 📌 Overview & Problem Explanation

The **Redundant Connection** problem asks us to find an edge in a graph that, if removed, would turn the graph back into a **tree**. 

### The Scenario
You are given a graph that started as a tree with $n$ nodes. A tree is a connected graph with no cycles. However, one additional edge was added to this tree, which inevitably created exactly one cycle. Your goal is to identify and return the edge that creates this cycle.

### Key Constraints & Rules
- **Input**: A list of edges `edges` where `edges[i] = [ai, bi]`, representing an undirected connection between node $a_i$ and $b_i$.
- **Output**: The last edge in the input list that, when removed, leaves the graph as a tree.
- **Constraints**:
    - $n = \text{edges.length}$
    - $1 \le n \le 1000$
    - $1 \le a_i, b_i \le n$
    - The graph is guaranteed to be connected.
- **Crucial Detail**: If there are multiple edges that could be removed to break the cycle, you must return the one that occurs **last** in the input array.

### Example Walkthrough
**Input**: `edges = [[1,2], [1,3], [2,3]]`
1. Process `[1,2]`: Node 1 and 2 are now connected.
2. Process `[1,3]`: Node 1 and 3 are now connected.
3. Process `[2,3]`: Node 2 and 3 are already connected indirectly through Node 1. Adding this edge creates a cycle $(1 \to 2 \to 3 \to 1)$.
**Result**: `[2,3]`

---

## ⚙️ Core Concepts: Union-Find (DSU)

To solve this problem optimally, we use the **Disjoint Set Union (DSU)**, also known as **Union-Find**.

### Why Union-Find?
While DFS or BFS can detect cycles in a graph, DSU is specifically designed for "connectivity" queries. It allows us to keep track of which nodes belong to which connected component and merge these components efficiently.

### How DSU Works
1. **Find Operation**: Determines which "set" (or component) a node belongs to by following parent pointers up to a root representative.
2. **Union Operation**: Merges two sets into one. If two nodes already share the same root, they are already connected; adding an edge between them **must** create a cycle.

### Optimizations
To ensure the DSU operations are nearly constant time, we implement two optimizations:
- **Path Compression**: During the `find` operation, we make every node on the path point directly to the root. This flattens the structure.
- **Union by Rank/Size**: We always attach the smaller tree under the root of the larger tree, preventing the tree from becoming a long chain (keeping it balanced).

---

## 🚀 Step-by-Step Logic

### The Algorithm
1. **Initialize**: Create a `parent` array where each node is its own parent (`parent[i] = i`).
2. **Iterate**: Loop through every edge `[u, v]` in the input list.
3. **Find Roots**: Find the root representative of node `u` and node `v`.
4. **Cycle Detection**:
   - If `find(u) == find(v)`, it means `u` and `v` are already part of the same connected component. Adding this edge closes a loop. **Return this edge immediately.**
5. **Union**: If they are in different components, call `union(u, v)` to merge the sets.
6. **Completion**: Since the problem guarantees exactly one redundant edge, the loop will always return an edge before finishing.

### Dry Run Trace
`edges = [[1,2], [2,3], [3,4], [1,4], [1,5]]`

| Edge | Find(u) | Find(v) | Action | Parent Array State (Simplified) |
| :--- | :--- | :--- | :--- | :--- |
| `[1,2]` | 1 | 2 | Union(1,2) | `parent[2] = 1` |
| `[2,3]` | 1 | 3 | Union(1,3) | `parent[3] = 1` |
| `[3,4]` | 1 | 4 | Union(1,4) | `parent[4] = 1` |
| `[1,4]` | 1 | 1 | **Cycle!** | Return `[1,4]` |

---

## 💻 Implementation

```python
class UnionFind:
    def __init__(self, n):
        # Initialize parent array where each node is its own root
        self.parent = list(range(n + 1))
        # Rank is used to keep the tree flat
        self.rank = [1] * (n + 1)

    def find(self, i):
        # Path Compression: Make the node point directly to the root
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        
        if root_i != root_j:
            # Union by Rank: Attach smaller tree to larger tree
            if self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            elif self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True # Successfully merged
        return False # Cycle detected

def solve(edges):
    n = len(edges)
    uf = UnionFind(n)
    
    for u, v in edges:
        # If union returns False, it means u and v were already connected
        if not uf.union(u, v):
            return [u, v]
    
    return []
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Union-Find (Optimal)** | $O(N \cdot \alpha(N))$ | $O(N)$ | $\alpha(N)$ is the Inverse Ackermann function, which is nearly $O(1)$ for all practical values of $N$. Space is used for the `parent` and `rank` arrays. |

- **Time**: We iterate through $N$ edges. Each `find` and `union` operation takes nearly constant time due to path compression and union by rank.
- **Space**: We store two arrays of size $N+1$ to track the graph structure.

---

## 🌍 Real-World Applications

The pattern used in "Redundant Connection" (detecting cycles and managing connected components) is fundamental in several engineering domains:

1. **Network Topology**: In computer networking, the **Spanning Tree Protocol (STP)** is used to find and disable redundant paths in a Local Area Network (LAN) to prevent "broadcast storms" (infinite loops of packets).
2. **Circuit Design**: Electrical engineers use cycle detection to ensure that certain circuit configurations do not create unintended short circuits or feedback loops.
3. **Social Network Analysis**: DSU is used to find "connected components" (clusters of friends) and to detect if adding a new friendship creates a cycle within a specific social circle.
4. **Image Processing**: The **Connected Component Labeling** algorithm (often implemented via DSU) is used in computer vision to identify distinct objects/blobs in a binary image.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2)
# Space Complexity: O(N)
# For each edge (u, v) in the input list, we check if u and v are already connected 
# using the edges processed so far. We use a Depth First Search (DFS) to 
# determine connectivity. If they are already connected, the current edge is the 
# redundant one that creates the cycle.
def findRedundantConnection_naive(edges):
    from collections import defaultdict
    
    adj = defaultdict(list)
    
    def has_path(start, target, visited):
        if start == target:
            return True
        visited.add(start)
        for neighbor in adj[start]:
            if neighbor not in visited:
                if has_path(neighbor, target, visited):
                    return True
        return False

    for u, v in edges:
        # Check if u and v are already connected before adding the edge
        if u in adj and v in adj and has_path(u, v, set()):
            return [u, v]
        adj[u].append(v)
        adj[v].append(u)
    
    return []

# --- APPROACH 2: Optimal (Union-Find) ---
# Time Complexity: O(N * alpha(N))
# Space Complexity: O(N)
# Union-Find (Disjoint Set Union) is the optimal way to detect cycles in an undirected 
# graph. By using path compression and union by rank, the amortized time complexity 
# per operation is nearly constant (inverse Ackermann function alpha(N)). 
# We iterate through the edges and try to union the two endpoints. If they 
# already belong to the same set, the current edge is the one that closes the cycle.
def findRedundantConnection(edges):
    n = len(edges)
    parent = list(range(n + 1))
    rank = [0] * (n + 1)

    def find(i):
        if parent[i] == i:
            return i
        # Path compression: update parent to the root
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            # Union by rank: attach smaller tree under larger tree
            if rank[root_i] > rank[root_j]:
                parent[root_j] = root_i
            elif rank[root_i] < rank[root_j]:
                parent[root_i] = root_j
            else:
                parent[root_i] = root_j
                rank[root_j] += 1
            return True
        return False

    for u, v in edges:
        if not union(u, v):
            return [u, v]
    
    return []

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package graphs;

import java.util.*;

public class RedundantConnection {
    private int[] parent;
    private int[] rank;

    public int[] findRedundantConnection(int[][] edges) {
        int n = edges.length;
        parent = new int[n + 1];
        rank = new int[n + 1];
        
        for (int i = 0; i <= n; i++) {
            parent[i] = i;
        }

        for (int[] edge : edges) {
            if (!union(edge[0], edge[1])) {
                return edge;
            }
        }
        return new int[0];
    }

    private int find(int i) {
        if (parent[i] == i) {
            return i;
        }
        // Path compression
        return parent[i] = find(parent[i]);
    }

    private boolean union(int i, int j) {
        int rootI = find(i);
        int rootJ = find(j);
        
        if (rootI != rootJ) {
            // Union by rank
            if (rank[rootI] > rank[rootJ]) {
                parent[rootJ] = rootI;
            } else if (rank[rootI] < rank[rootJ]) {
                parent[rootI] = rootJ;
            } else {
                parent[rootI] = rootJ;
                rank[rootJ]++;
            }
            return true;
        }
        return false;
    }

    public static void main(String[] args) {
        RedundantConnection sol = new RedundantConnection();
        int[][] edges = {{1,2}, {1,3}, {2,3}};
        int[] result = sol.findRedundantConnection(edges);
        System.out.println(Arrays.toString(result)); // Output: [2, 3]
    }
}
\"\"\"""",
}

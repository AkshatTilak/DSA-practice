"""
Challenge: q02_clone_graph
Difficulty: Medium
Link: https://leetcode.com/problems/clone-graph/

Problem:
Clone deep copy graph.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(V + E)
# Space Complexity: O(V)
# This approach uses a recursive Depth First Search (DFS). 
# We maintain a dictionary to map original nodes to their corresponding cloned nodes. 
# If a node has already been cloned, we return the clone; otherwise, we create it 
# and recursively clone its neighbors.

class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def solve_naive(node: 'Node') -> 'Node':
    if not node:
        return None
    
    visited = {}

    def dfs(curr_node):
        # If the node was already cloned, return the clone from the map
        if curr_node in visited:
            return visited[curr_node]
        
        # Create a new node as a clone
        clone = Node(curr_node.val)
        visited[curr_node] = clone
        
        # Recursively clone all neighbors
        for neighbor in curr_node.neighbors:
            clone.neighbors.append(dfs(neighbor))
            
        return clone

    return dfs(node)

# --- APPROACH 2: Optimal (Iterative BFS) ---
# Time Complexity: O(V + E)
# Space Complexity: O(V)
# This approach uses Breadth First Search (BFS) with a queue. 
# It is optimal because it visits every node and edge exactly once. 
# Unlike the recursive DFS, the iterative BFS avoids potential StackOverflow errors 
# for extremely deep graphs (though rare for most competitive programming constraints).
# The dictionary ensures that each node is instantiated exactly once.

from collections import deque

def solve_optimal(node: 'Node') -> 'Node':
    if not node:
        return None
    
    # Mapping from original node to cloned node
    visited = {node: Node(node.val)}
    queue = deque([node])
    
    while queue:
        curr = queue.popleft()
        
        for neighbor in curr.neighbors:
            # If the neighbor hasn't been cloned yet
            if neighbor not in visited:
                # Create clone and add to mapping
                visited[neighbor] = Node(neighbor.val)
                # Add to queue to process its neighbors later
                queue.append(neighbor)
            
            # Link the clone of the current node to the clone of the neighbor
            visited[curr].neighbors.append(visited[neighbor])
            
    return visited[node]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

import java.util.*;

class Node {
    public int val;
    public List<Node> neighbors;
    public Node() {
        val = 0;
        neighbors = new ArrayList<Node>();
    }
    public Node(int _val) {
        val = _val;
        neighbors = new ArrayList<Node>();
    }
    public Node(int _val, ArrayList<Node> _neighbors) {
        val = _val;
        neighbors = _neighbors;
    }
}

public class CloneGraph {
    public Node cloneGraph(Node node) {
        if (node == null) {
            return null;
        }

        // Map to keep track of original node -> cloned node
        Map<Node, Node> visited = new HashMap<>();
        
        // Use a queue for BFS traversal
        Queue<Node> queue = new LinkedList<>();
        
        // Initialize the clone for the start node
        visited.put(node, new Node(node.val));
        queue.add(node);
        
        while (!queue.isEmpty()) {
            Node curr = queue.poll();
            
            for (Node neighbor : curr.neighbors) {
                if (!visited.containsKey(neighbor)) {
                    // Clone the neighbor if not visited
                    visited.put(neighbor, new Node(neighbor.val));
                    queue.add(neighbor);
                }
                // Add the cloned neighbor to the current cloned node's neighbors list
                visited.get(curr).neighbors.add(visited.get(neighbor));
            }
        }
        
        return visited.get(node);
    }
}
"""

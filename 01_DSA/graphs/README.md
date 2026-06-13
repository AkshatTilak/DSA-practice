# Graphs

A Graph is a non-linear data structure consisting of a finite set of vertices (or nodes) and a set of edges connecting them. Edges can be directed/undirected and weighted/unweighted. Graphs represent network relations such as social connections, network routing maps, and dependency trees. The two primary search traversals are Depth-First Search (DFS) and Breadth-First Search (BFS).

---

## 🗺️ ASCII Execution Flow: BFS Grid Traversal

Here is the BFS traversal mapping for finding connected land components (Islands) in a 2D binary grid:

```text
Grid representation (1 = Land, 0 = Water):
  [ 1, 1, 0 ]
  [ 1, 0, 0 ]
  [ 0, 0, 1 ]

Queue State & Traversal Steps:
1. Start at Land index (0,0): IslandCount = 1
   - Push to Queue: [ (0,0) ]
   - Mark as Visited: { (0,0) }
2. Pop (0,0). Inspect valid unvisited neighbors (1,0) and (0,1):
   - Push neighbors: Queue: [ (1,0), (0,1) ]
   - Mark Visited: { (0,0), (1,0), (0,1) }
3. Pop (1,0). Neighbor (1,1) is Water, (0,0) is Visited. No push.
4. Pop (0,1). Neighbor (1,1) is Water. No push. Queue is empty.
5. Search grid for next unvisited Land: Found (2,2): IslandCount = 2
   - Push to Queue: [ (2,2) ]
   - Mark Visited: { (0,0), (1,0), (0,1), (2,2) }
6. Pop (2,2). Queue empty. Grid scan finished.
Output Islands ──> 2
```

---

## 📊 Complexity Analysis

| Algorithm | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Breadth-First Search (BFS) | $O(V + E)$ | $O(V)$ |
| Depth-First Search (DFS) | $O(V + E)$ | $O(V)$ (recursion stack) |
| Dijkstra's (Shortest Path) | $O((V + E) \log V)$ | $O(V)$ |

---

## 🏢 Real-World Production Use-Case

### Social Networks: LinkedIn Degrees of Separation Lookup
LinkedIn displays mutual connection statuses (1st, 2nd, 3rd+ degree connections) on user profiles.
1. The user relationship directory is modeled as a **Graph** where nodes are profiles and edges are friendships/connections.
2. When a profile is viewed, LinkedIn runs a shortest-path **BFS traversal** starting at the viewer's node.
3. The BFS expands level-by-level (degree-by-degree) to search for the target profile's vertex.
4. Using an in-memory graph database (like Neo4j or customized vertex-caches), this traversal finds connection paths in milliseconds, preventing database bottlenecks.
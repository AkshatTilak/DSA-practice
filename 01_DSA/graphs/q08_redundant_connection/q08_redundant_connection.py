"""
Challenge: q08_redundant_connection
Difficulty: Medium
Link: https://leetcode.com/problems/redundant-connection/

Problem:
Union-find cycle detection.
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
"""
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
"""

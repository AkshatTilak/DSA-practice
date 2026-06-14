"""
Challenge: q04_gnn_aggregation
Difficulty: Hard
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Graph neighborhood feature aggregator.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N * E * D)
# Space Complexity: O(N * D)
# The naive approach iterates through every node in the graph. For each node, it scans the entire edge list to find neighbors, 
# then manually aggregates their features. This results in a complexity that depends on the product of nodes and edges.
import numpy as np

def solve_naive(X, edge_index, agg_type='sum'):
    num_nodes = X.shape[0]
    feature_dim = X.shape[1]
    result = np.zeros((num_nodes, feature_dim))
    
    src, dst = edge_index
    
    for i in range(num_nodes):
        # Find neighbors of node i (where i is the destination)
        neighbors = []
        for j in range(len(src)):
            if dst[j] == i:
                neighbors.append(src[j])
        
        if not neighbors:
            continue
            
        neighbor_features = X[neighbors]
        
        if agg_type == 'sum':
            result[i] = np.sum(neighbor_features, axis=0)
        elif agg_type == 'mean':
            result[i] = np.mean(neighbor_features, axis=0)
        elif agg_type == 'max':
            result[i] = np.max(neighbor_features, axis=0)
            
    return result

# --- APPROACH 2: Optimal (Vectorized Scatter Aggregation) ---
# Time Complexity: O(E * D)
# Space Complexity: O(N * D)
# This approach uses NumPy's unbuffered in-place operations (np.add.at, np.maximum.at). 
# Instead of looping over nodes, we iterate over the edges once. The time complexity is linear 
# relative to the number of edges and the feature dimension, which is optimal for graph traversal.
import numpy as np

def solve_optimal(X, edge_index, agg_type='sum'):
    X = np.asanyarray(X, dtype=np.float64)
    edge_index = np.asanyarray(edge_index, dtype=np.int64)
    
    num_nodes = X.shape[0]
    feature_dim = X.shape[1]
    src, dst = edge_index
    
    # Initialize output array
    out = np.zeros((num_nodes, feature_dim), dtype=np.float64)
    
    if agg_type == 'sum':
        # np.add.at handles repeated indices in 'dst' correctly (unbuffered)
        np.add.at(out, dst, X[src])
        
    elif agg_type == 'mean':
        # Sum all features first
        np.add.at(out, dst, X[src])
        # Compute degree for each node
        deg = np.bincount(dst, minlength=num_nodes).astype(np.float64)
        # Avoid division by zero for isolated nodes
        deg_mask = deg > 0
        out[deg_mask] /= deg[deg_mask][:, np.newaxis]
        
    elif agg_type == 'max':
        # Initialize with negative infinity to correctly handle max of negative numbers
        out.fill(-np.inf)
        np.maximum.at(out, dst, X[src])
        # Replace remaining -inf (nodes with no neighbors) with 0
        out[np.isinf(out)] = 0
    
    else:
        raise ValueError(f"Unsupported aggregation type: {agg_type}")
        
    return out

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package architectures;

import java.util.*;

public class GnnAggregation {
    /**
     * Aggregates neighborhood features for a graph.
     * 
     * @param X The node feature matrix [numNodes][featureDim]
     * @param edgeIndex The edge list [2][numEdges] (src, dst)
     * @param aggType The type of aggregation ("sum", "mean", "max")
     * @return The aggregated feature matrix [numNodes][featureDim]
     */
    public static double[][] aggregate(double[][] X, int[][] edgeIndex, String aggType) {
        int numNodes = X.length;
        int featureDim = X[0].length;
        int numEdges = edgeIndex[0].length;
        double[][] result = new double[numNodes][featureDim];
        
        if ("sum".equals(aggType)) {
            for (int i = 0; i < numEdges; i++) {
                int src = edgeIndex[0][i];
                int dst = edgeIndex[1][i];
                for (int d = 0; d < featureDim; d++) {
                    result[dst][d] += X[src][d];
                }
            }
        } else if ("mean".equals(aggType)) {
            int[] counts = new int[numNodes];
            for (int i = 0; i < numEdges; i++) {
                int src = edgeIndex[0][i];
                int dst = edgeIndex[1][i];
                counts[dst]++;
                for (int d = 0; d < featureDim; d++) {
                    result[dst][d] += X[src][d];
                }
            }
            for (int i = 0; i < numNodes; i++) {
                if (counts[i] > 0) {
                    for (int d = 0; d < featureDim; d++) {
                        result[i][d] /= counts[i];
                    }
                }
            }
        } else if ("max".equals(aggType)) {
            // Initialize with very small value
            for (int i = 0; i < numNodes; i++) {
                Arrays.fill(result[i], Double.NEGATIVE_INFINITY);
            }
            for (int i = 0; i < numEdges; i++) {
                int src = edgeIndex[0][i];
                int dst = edgeIndex[1][i];
                for (int d = 0; d < featureDim; d++) {
                    result[dst][d] = Math.max(result[dst][d], X[src][d]);
                }
            }
            // Replace NEGATIVE_INFINITY with 0 for isolated nodes
            for (int i = 0; i < numNodes; i++) {
                for (int d = 0; d < featureDim; d++) {
                    if (result[i][d] == Double.NEGATIVE_INFINITY) {
                        result[i][d] = 0.0;
                    }
                }
            }
        } else {
            throw new IllegalArgumentException("Unsupported aggregation type: " + aggType);
        }
        
        return result;
    }

    public static void main(String[] args) {
        double[][] X = {
            {1.0, 2.0},
            {3.0, 4.0},
            {5.0, 6.0}
        };
        int[][] edgeIndex = {
            {0, 1, 2}, // sources
            {1, 2, 1}  // destinations
        };
        
        double[][] res = aggregate(X, edgeIndex, "sum");
        // Result for node 1: features of node 0 + node 2 = [1+5, 2+6] = [6, 8]
        // Result for node 2: features of node 1 = [3, 4]
    }
}
"""

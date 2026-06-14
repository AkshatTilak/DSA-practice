INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Graph neighborhood feature aggregator.',
    'groups': ['Deep Learning', 'Graph Neural Networks'],
    'readme_content': """# GNN Neighborhood Feature Aggregation

## 1. Overview & Concept Card

**Graph Neural Networks (GNNs)** are a class of deep learning architectures designed to perform inference on data described by graphs (nodes and edges). Unlike traditional Neural Networks that assume data is independent and identically distributed (IID) or structured in a grid (like images), GNNs explicitly model the relationships between entities.

**Neighborhood Feature Aggregation** is the fundamental operation of GNNs, often referred to as the **Message Passing** phase. The core objective is to compute a representation (embedding) for a target node by "aggregating" information from its immediate neighbors. This allows a node to incorporate the local structural context of the graph into its own feature vector.

### Core Objectives:
- **Information Propagation**: Move feature information from one node to another across edges.
- **Permutation Invariance**: The result of the aggregation must be the same regardless of the order in which the neighbors are processed (since graphs have no inherent ordering of neighbors).
- **Local Contextualization**: Transform raw node features into "context-aware" features based on the neighborhood.

---

## 2. Theoretical Foundations & Math

The general framework for GNN aggregation is defined by the **Message Passing Neural Network (MPNN)** formalism. For a node $v$, the update of its feature vector $h_v$ at layer $k$ is defined as:

$$h_v^{(k)} = \text{UPDATE}^{(k)} \left( h_v^{(k-1)}, \text{AGGREGATE}^{(k)} \left( \{ h_u^{(k-1)} : u \in \mathcal{N}(v) \} \right) \right)$$

### Mathematical Components:
1.  $\mathcal{N}(v)$: The set of neighbors of node $v$.
2.  $h_u^{(k-1)}$: The feature vector of neighbor $u$ from the previous layer.
3.  $\text{AGGREGATE}(\cdot)$: A permutation-invariant function that collapses a set of vectors into a single vector.
4.  $\text{UPDATE}(\cdot)$: A function (usually a MLP or a gated unit) that combines the node's current state with the aggregated neighborhood message.

### Common Aggregation Functions ($\bigoplus$):
Depending on the task, different aggregation operators are used:

| Operator | Formula | Property | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Sum** | $\sum_{u \in \mathcal{N}(v)} h_u$ | Captures local structure/degree | When the number of neighbors is an important feature. |
| **Mean** | $\frac{1}{|\mathcal{N}(v)|} \sum_{u \in \mathcal{N}(v)} h_u$ | Captures distribution of features | When the proportion of neighbor types is more important than total count. |
| **Max** | $\max_{u \in \mathcal{N}(v)} (h_u)$ | Captures "strongest" signal | Identifying the most prominent feature among neighbors (e.g., detecting a specific motif). |

---

## 3. Step-by-Step Logic

To implement a neighborhood aggregator, we must map the graph topology (adjacency) to the node features.

### Algorithmic Implementation Steps:

1.  **Input Representation**: 
    - Node Feature Matrix $X \in \mathbb{R}^{N \times D}$ (where $N$ is the number of nodes and $D$ is the feature dimension).
    - Adjacency Matrix $A \in \{0, 1\}^{N \times N}$ (where $A_{ij}=1$ if an edge exists between $i$ and $j$).

2.  **Message Generation**:
    - For each node $v$, identify the indices of its neighbors $\mathcal{N}(v)$.
    - Collect the feature vectors $X_u$ for all $u \in \mathcal{N}(v)$.

3.  **Aggregation (The Core Step)**:
    - **For Sum Aggregation**: Perform matrix multiplication $A \times X$. The entry $(i, j)$ of the resulting matrix is the sum of the $j$-th feature of all neighbors of node $i$.
    - **For Mean Aggregation**: Normalize the adjacency matrix $A$ such that each row sums to 1 (i.e., $D^{-1}A$, where $D$ is the degree matrix), then multiply by $X$.
    - **For Max Aggregation**: Iterate through the adjacency list and apply the `max` operator across the feature dimension for all neighbors.

4.  **Self-Loop Inclusion**:
    - In most GNNs (like GCN), a node is considered its own neighbor. This is implemented by adding the Identity matrix $I$ to the adjacency matrix $A$: $\tilde{A} = A + I$.

5.  **Transformation**:
    - Pass the aggregated vector through a learnable weight matrix $W$ and a non-linear activation function $\sigma$ (e.g., ReLU).

### Reference Implementation (Optimal Approach)

```python
import numpy as np

def solve_optimal(adj_matrix, node_features, aggregation_type='sum'):
    \"\"\"
    Optimal implementation of GNN aggregation.
    
    Args:
        adj_matrix (np.ndarray): Binary adjacency matrix (N x N)
        node_features (np.ndarray): Node features (N x D)
        aggregation_type (str): 'sum', 'mean', or 'max'
    Returns:
        np.ndarray: Aggregated feature matrix (N x D)
    \"\"\"
    # 1. Sum Aggregation: Matrix multiplication is the most efficient way
    if aggregation_type == 'sum':
        return np.dot(adj_matrix, node_features)
    
    # 2. Mean Aggregation: Row-normalize adj_matrix then multiply
    elif aggregation_type == 'mean':
        degree = np.sum(adj_matrix, axis=1, keepdims=True)
        # Avoid division by zero for isolated nodes
        degree_inv = np.where(degree > 0, 1.0 / degree, 0)
        return np.dot(adj_matrix, node_features) * degree_inv
    
    # 3. Max Aggregation: Requires iterating or masked reductions
    elif aggregation_type == 'max':
        # Masked approach: set non-neighbors to -infinity
        # shape: (N, N, 1) * (1, 1, D) -> (N, N, D)
        masked_features = adj_matrix[:, :, np.newaxis] * node_features[np.newaxis, :, :]
        # Replace 0s (non-neighbors) with very small number for max
        masked_features[adj_matrix[:, :, np.newaxis] == 0] = -np.inf
        return np.max(masked_features, axis=1)
    
    else:
        raise ValueError("Unsupported aggregation type")
```

---

## 4. Complexity & Training Details

### Computational Complexity

Let $N$ be the number of nodes, $E$ be the number of edges, and $D$ be the feature dimension.

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Sum Aggregation** | $O(N^2 D)$ (Dense) / $O(ED)$ (Sparse) | $O(ND)$ | Dense matrix mult is $N^2 D$; sparse is proportional to edges. |
| **Mean Aggregation**| $O(N^2 D)$ (Dense) / $O(ED)$ (Sparse) | $O(ND)$ | Same as sum, with an additional $O(N)$ for degree calculation. |
| **Max Aggregation** | $O(ED)$ | $O(ND)$ | Must visit every edge to find the maximum. |

### Hyperparameters & Training Considerations:
- **Aggregation Choice**: Choosing `sum` vs `mean` can fundamentally change the model's ability to distinguish between different graph structures (e.g., the Weisfeiler-Lehman test).
- **Weight Initialization**: Weights $W$ are typically initialized using Glorot (Xavier) initialization to prevent vanishing/exploding gradients during the recursive aggregation process.
- **Over-smoothing**: If too many aggregation layers are added, node embeddings tend to converge to the same value, making them indistinguishable. This is why GNNs are typically shallow (2-4 layers).

---

## 5. Real-World Applications

Neighborhood aggregation is the engine behind several industry-standard architectures:

1.  **Recommendation Systems (Pinterest PinSage)**: 
    - Nodes are pins/boards. Aggregation gathers features from similar pins to suggest new content to users.
2.  **Drug Discovery & Chemistry (Graph Convolutional Networks - GCN)**: 
    - Nodes are atoms; edges are chemical bonds. Aggregation summarizes the chemical environment surrounding an atom to predict molecular toxicity or solubility.
3.  **Fraud Detection (Financial Networks)**: 
    - Nodes are accounts; edges are transactions. Aggregation identifies "clusters" of suspicious activity by propagating "fraudulence" scores from known bad actors to their neighbors.
4.  **Knowledge Graphs (GraphSAGE)**: 
    - Uses **sampled aggregation** (taking a fixed-size random sample of neighbors) to handle massive graphs where calculating the full neighborhood sum is computationally impossible.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

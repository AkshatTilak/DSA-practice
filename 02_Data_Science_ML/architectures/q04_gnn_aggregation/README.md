# GNN Neighborhood Feature Aggregation

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
    """
    Optimal implementation of GNN aggregation.
    
    Args:
        adj_matrix (np.ndarray): Binary adjacency matrix (N x N)
        node_features (np.ndarray): Node features (N x D)
        aggregation_type (str): 'sum', 'mean', or 'max'
    Returns:
        np.ndarray: Aggregated feature matrix (N x D)
    """
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
    - Uses **sampled aggregation** (taking a fixed-size random sample of neighbors) to handle massive graphs where calculating the full neighborhood sum is computationally impossible.
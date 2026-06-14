# K-Means Clustering

K-Means is one of the most popular and fundamental **Unsupervised Learning** algorithms. Its primary objective is to partition a dataset into $K$ distinct, non-overlapping subgroups (clusters) where each data point belongs to the cluster with the nearest mean.

Unlike supervised learning, K-Means does not use labels. Instead, it discovers inherent patterns in the data based on the **geometric distance** between points.

---

##  Theoretical Foundations & Math

### 1. The Objective Function
The goal of K-Means is to minimize the **Within-Cluster Sum of Squares (WCSS)**, also known as **Inertia**. Mathematically, we want to find $K$ centroids $\mu_1, \mu_2, \dots, \mu_k$ that minimize the following cost function:

$$J = \sum_{i=1}^{K} \sum_{x \in S_i} \| x - \mu_i \|^2$$

**Where:**
- $K$: The number of clusters.
- $S_i$: The set of points assigned to cluster $i$.
- $x$: A data point in the cluster.
- $\mu_i$: The centroid (mean) of cluster $i$.
- $\| x - \mu_i \|^2$: The squared **Euclidean Distance** between the point and the centroid.

### 2. Distance Metric
K-Means typically uses the **L2 Norm (Euclidean Distance)** to determine similarity:
$$\text{dist}(x, y) = \sqrt{\sum_{j=1}^{d} (x_j - y_j)^2}$$
Because it relies on distance, **feature scaling (normalization/standardization)** is critical; otherwise, features with larger scales will dominate the clustering process.

---

## Step-by-Step Logic

The K-Means algorithm employs an iterative refinement technique called **Lloyd's Algorithm**, which alternates between two main steps:

### Step 1: Initialization
Choose $K$ initial centroids. 
- **Random Initialization**: Pick $K$ random points from the dataset.
- **K-Means++**: A smarter initialization strategy that spreads out initial centroids to speed up convergence and avoid poor local optima.

### Step 2: Assignment (The "Expectation" Step)
Assign each data point to the nearest centroid based on the Euclidean distance.
$$\text{cluster}(x) = \arg\min_{i} \| x - \mu_i \|^2$$

### Step 3: Update (The "Maximization" Step)
Recalculate the centroid of each cluster by taking the mean of all points assigned to that cluster.
$$\mu_i = \frac{1}{|S_i|} \sum_{x \in S_i} x$$

### Step 4: Convergence
Repeat Steps 2 and 3 until one of the following conditions is met:
1. The centroids no longer change positions.
2. The assignments of points to clusters remain the same.
3. A maximum number of iterations is reached.

---

## Implementation

Below is the optimal implementation of the K-Means algorithm from scratch.

```python
import numpy as np

def solve_optimal(X, k, max_iters=100, tol=1e-4):
    """
    Implements the K-Means clustering algorithm.
    
    Args:
        X (np.ndarray): Input data of shape (n_samples, n_features)
        k (int): Number of clusters
        max_iters (int): Maximum number of iterations
        tol (float): Convergence tolerance
        
    Returns:
        centroids (np.ndarray): Final cluster centroids
        labels (np.ndarray): Index of the cluster each sample belongs to
    """
    # 1. Initialization: Randomly pick k points as initial centroids
    n_samples, n_features = X.shape
    random_idx = np.random.choice(n_samples, k, replace=False)
    centroids = X[random_idx]
    
    for i in range(max_iters):
        # 2. Assignment Step
        # Compute distance from each point to each centroid
        # Using broadcasting: (n_samples, 1, n_features) - (1, k, n_features)
        distances = np.linalg.norm(X[:, np.newaxis] - centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        
        # Store old centroids to check for convergence
        old_centroids = centroids.copy()
        
        # 3. Update Step
        for j in range(k):
            # Calculate the mean of all points assigned to cluster j
            cluster_points = X[labels == j]
            if len(cluster_points) > 0:
                centroids[j] = np.mean(cluster_points, axis=0)
        
        # 4. Convergence Check
        # If the centroids move less than the tolerance, stop
        if np.linalg.norm(centroids - old_centroids) < tol:
            break
            
    return centroids, labels

# Example Usage
if __name__ == "__main__":
    # Create a dummy dataset
    np.random.seed(42)
    data = np.vstack([
        np.random.randn(100, 2) + [2, 2],
        np.random.randn(100, 2) + [-2, -2],
        np.random.randn(100, 2) + [2, -2]
    ])
    
    centroids, labels = solve_optimal(data, k=3)
    print("Final Centroids:\n", centroids)
```

---

## Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Assignment** | $O(n \cdot k \cdot d)$ | $O(n \cdot d)$ | $n$: samples, $k$: clusters, $d$: dimensions. |
| **Update** | $O(n \cdot d)$ | $O(k \cdot d)$ | Averaging points for each centroid. |
| **Total (per iter)**| $O(n \cdot k \cdot d)$ | $O((n+k) \cdot d)$ | Iterates until convergence. |

### Key Hyperparameters
- **$K$ (Number of Clusters)**: The most critical hyperparameter. 
    - **Elbow Method**: Plot WCSS vs $K$ and look for the "elbow" point where the rate of decrease slows down.
    - **Silhouette Score**: Measures how similar an object is to its own cluster compared to other clusters.
- **Max Iterations**: Prevents infinite loops in case of oscillating assignments.
- **Tolerance**: Defines the threshold for "convergence."

---

## Real-World Applications

1. **Customer Segmentation**: Marketing teams use K-Means to group customers by purchasing behavior, age, or spending habits to create targeted ad campaigns.
2. **Image Compression (Color Quantization)**: Reducing the number of colors in an image by clustering similar pixel colors and replacing them with the cluster centroid color.
3. **Anomaly Detection**: Points that are very far from any cluster centroid (high distance) can be flagged as outliers or fraudulent transactions.
4. **Document Clustering**: Grouping similar news articles or research papers based on TF-IDF vector representations of their text.

## Summary Table: Pros & Cons

| Pros | Cons |
| :--- | :--- |
| Simple to understand and implement. | Sensitive to initial centroid placement (local optima). |
| Scales well to large datasets. | Requires $K$ to be specified in advance. |
| Guaranteed convergence. | Struggles with non-spherical or varying-sized clusters. |
| Efficient $O(nkd)$ complexity. | Highly sensitive to outliers (which pull the mean). |
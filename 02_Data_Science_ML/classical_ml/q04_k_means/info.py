INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Cluster iterative centroids.',
    'groups': ['Classical ML', 'Unsupervised Learning'],
    'readme_content': """# K-Means Clustering

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
    \"\"\"
    Implements the K-Means clustering algorithm.
    
    Args:
        X (np.ndarray): Input data of shape (n_samples, n_features)
        k (int): Number of clusters
        max_iters (int): Maximum number of iterations
        tol (float): Convergence tolerance
        
    Returns:
        centroids (np.ndarray): Final cluster centroids
        labels (np.ndarray): Index of the cluster each sample belongs to
    \"\"\"
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
| Efficient $O(nkd)$ complexity. | Highly sensitive to outliers (which pull the mean). |""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(I * k * n * d)
# Space Complexity: O(k * d + n)
# This approach implements the basic Lloyd's algorithm using standard Python lists and loops.
# It uses random initialization by picking k random points from the dataset.
import math
import random

def solve_naive(X, k, max_iters=100):
    if not X or k <= 0:
        return [], []
    
    n = len(X)
    d = len(X[0])
    
    # Randomly initialize centroids from the data points
    centroids = random.sample(X, k)
    labels = [0] * n
    
    for _ in range(max_iters):
        # Assignment Step: Assign each point to the nearest centroid
        changed = False
        for i in range(n):
            min_dist = float('inf')
            best_cluster = 0
            for j in range(k):
                # Euclidean distance calculation
                dist = math.sqrt(sum((X[i][m] - centroids[j][m])**2 for m in range(d)))
                if dist < min_dist:
                    min_dist = dist
                    best_cluster = j
            
            if labels[i] != best_cluster:
                labels[i] = best_cluster
                changed = True
        
        if not changed:
            break
            
        # Update Step: Recalculate centroids as the mean of assigned points
        new_centroids = [[0.0] * d for _ in range(k)]
        counts = [0] * k
        
        for i in range(n):
            cluster = labels[i]
            counts[cluster] += 1
            for m in range(d):
                new_centroids[cluster][m] += X[i][m]
        
        for j in range(k):
            if counts[j] > 0:
                for m in range(d):
                    new_centroids[j][m] /= counts[j]
            else:
                # If a cluster becomes empty, re-initialize it to a random point
                new_centroids[j] = random.choice(X)
                
        centroids = new_centroids
        
    return centroids, labels

# --- APPROACH 2: Optimal (K-Means++ with NumPy) ---
# Time Complexity: O(I * k * n * d)
# Space Complexity: O(k * d + n)
# This approach is optimal because it uses NumPy for vectorized distance calculations, 
# significantly reducing the overhead of Python loops. Additionally, it implements 
# K-Means++ initialization, which ensures faster convergence and a better final 
# clustering result by spreading out the initial centroids.
import numpy as np

def solve_optimal(X, k, max_iters=100):
    X = np.array(X)
    n, d = X.shape
    
    if n == 0 or k <= 0:
        return [], []

    # K-Means++ Initialization
    centroids = np.empty((k, d))
    # 1. Pick the first centroid randomly from X
    centroids[0] = X[np.random.randint(n)]
    
    for i in range(1, k):
        # Compute distance from each point to the nearest already chosen centroid
        # Use squared Euclidean distance
        distances = np.min([np.sum((X - c)**2, axis=1) for c in centroids[:i]], axis=0)
        # Select next centroid with probability proportional to D(x)^2
        probs = distances / np.sum(distances)
        cumulative_probs = np.cumsum(probs)
        r = np.random.rand()
        idx = np.searchsorted(cumulative_probs, r)
        centroids[i] = X[idx]

    labels = np.zeros(n, dtype=int)
    
    for _ in range(max_iters):
        # Assignment Step (Vectorized)
        # Compute distances from all points to all centroids: (n, k)
        # dist(a, b)^2 = |a|^2 + |b|^2 - 2ab
        dist_sq = np.sum(X**2, axis=1)[:, np.newaxis] + np.sum(centroids**2, axis=1) - 2 * np.dot(X, centroids.T)
        new_labels = np.argmin(dist_sq, axis=1)
        
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        
        # Update Step (Vectorized)
        new_centroids = np.array([X[labels == i].mean(axis=0) if np.any(labels == i) 
                                  else X[np.random.randint(n)] for i in range(k)])
        centroids = new_centroids

    return centroids.tolist(), labels.tolist()

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package classical_ml;

import java.util.*;

public class KMeans {
    public static class Result {
        public double[][] centroids;
        public int[] labels;

        public Result(double[][] centroids, int[] labels) {
            this.centroids = centroids;
            this.labels = labels;
        }
    }

    public static Result solve(double[][] X, int k, int maxIters) {
        if (X == null || X.length == 0 || k <= 0) return null;
        int n = X.length;
        int d = X[0].length;
        
        // K-Means++ Initialization
        double[][] centroids = new double[k][d];
        Random rand = new Random();
        centroids[0] = X[rand.nextInt(n)].clone();
        
        for (int i = 1; i < k; i++) {
            double[] minDistSq = new double[n];
            double sumMinDistSq = 0;
            for (int j = 0; j < n; j++) {
                double minSq = Double.MAX_VALUE;
                for (int c = 0; c < i; c++) {
                    double distSq = 0;
                    for (int m = 0; m < d; m++) {
                        distSq += Math.pow(X[j][m] - centroids[c][m], 2);
                    }
                    minSq = Math.min(minSq, distSq);
                }
                minDistSq[j] = minSq;
                sumMinDistSq += minSq;
            }
            
            double target = rand.nextDouble() * sumMinDistSq;
            double currentSum = 0;
            for (int j = 0; j < n; j++) {
                currentSum += minDistSq[j];
                if (currentSum >= target) {
                    centroids[i] = X[j].clone();
                    break;
                }
            }
        }

        int[] labels = new int[n];
        for (int iter = 0; iter < maxIters; iter++) {
            boolean changed = false;
            
            // Assignment
            for (int i = 0; i < n; i++) {
                double minDist = Double.MAX_VALUE;
                int bestCluster = 0;
                for (int j = 0; j < k; j++) {
                    double distSq = 0;
                    for (int m = 0; m < d; m++) {
                        distSq += Math.pow(X[i][m] - centroids[j][m], 2);
                    }
                    if (distSq < minDist) {
                        minDist = distSq;
                        bestCluster = j;
                    }
                }
                if (labels[i] != bestCluster) {
                    labels[i] = bestCluster;
                    changed = true;
                }
            }
            
            if (!changed) break;
            
            // Update
            double[][] newCentroids = new double[k][d];
            int[] counts = new int[k];
            for (int i = 0; i < n; i++) {
                int cluster = labels[i];
                counts[cluster]++;
                for (int m = 0; m < d; m++) {
                    newCentroids[cluster][m] += X[i][m];
                }
            }
            
            for (int j = 0; j < k; j++) {
                if (counts[j] > 0) {
                    for (int m = 0; m < d; m++) {
                        newCentroids[j][m] /= counts[j];
                    }
                } else {
                    newCentroids[j] = X[rand.nextInt(n)].clone();
                }
            }
            centroids = newCentroids;
        }
        
        return new Result(centroids, labels);
    }
}
\"\"\"""",
}

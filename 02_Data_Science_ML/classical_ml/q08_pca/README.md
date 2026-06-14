# Principal Component Analysis (PCA)

## 📌 Overview & Concept Card

**Principal Component Analysis (PCA)** is a powerful unsupervised linear transformation technique used primarily for **dimensionality reduction**. Its core objective is to transform a high-dimensional dataset into a lower-dimensional form while retaining as much of the original **variance** (information) as possible.

In many real-world datasets, features are often redundant or highly correlated. PCA identifies the directions (called **Principal Components**) along which the variation in the data is maximal. By projecting the data onto these components, we can reduce the number of features, mitigate the "Curse of Dimensionality," reduce noise, and enable the visualization of complex data in 2D or 3D space.

### Core Objectives:
- **Feature Reduction**: Reduce the number of input variables to decrease computational cost.
- **Noise Filtering**: Remove components with low variance, which often represent noise.
- **Visualization**: Project high-dimensional data into 2D or 3D for exploratory data analysis.
- **Decorrelation**: Transform correlated features into a set of linearly uncorrelated components.

---

## 📐 Theoretical Foundations & Math

PCA relies on linear algebra, specifically the concepts of **Covariance**, **Eigenvectors**, and **Eigenvalues**.

### 1. Standardization
Since PCA is based on variance, it is sensitive to the scale of the features. If one feature ranges from 0 to 1 and another from 0 to 1000, the latter will dominate the principal components. We apply **Z-score normalization**:
$$z = \frac{x - \mu}{\sigma}$$
Where $\mu$ is the mean and $\sigma$ is the standard deviation.

### 2. The Covariance Matrix
The covariance matrix $\Sigma$ captures how two variables change together. For a centered data matrix $X$ (where columns have mean 0), the covariance matrix is calculated as:
$$\Sigma = \frac{1}{n-1} X^T X$$
- **Diagonal elements**: Variance of individual features.
- **Off-diagonal elements**: Covariance between feature $i$ and feature $j$.

### 3. Eigen-Decomposition
We solve the characteristic equation to find the **eigenvalues** ($\lambda$) and **eigenvectors** ($v$):
$$\Sigma v = \lambda v$$
- **Eigenvector ($v$)**: Defines the direction of the new axis (the Principal Component).
- **Eigenvalue ($\lambda$)**: Defines the magnitude of the variance explained by that eigenvector.

### 4. Explained Variance Ratio
To decide how many components ($k$) to keep, we calculate the proportion of total variance explained by each component:
$$\text{Explained Variance Ratio} = \frac{\lambda_i}{\sum_{j=1}^{d} \lambda_j}$$

---

## 🛠️ Step-by-Step Logic

The implementation of PCA follows a strict linear algebraic pipeline:

1.  **Center the Data**: Subtract the mean of each feature from the dataset. This ensures the data is centered at the origin.
2.  **Compute Covariance Matrix**: Generate the $d \times d$ matrix representing the relationships between all pairs of features.
3.  **Eigendecomposition**: Compute the eigenvalues and corresponding eigenvectors of the covariance matrix.
4.  **Sort and Select**: 
    - Sort eigenvalues in descending order.
    - Select the top $k$ eigenvectors corresponding to the $k$ largest eigenvalues.
5.  **Projection**: Create a projection matrix $W$ from the selected eigenvectors. Transform the original data $X$ into the new subspace $X'$:
    $$X' = X \cdot W$$

### Implementation Example (Optimal Approach)

```python
import numpy as np

def solve_optimal(X, k):
    """
    Performs PCA to reduce dimensionality to k components.
    X: Input data matrix of shape (n_samples, n_features)
    k: Number of principal components to keep
    """
    # 1. Standardization (Centering)
    X_centered = X - np.mean(X, axis=0)
    
    # 2. Compute Covariance Matrix
    # rowvar=False indicates that columns are variables, rows are observations
    cov_matrix = np.cov(X_centered, rowvar=False)
    
    # 3. Eigen-decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # 4. Sort eigenvectors by eigenvalues in descending order
    # eigh returns them in ascending order, so we reverse them
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # 5. Select the top k eigenvectors
    projection_matrix = eigenvectors[:, :k]
    
    # 6. Project the data onto the principal components
    X_pca = np.dot(X_centered, projection_matrix)
    
    return X_pca, eigenvalues[:k]

# Example usage
if __name__ == "__main__":
    data = np.array([[2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0], [2.3, 2.7], [2, 1.6], [1, 1.1], [1.5, 1.6], [1.1, 0.9]])
    reduced_data, var = solve_optimal(data, 1)
    print("Reduced Data:\n", reduced_data)
```

---

## ⏱️ Complexity & Training Details

### Computational Complexity
Given $n$ samples and $d$ features:

| Step | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Centering** | $O(nd)$ | $O(nd)$ | Simple subtraction across matrix |
| **Covariance Matrix** | $O(d^2 n)$ | $O(d^2)$ | Matrix multiplication $X^T X$ |
| **Eigen-decomposition** | $O(d^3)$ | $O(d^2)$ | Solving for eigenvalues/vectors |
| **Projection** | $O(ndk)$ | $O(nk)$ | Dot product with projection matrix |

**Total Time Complexity**: $O(d^2 n + d^3)$. 
*Crucial Insight*: PCA becomes computationally expensive as the number of features $d$ increases, regardless of the number of samples $n$.

### Key Hyperparameters & Metrics
- **$k$ (Number of Components)**: The most critical hyperparameter. Often chosen by plotting a "Scree Plot" and looking for the "elbow" or by ensuring a cumulative explained variance (e.g., $> 95\%$).
- **Explained Variance**: Used as the primary metric to evaluate how much information was lost during reduction.

---

## 🌍 Real-World Applications

1.  **Image Processing (Eigenfaces)**:
    In facial recognition, PCA is used to reduce the thousands of pixels in an image to a few "eigenfaces" (principal components of face images), allowing the system to compare faces based on a few key features rather than every pixel.

2.  **Genomics**:
    Biologists deal with datasets containing tens of thousands of gene expression levels. PCA helps identify the most significant genetic markers and visualize clusters of similar samples (e.g., distinguishing healthy vs. diseased tissues).

3.  **Financial Analysis**:
    Used in portfolio management to identify the primary drivers of risk and return across a large set of correlated assets (stock market indices).

4.  **Preprocessing for Other ML Models**:
    PCA is often used as a step before applying algorithms like **K-Means Clustering** or **Support Vector Machines (SVM)** to improve training speed and prevent overfitting by reducing the feature space.
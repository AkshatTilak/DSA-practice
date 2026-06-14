INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Eigenvalue dimension reduction.',
    'groups': ['Classical ML', 'Dimensionality Reduction'],
    'readme_content': """# Principal Component Analysis (PCA)

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
    \"\"\"
    Performs PCA to reduce dimensionality to k components.
    X: Input data matrix of shape (n_samples, n_features)
    k: Number of principal components to keep
    \"\"\"
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
    PCA is often used as a step before applying algorithms like **K-Means Clustering** or **Support Vector Machines (SVM)** to improve training speed and prevent overfitting by reducing the feature space.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n * d^2 + d^3)
# Space Complexity: O(d^2)
# This approach follows the textbook definition of PCA:
# 1. Center the data by subtracting the mean.
# 2. Compute the covariance matrix.
# 3. Perform eigen-decomposition on the covariance matrix.
# 4. Sort eigenvectors by eigenvalues in descending order.
# 5. Project the centered data onto the top k eigenvectors.
import numpy as np

def solve_naive(X: np.ndarray, n_components: int) -> np.ndarray:
    # 1. Center the data
    X_centered = X - np.mean(X, axis=0)
    
    # 2. Compute covariance matrix
    # rowvar=False means columns are variables, rows are observations
    cov_matrix = np.cov(X_centered, rowvar=False)
    
    # 3. Eigen-decomposition
    # eigh is used instead of eig because the covariance matrix is symmetric
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # 4. Sort eigenvalues and eigenvectors in descending order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # 5. Select the top n_components
    projection_matrix = eigenvectors[:, :n_components]
    
    # 6. Project data
    X_reduced = np.dot(X_centered, projection_matrix)
    
    return X_reduced

# --- APPROACH 2: Optimal (SVD - Singular Value Decomposition) ---
# Time Complexity: O(n * d * min(n, d))
# Space Complexity: O(n * d)
# This approach is optimal because it avoids the explicit computation of the 
# covariance matrix (which can be numerically unstable and expensive for large d).
# The Singular Value Decomposition (SVD) of the centered data X = U * S * V^T 
# provides the right singular vectors V, which are equivalent to the 
# eigenvectors of the covariance matrix (X^T * X) / (n-1).
import numpy as np

def solve_optimal(X: np.ndarray, n_components: int) -> np.ndarray:
    # Ensure X is a float array for precision
    X = np.asanyarray(X, dtype=np.float64)
    
    # 1. Center the data
    X_centered = X - np.mean(X, axis=0)
    
    # 2. Compute SVD
    # U: left singular vectors
    # S: singular values (square roots of eigenvalues * sqrt(n-1))
    # Vt: right singular vectors (transposed)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    
    # 3. The columns of V (rows of Vt) are the principal components
    # We take the first n_components rows of Vt
    components = Vt[:n_components]
    
    # 4. Project the centered data onto the principal components
    # X_reduced = X_centered @ V_k = X_centered @ Vt_k.T
    X_reduced = np.dot(X_centered, components.T)
    
    return X_reduced

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package classical_ml;

import java.util.*;

/**
 * PCA implementation using a conceptual Linear Algebra library 
 * (Similar to Apache Commons Math or EJML).
 */
public class Pca {

    public static double[][] fitTransform(double[][] X, int nComponents) {
        int n = X.length;
        int d = X[0].length;
        
        // 1. Center the data
        double[] means = new double[d];
        for (int j = 0; j < d; j++) {
            double sum = 0;
            for (int i = 0; i < n; i++) {
                sum += X[i][j];
            }
            means[j] = sum / n;
        }
        
        double[][] XCentered = new double[n][d];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < d; j++) {
                XCentered[i][j] = X[i][j] - means[j];
            }
        }
        
        // 2. Compute Covariance Matrix (X^T * X) / (n - 1)
        double[][] cov = new double[d][d];
        for (int i = 0; i < d; i++) {
            for (int j = 0; j < d; j++) {
                double sum = 0;
                for (int k = 0; k < n; k++) {
                    sum += XCentered[k][i] * XCentered[k][j];
                }
                cov[i][j] = sum / (n - 1);
            }
        }
        
        // 3. Eigen-decomposition (Simulation of a library call like EigenDecomposition)
        // In a real production environment, one would use:
        // EigenDecomposition ed = new EigenDecomposition(new Array2DRowRealMatrix(cov));
        // RealMatrix eigenvectors = ed.getV();
        
        // For this example, assume we have a method that returns sorted eigenvectors
        double[][] allEigenvectors = mockEigenDecomposition(cov); 
        
        // 4. Projection
        double[][] XReduced = new double[n][nComponents];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < nComponents; j++) {
                double dotProduct = 0;
                for (int k = 0; k < d; k++) {
                    dotProduct += XCentered[i][k] * allEigenvectors[k][j];
                }
                XReduced[i][j] = dotProduct;
            }
        }
        
        return XReduced;
    }

    private static double[][] mockEigenDecomposition(double[][] cov) {
        // This is a placeholder for the actual numerical algorithm (like QR algorithm)
        // that computes eigenvectors sorted by eigenvalue magnitude.
        int d = cov.length;
        return new double[d][d]; 
    }
    
    public static void main(String[] args) {
        double[][] data = {
            {2.5, 2.4},
            {0.5, 0.7},
            {2.2, 2.9},
            {1.9, 2.2},
            {3.1, 3.0},
            {2.3, 2.7},
            {2.0, 1.6},
            {1.0, 1.1},
            {1.5, 1.6},
            {1.1, 0.9}
        };
        double[][] reduced = fitTransform(data, 1);
        System.out.println("Reduced data shape: " + reduced.length + "x" + reduced[0].length);
    }
}
\"\"\"""",
}

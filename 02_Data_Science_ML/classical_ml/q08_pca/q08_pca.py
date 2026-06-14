"""
Challenge: q08_pca
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Eigenvalue dimension reduction.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

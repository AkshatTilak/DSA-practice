"""
Challenge: q06_support_vector_machines
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Hyperplane margins.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N * D)
# Space Complexity: O(1)
# This approach iterates through each data point and calculates the geometric margin individually 
# using basic Python loops and arithmetic, avoiding any vectorization or heavy libraries.
def calculate_margin_naive(X, y, w, b):
    if not X or len(X) == 0:
        return 0.0
    
    # Calculate the L2 norm of the weight vector w manually
    w_norm_sq = 0.0
    for val in w:
        w_norm_sq += val * val
    w_norm = w_norm_sq**0.5
    
    if w_norm == 0:
        return 0.0
        
    min_margin = float('inf')
    for i in range(len(X)):
        # Calculate dot product of X[i] and w
        dot_product = 0.0
        for j in range(len(w)):
            dot_product += X[i][j] * w[j]
        
        # Geometric margin formula: y_i * (w^T * x_i + b) / ||w||
        # y[i] is assumed to be in {-1, 1}
        current_margin = (y[i] * (dot_product + b)) / w_norm
        if current_margin < min_margin:
            min_margin = current_margin
            
    return float(min_margin)

# --- APPROACH 2: Optimal (NumPy Vectorization) ---
# Time Complexity: O(N * D)
# Space Complexity: O(N)
# This approach uses NumPy's highly optimized BLAS backends for matrix-vector multiplication.
# It computes all distance values in a single vectorized operation, significantly reducing 
# overhead and improving performance on large datasets.
import numpy as np

def calculate_margin_optimal(X, y, w, b):
    # Convert inputs to numpy arrays for vectorization
    X = np.asarray(X)
    y = np.asarray(y)
    w = np.asarray(w)
    
    if X.size == 0:
        return 0.0
        
    # Calculate the L2 norm of weight vector w
    w_norm = np.linalg.norm(w)
    if w_norm == 0:
        return 0.0
        
    # X @ w computes the dot product for all samples: (N, D) @ (D,) -> (N,)
    # (X @ w + b) is the functional margin for each point
    # y * (X @ w + b) scales by the label to get signed functional margins
    # Dividing by w_norm converts functional margins to geometric margins
    margins = (y * (X @ w + b)) / w_norm
    
    return float(np.min(margins))

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package classical_ml;

import java.util.Arrays;

public class SupportVectorMachines {

    /**
     * Calculates the geometric margin of a hyperplane relative to a dataset.
     * 
     * @param X The input feature matrix [N][D]
     * @param y The labels array [N], expected values are -1 or 1
     * @param w The weight vector [D]
     * @param b The bias scalar
     * @return The minimum geometric margin
     */
    public static double calculateMargin(double[][] X, int[] y, double[] w, double b) {
        if (X == null || X.length == 0) {
            return 0.0;
        }

        // Calculate L2 norm of weight vector w
        double wNormSq = 0.0;
        for (double val : w) {
            wNormSq += val * val;
        }
        double wNorm = Math.sqrt(wNormSq);

        if (wNorm == 0) {
            return 0.0;
        }

        double minMargin = Double.POSITIVE_INFINITY;
        int numSamples = X.length;
        int numFeatures = w.length;

        for (int i = 0; i < numSamples; i++) {
            double dotProduct = 0.0;
            for (int j = 0; j < numFeatures; j++) {
                dotProduct += X[i][j] * w[j];
            }
            
            // Geometric margin: y_i * (w^T * x_i + b) / ||w||
            double currentMargin = (y[i] * (dotProduct + b)) / wNorm;
            if (currentMargin < minMargin) {
                minMargin = currentMargin;
            }
        }

        return minMargin;
    }

    public static void main(String[] args) {
        double[][] X = {{1.0, 2.0}, {2.0, 1.0}, {3.0, 3.0}, {1.0, 0.0}};
        int[] y = {1, 1, -1, -1};
        double[] w = {1.0, 1.0};
        double b = -4.0;
        
        System.out.println("Margin: " + calculateMargin(X, y, w, b));
    }
}
"""

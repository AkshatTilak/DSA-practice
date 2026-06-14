"""
Challenge: q05_backpropagation
Difficulty: Hard
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Gradient backprop neural layer.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(batch_size * in_features * out_features)
# Space Complexity: O(batch_size * in_features + in_features * out_features + out_features)
# This approach implements the matrix multiplication and summation using nested loops,
# mimicking the mathematical definition of gradients without utilizing vectorized libraries.
import numpy as np

def solve_naive(X, W, B, dY):
    """
    Naive implementation of backpropagation for a linear layer.
    X: (batch_size, in_features)
    W: (in_features, out_features)
    B: (out_features,)
    dY: (batch_size, out_features)
    """
    batch_size, in_features = X.shape
    in_features_w, out_features = W.shape
    
    # dX = dY @ W.T
    dX = np.zeros((batch_size, in_features))
    for i in range(batch_size):
        for j in range(in_features):
            sum_val = 0
            for k in range(out_features):
                sum_val += dY[i, k] * W[j, k]
            dX[i, j] = sum_val
            
    # dW = X.T @ dY
    dW = np.zeros((in_features, out_features))
    for i in range(in_features):
        for j in range(out_features):
            sum_val = 0
            for k in range(batch_size):
                sum_val += X[k, i] * dY[k, j]
            dW[i, j] = sum_val
            
    # dB = sum(dY, axis=0)
    dB = np.zeros(out_features)
    for j in range(out_features):
        sum_val = 0
        for i in range(batch_size):
            sum_val += dY[i, j]
        dB[j] = sum_val
        
    return dX, dW, dB

# --- APPROACH 2: Optimal (Vectorized NumPy) ---
# Time Complexity: O(batch_size * in_features * out_features)
# Space Complexity: O(batch_size * in_features + in_features * out_features + out_features)
# This approach uses NumPy's highly optimized BLAS backend for matrix multiplication.
# Vectorization allows the hardware to utilize SIMD instructions and efficient cache 
# management, significantly reducing the constant factor of the O(N^3) complexity.
import numpy as np

def solve_optimal(X, W, B, dY):
    """
    Optimal implementation of backpropagation for a linear layer using vectorization.
    X: (batch_size, in_features)
    W: (in_features, out_features)
    B: (out_features,)
    dY: (batch_size, out_features)
    """
    # dL/dX = dL/dY * W^T
    # (batch_size, out_features) @ (out_features, in_features) -> (batch_size, in_features)
    dX = np.dot(dY, W.T)
    
    # dL/dW = X^T * dL/dY
    # (in_features, batch_size) @ (batch_size, out_features) -> (in_features, out_features)
    dW = np.dot(X.T, dY)
    
    # dL/dB = sum of dL/dY over the batch dimension
    # (batch_size, out_features) -> (out_features,)
    dB = np.sum(dY, axis=0)
    
    return dX, dW, dB

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package architectures;

import java.util.Arrays;

public class Backpropagation {
    /**
     * Computes the gradients for a linear layer.
     * 
     * @param X Input matrix of shape [batchSize][inFeatures]
     * @param W Weight matrix of shape [inFeatures][outFeatures]
     * @param B Bias vector of shape [outFeatures]
     * @param dY Gradient of loss w.r.t output of shape [batchSize][outFeatures]
     * @return A result object containing dX, dW, and dB.
     */
    public static class Gradients {
        public double[][] dX;
        public double[][] dW;
        public double[] dB;

        public Gradients(double[][] dX, double[][] dW, double[] dB) {
            this.dX = dX;
            this.dW = dW;
            this.dB = dB;
        }
    }

    public static Gradients solve(double[][] X, double[][] W, double[] B, double[][] dY) {
        int batchSize = X.length;
        int inFeatures = X[0].length;
        int outFeatures = W[0].length;

        double[][] dX = new double[batchSize][inFeatures];
        double[][] dW = new double[inFeatures][outFeatures];
        double[] dB = new double[outFeatures];

        // Calculate dX = dY @ W^T
        for (int i = 0; i < batchSize; i++) {
            for (int j = 0; j < inFeatures; j++) {
                double sum = 0;
                for (int k = 0; k < outFeatures; k++) {
                    sum += dY[i][k] * W[j][k];
                }
                dX[i][j] = sum;
            }
        }

        // Calculate dW = X^T @ dY
        for (int i = 0; i < inFeatures; i++) {
            for (int j = 0; j < outFeatures; j++) {
                double sum = 0;
                for (int k = 0; k < batchSize; k++) {
                    sum += X[k][i] * dY[k][j];
                }
                dW[i][j] = sum;
            }
        }

        // Calculate dB = sum(dY, axis=0)
        for (int j = 0; j < outFeatures; j++) {
            double sum = 0;
            for (int i = 0; i < batchSize; i++) {
                sum += dY[i][j];
            }
            dB[j] = sum;
        }

        return new Gradients(dX, dW, dB);
    }

    public static void main(String[] args) {
        // Simple test case
        double[][] X = {{1.0, 2.0}, {3.0, 4.0}};
        double[][] W = {{0.1, 0.2}, {0.3, 0.4}};
        double[] B = {0.5, 0.6};
        double[][] dY = {{0.01, 0.02}, {0.03, 0.04}};
        
        Gradients g = solve(X, W, B, dY);
        System.out.println("dX: " + Arrays.deepToString(g.dX));
        System.out.println("dW: " + Arrays.deepToString(g.dW));
        System.out.println("dB: " + Arrays.toString(g.dB));
    }
}
"""

"""
Challenge: q01_self_attention
Difficulty: Hard
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Calculate scaled dot-product self-attention weights and final contextual projections.
"""

# --- STARTER TEMPLATE FOR USER ---
import numpy as np

def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Returns (output, attention_weights)
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n * m * (dk + dv))
# Space Complexity: O(n * m)
# This approach avoids using NumPy's optimized matrix multiplication and instead uses nested loops to calculate the dot products and the final projections. It serves as a conceptual implementation of the attention mechanism.
import numpy as np

def scaled_dot_product_attention_naive(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n, dk = Q.shape
    m, dk_k = K.shape
    m_v, dv = V.shape
    
    if dk != dk_k:
        raise ValueError("Dimension of Q and K must match.")
    if m != m_v:
        raise ValueError("Number of keys must match number of values.")

    # 1. Calculate QK^T manually
    scores = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            dot_product = 0
            for k in range(dk):
                dot_product += Q[i, k] * K[j, k]
            scores[i, j] = dot_product / np.sqrt(dk)

    # 2. Softmax manually (row-wise)
    attention_weights = np.zeros((n, m))
    for i in range(n):
        # Numerical stability: subtract max
        row_max = np.max(scores[i, :])
        exp_sum = 0
        row_exp = np.zeros(m)
        for j in range(m):
            row_exp[j] = np.exp(scores[i, j] - row_max)
            exp_sum += row_exp[j]
        for j in range(m):
            attention_weights[i, j] = row_exp[j] / exp_sum

    # 3. Calculate AttentionWeights * V manually
    output = np.zeros((n, dv))
    for i in range(n):
        for j in range(dv):
            val_sum = 0
            for k in range(m):
                val_sum += attention_weights[i, k] * V[k, j]
            output[i, j] = val_sum

    return output, attention_weights

# --- APPROACH 2: Optimal (Vectorized NumPy) ---
# Time Complexity: O(n * m * (dk + dv))
# Space Complexity: O(n * m)
# This approach uses NumPy's highly optimized BLAS-backed matrix multiplication (@ operator) and vectorized operations. It is optimal because it minimizes Python overhead and leverages SIMD instructions for floating-point calculations.
def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # d_k is the dimensionality of the query/key vectors
    dk = Q.shape[-1]
    
    # Step 1: Compute scaled dot-product scores
    # Q: (n, dk), K: (m, dk) -> scores: (n, m)
    # Using np.matmul or @ for efficient matrix multiplication
    scores = (Q @ K.T) / np.sqrt(dk)
    
    # Step 2: Apply softmax to get attention weights
    # For numerical stability, subtract the maximum value in each row
    # softmax(x) = exp(x - max(x)) / sum(exp(x - max(x)))
    # axis=-1 ensures softmax is computed across the key dimension (m)
    max_scores = np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(scores - max_scores)
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    
    # Step 3: Compute final contextual projections
    # weights: (n, m), V: (m, dv) -> output: (n, dv)
    output = attention_weights @ V
    
    return output, attention_weights

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package architectures;

import java.util.Arrays;

public class SelfAttention {

    /**
     * Calculates scaled dot-product attention.
     * 
     * @param Q Query matrix [n][dk]
     * @param K Key matrix [m][dk]
     * @param V Value matrix [m][dv]
     * @return An array containing [outputMatrix, weightsMatrix]
     */
    public static double[][][] scaledDotProductAttention(double[][] Q, double[][] K, double[][] V) {
        int n = Q.length;
        int dk = Q[0].length;
        int m = K.length;
        int dv = V[0].length;

        // 1. Q * K^T / sqrt(dk)
        double[][] scores = new double[n][m];
        double scale = Math.sqrt(dk);
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                double dot = 0;
                for (int k = 0; k < dk; k++) {
                    dot += Q[i][k] * K[j][k];
                }
                scores[i][j] = dot / scale;
            }
        }

        // 2. Softmax (Row-wise)
        double[][] weights = new double[n][m];
        for (int i = 0; i < n; i++) {
            double maxVal = Double.NEGATIVE_INFINITY;
            for (int j = 0; j < m; j++) {
                if (scores[i][j] > maxVal) maxVal = scores[i][j];
            }

            double sumExp = 0;
            for (int j = 0; j < m; j++) {
                weights[i][j] = Math.exp(scores[i][j] - maxVal);
                sumExp += weights[i][j];
            }

            for (int j = 0; j < m; j++) {
                weights[i][j] /= sumExp;
            }
        }

        // 3. Weights * V
        double[][] output = new double[n][dv];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < dv; j++) {
                double sum = 0;
                for (int k = 0; k < m; k++) {
                    sum += weights[i][k] * V[k][j];
                }
                output[i][j] = sum;
            }
        }

        return new double[][][]{output, weights};
    }

    public static void main(String[] args) {
        double[][] Q = {{1.0, 0.0, 1.0}, {0.0, 1.0, 0.0}};
        double[][] K = {{1.0, 0.0, 1.0}, {0.0, 1.0, 0.0}, {1.0, 1.0, 1.0}};
        double[][] V = {{10.0, 0.0}, {0.0, 5.0}, {2.0, 2.0}};

        double[][][] result = scaledDotProductAttention(Q, K, V);
        double[][] output = result[0];
        double[][] weights = result[1];

        System.out.println("Output: " + Arrays.deepToString(output));
        System.out.println("Weights: " + Arrays.deepToString(weights));
    }
}
"""

"""
Challenge: q04_log_loss
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Binary cross-entropy loss.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach uses a simple for-loop to iterate through the labels and predictions.
# It uses basic math.log and manually clips the values to avoid numerical instability 
# (log(0) is undefined).
import math

def solve_naive(y_true, y_pred):
    """
    Computes binary cross-entropy loss using a naive loop.
    """
    if not y_true or not y_pred:
        return 0.0
    
    if len(y_true) != len(y_pred):
        raise ValueError("The length of y_true and y_pred must be the same.")
    
    n = len(y_true)
    total_loss = 0.0
    eps = 1e-15  # Small constant to prevent log(0)
    
    for yt, yp in zip(y_true, y_pred):
        # Clip yp to be within [eps, 1 - eps]
        yp_clipped = max(eps, min(1.0 - eps, yp))
        total_loss += yt * math.log(yp_clipped) + (1 - yt) * math.log(1.0 - yp_clipped)
        
    return -total_loss / n

# --- APPROACH 2: Optimal (Vectorized NumPy) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach is optimal for production data science tasks because it leverages 
# NumPy's SIMD (Single Instruction, Multiple Data) optimizations. Vectorization 
# removes Python loop overhead, making it orders of magnitude faster for large datasets.
import numpy as np

def solve_optimal(y_true, y_pred):
    """
    Computes binary cross-entropy loss using NumPy vectorization.
    """
    # Convert inputs to numpy arrays for vectorized operations
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    if y_true.size == 0:
        return 0.0
    
    if y_true.shape != y_pred.shape:
        raise ValueError("The shapes of y_true and y_pred must be the same.")
    
    # Clipping to avoid log(0) or log(1) which results in -inf or nan
    eps = 1e-15
    y_pred = np.clip(y_pred, eps, 1 - eps)
    
    # Formula: -1/N * sum(y_true * log(y_pred) + (1 - y_true) * log(1 - y_pred))
    loss = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
    return float(loss)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

import java.util.Objects;

public class LogLoss {
    /**
     * Computes the binary cross-entropy loss.
     * 
     * @param yTrue Array of ground truth labels (0 or 1).
     * @param yPred Array of predicted probabilities (0.0 to 1.0).
     * @return The computed log loss.
     * @throws IllegalArgumentException if inputs are null or have different lengths.
     */
    public static double computeLogLoss(double[] yTrue, double[] yPred) {
        if (yTrue == null || yPred == null) {
            throw new IllegalArgumentException("Input arrays cannot be null.");
        }
        if (yTrue.length != yPred.length) {
            throw new IllegalArgumentException("Input arrays must have the same length.");
        }
        if (yTrue.length == 0) {
            return 0.0;
        }

        double totalLoss = 0.0;
        double eps = 1e-15;
        int n = yTrue.length;

        for (int i = 0; i < n; i++) {
            double yt = yTrue[i];
            double yp = yPred[i];
            
            // Clip prediction to avoid log(0)
            double ypClipped = Math.max(eps, Math.min(1.0 - eps, yp));
            
            totalLoss += yt * Math.log(ypClipped) + (1.0 - yt) * Math.log(1.0 - ypClipped);
        }

        return -totalLoss / n;
    }

    public static void main(String[] args) {
        double[] yTrue = {1.0, 0.0, 1.0, 1.0};
        double[] yPred = {0.9, 0.1, 0.8, 0.4};
        System.out.println("Log Loss: " + computeLogLoss(yTrue, yPred));
    }
}
"""

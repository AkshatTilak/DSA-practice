"""
Challenge: q05_mape
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Mean Absolute Percentage Error.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses a simple for-loop to iterate through the lists and calculate the 
# absolute percentage error for each pair of actual and predicted values.
def solve_naive(y_true: list, y_pred: list) -> float:
    if not y_true or not y_pred:
        return 0.0
    
    if len(y_true) != len(y_pred):
        raise ValueError("The length of y_true and y_pred must be equal.")
    
    total_ape = 0.0
    n = len(y_true)
    
    for i in range(n):
        actual = y_true[i]
        predicted = y_pred[i]
        
        # Handle division by zero: if actual is 0, we use a very small epsilon
        # to avoid ZeroDivisionError, as is common in basic implementations.
        denominator = actual if actual != 0 else 1e-10
        total_ape += abs((actual - predicted) / denominator)
    
    mape = (total_ape / n) * 100
    return float(mape)

# --- APPROACH 2: Optimal (NumPy Vectorization) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach is optimal for Data Science/ML tasks because it leverages NumPy's 
# SIMD (Single Instruction, Multiple Data) capabilities. Vectorized operations 
# are implemented in C and are significantly faster than Python loops for large datasets.
import numpy as np

def solve_optimal(y_true: list, y_pred: list) -> float:
    if not y_true or not y_pred:
        return 0.0
    
    # Convert inputs to numpy arrays for vectorized operations
    y_true_arr = np.array(y_true, dtype=np.float64)
    y_pred_arr = np.array(y_pred, dtype=np.float64)
    
    if y_true_arr.shape != y_pred_arr.shape:
        raise ValueError("The length of y_true and y_pred must be equal.")
    
    # Use a mask or np.where to handle potential zeros in y_true to avoid division by zero
    # This prevents the result from becoming 'inf' or 'nan'
    epsilon = 1e-10
    safe_y_true = np.where(y_true_arr == 0, epsilon, y_true_arr)
    
    # Vectorized MAPE formula: (1/n) * sum(|(y_true - y_pred) / y_true|) * 100
    ape = np.abs((y_true_arr - y_pred_arr) / safe_y_true)
    mape = np.mean(ape) * 100
    
    return float(mape)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

import java.util.Objects;

public class Mape {
    /**
     * Calculates the Mean Absolute Percentage Error (MAPE).
     * 
     * @param yTrue Array of actual values.
     * @param yPred Array of predicted values.
     * @return The MAPE value as a percentage.
     * @throws IllegalArgumentException if arrays are null or have different lengths.
     */
    public static double solveOptimal(double[] yTrue, double[] yPred) {
        if (yTrue == null || yPred == null) {
            throw new IllegalArgumentException("Input arrays cannot be null.");
        }
        if (yTrue.length != yPred.length) {
            throw new IllegalArgumentException("The length of yTrue and yPred must be equal.");
        }
        if (yTrue.length == 0) {
            return 0.0;
        }

        double totalApe = 0.0;
        int n = yTrue.length;
        double epsilon = 1e-10;

        for (int i = 0; i < n; i++) {
            double actual = yTrue[i];
            double predicted = yPred[i];
            
            // Handle division by zero using epsilon for stability
            double denominator = (actual == 0) ? epsilon : actual;
            totalApe += Math.abs((actual - predicted) / denominator);
        }

        return (totalApe / n) * 100.0;
    }

    public static void main(String[] args) {
        double[] actuals = {100.0, 150.0, 200.0, 0.0};
        double[] forecasts = {110.0, 140.0, 210.0, 5.0};
        System.out.println("MAPE: " + solveOptimal(actuals, forecasts));
    }
}
"""

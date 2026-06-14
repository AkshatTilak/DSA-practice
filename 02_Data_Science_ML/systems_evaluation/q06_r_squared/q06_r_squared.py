"""
Challenge: q06_r_squared
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Coefficient of determination.
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
# This approach uses explicit for-loops to calculate the mean, the sum of squares of residuals (SS_res), 
# and the total sum of squares (SS_tot). It is a straightforward implementation of the mathematical formula.
def solve_naive(y_true, y_pred):
    if not y_true or not y_pred:
        return 0.0
    if len(y_true) != len(y_pred):
        raise ValueError("The length of y_true and y_pred must be the same.")
    
    n = len(y_true)
    
    # Calculate mean of y_true
    sum_true = 0.0
    for val in y_true:
        sum_true += val
    mean_true = sum_true / n
    
    # Calculate SS_res and SS_tot
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(n):
        ss_res += (y_true[i] - y_pred[i]) ** 2
        ss_tot += (y_true[i] - mean_true) ** 2
        
    # Handle edge case where SS_tot is 0 (all y_true values are the same)
    if ss_tot == 0:
        return 0.0 if ss_res != 0 else 1.0
        
    return 1 - (ss_res / ss_tot)

# --- APPROACH 2: Optimal (Vectorized-style Pythonic) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach leverages Python's built-in sum() function with generator expressions, which are 
# implemented in C and are significantly faster than explicit for-loops. It maintains O(1) 
# auxiliary space by not creating intermediate lists.
def solve_optimal(y_true, y_pred):
    if not y_true or not y_pred:
        return 0.0
    
    n = len(y_true)
    if n != len(y_pred):
        raise ValueError("The length of y_true and y_pred must be the same.")
    
    # Calculate mean efficiently
    mean_true = sum(y_true) / n
    
    # Calculate SS_res and SS_tot using generator expressions
    # These are memory efficient as they don't materialize the list in memory
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred))
    ss_tot = sum((yt - mean_true) ** 2 for yt in y_true)
    
    # Handle the case where the variance of y_true is zero
    if ss_tot == 0:
        # If the prediction is also a constant equal to the true value, R^2 is 1.0
        return 1.0 if ss_res == 0 else 0.0
        
    return 1 - (ss_res / ss_tot)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

public class RSquared {
    /**
     * Calculates the coefficient of determination (R^2).
     * 
     * @param yTrue Array of actual observed values.
     * @param yPred Array of predicted values.
     * @return The R^2 score.
     * @throws IllegalArgumentException if input arrays are null or have different lengths.
     */
    public static double calculateRSquared(double[] yTrue, double[] yPred) {
        if (yTrue == null || yPred == null) {
            throw new IllegalArgumentException("Input arrays cannot be null.");
        }
        if (yTrue.length != yPred.length) {
            throw new IllegalArgumentException("Input arrays must have the same length.");
        }
        if (yTrue.length == 0) {
            return 0.0;
        }

        int n = yTrue.length;
        double sumTrue = 0.0;
        for (double val : yTrue) {
            sumTrue += val;
        }
        double meanTrue = sumTrue / n;

        double ssRes = 0.0;
        double ssTot = 0.0;
        for (int i = 0; i < n; i++) {
            double diffRes = yTrue[i] - yPred[i];
            double diffTot = yTrue[i] - meanTrue;
            ssRes += diffRes * diffRes;
            ssTot += diffTot * diffTot;
        }

        if (ssTot == 0) {
            return (ssRes == 0) ? 1.0 : 0.0;
        }

        return 1.0 - (ssRes / ssTot);
    }

    public static void main(String[] args) {
        double[] yTrue = {3, -0.5, 2, 7};
        double[] yPred = {2.5, 0.0, 2, 8};
        System.out.println("R^2 Score: " + calculateRSquared(yTrue, yPred));
    }
}
"""

"""
Challenge: q03_mean_squared_error
Difficulty: Easy
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
MSE calculator.
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
# Space Complexity: O(n)
# This approach calculates the squared differences and stores them in a temporary list before summing them up.
def solve_naive(y_true, y_pred):
    if not y_true or not y_pred:
        return 0.0
    
    if len(y_true) != len(y_pred):
        raise ValueError("The lengths of y_true and y_pred must be equal.")
    
    squared_errors = []
    for i in range(len(y_true)):
        diff = y_true[i] - y_pred[i]
        squared_errors.append(diff ** 2)
    
    return sum(squared_errors) / len(y_true)

# --- APPROACH 2: Optimal (Generator Expression) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses a generator expression within the sum() function, avoiding the creation of an intermediate list in memory. 
# It is optimal because it processes the elements in a single pass with constant auxiliary space.
def solve_optimal(y_true, y_pred):
    if not y_true:
        return 0.0
    
    n = len(y_true)
    if n != len(y_pred):
        raise ValueError("The lengths of y_true and y_pred must be equal.")
    
    # Using a generator expression to calculate MSE efficiently
    mse = sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred)) / n
    return float(mse)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

public class MeanSquaredError {
    /**
     * Calculates the Mean Squared Error between true values and predicted values.
     * 
     * @param yTrue Array of ground truth values.
     * @param yPred Array of predicted values.
     * @return The calculated MSE.
     * @throws IllegalArgumentException if the input arrays have different lengths.
     */
    public static double calculateMSE(double[] yTrue, double[] yPred) {
        if (yTrue == null || yPred == null) {
            return 0.0;
        }
        
        if (yTrue.length != yPred.length) {
            throw new IllegalArgumentException("The lengths of yTrue and yPred must be equal.");
        }
        
        if (yTrue.length == 0) {
            return 0.0;
        }

        double sumSquaredErrors = 0.0;
        for (int i = 0; i < yTrue.length; i++) {
            double diff = yTrue[i] - yPred[i];
            sumSquaredErrors += diff * diff;
        }

        return sumSquaredErrors / yTrue.length;
    }

    public static void main(String[] args) {
        double[] trueVals = {1.0, 2.0, 3.0};
        double[] predVals = {1.1, 1.9, 3.2};
        System.out.println("MSE: " + calculateMSE(trueVals, predVals));
    }
}
"""

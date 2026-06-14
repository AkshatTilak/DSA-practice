"""
Challenge: q01_linear_regression
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Implement linear regression fitting using gradient descent from scratch.
"""

# --- STARTER TEMPLATE FOR USER ---
import numpy as np

def fit_linear_regression(X: np.ndarray, y: np.ndarray, lr=0.01, epochs=100) -> tuple[np.ndarray, float]:
    # Return weights (np.ndarray) and bias (float)
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(epochs * n_samples * n_features)
# Space Complexity: O(n_features)
# This approach implements gradient descent using nested Python loops to calculate the predictions and gradients.
# While logically correct, it is highly inefficient for larger datasets as it does not leverage 
# vectorized operations provided by NumPy.
def fit_linear_regression_naive(X: np.ndarray, y: np.ndarray, lr=0.01, epochs=100) -> tuple[np.ndarray, float]:
    n_samples, n_features = X.shape
    weights = np.zeros(n_features)
    bias = 0.0
    
    for _ in range(epochs):
        dw = np.zeros(n_features)
        db = 0.0
        
        for i in range(n_samples):
            # Linear combination: y_hat = sum(x_ij * w_j) + b
            prediction = 0.0
            for j in range(n_features):
                prediction += X[i, j] * weights[j]
            prediction += bias
            
            error = prediction - y[i]
            
            # Gradient for weights and bias
            for j in range(n_features):
                dw[j] += error * X[i, j]
            db += error
            
        # Update weights and bias using the average gradient
        for j in range(n_features):
            weights[j] -= lr * (dw[j] / n_samples)
        bias -= lr * (db / n_samples)
        
    return weights, bias

# --- APPROACH 2: Optimal (Vectorized Gradient Descent) ---
# Time Complexity: O(epochs * n_samples * n_features)
# Space Complexity: O(n_features)
# This approach is optimal because it uses NumPy's vectorized operations (matrix multiplication), 
# which are implemented in C and BLAS. This drastically reduces the overhead of Python loops 
# and allows for simultaneous calculations across all samples, maximizing CPU cache efficiency.
def fit_linear_regression(X: np.ndarray, y: np.ndarray, lr=0.01, epochs=100) -> tuple[np.ndarray, float]:
    n_samples, n_features = X.shape
    weights = np.zeros(n_features)
    bias = 0.0
    
    for _ in range(epochs):
        # Vectorized prediction: y_hat = Xw + b
        y_pred = np.dot(X, weights) + bias
        
        # Calculate the error vector
        error = y_pred - y
        
        # Vectorized gradients
        # dw = (1/n) * X^T * error
        # db = (1/n) * sum(error)
        dw = (1 / n_samples) * np.dot(X.T, error)
        db = (1 / n_samples) * np.sum(error)
        
        # Update parameters
        weights -= lr * dw
        bias -= lr * db
        
    return weights, bias

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package classical_ml;

import java.util.Arrays;

public class LinearRegression {
    /**
     * Fits a linear regression model using gradient descent.
     * 
     * @param X      Feature matrix of size [n_samples][n_features]
     * @param y      Target vector of size [n_samples]
     * @param lr     Learning rate
     * @param epochs Number of iterations
     * @return An object containing weights and bias
     */
    public static Model fitLinearRegression(double[][] X, double[] y, double lr, int epochs) {
        int nSamples = X.length;
        int nFeatures = X[0].length;
        double[] weights = new double[nFeatures];
        double bias = 0.0;

        for (int epoch = 0; epoch < epochs; epoch++) {
            double[] dw = new double[nFeatures];
            double db = 0.0;

            for (int i = 0; i < nSamples; i++) {
                double prediction = 0.0;
                for (int j = 0; j < nFeatures; j++) {
                    prediction += X[i][j] * weights[j];
                }
                prediction += bias;

                double error = prediction - y[i];

                for (int j = 0; j < nFeatures; j++) {
                    dw[j] += error * X[i][j];
                }
                db += error;
            }

            // Update weights and bias
            for (int j = 0; j < nFeatures; j++) {
                weights[j] -= lr * (dw[j] / nSamples);
            }
            bias -= lr * (db / nSamples);
        }

        return new Model(weights, bias);
    }

    public static class Model {
        public double[] weights;
        public double bias;

        public Model(double[] weights, double bias) {
            this.weights = weights;
            this.bias = bias;
        }

        @Override
        public String toString() {
            return "Weights: " + Arrays.toString(weights) + ", Bias: " + bias;
        }
    }

    public static void main(String[] args) {
        double[][] X = {{1.0, 2.0}, {2.0, 3.0}, {3.0, 4.0}};
        double[] y = {5.0, 7.0, 9.0};
        Model model = fitLinearRegression(X, y, 0.01, 1000);
        System.out.println(model);
    }
}
"""

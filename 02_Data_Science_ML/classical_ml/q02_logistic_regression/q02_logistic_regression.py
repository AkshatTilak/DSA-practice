"""
Challenge: q02_logistic_regression
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Logistic regression classification.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(iterations * m * n)
# Space Complexity: O(n)
# This approach implements Logistic Regression using explicit Python loops for weight updates 
# and gradient calculations instead of vectorized operations. It is inefficient for large 
# datasets due to the overhead of Python loops.
import numpy as np

class LogisticRegressionNaive:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.lr = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = None

    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        m, n = X.shape
        self.weights = np.zeros(n)
        self.bias = 0.0

        for _ in range(self.iterations):
            # Naive loop-based calculation of predictions
            y_pred = np.zeros(m)
            for i in range(m):
                linear_model = 0
                for j in range(n):
                    linear_model += X[i][j] * self.weights[j]
                linear_model += self.bias
                y_pred[i] = self._sigmoid(linear_model)

            # Naive loop-based gradient computation
            dw = np.zeros(n)
            db = 0.0
            for i in range(m):
                diff = y_pred[i] - y[i]
                for j in range(n):
                    dw[j] += diff * X[i][j]
                db += diff
            
            # Update weights
            for j in range(n):
                self.weights[j] -= self.lr * (dw[j] / m)
            self.bias -= self.lr * (db / m)

    def predict(self, X):
        m, n = X.shape
        predictions = np.zeros(m)
        for i in range(m):
            linear_model = 0
            for j in range(n):
                linear_model += X[i][j] * self.weights[j]
            linear_model += self.bias
            predictions[i] = 1 if self._sigmoid(linear_model) >= 0.5 else 0
        return predictions

def solve_naive(X, y, lr=0.01, iters=1000):
    model = LogisticRegressionNaive(learning_rate=lr, iterations=iters)
    model.fit(X, y)
    return model.predict(X)

# --- APPROACH 2: Optimal (Vectorized Gradient Descent) ---
# Time Complexity: O(iterations * m * n)
# Space Complexity: O(n)
# This approach is optimal because it leverages NumPy's vectorized operations (BLAS), 
# which utilize SIMD instructions and highly optimized C/Fortran backends to perform 
# matrix-vector multiplications, significantly reducing the constant factor of 
# execution time compared to Python loops.
import numpy as np

class LogisticRegressionOptimal:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.lr = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = None

    def _sigmoid(self, z):
        # Use clip to prevent overflow in exp
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        m, n = X.shape
        # Initialize parameters
        self.weights = np.zeros(n)
        self.bias = 0.0

        for _ in range(self.iterations):
            # Vectorized linear combination and activation
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self._sigmoid(linear_model)

            # Vectorized gradient computation
            # Gradient of J w.r.t weights: (1/m) * X^T * (y_pred - y)
            dw = (1 / m) * np.dot(X.T, (y_predicted - y))
            # Gradient of J w.r.t bias: (1/m) * sum(y_pred - y)
            db = (1 / m) * np.sum(y_predicted - y)

            # Parameter updates
            self.weights -= self.lr * dw
            self.bias -= self.lr * db

    def predict(self, X):
        linear_model = np.dot(X, self.weights) + self.bias
        y_predicted = self._sigmoid(linear_model)
        return np.where(y_predicted >= 0.5, 1, 0)

def solve_optimal(X, y, lr=0.01, iters=1000):
    model = LogisticRegressionOptimal(learning_rate=lr, iterations=iters)
    model.fit(X, y)
    return model.predict(X)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package classical_ml;

import java.util.Arrays;

public class LogisticRegression {
    private double learningRate;
    private int iterations;
    private double[] weights;
    private double bias;

    public LogisticRegression(double learningRate, int iterations) {
        this.learningRate = learningRate;
        this.iterations = iterations;
    }

    private double sigmoid(double z) {
        return 1.0 / (1.0 + Math.exp(-z));
    }

    public void fit(double[][] X, int[] y) {
        int m = X.length;
        int n = X[0].length;
        this.weights = new double[n];
        this.bias = 0.0;

        for (int iter = 0; iter < iterations; iter++) {
            double[] yPred = new double[m];
            for (int i = 0; i < m; i++) {
                double linearModel = 0.0;
                for (int j = 0; j < n; j++) {
                    linearModel += X[i][j] * weights[j];
                }
                linearModel += bias;
                yPred[i] = sigmoid(linearModel);
            }

            double[] dw = new double[n];
            double db = 0.0;
            for (int i = 0; i < m; i++) {
                double diff = yPred[i] - y[i];
                for (int j = 0; j < n; j++) {
                    dw[j] += diff * X[i][j];
                }
                db += diff;
            }

            for (int j = 0; j < n; j++) {
                weights[j] -= learningRate * (dw[j] / m);
            }
            bias -= learningRate * (db / m);
        }
    }

    public int[] predict(double[][] X) {
        int m = X.length;
        int n = X[0].length;
        int[] predictions = new int[m];

        for (int i = 0; i < m; i++) {
            double linearModel = 0.0;
            for (int j = 0; j < n; j++) {
                linearModel += X[i][j] * weights[j];
            }
            linearModel += bias;
            predictions[i] = sigmoid(linearModel) >= 0.5 ? 1 : 0;
        }
        return predictions;
    }

    public static void main(String[] args) {
        double[][] X = {{1.0, 2.0}, {2.0, 1.0}, {3.0, 4.0}, {4.0, 3.0}};
        int[] y = {0, 0, 1, 1};
        LogisticRegression lr = new LogisticRegression(0.1, 1000);
        lr.fit(X, y);
        int[] preds = lr.predict(X);
        System.out.println(Arrays.toString(preds));
    }
}
"""

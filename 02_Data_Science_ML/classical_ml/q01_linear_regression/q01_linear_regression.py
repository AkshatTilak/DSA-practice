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

def fit_linear_regression_optimal(X, y, lr=0.01, epochs=100):
    n_samples, n_features = X.shape
    w = np.zeros(n_features)
    b = 0.0
    for _ in range(epochs):
        predictions = np.dot(X, w) + b
        dw = (1/n_samples) * np.dot(X.T, (predictions - y))
        db = (1/n_samples) * np.sum(predictions - y)
        w -= lr * dw
        b -= lr * db
    return w, b

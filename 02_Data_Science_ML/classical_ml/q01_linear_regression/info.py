INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Implement linear regression fitting using gradient descent from scratch.',
    'groups': ['Classical ML', 'Optimization'],
    'starter_code': 'import numpy as np\n\ndef fit_linear_regression(X: np.ndarray, y: np.ndarray, lr=0.01, epochs=100) -> tuple[np.ndarray, float]:\n    # Return weights (np.ndarray) and bias (float)\n    pass',
    'solutions': 'def fit_linear_regression_optimal(X, y, lr=0.01, epochs=100):\n    n_samples, n_features = X.shape\n    w = np.zeros(n_features)\n    b = 0.0\n    for _ in range(epochs):\n        predictions = np.dot(X, w) + b\n        dw = (1/n_samples) * np.dot(X.T, (predictions - y))\n        db = (1/n_samples) * np.sum(predictions - y)\n        w -= lr * dw\n        b -= lr * db\n    return w, b',
    'test_code': 'def test_linear():\n    pass',
    'readme_content': '# Linear Regression\nGradient descent optimization.',
}

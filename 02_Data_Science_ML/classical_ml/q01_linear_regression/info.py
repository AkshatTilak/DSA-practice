INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Implement linear regression fitting using gradient descent from scratch.',
    'groups': ['Classical ML', 'Optimization'],
    'starter_code': """import numpy as np

def fit_linear_regression(X: np.ndarray, y: np.ndarray, lr=0.01, epochs=100) -> tuple[np.ndarray, float]:
    # Return weights (np.ndarray) and bias (float)
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_linear():
    pass""",
    'readme_content': """# Linear Regression via Gradient Descent

## 🗂️ Concept Card: Linear Regression
**Linear Regression** is one of the most fundamental algorithms in Supervised Learning. Its primary objective is to model the relationship between a scalar response (dependent variable) and one or more explanatory variables (independent variables) by fitting a **linear equation** to observed data.

In a professional software engineering context, implementing this via **Gradient Descent** (rather than the Closed-Form Normal Equation) is crucial because Gradient Descent scales significantly better to large datasets where computing the inverse of a matrix becomes computationally prohibitive.

### Core Objective
Find the optimal parameters—**weights ($\mathbf{w}$)** and **bias ($b$)**—that minimize the difference between the predicted values and the actual target values, effectively finding the "line of best fit."

---

## 📐 Theoretical Foundations & Math

### 1. The Linear Hypothesis
For a dataset with $n$ features, the prediction $\hat{y}$ is a linear combination of the input features $X$:
$$\hat{y} = X\mathbf{w} + b$$
Where:
- $X$: Input feature matrix of shape $(n_{samples}, n_{features})$.
- $\mathbf{w}$: Weight vector of shape $(n_{features},)$.
- $b$: Bias (intercept) scalar.

### 2. The Cost Function: Mean Squared Error (MSE)
To measure how "wrong" our model is, we use the **Mean Squared Error**. We square the residuals to ensure positive values and to penalize larger errors more heavily:
$$J(\mathbf{w}, b) = \frac{1}{2n} \sum_{i=1}^{n} (\hat{y}_i - y_i)^2$$
*(Note: The $\frac{1}{2}$ is a mathematical convenience that cancels out during differentiation.)*

### 3. Optimization: Gradient Descent
Gradient Descent iteratively updates parameters in the opposite direction of the gradient of the cost function to reach the global minimum.

**The Gradients:**
To update $\mathbf{w}$ and $b$, we calculate the partial derivatives of $J$ with respect to each:

1. **Partial derivative w.r.t weights ($\mathbf{w}$):**
   $$\frac{\partial J}{\partial \mathbf{w}} = \frac{1}{n} X^T (X\mathbf{w} + b - y)$$
2. **Partial derivative w.r.t bias ($b$):**
   $$\frac{\partial J}{\partial b} = \frac{1}{n} \sum (\hat{y} - y)$$

**The Update Rule:**
$$\mathbf{w} = \mathbf{w} - \alpha \cdot \frac{\partial J}{\partial \mathbf{w}}$$
$$b = b - \alpha \cdot \frac{\partial J}{\partial b}$$
Where $\alpha$ is the **learning rate**, controlling the size of the step taken toward the minimum.

---

## 🛠️ Step-by-Step Logic

The implementation in `fit_linear_regression_optimal` follows a vectorized approach to maximize NumPy's performance:

1. **Initialization**: 
   - Initialize weights $\mathbf{w}$ as a zero vector of size `n_features`.
   - Initialize bias $b$ as `0.0`.
2. **Prediction (Forward Pass)**: 
   - Compute $\hat{y}$ using the dot product: `predictions = np.dot(X, w) + b`. This calculates the prediction for all samples simultaneously.
3. **Error Calculation**: 
   - Compute the difference $(predictions - y)$. This vector represents the residual error for every sample.
4. **Gradient Computation**:
   - **Weight Gradient (`dw`)**: Multiply the transpose of $X$ by the error vector and scale by $1/n$. This effectively sums the errors weighted by the feature values.
   - **Bias Gradient (`db`)**: Take the average of the error vector.
5. **Parameter Update**: 
   - Subtract the product of the learning rate and the gradient from the current $\mathbf{w}$ and $b$.
6. **Iteration**: 
   - Repeat steps 2–5 for the specified number of `epochs`.

```python
# Key Logic Mapping from Solution
dw = (1/n_samples) * np.dot(X.T, (predictions - y)) # Matrix form of weight gradient
db = (1/n_samples) * np.sum(predictions - y)       # Average of errors for bias
```

---

## ⚙️ Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Training** | $O(\text{epochs} \cdot n \cdot f)$ | $O(f)$ | $n$ = samples, $f$ = features. |
| **Inference** | $O(f)$ | $O(1)$ | A single dot product and addition. |

### Critical Hyperparameters
- **Learning Rate ($\alpha$)**: 
  - If too high: The model may overshoot the minimum and diverge.
  - If too low: Convergence will be extremely slow.
- **Epochs**: 
  - The number of passes over the training set. Too few leads to underfitting; too many may lead to unnecessary computation (though linear regression is generally resistant to overfitting compared to deep networks).

---

## 🌍 Real-World Applications

Linear Regression is used across industries wherever a continuous numerical value needs to be predicted based on historical trends:

1. **Finance & Economics**: 
   - Predicting stock price trends based on market indices.
   - Estimating the impact of interest rate changes on housing demand.
2. **Healthcare**: 
   - Predicting a patient's blood pressure based on age, BMI, and weight.
   - Analyzing the relationship between drug dosage and efficacy.
3. **Marketing & Sales**: 
   - **Customer Lifetime Value (CLV)**: Predicting how much a customer will spend over their lifetime based on acquisition channel and initial spend.
   - Predicting sales revenue based on advertising spend across different platforms.
4. **Engineering**: 
   - Estimating the remaining useful life (RUL) of a mechanical component based on sensor data (vibration, temperature).""",
}

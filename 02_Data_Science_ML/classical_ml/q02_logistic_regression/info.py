INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Logistic regression classification.',
    'groups': ['Classical ML', 'Optimization'],
    'readme_content': """# Logistic Regression

## 📌 Overview & Concept Card

**Logistic Regression** is a fundamental supervised learning algorithm used primarily for **binary classification** problems. Despite its name, it is not used for predicting continuous values (regression) but rather for predicting the probability that a given input belongs to a specific discrete category (usually labeled as 0 or 1).

The core objective of Logistic Regression is to find a relationship between a set of independent variables (features) and a dependent binary variable. It achieves this by passing a linear combination of inputs through a non-linear activation function called the **Sigmoid (Logistic) Function**, which maps any real-valued number into a value between 0 and 1.

### Key Characteristics
- **Type**: Discriminative Classifier.
- **Output**: Probability estimate $P(y=1|x)$.
- **Decision Boundary**: A linear hyperplane that separates the two classes.
- **Requirement**: Assumes that the independent variables are linearly related to the **log-odds** of the dependent variable.

---

## 🧬 Theoretical Foundations & Math

### 1. The Hypothesis Function
In Linear Regression, the output is $z = w^T x + b$. However, $z$ can range from $-\infty$ to $+\infty$. To convert this into a probability, we use the **Sigmoid Function** $\sigma(z)$:

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

The Logistic Regression hypothesis is defined as:
$$h_\theta(x) = \sigma(\theta^T x) = \frac{1}{1 + e^{-(\theta_0 + \theta_1 x_1 + ... + \theta_n x_n)}}$$

Where:
- $\theta$ represents the weights (parameters) of the model.
- $x$ is the input feature vector.
- $h_\theta(x)$ is the predicted probability that $y=1$.

### 2. The Decision Boundary
To make a final classification, we apply a threshold (typically $0.5$):
- If $h_\theta(x) \geq 0.5 \implies \text{Class 1}$
- If $h_\theta(x) < 0.5 \implies \text{Class 0}$

### 3. The Cost Function: Log Loss
We cannot use Mean Squared Error (MSE) for Logistic Regression because the resulting cost function would be **non-convex**, meaning it would have many local minima, making gradient descent unreliable. Instead, we use **Binary Cross-Entropy (Log Loss)**:

$$J(\theta) = -\frac{1}{m} \sum_{i=1}^{m} \left[ y^{(i)} \log(h_\theta(x^{(i)})) + (1 - y^{(i)}) \log(1 - h_\theta(x^{(i)})) \right]$$

**Intuition**:
- If $y=1$ and $h_\theta(x) \to 0$, the cost $\to \infty$.
- If $y=0$ and $h_\theta(x) \to 1$, the cost $\to \infty$.
- If the prediction matches the label, the cost $\to 0$.

### 4. Optimization: Gradient Descent
To minimize $J(\theta)$, we update the weights iteratively in the opposite direction of the gradient:
$$\theta_j := \theta_j - \alpha \frac{\partial J(\theta)}{\partial \theta_j}$$

The gradient for Logistic Regression simplifies to a form very similar to Linear Regression:
$$\frac{\partial J(\theta)}{\partial \theta_j} = \frac{1}{m} \sum_{i=1}^{m} (h_\theta(x^{(i)}) - y^{(i)}) x_j^{(i)}$$

---

## 🛠️ Step-by-Step Logic

Implementing Logistic Regression from scratch follows these algorithmic steps:

1.  **Initialization**: Initialize the weight vector $\theta$ (usually with zeros or small random numbers) and the learning rate $\alpha$.
2.  **Linear Combination (Forward Pass)**:
    - Compute the weighted sum of inputs: $z = \sum (w_i x_i) + b$.
3.  **Activation**:
    - Pass $z$ through the Sigmoid function $\sigma(z)$ to get the probability $p$.
4.  **Compute Error**:
    - Calculate the difference between the predicted probability $p$ and the actual label $y$.
5.  **Gradient Calculation (Backward Pass)**:
    - Compute the partial derivative of the cost function with respect to each weight $\theta_j$.
6.  **Weight Update**:
    - Adjust the weights: $\theta_{new} = \theta_{old} - \alpha \cdot \text{gradient}$.
7.  **Iteration**:
    - Repeat steps 2–6 for a fixed number of epochs or until the cost function converges (stops decreasing significantly).

---

## 📈 Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Training** | $O(\text{epochs} \cdot m \cdot n)$ | $O(n)$ | $m = \text{samples}, n = \text{features}$ |
| **Inference** | $O(n)$ | $O(n)$ | A single dot product and one sigmoid call |

### Key Hyperparameters
- **Learning Rate ($\alpha$)**: Controls the step size during gradient descent. Too large can cause divergence; too small makes training slow.
- **Regularization ($\lambda$)**: L1 (Lasso) or L2 (Ridge) is often added to the cost function to prevent overfitting by penalizing large weights.
- **Iterations/Epochs**: The number of times the algorithm sees the entire dataset.

### Evaluation Metrics
Unlike regression, we don't use $R^2$. We use:
- **Accuracy**: Proportion of correct predictions.
- **Precision/Recall**: Critical for imbalanced datasets.
- **F1-Score**: Harmonic mean of precision and recall.
- **ROC-AUC**: Area under the Receiver Operating Characteristic curve; measures the model's ability to distinguish between classes.

---

## 🌍 Real-World Applications

Logistic Regression is widely used in industry due to its efficiency and interpretability:

1.  **Medical Diagnosis**: Predicting whether a patient has a disease (e.g., Diabetes: Yes/No) based on symptoms and biometric data.
2.  **Financial Services**: **Credit Scoring** — predicting the probability that a loan applicant will default on payments.
3.  **Marketing & Sales**: **Churn Prediction** — determining if a customer is likely to cancel a subscription based on usage patterns.
4.  **Email Filtering**: Basic **Spam Detection** — classifying an email as "Spam" or "Ham" based on keyword frequency.
5.  **Cybersecurity**: Detecting whether a network login attempt is fraudulent or legitimate.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

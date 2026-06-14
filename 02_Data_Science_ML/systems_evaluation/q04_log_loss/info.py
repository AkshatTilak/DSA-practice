INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Binary cross-entropy loss.',
    'groups': ['Evaluation & Metrics', 'Deep Learning'],
    'readme_content': """# Log Loss (Binary Cross-Entropy)

## 📌 Overview & Concept Card
**Log Loss**, short for **Logarithmic Loss**, is the primary evaluation metric used for binary classification models that output probabilities rather than hard labels. While accuracy simply measures whether a prediction was "right or wrong," Log Loss measures the **uncertainty** of the prediction.

The core objective of Log Loss is to penalize false classifications based on the **confidence** of the prediction. A model that is confidently wrong is penalized much more heavily than a model that is hesitantly wrong. This makes it the standard objective function (cost function) for training Logistic Regression and Neural Networks for binary classification tasks.

| Feature | Description |
| :--- | :--- |
| **Input** | Actual labels $y \in \{0, 1\}$ and predicted probabilities $p \in [0, 1]$ |
| **Goal** | Minimize the distance between the predicted probability and the actual label |
| **Sensitivity** | Highly sensitive to confident but incorrect predictions |
| **Common Names** | Binary Cross-Entropy (BCE), Logarithmic Loss |

---

## 📐 Theoretical Foundations & Math

### The Mathematical Formula
For a dataset with $N$ samples, the Log Loss is defined as:

$$ \text{Log Loss} = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \ln(p_i) + (1 - y_i) \ln(1 - p_i) \right] $$

**Where:**
- $N$: Total number of observations.
- $y_i$: The ground truth label (either $0$ or $1$).
- $p_i$: The predicted probability that the observation belongs to class $1$.
- $\ln$: The natural logarithm.

### Intuition Breakdown
The formula is a "switch" mechanism based on the value of $y_i$:

1. **When the actual class is $y=1$**: 
   The term $(1 - y_i) \ln(1 - p_i)$ becomes $0$. The loss depends only on $-\ln(p_i)$.
   - As $p_i \to 1$ (Correct), $\ln(1) = 0$, so loss $\to 0$.
   - As $p_i \to 0$ (Incorrect), $\ln(0) \to -\infty$, so loss $\to \infty$.

2. **When the actual class is $y=0$**: 
   The term $y_i \ln(p_i)$ becomes $0$. The loss depends only on $-\ln(1 - p_i)$.
   - As $p_i \to 0$ (Correct), $\ln(1) = 0$, so loss $\to 0$.
   - As $p_i \to 1$ (Incorrect), $\ln(0) \to -\infty$, so loss $\to \infty$.

### Why Logarithms?
Logarithms are used because they transform the product of probabilities (likelihood) into a sum, which is computationally easier to differentiate during gradient descent. Furthermore, the steep slope of the negative log curve ensures that "confident mistakes" are heavily penalized.

---

## ⚙️ Step-by-Step Logic

To implement Log Loss programmatically, we follow these steps:

1. **Input Validation**: Ensure that predicted probabilities $p$ are within the range $(0, 1)$.
2. **Probability Clipping**: This is a critical engineering step. If $p_i = 0$ or $p_i = 1$, $\ln(0)$ results in negative infinity, which crashes the calculation. We "clip" the values to a tiny epsilon (e.g., $1e-15$) such that $0 \le p \le 1$ becomes $\epsilon \le p \le 1-\epsilon$.
3. **Element-wise Computation**:
   - For every sample, calculate $y \cdot \ln(p)$.
   - For every sample, calculate $(1-y) \cdot \ln(1-p)$.
4. **Summation**: Sum these two components across all samples.
5. **Averaging**: Divide the total sum by $N$ and multiply by $-1$ to get the final positive loss value.

### Implementation

```python
import numpy as np

def solve_optimal(y_true, y_pred):
    \"\"\"
    Computes the Binary Cross-Entropy (Log Loss).
    
    Args:
        y_true (list or np.array): Actual binary labels (0 or 1).
        y_pred (list or np.array): Predicted probabilities [0, 1].
        
    Returns:
        float: The calculated log loss.
    \"\"\"
    # Convert inputs to numpy arrays for vectorized operations
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # 1. Clipping: Prevent log(0) by bounding predictions
    # This replaces 0 with epsilon and 1 with 1-epsilon
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    
    # 2. Apply the Log Loss formula
    # Log Loss = -1/N * sum(y*log(p) + (1-y)*log(1-p))
    loss = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
    return loss

# Example Usage:
# y_true = [1, 0, 1, 1]
# y_pred = [0.9, 0.1, 0.8, 0.3] # The last one is a "confident" mistake
# print(solve_optimal(y_true, y_pred))
```

---

## 📈 Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Inference (Calculation)** | $O(N)$ | $O(1)$ or $O(N)$ | Linear pass over the predictions. $O(N)$ if storing intermediate arrays. |
| **Training (Optimization)** | $O(N \cdot Epochs)$ | $O(W)$ | Where $W$ is the number of model weights. |

### Key Hyperparameters/Details
- **Epsilon ($\epsilon$)**: The choice of clipping value (usually $1e-7$ to $1e-15$) prevents numerical instability.
- **Relationship to Accuracy**: A model can have high accuracy but high Log Loss if it is "barely" correct (e.g., predicting $0.51$ for a label of $1$). Conversely, it can have low accuracy but low Log Loss if its mistakes are cautious.

---

## 🌍 Real-World Applications

1. **Logistic Regression**: Log Loss is the native cost function for Logistic Regression. The optimization process (Gradient Descent) aims to minimize this specific value to find the optimal weights.
2. **Neural Networks (Binary Classification)**: In deep learning, the output layer usually consists of a **Sigmoid** activation function paired with a **Binary Cross-Entropy (BCE)** loss function.
3. **Click-Through Rate (CTR) Prediction**: In ad-tech, predicting whether a user will click an ad (1) or not (0) requires probabilities. Log Loss is used to ensure the predicted probability reflects the actual click frequency.
4. **Kaggle Competitions**: Many binary classification competitions use Log Loss as the primary leaderboard metric because it rewards well-calibrated probabilities over simple hard-label accuracy.
5. **Medical Diagnosis**: When predicting the probability of a disease, it is more useful to know the confidence of the diagnosis than a simple Yes/No, making Log Loss an ideal evaluation tool.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach uses a simple for-loop to iterate through the labels and predictions.
# It uses basic math.log and manually clips the values to avoid numerical instability 
# (log(0) is undefined).
import math

def solve_naive(y_true, y_pred):
    \"\"\"
    Computes binary cross-entropy loss using a naive loop.
    \"\"\"
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
    \"\"\"
    Computes binary cross-entropy loss using NumPy vectorization.
    \"\"\"
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
\"\"\"
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
\"\"\"""",
}

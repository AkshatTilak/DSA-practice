INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Coefficient of determination.',
    'groups': ['Evaluation & Metrics'],
    'readme_content': """# R Squared (Coefficient of Determination)

## 📌 Overview & Concept Card
**R Squared ($R^2$)**, also known as the **Coefficient of Determination**, is a fundamental statistical measure used in regression analysis to evaluate the performance of a predictive model. It quantifies the proportion of the variance in the dependent variable (target) that is predictable from the independent variable(s) (features).

In simpler terms, $R^2$ tells us how well the regression line "fits" the actual data points. While metrics like Mean Absolute Error (MAE) or Root Mean Squared Error (RMSE) provide errors in the original units of the target variable, $R^2$ provides a **scale-independent** measure of fit, typically ranging from $0$ to $1$ (though it can be negative).

### Core Objective
The objective of $R^2$ is to compare the fit of your chosen model against a **baseline model**. The baseline model is the simplest possible predictor: a horizontal line representing the **mean of the actual observed values**.

---

## 📐 Theoretical Foundations & Math

To understand $R^2$, we must define two critical components: the **Total Sum of Squares ($SS_{tot}$)** and the **Residual Sum of Squares ($SS_{res}$)**.

### 1. Total Sum of Squares ($SS_{tot}$)
This measures the total variance in the observed data. It represents the error we would have if we simply predicted the mean ($\bar{y}$) for every single observation.
$$SS_{tot} = \sum_{i=1}^{n} (y_i - \bar{y})^2$$
*   $y_i$: The actual observed value.
*   $\bar{y}$: The mean of all observed values.

### 2. Residual Sum of Squares ($SS_{res}$)
Also known as the Sum of Squared Errors (SSE), this measures the variance that the model **fails** to capture. It is the sum of the squared differences between the actual values and the model's predictions.
$$SS_{res} = \sum_{i=1}^{n} (y_i - \hat{y}_i)^2$$
*   $\hat{y}_i$: The value predicted by the regression model.

### 3. The $R^2$ Equation
The coefficient of determination is calculated as:
$$R^2 = 1 - \frac{SS_{res}}{SS_{tot}}$$

### Interpretation of Results
| $R^2$ Value | Meaning |
| :--- | :--- |
| **$R^2 = 1.0$** | Perfect fit; the model explains all the variability of the response data around its mean. |
| **$0 < R^2 < 1$** | The model explains a portion of the variability. Higher is generally better. |
| **$R^2 = 0$** | The model performs no better than a horizontal line drawn at the mean of the data. |
| **$R^2 < 0$** | The model is **worse** than the mean baseline. This happens when the model's predictions are further from the data than the mean is. |

---

## ⚙️ Step-by-Step Logic

To implement $R^2$ programmatically, follow these algorithmic steps:

1.  **Calculate the Mean**: Find the average ($\bar{y}$) of the ground truth labels (`y_true`).
2.  **Compute $SS_{tot}$**: Iterate through `y_true`, subtract the mean from each value, square the result, and sum them up.
3.  **Compute $SS_{res}$**: Iterate through `y_true` and `y_pred` simultaneously. Subtract the prediction from the actual value, square the result, and sum them up.
4.  **Apply Formula**: Divide $SS_{res}$ by $SS_{tot}$ and subtract the result from $1$.
5.  **Handle Edge Cases**: If $SS_{tot} = 0$ (meaning all actual values are the same), $R^2$ is technically undefined, though implementations often return $0.0$ or $1.0$ depending on whether the predictions are also constant.

### Implementation

```python
import numpy as np

def solve_optimal(y_true, y_pred):
    \"\"\"
    Calculates the R Squared (Coefficient of Determination) score.
    
    Args:
        y_true (list or np.array): Actual observed values.
        y_pred (list or np.array): Predicted values from the model.
        
    Returns:
        float: The R^2 score.
    \"\"\"
    # Convert to numpy arrays for vectorized operations
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # 1. Calculate the mean of the actual values
    y_mean = np.mean(y_true)
    
    # 2. Calculate Total Sum of Squares (SS_tot)
    # Variance of the data relative to the mean
    ss_tot = np.sum((y_true - y_mean)**2)
    
    # 3. Calculate Residual Sum of Squares (SS_res)
    # Variance of the data relative to the model predictions
    ss_res = np.sum((y_true - y_pred)**2)
    
    # Edge case: if ss_tot is 0, the data has no variance
    if ss_tot == 0:
        return 0.0 if ss_res != 0 else 1.0
    
    # 4. Final R^2 calculation
    r_squared = 1 - (ss_res / ss_tot)
    
    return r_squared

# --- Example Usage ---
actual = [3, -0.5, 2, 7]
predicted = [2.5, 0.0, 2, 8]
print(f"R^2 Score: {solve_optimal(actual, predicted):.4f}") 
# Expected output: ~0.9486
```

---

## 📊 Complexity & Training Details

### Computational Complexity
| Phase | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Mean Calculation** | $O(n)$ | $O(1)$ | Single pass over the dataset. |
| **$SS_{tot}$ Calculation** | $O(n)$ | $O(1)$ | Single pass over the dataset. |
| **$SS_{res}$ Calculation** | $O(n)$ | $O(1)$ | Single pass over the dataset. |
| **Overall** | **$O(n)$** | **$O(1)$** | Linear time relative to number of samples. |

### Critical Considerations
- **Overfitting**: $R^2$ always increases (or stays the same) when more features are added to a model, even if those features are irrelevant. This can lead to an over-optimistic view of the model.
- **The Solution (Adjusted $R^2$)**: To combat overfitting, data scientists use **Adjusted $R^2$**, which penalizes the addition of unnecessary predictors:
  $$\text{Adjusted } R^2 = 1 - \left[ \frac{(1 - R^2)(n - 1)}{n - k - 1} \right]$$
  *(where $n$ is sample size and $k$ is the number of predictors).*

---

## 🚀 Real-World Applications

1.  **Real Estate Valuation**: When predicting house prices, $R^2$ tells the agent what percentage of the price variation is explained by features like square footage, location, and number of bedrooms.
2.  **Financial Forecasting**: In stock price trend analysis, $R^2$ helps analysts determine if a specific technical indicator (like a Moving Average) actually explains the movement of the asset price.
3.  **Scientific Experiments**: In chemistry or physics, $R^2$ is used to verify how well a theoretical linear equation (like Beer-Lambert Law) matches the experimentally observed data.
4.  **Marketing Attribution**: Determining how much of the variance in total sales ($y$) can be explained by spend on different advertising channels ($x_1, x_2, ... x_n$).""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

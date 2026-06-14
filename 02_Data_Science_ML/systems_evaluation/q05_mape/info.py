INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Mean Absolute Percentage Error.',
    'groups': ['Evaluation & Metrics'],
    'readme_content': """# Mean Absolute Percentage Error (MAPE)

## 🌟 Overview & Concept Card
**Mean Absolute Percentage Error (MAPE)** is a fundamental evaluation metric used primarily in regression analysis and time-series forecasting. Unlike metrics such as Mean Absolute Error (MAE) or Root Mean Squared Error (RMSE), which provide errors in the same units as the target variable, MAPE expresses the error as a **percentage**.

The core objective of MAPE is to provide a **scale-independent** measure of accuracy. This allows data scientists to compare the forecasting performance across different datasets or different scales of the same variable (e.g., comparing the accuracy of sales forecasts for a small boutique versus a global retail chain).

### Key Characteristics
- **Relative Metric**: It measures the error relative to the actual value.
- **Intuitive Interpretation**: A MAPE of 10% means that, on average, the predictions are off by 10% of the actual values.
- **Non-Negative**: Because it uses absolute values, the result is always $\ge 0$.

---

## 📐 Theoretical Foundations & Math

MAPE is calculated by taking the average of the absolute percentage differences between the predicted values and the actual values.

### The Mathematical Formula
$$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$

**Where:**
- $n$: The total number of observations (sample size).
- $y_i$: The **Actual** value for the $i$-th observation.
- $\hat{y}_i$: The **Forecasted/Predicted** value for the $i$-th observation.
- $| \dots |$: The absolute value operator, which ensures that positive and negative errors do not cancel each other out.

### Critical Mathematical Nuances
1. **The Zero Division Problem**: The most significant limitation of MAPE is that it is **undefined** when any actual value $y_i = 0$, as it leads to division by zero.
2. **Asymmetry (Bias)**: MAPE penalizes over-forecasts more heavily than under-forecasts. If the actual value is small, a large over-forecast can lead to a percentage error significantly greater than 100%, whereas an under-forecast is capped at 100% (if the prediction is 0).
3. **Scale Independence**: Because the error is divided by $y_i$, the unit of measure is cancelled out, making it a dimensionless percentage.

---

## 🛠️ Step-by-Step Logic

To implement MAPE programmatically, we follow a sequence of element-wise operations. Here is the logical flow:

1. **Input Validation**: Ensure that the input arrays (Actuals and Predictions) are of the same length.
2. **Difference Calculation**: Compute the absolute difference between the actual and predicted values: $|y_i - \hat{y}_i|$.
3. **Normalization (Percentage)**: Divide that absolute difference by the actual value: $\frac{|y_i - \hat{y}_i|}{y_i}$.
4. **Aggregation**: Sum all these individual percentage errors.
5. **Averaging**: Divide the total sum by the number of observations $n$.
6. **Scaling**: Multiply by 100 to convert the decimal to a percentage.

### Implementation

```python
import numpy as np

def solve_optimal(actual, predicted):
    \"\"\"
    Calculates the Mean Absolute Percentage Error (MAPE).
    
    Args:
        actual (list or np.array): The ground truth values.
        predicted (list or np.array): The predicted values from the model.
        
    Returns:
        float: The MAPE value expressed as a percentage.
    \"\"\"
    # Convert inputs to numpy arrays for vectorized operations
    y_true = np.array(actual)
    y_pred = np.array(predicted)
    
    # Handle division by zero: 
    # In a real-world production scenario, we might replace zeros with 
    # a very small epsilon or filter out the zero entries.
    if np.any(y_true == 0):
        raise ValueError("MAPE is undefined when actual values contain zero.")

    # Step-by-step vectorized calculation
    # 1. Calculate absolute percentage error for each element
    ape = np.abs((y_true - y_pred) / y_true)
    
    # 2. Calculate the mean of those errors and multiply by 100
    mape = np.mean(ape) * 100
    
    return mape

# Example Usage
actual_values = [100, 150, 200, 250]
predicted_values = [110, 140, 190, 260]

result = solve_optimal(actual_values, predicted_values)
print(f"MAPE: {result:.2f}%") 
# Calculation: (|10/100| + |10/150| + |10/200| + |10/250|) / 4 * 100
# (0.1 + 0.0667 + 0.05 + 0.04) / 4 * 100 = 6.4175%
```

---

## 📉 Complexity & Performance Analysis

Since MAPE involves a single pass over the data, its computational profile is very efficient.

| Complexity | Notation | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | $O(n)$ | We perform a constant number of operations for each of the $n$ elements in the input arrays. |
| **Space Complexity** | $O(1)$ or $O(n)$ | $O(1)$ if calculated via a loop; $O(n)$ if using NumPy arrays to store intermediate results (vectorization). |

### Comparison with other Metrics

| Metric | Scale Dependent? | Sensitivity to Outliers | Handles $y=0$? | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | Yes | Linear | Yes | General regression, robust to outliers. |
| **RMSE** | Yes | Quadratic (High) | Yes | When large errors are particularly undesirable. |
| **MAPE** | **No** | High (if $y$ is small) | **No** | Business reporting, comparing across scales. |

---

## 🌍 Real-World Applications

MAPE is widely used in industries where stakeholders prefer percentages over raw units for intuitive understanding:

1. **Demand Forecasting (Retail)**: A supply chain manager needs to know if the forecast for "T-shirts" is accurate. Knowing the error is "500 units" is useless without knowing if they sell 1,000 or 1,000,000. A MAPE of 5% provides an immediate sense of reliability.
2. **Financial Budgeting**: Comparing the budget variance across different departments. The Marketing budget might be \$1M and the HR budget \$100k; MAPE allows the CFO to see which department's budget is more "off" relative to its size.
3. **Energy Load Prediction**: Utility companies predict hourly electricity demand. Because demand fluctuates wildly between seasons, MAPE helps evaluate the model's consistency across high-load (winter) and low-load (spring) periods.
4. **Econometrics**: Predicting GDP growth or inflation rates across different countries with wildly different economic sizes.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses a simple for-loop to iterate through the lists and calculate the 
# absolute percentage error for each pair of actual and predicted values.
def solve_naive(y_true: list, y_pred: list) -> float:
    if not y_true or not y_pred:
        return 0.0
    
    if len(y_true) != len(y_pred):
        raise ValueError("The length of y_true and y_pred must be equal.")
    
    total_ape = 0.0
    n = len(y_true)
    
    for i in range(n):
        actual = y_true[i]
        predicted = y_pred[i]
        
        # Handle division by zero: if actual is 0, we use a very small epsilon
        # to avoid ZeroDivisionError, as is common in basic implementations.
        denominator = actual if actual != 0 else 1e-10
        total_ape += abs((actual - predicted) / denominator)
    
    mape = (total_ape / n) * 100
    return float(mape)

# --- APPROACH 2: Optimal (NumPy Vectorization) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach is optimal for Data Science/ML tasks because it leverages NumPy's 
# SIMD (Single Instruction, Multiple Data) capabilities. Vectorized operations 
# are implemented in C and are significantly faster than Python loops for large datasets.
import numpy as np

def solve_optimal(y_true: list, y_pred: list) -> float:
    if not y_true or not y_pred:
        return 0.0
    
    # Convert inputs to numpy arrays for vectorized operations
    y_true_arr = np.array(y_true, dtype=np.float64)
    y_pred_arr = np.array(y_pred, dtype=np.float64)
    
    if y_true_arr.shape != y_pred_arr.shape:
        raise ValueError("The length of y_true and y_pred must be equal.")
    
    # Use a mask or np.where to handle potential zeros in y_true to avoid division by zero
    # This prevents the result from becoming 'inf' or 'nan'
    epsilon = 1e-10
    safe_y_true = np.where(y_true_arr == 0, epsilon, y_true_arr)
    
    # Vectorized MAPE formula: (1/n) * sum(|(y_true - y_pred) / y_true|) * 100
    ape = np.abs((y_true_arr - y_pred_arr) / safe_y_true)
    mape = np.mean(ape) * 100
    
    return float(mape)

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package systems_evaluation;

import java.util.Objects;

public class Mape {
    /**
     * Calculates the Mean Absolute Percentage Error (MAPE).
     * 
     * @param yTrue Array of actual values.
     * @param yPred Array of predicted values.
     * @return The MAPE value as a percentage.
     * @throws IllegalArgumentException if arrays are null or have different lengths.
     */
    public static double solveOptimal(double[] yTrue, double[] yPred) {
        if (yTrue == null || yPred == null) {
            throw new IllegalArgumentException("Input arrays cannot be null.");
        }
        if (yTrue.length != yPred.length) {
            throw new IllegalArgumentException("The length of yTrue and yPred must be equal.");
        }
        if (yTrue.length == 0) {
            return 0.0;
        }

        double totalApe = 0.0;
        int n = yTrue.length;
        double epsilon = 1e-10;

        for (int i = 0; i < n; i++) {
            double actual = yTrue[i];
            double predicted = yPred[i];
            
            // Handle division by zero using epsilon for stability
            double denominator = (actual == 0) ? epsilon : actual;
            totalApe += Math.abs((actual - predicted) / denominator);
        }

        return (totalApe / n) * 100.0;
    }

    public static void main(String[] args) {
        double[] actuals = {100.0, 150.0, 200.0, 0.0};
        double[] forecasts = {110.0, 140.0, 210.0, 5.0};
        System.out.println("MAPE: " + solveOptimal(actuals, forecasts));
    }
}
\"\"\"""",
}

INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Hyperplane margins.',
    'groups': ['Classical ML', 'Optimization'],
    'readme_content': """# Support Vector Machines: Hyperplane Margins

## 📌 Overview & Concept Card

**Support Vector Machines (SVM)** are powerful supervised learning models used for both classification and regression, though they are most renowned for binary classification. The core objective of an SVM is to find the **Optimal Hyperplane** that separates data points of two different classes with the maximum possible distance.

### What is the Hyperplane Margin?
In a $d$-dimensional space, a **hyperplane** is a flat affine subspace of dimension $d-1$. For a 2D space, the hyperplane is simply a line. 

The **margin** is the perpendicular distance between the separating hyperplane and the closest data points from either class. These closest points are called **Support Vectors**. The fundamental intuition behind SVM is that a larger margin provides a "safety buffer," reducing the risk of misclassifying future unseen data (improving generalization).

| Term | Definition |
| :--- | :--- |
| **Hyperplane** | The decision boundary that separates classes. |
| **Support Vectors** | The data points nearest to the hyperplane; they "support" the boundary. |
| **Hard Margin** | A strict boundary that allows no misclassifications (only works for linearly separable data). |
| **Soft Margin** | A flexible boundary that allows some points to be misclassified or fall inside the margin to handle noise. |
| **Kernel Trick** | A method to map non-linear data into higher-dimensional space to make it linearly separable. |

---

## 📐 Theoretical Foundations & Math

### 1. The Decision Boundary
A linear hyperplane is defined by the equation:
$$w^T x + b = 0$$
Where:
- $w$ is the **weight vector** (normal to the hyperplane).
- $b$ is the **bias** (offset from the origin).
- $x$ is the input feature vector.

For a binary classification problem with labels $y \in \{-1, 1\}$, the classifier predicts:
- $\text{Class } 1 \text{ if } w^T x + b \ge 0$
- $\text{Class } -1 \text{ if } w^T x + b < 0$

### 2. Defining the Margin
To ensure a gap between classes, we define two "canonical" hyperplanes:
1. $w^T x + b = 1$
2. $w^T x + b = -1$

The distance between these two planes is the **Margin**, calculated as:
$$\text{Margin} = \frac{2}{\|w\|}$$

### 3. The Optimization Problem (Hard Margin)
To maximize the margin, we need to minimize $\|w\|$. To make the math easier (quadratic optimization), we minimize:
$$\min_{w, b} \frac{1}{2} \|w\|^2$$
**Subject to:** $y_i(w^T x_i + b) \ge 1$ for all $i=1, \dots, n$.

### 4. Soft Margin & Hinge Loss
Real-world data is rarely perfectly separable. We introduce **slack variables** $\xi_i \ge 0$ that allow some points to violate the margin. The new objective function becomes:
$$\min_{w, b, \xi} \frac{1}{2} \|w\|^2 + C \sum_{i=1}^n \xi_i$$
Where **$C$** is a hyperparameter:
- **Large $C$**: Penalizes misclassifications heavily (tends toward Hard Margin $\rightarrow$ risk of overfitting).
- **Small $C$**: Allows more misclassifications for a wider margin (tends toward generalization $\rightarrow$ risk of underfitting).

---

## 🛠️ Step-by-Step Logic

The process of implementing and training an SVM to find the optimal hyperplane margin follows these logical steps:

### Step 1: Feature Scaling
SVMs are distance-based. If one feature has a range of $[0, 1]$ and another $[0, 1000]$, the larger feature will dominate the weight vector $w$. **Standardization (Z-score scaling)** is mandatory.

### Step 2: Choosing the Kernel
If the data is not linearly separable in the current space, a **Kernel Function** is used to project data into a higher dimension:
- **Linear**: No transformation.
- **Polynomial**: $(x \cdot z + r)^d$.
- **Radial Basis Function (RBF)**: $\exp(-\gamma \|x - z\|^2)$. (The most common for non-linear data).

### Step 3: Solving the Dual Problem
Instead of solving for $w$ and $b$ directly (the Primal problem), SVMs usually solve the **Lagrangian Dual**. This transforms the problem into finding coefficients $\alpha_i$ (Lagrange multipliers):
$$\max_{\alpha} \sum \alpha_i - \frac{1}{2} \sum \sum \alpha_i \alpha_j y_i y_j (x_i \cdot x_j)$$
The key advantage here is that the data only appears as **dot products** $(x_i \cdot x_j)$, which allows the "Kernel Trick" to replace the dot product with a kernel function $K(x_i, x_j)$.

### Step 4: Identifying Support Vectors
Once $\alpha$ is optimized, most $\alpha_i$ will be $0$. The points where $\alpha_i > 0$ are the **Support Vectors**. The final decision boundary is determined solely by these points.

---

## 🚀 Complexity & Training Details

### Computational Complexity
| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Training** | $O(n^2 \cdot d)$ to $O(n^3 \cdot d)$ | $O(n^2)$ | $n$ is number of samples, $d$ is features. Training is expensive for large datasets. |
| **Inference** | $O(n_{SV} \cdot d)$ | $O(n_{SV} \cdot d)$ | $n_{SV}$ is the number of Support Vectors. Fast, as it only depends on SVs. |

### Hyperparameter Tuning
- **$C$**: Controls the trade-off between maximizing the margin and minimizing classification error.
- **$\gamma$ (Gamma)**: Specifically for RBF kernels. It defines how far the influence of a single training example reaches. 
    - High $\gamma$: Only nearby points are considered (complex boundary, high variance).
    - Low $\gamma$: Faraway points are considered (smoother boundary, high bias).

---

## 🌍 Real-World Applications

1. **Bioinformatics (Protein Classification)**: SVMs are highly effective in high-dimensional spaces, making them ideal for classifying proteins or genes where the number of features often exceeds the number of samples.
2. **Text Categorization (Spam Detection)**: Using a linear kernel, SVMs can efficiently handle sparse, high-dimensional word-count vectors to distinguish between "Spam" and "Ham."
3. **Image Recognition (Face Detection)**: By using RBF or Polynomial kernels, SVMs can find non-linear boundaries to separate face-like patterns from non-face backgrounds.
4. **Handwriting Recognition**: Used to classify handwritten digits by mapping the pixel intensity vectors into a higher-dimensional space where digits are linearly separable.

---

## 💻 Implementation Example (Conceptual)

While the starter template is empty, a standard implementation using `scikit-learn` would look like this:

```python
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def solve_optimal(X, y):
    # 1. Scale the data (Critical for SVM)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 2. Split the data
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)
    
    # 3. Initialize SVM with RBF kernel and a specific C value
    # C=1.0 is the default balance between margin and error
    model = svm.SVC(kernel='rbf', C=1.0, gamma='scale')
    
    # 4. Fit the model (Solving the Quadratic Programming problem)
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    accuracy = model.score(X_test, y_test)
    return accuracy, model.support_vectors_
```""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N * D)
# Space Complexity: O(1)
# This approach iterates through each data point and calculates the geometric margin individually 
# using basic Python loops and arithmetic, avoiding any vectorization or heavy libraries.
def calculate_margin_naive(X, y, w, b):
    if not X or len(X) == 0:
        return 0.0
    
    # Calculate the L2 norm of the weight vector w manually
    w_norm_sq = 0.0
    for val in w:
        w_norm_sq += val * val
    w_norm = w_norm_sq**0.5
    
    if w_norm == 0:
        return 0.0
        
    min_margin = float('inf')
    for i in range(len(X)):
        # Calculate dot product of X[i] and w
        dot_product = 0.0
        for j in range(len(w)):
            dot_product += X[i][j] * w[j]
        
        # Geometric margin formula: y_i * (w^T * x_i + b) / ||w||
        # y[i] is assumed to be in {-1, 1}
        current_margin = (y[i] * (dot_product + b)) / w_norm
        if current_margin < min_margin:
            min_margin = current_margin
            
    return float(min_margin)

# --- APPROACH 2: Optimal (NumPy Vectorization) ---
# Time Complexity: O(N * D)
# Space Complexity: O(N)
# This approach uses NumPy's highly optimized BLAS backends for matrix-vector multiplication.
# It computes all distance values in a single vectorized operation, significantly reducing 
# overhead and improving performance on large datasets.
import numpy as np

def calculate_margin_optimal(X, y, w, b):
    # Convert inputs to numpy arrays for vectorization
    X = np.asarray(X)
    y = np.asarray(y)
    w = np.asarray(w)
    
    if X.size == 0:
        return 0.0
        
    # Calculate the L2 norm of weight vector w
    w_norm = np.linalg.norm(w)
    if w_norm == 0:
        return 0.0
        
    # X @ w computes the dot product for all samples: (N, D) @ (D,) -> (N,)
    # (X @ w + b) is the functional margin for each point
    # y * (X @ w + b) scales by the label to get signed functional margins
    # Dividing by w_norm converts functional margins to geometric margins
    margins = (y * (X @ w + b)) / w_norm
    
    return float(np.min(margins))

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package classical_ml;

import java.util.Arrays;

public class SupportVectorMachines {

    /**
     * Calculates the geometric margin of a hyperplane relative to a dataset.
     * 
     * @param X The input feature matrix [N][D]
     * @param y The labels array [N], expected values are -1 or 1
     * @param w The weight vector [D]
     * @param b The bias scalar
     * @return The minimum geometric margin
     */
    public static double calculateMargin(double[][] X, int[] y, double[] w, double b) {
        if (X == null || X.length == 0) {
            return 0.0;
        }

        // Calculate L2 norm of weight vector w
        double wNormSq = 0.0;
        for (double val : w) {
            wNormSq += val * val;
        }
        double wNorm = Math.sqrt(wNormSq);

        if (wNorm == 0) {
            return 0.0;
        }

        double minMargin = Double.POSITIVE_INFINITY;
        int numSamples = X.length;
        int numFeatures = w.length;

        for (int i = 0; i < numSamples; i++) {
            double dotProduct = 0.0;
            for (int j = 0; j < numFeatures; j++) {
                dotProduct += X[i][j] * w[j];
            }
            
            // Geometric margin: y_i * (w^T * x_i + b) / ||w||
            double currentMargin = (y[i] * (dotProduct + b)) / wNorm;
            if (currentMargin < minMargin) {
                minMargin = currentMargin;
            }
        }

        return minMargin;
    }

    public static void main(String[] args) {
        double[][] X = {{1.0, 2.0}, {2.0, 1.0}, {3.0, 3.0}, {1.0, 0.0}};
        int[] y = {1, 1, -1, -1};
        double[] w = {1.0, 1.0};
        double b = -4.0;
        
        System.out.println("Margin: " + calculateMargin(X, y, w, b));
    }
}
\"\"\"""",
}

# Classical Machine Learning

Classical Machine Learning focuses on predictive algorithms that extract patterns from structured data without deep neural networks. Core modeling techniques include linear systems (Linear/Logistic Regression), tree-based models (Decision Trees, Random Forests, Gradient Boosted Trees), hyperplanes (Support Vector Machines), and clustering techniques (K-Means).

---

## 🗺️ ASCII Execution Flow: Gradient Descent

Here is the parameter optimization loop of finding the global minimum of a Cost Function $J(w)$ using Gradient Descent:

```text
Cost J(w)
   │
   ├─● Start (Initial weight w_0, high error)
   │  ╲
   │   ▼ Gradient = dJ/dw (Negative direction steps)
   │    ╲
   │     ▼ w_new = w_old - lr * (dJ/dw)
   │      ╲
   │       ▼
   ├─────────● Minimum (Optimal weight w*, zero gradient)
   └────────────────────────── w (Weight Parameter)

Gradient Descent Loop:
1. Initialize weights w and bias b.
2. Predict y_hat = Xw + b.
3. Compute loss gradient: dJ/dw = (1/N) * X^T * (y_hat - y).
4. Update weights: w = w - lr * dJ/dw.
5. Repeat until convergence.
```

---

## 📊 Model Complexities & Trade-offs

| Model | Training Complexity | Inference Complexity | Feature Requirements |
| :--- | :--- | :--- | :--- |
| Linear Regression | $O(N \cdot D^2 + D^3)$ | $O(D)$ | Linear relations, scaled features |
| Decision Tree | $O(N \cdot D \log N)$ | $O(Depth)$ | Handles non-linearities, no scaling |
| Random Forest | $O(Trees \cdot N \cdot D \log N)$ | $O(Trees \cdot Depth)$ | Robust to overfitting, high memory |

---

## 🏢 Real-World Production Use-Case

### Fintech: Real-time Credit Risk Default Engine
When a user requests a loan or credit line increase, the bank must estimate their default probability in milliseconds.
1. The scoring engine pulls features (e.g. debt-to-income ratio, active accounts, credit history length).
2. It runs feature values through a pre-trained **Logistic Regression** model or a shallow **Decision Tree**.
3. Because linear and tree inference is extremely fast ($O(D)$ operations), the scoring completes within 10ms.
4. The classification probability dictates loan approvals and individual interest rates instantly at checkout points.
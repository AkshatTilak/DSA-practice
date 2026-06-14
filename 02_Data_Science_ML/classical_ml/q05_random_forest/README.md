# Random Forest (Ensemble Bagging Trees)

## 🗂️ Concept Card: Random Forest
**Random Forest** is a powerful ensemble learning method used for both **classification** and **regression**. It operates by constructing a multitude of decision trees during training and outputting the class that is the mode of the classes (classification) or mean prediction (regression) of the individual trees.

At its core, Random Forest is an implementation of **Bagging (Bootstrap Aggregating)**. While a single decision tree is prone to **overfitting** (high variance), a Random Forest mitigates this by averaging multiple "decorrelated" trees, effectively reducing the variance without significantly increasing the bias.

### Core Objectives
- **Reduce Overfitting:** By combining multiple trees, the model generalizes better to unseen data.
- **Increase Robustness:** It handles outliers and noise better than a single decision tree.
- **Feature Importance:** It provides an intrinsic way to measure which features contribute most to the predictive power.

---

## 📐 Theoretical Foundations & Mathematics

### 1. Bootstrap Aggregating (Bagging)
Bagging involves two main steps:
1.  **Bootstrapping:** Creating multiple random subsets of the training data. If the original dataset has $N$ samples, a bootstrap sample is created by picking $N$ samples **with replacement**. This means some samples will appear multiple times, while others (roughly 36.8%, known as **Out-of-Bag** or OOB samples) will not appear at all.
2.  **Aggregating:** Combining the predictions of all trees.
    - **Classification:** $\hat{y} = \text{mode}(\hat{y}_1, \hat{y}_2, \dots, \hat{y}_B)$
    - **Regression:** $\hat{y} = \frac{1}{B} \sum_{i=1}^{B} \hat{y}_i$
    *(Where $B$ is the number of trees).*

### 2. The "Random" in Random Forest: Feature Subspacing
Unlike standard bagging, which uses all features for every split, Random Forest introduces **Feature Randomness**. At each node of the decision tree:
- Instead of searching for the best split among *all* $M$ features, the algorithm selects a **random subset** of $m$ features (where $m < M$).
- The best split is then chosen from this random subset.

**Why do this?** If one feature is a very strong predictor, every tree in a standard bagging ensemble will split on that feature first, making the trees highly correlated. By restricting the features, we force the trees to look for other patterns, **decorrelating** the trees and further reducing variance.

### 3. Splitting Criteria (The Engine)
Each individual tree in the forest is grown using criteria such as:
- **Gini Impurity (Classification):** $G = 1 - \sum_{i=1}^{C} (p_i)^2$
- **Entropy/Information Gain (Classification):** $H = -\sum_{i=1}^{C} p_i \log_2(p_i)$
- **Mean Squared Error (Regression):** $MSE = \frac{1}{n} \sum (y_i - \hat{y})^2$

---

## 🛠️ Step-by-Step Logic

The implementation of a Random Forest follows this logical pipeline:

1.  **Initialization:** Define the number of trees ($T$) and the number of features to consider at each split ($m$).
2.  **Bootstrap Sampling:** For each tree $i \in \{1 \dots T\}$:
    - Generate a bootstrap sample $S_i$ from the training set.
3.  **Tree Construction:** Build a decision tree on $S_i$:
    - At each node, randomly select $m$ features.
    - Find the best split among those $m$ features using Gini or Entropy.
    - Split the data and repeat recursively until a stopping criterion (like `max_depth`) is reached.
4.  **Prediction (Inference):**
    - Pass the input sample $X$ through all $T$ trees.
    - Collect predictions $\hat{y}_1, \hat{y}_2, \dots, \hat{y}_T$.
    - **Aggregate:** Return the majority vote (Classification) or the average (Regression).

### Implementation Example (Conceptual)
```python
from sklearn.ensemble import RandomForestClassifier

def solve():
    # Initialize the Random Forest
    # n_estimators: Number of trees in the forest
    # max_features: Number of features to consider at each split ('sqrt' is standard)
    model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        max_features='sqrt', 
        random_state=42
    )
    
    # Training: This performs bootstrapping and tree building internally
    model.fit(X_train, y_train)
    
    # Inference: This performs aggregation of all T trees
    predictions = model.predict(X_test)
    return predictions
```

---

## ⏱️ Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Training** | $O(T \cdot n \log n \cdot m)$ | $O(T \cdot \text{nodes})$ | $T$ = trees, $n$ = samples, $m$ = features sampled per split. |
| **Inference** | $O(T \cdot \text{depth})$ | $O(1)$ | Prediction requires traversing $T$ trees of a certain depth. |

### Hyperparameter Tuning Guide

| Hyperparameter | Effect | Tuning Direction |
| :--- | :--- | :--- |
| `n_estimators` | Number of trees. | $\uparrow$ Better stability, but $\uparrow$ training time. |
| `max_depth` | Depth of each tree. | $\uparrow$ Captures more detail, but $\uparrow$ risk of overfitting. |
| `max_features` | Size of random feature subset. | $\downarrow$ Decreases correlation between trees (increases randomness). |
| `min_samples_split`| Min samples required to split a node. | $\uparrow$ Prevents the model from learning noise (regularization). |

---

## 🌍 Real-World Applications

Random Forests are "workhorse" models in industry because they require very little data preprocessing (no need for scaling) and are highly interpretable via feature importance.

1.  **Banking & Finance:** 
    - **Credit Scoring:** Predicting the probability of default based on historical customer data.
    - **Fraud Detection:** Identifying anomalous transaction patterns by aggregating decision boundaries.
2.  **Healthcare:**
    - **Disease Diagnosis:** Classifying whether a tumor is malignant or benign based on genomic features.
    - **Patient Risk Stratification:** Predicting the likelihood of hospital readmission.
3.  **E-commerce:**
    - **Churn Prediction:** Identifying customers likely to leave a service based on usage behavior.
    - **Recommendation Baselines:** Acting as a baseline model to predict if a user will click a product.
4.  **Bioinformatics:**
    - **Gene Classification:** Determining the function of a gene based on its expression patterns across different conditions.
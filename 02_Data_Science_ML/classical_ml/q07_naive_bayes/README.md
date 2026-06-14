# Naive Bayes Classification

## 🌟 Overview & Concept Card

**Naive Bayes** is a family of probabilistic machine learning algorithms based on **Bayes' Theorem**. It is primarily used for classification tasks. The "Naive" part of the name comes from the strong (and often unrealistic) assumption that **all features are conditionally independent** of each other given the class label.

Despite this oversimplification, Naive Bayes is remarkably effective for high-dimensional datasets, particularly in text classification and real-time predictions, due to its computational efficiency and low variance.

### Core Objective
The objective of a Naive Bayes classifier is to determine the probability that a given data point belongs to a specific class $C$, given its features $X = (x_1, x_2, ..., x_n)$, and then assign the data point to the class with the highest probability.

---

## 📚 Theoretical Foundations & Math

### 1. Bayes' Theorem
At the heart of the algorithm is Bayes' Theorem, which describes the probability of an event based on prior knowledge of conditions that might be related to the event:

$$P(C | X) = \frac{P(X | C) \cdot P(C)}{P(X)}$$

**Where:**
- $P(C | X)$: **Posterior Probability**. The probability of class $C$ given the observed features $X$.
- $P(X | C)$: **Likelihood**. The probability of observing features $X$ given that the class is $C$.
- $P(C)$: **Prior Probability**. The baseline probability of class $C$ occurring in the population.
- $P(X)$: **Evidence**. The total probability of observing features $X$ across all possible classes.

### 2. The "Naive" Assumption
Calculating $P(X | C)$ for a large set of features is computationally expensive. Naive Bayes simplifies this by assuming that features are independent:
$$P(x_1, x_2, ..., x_n | C) = P(x_1 | C) \cdot P(x_2 | C) \cdot ... \cdot P(x_n | C)$$

Substituting this back into the formula, the decision rule becomes:
$$\text{Class} = \arg\max_{C} \left[ P(C) \prod_{i=1}^{n} P(x_i | C) \right]$$
*(Note: $P(X)$ is ignored during optimization because it is constant for all classes $C$.)*

### 3. Distribution Variants
Depending on the nature of the features, different probability distributions are used to calculate $P(x_i | C)$:

| Variant | Feature Type | Probability Distribution Formula |
| :--- | :--- | :--- |
| **Gaussian NB** | Continuous | $P(x_i | C) = \frac{1}{\sqrt{2\pi\sigma_C^2}} \exp\left(-\frac{(x_i - \mu_C)^2}{2\sigma_C^2}\right)$ |
| **Multinomial NB** | Discrete / Counts | $P(x_i | C) = \frac{\text{count}(x_i, C) + \alpha}{\text{count}(C) + \alpha \cdot n}$ |
| **Bernoulli NB** | Binary (0/1) | $P(x_i | C) = P(x_i | C)^{x_i} \cdot (1 - P(x_i | C))^{1-x_i}$ |

**$\alpha$ (Laplace Smoothing):** Used in Multinomial/Bernoulli to prevent "Zero Probability" errors when a feature never appears in a specific class during training.

---

## 🛠️ Step-by-Step Logic

To implement Naive Bayes (specifically Gaussian), the algorithm follows these steps:

1.  **Training Phase (Parameter Estimation):**
    *   Split the training data by class $C$.
    *   For every feature $i$ in every class $C$:
        *   Calculate the **Mean** ($\mu_{i,C}$).
        *   Calculate the **Variance** ($\sigma_{i,C}^2$).
    *   Calculate the **Prior Probability** $P(C) = \frac{\text{Samples in } C}{\text{Total Samples}}$.

2.  **Inference Phase (Prediction):**
    *   For a new input vector $X$:
        *   For each possible class $C$:
            *   Calculate the likelihood $P(x_i | C)$ using the Gaussian PDF.
            *   Compute the total score: $\text{Score}_C = \log(P(C)) + \sum \log(P(x_i | C))$.
            *   *(We use $\log$ to prevent **arithmetic underflow** caused by multiplying many small probabilities).*
    *   Return the class $C$ with the maximum $\text{Score}_C$.

### Implementation

```python
import numpy as np

class NaiveBayesClassifier:
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.classes = np.unique(y)
        n_classes = len(self.classes)

        # Initialize parameters
        self.mean = np.zeros((n_classes, n_features))
        self.var = np.zeros((n_classes, n_features))
        self.priors = np.zeros(n_classes)

        for idx, c in enumerate(self.classes):
            X_c = X[y == c]
            self.mean[idx, :] = X_c.mean(axis=0)
            self.var[idx, :] = X_c.var(axis=0)
            self.priors[idx] = X_c.shape[0] / float(n_samples)

    def _pdf(self, class_idx, x):
        mean = self.mean[class_idx]
        var = self.var[class_idx]
        # Gaussian Probability Density Function
        numerator = np.exp(- (x - mean)**2 / (2 * var))
        denominator = np.sqrt(2 * np.pi * var)
        return numerator / denominator

    def predict(self, X):
        y_pred = [self._predict_single(x) for x in X]
        return np.array(y_pred)

    def _predict_single(self, x):
        posteriors = []

        for idx, c in enumerate(self.classes):
            # Use log-sum to avoid underflow
            prior = np.log(self.priors[idx])
            # Calculate log-likelihood for each feature and sum them
            likelihood = np.sum(np.log(self._pdf(idx, x) + 1e-9)) 
            posterior = prior + likelihood
            posteriors.append(posterior)

        return self.classes[np.argmax(posteriors)]

def solve():
    # Example usage
    X_train = np.array([[1, 2], [1, 1], [5, 6], [6, 5]])
    y_train = np.array([0, 0, 1, 1]) # Class 0: Small values, Class 1: Large values
    
    nb = NaiveBayesClassifier()
    nb.fit(X_train, y_train)
    
    X_test = np.array([[1.5, 1.5], [5.5, 5.5]])
    predictions = nb.predict(X_test)
    print(f"Predictions: {predictions}") # Expected: [0, 1]
```

---

## 📉 Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Training** | $O(N \cdot D)$ | $O(C \cdot D)$ | $N$=samples, $D$=features, $C$=classes. We only store means/vars. |
| **Inference** | $O(C \cdot D)$ | $O(C)$ | Must compute the likelihood for every feature per class. |

### Key Hyperparameters & Metrics
- **$\alpha$ (Smoothing):** Crucial for MultinomialNB to ensure $P(x_i|C) \neq 0$.
- **Evaluation Metrics:** Since NB is a classifier, use **Accuracy**, **Precision**, **Recall**, and **F1-Score**.
- **Log-Transform:** Essential for numerical stability.

---

## 🌍 Real-World Applications

1.  **Spam Filtering**: The classic use case. Features are word frequencies (Multinomial NB). If the word "Winner" or "Free" appears frequently in the "Spam" class, the posterior probability for a new email containing those words increases.
2.  **Sentiment Analysis**: Categorizing movie reviews or tweets as Positive, Negative, or Neutral based on the presence of specific keywords.
3.  **Medical Diagnosis**: Predicting the probability of a disease given a set of symptoms. (e.g., If "Fever" and "Cough" are present, what is $P(\text{Flu} | \text{Fever, Cough})$?).
4.  **Document Categorization**: Sorting news articles into categories like "Politics," "Sports," or "Technology."

### Summary Table: Pros vs. Cons

| Pros | Cons |
| :--- | :--- |
| Extremely fast to train and predict. | The independence assumption is rarely true in reality. |
| Works well with high-dimensional data. | Sensitive to irrelevant features. |
| Requires less training data than complex models. | "Zero frequency" problem (requires smoothing). |
| Robust to noise if data is large. | Poor probability estimates (though class ranking is often correct). |
INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Bayesian probability classification.',
    'groups': ['Classical ML', 'Probabilistic Models'],
    'readme_content': """# Naive Bayes Classification

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
| Robust to noise if data is large. | Poor probability estimates (though class ranking is often correct). |""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N * D) for fit, O(M * K * D) for predict
# Space Complexity: O(K * D) to store mean and variance for each class
# [This approach implements Gaussian Naive Bayes using standard Python lists and raw probability multiplication. 
# It is susceptible to numerical underflow because multiplying many small probabilities leads to values 
# that exceed the precision of floating-point numbers.]
import math

def solve_naive(X_train, y_train, X_test):
    # Separate data by class
    classes = set(y_train)
    stats = {}
    
    for c in classes:
        X_c = [X_train[i] for i in range(len(X_train)) if y_train[i] == c]
        num_samples = len(X_c)
        num_features = len(X_train[0])
        
        means = []
        vars_ = []
        for j in range(num_features):
            feat_vals = [row[j] for row in X_c]
            mean = sum(feat_vals) / num_samples
            variance = sum((x - mean)**2 for x in feat_vals) / num_samples
            means.append(mean)
            vars_.append(variance + 1e-9) # Avoid division by zero
        
        stats[c] = {
            'mean': means,
            'var': vars_,
            'prior': num_samples / len(y_train)
        }

    def calculate_likelihood(x, mean, var):
        exponent = math.exp(-((x - mean)**2) / (2 * var))
        return (1 / math.sqrt(2 * math.pi * var)) * exponent

    predictions = []
    for sample in X_test:
        best_class = None
        max_prob = -1
        
        for c in classes:
            prob = stats[c]['prior']
            for j in range(len(sample)):
                prob *= calculate_likelihood(sample[j], stats[c]['mean'][j], stats[c]['var'][j])
            
            if prob > max_prob:
                max_prob = prob
                best_class = c
        predictions.append(best_class)
        
    return predictions

# --- APPROACH 2: Optimal (Gaussian NB with Log-Sum and Vectorization) ---
# Time Complexity: O(N * D) for fit, O(M * K * D) for predict
# Space Complexity: O(K * D) to store model parameters
# [This approach is optimal because it uses NumPy for vectorized operations, significantly increasing 
# computation speed. Crucially, it operates in the log-space to prevent numerical underflow, converting 
# the product of probabilities into a sum of logarithms. This is the standard implementation 
# for production-grade Naive Bayes classifiers.]
import numpy as np

class GaussianNaiveBayes:
    def __init__(self, var_smoothing=1e-9):
        self.var_smoothing = var_smoothing
        self.classes = None
        self.means = None
        self.vars = None
        self.priors = None

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        self.classes = np.unique(y)
        n_features = X.shape[1]
        n_classes = len(self.classes)
        
        self.means = np.zeros((n_classes, n_features))
        self.vars = np.zeros((n_classes, n_features))
        self.priors = np.zeros(n_classes)
        
        for i, c in enumerate(self.classes):
            X_c = X[y == c]
            self.means[i, :] = X_c.mean(axis=0)
            self.vars[i, :] = X_c.var(axis=0) + self.var_smoothing
            self.priors[i] = X_c.shape[0] / float(X.shape[0])

    def predict(self, X):
        X = np.array(X)
        # Use log-likelihood to avoid underflow: 
        # log(P(C|X)) proportional to log(P(C)) + sum(log(P(xi|C)))
        # log(P(xi|C)) = -0.5 * log(2 * pi * var) - (x - mean)^2 / (2 * var)
        
        predictions = []
        for x in X:
            posteriors = []
            for i in range(len(self.classes)):
                prior = np.log(self.priors[i])
                # Vectorized Gaussian log-pdf
                likelihood = -0.5 * np.sum(np.log(2. * np.pi * self.vars[i])) \
                             - 0.5 * np.sum(((x - self.means[i])**2) / self.vars[i])
                posteriors.append(prior + likelihood)
            
            predictions.append(self.classes[np.argmax(posteriors)])
            
        return np.array(predictions)

def solve_optimal(X_train, y_train, X_test):
    gnb = GaussianNaiveBayes()
    gnb.fit(X_train, y_train)
    return gnb.predict(X_test).tolist()

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package classical_ml;

import java.util.*;

public class GaussianNaiveBayes {
    private double[][] means;
    private double[][] vars;
    private double[] priors;
    private double[] classes;
    private double varSmoothing = 1e-9;

    public void fit(double[][] X, int[] y) {
        int nSamples = X.length;
        int nFeatures = X[0].length;
        
        // Identify unique classes
        Set<Integer> uniqueClassesSet = new HashSet<>();
        for (int label : y) uniqueClassesSet.add(label);
        this.classes = uniqueClassesSet.stream().mapToInt(Integer::intValue).sorted().toArray();
        int nClasses = classes.length;
        
        means = new double[nClasses][nFeatures];
        vars = new double[nClasses][nFeatures];
        priors = new double[nClasses];
        
        for (int i = 0; i < nClasses; i++) {
            int c = classes[i];
            List<double[]> X_c = new ArrayList<>();
            for (int j = 0; j < nSamples; j++) {
                if (y[j] == c) X_c.add(X[j]);
            }
            
            int count = X_c.size();
            priors[i] = (double) count / nSamples;
            
            for (int f = 0; f < nFeatures; f++) {
                double sum = 0;
                for (double[] row : X_c) sum += row[f];
                double mean = sum / count;
                means[i][f] = mean;
                
                double varSum = 0;
                for (double[] row : X_c) varSum += Math.pow(row[f] - mean, 2);
                vars[i][f] = (varSum / count) + varSmoothing;
            }
        }
    }

    public int[] predict(double[][] X) {
        int nSamples = X.length;
        int nClasses = classes.length;
        int[] predictions = new int[nSamples];
        
        for (int i = 0; i < nSamples; i++) {
            double maxLogProb = Double.NEGATIVE_INFINITY;
            int bestClass = -1;
            
            for (int cIdx = 0; cIdx < nClasses; cIdx++) {
                double logProb = Math.log(priors[cIdx]);
                for (int f = 0; f < X[0].length; f++) {
                    double mean = means[cIdx][f];
                    double var = vars[cIdx][f];
                    double xVal = X[i][f];
                    // Log of Gaussian PDF
                    logProb += -0.5 * Math.log(2 * Math.PI * var) 
                               - Math.pow(xVal - mean, 2) / (2 * var);
                }
                
                if (logProb > maxLogProb) {
                    maxLogProb = logProb;
                    bestClass = classes[cIdx];
                }
            }
            predictions[i] = bestClass;
        }
        return predictions;
    }

    public static void main(String[] args) {
        double[][] X_train = {{1.0, 2.0}, {1.1, 2.1}, {5.0, 8.0}, {5.1, 8.1}};
        int[] y_train = {0, 0, 1, 1};
        double[][] X_test = {{1.2, 2.2}, {4.9, 7.9}};
        
        GaussianNaiveBayes gnb = new GaussianNaiveBayes();
        gnb.fit(X_train, y_train);
        int[] preds = gnb.predict(X_test);
        System.out.println(Arrays.toString(preds)); // Expected: [0, 1]
    }
}
\"\"\"""",
}

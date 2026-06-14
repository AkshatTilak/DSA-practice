"""
Challenge: q07_naive_bayes
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Bayesian probability classification.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

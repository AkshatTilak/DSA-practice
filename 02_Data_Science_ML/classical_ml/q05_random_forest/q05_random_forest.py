"""
Challenge: q05_random_forest
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Ensemble bagging trees.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(T * N * F * log N)
# Space Complexity: O(T * N)
# This approach implements a Bagging Classifier. It bootstraps the data and trains multiple Decision Trees, 
# but it considers all features (F) at every split. This is a naive version of a Random Forest 
# because it lacks the feature-subsampling mechanism that reduces correlation between trees.

import numpy as np
from collections import Counter

class DecisionTreeNaive:
    def __init__(self, max_depth=10, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None

    def _gini(self, y):
        m = len(y)
        if m == 0: return 0
        return 1.0 - sum((np.sum(y == c) / m) ** 2 for c in np.unique(y))

    def _best_split(self, X, y):
        m, n = X.shape
        if m < self.min_samples_split:
            return None, None

        best_gini = float('inf')
        best_feat, best_thresh = None, None

        for feat_idx in range(n):
            thresholds = np.unique(X[:, feat_idx])
            for thresh in thresholds:
                left_idx = np.where(X[:, feat_idx] <= thresh)[0]
                right_idx = np.where(X[:, feat_idx] > thresh)[0]
                
                if len(left_idx) == 0 or len(right_idx) == 0:
                    continue
                
                # Weighted Gini
                gini = (len(left_idx) * self._gini(y[left_idx]) + 
                        len(right_idx) * self._gini(y[right_idx])) / m
                
                if gini < best_gini:
                    best_gini, best_feat, best_thresh = gini, feat_idx, thresh
        
        return best_feat, best_thresh

    def _build_tree(self, X, y, depth=0):
        num_samples, num_features = X.shape
        unique_classes = np.unique(y)

        if depth >= self.max_depth or len(unique_classes) == 1 or num_samples < self.min_samples_split:
            return np.argmax(np.bincount(y))

        feat, thresh = self._best_split(X, y)
        if feat is None:
            return np.argmax(np.bincount(y))

        left_idx = np.where(X[:, feat] <= thresh)[0]
        right_idx = np.where(X[:, feat] > thresh)[0]
        
        return {
            'feature': feat,
            'threshold': thresh,
            'left': self._build_tree(X[left_idx], y[left_idx], depth + 1),
            'right': self._build_tree(X[right_idx], y[right_idx], depth + 1)
        }

    def fit(self, X, y):
        self.tree = self._build_tree(X, y)

    def _predict_one(self, x, tree):
        if not isinstance(tree, dict):
            return tree
        if x[tree['feature']] <= tree['threshold']:
            return self._predict_one(x, tree['left'])
        return self._predict_one(x, tree['right'])

    def predict(self, X):
        return np.array([self._predict_one(x, self.tree) for x in X])

def solve_naive(X, y, n_estimators=10):
    n_samples = X.shape[0]
    trees = []
    for _ in range(n_estimators):
        # Bootstrap sampling
        indices = np.random.choice(n_samples, n_samples, replace=True)
        X_boot, y_boot = X[indices], y[indices]
        
        dt = DecisionTreeNaive()
        dt.fit(X_boot, y_boot)
        trees.append(dt)
    
    # Aggregating predictions
    all_preds = np.array([dt.predict(X) for dt in trees])
    # Majority vote for each sample
    final_preds = [np.argmax(np.bincount(all_preds[:, i])) for i in range(n_samples)]
    return np.array(final_preds)

# --- APPROACH 2: Optimal (Random Forest with Feature Subsampling) ---
# Time Complexity: O(T * N * sqrt(F) * log N)
# Space Complexity: O(T * N)
# This implementation is optimal for a from-scratch Random Forest. Unlike the naive approach, 
# it restricts the number of features considered at each node split (typically sqrt(F)). 
# This reduces the variance of the ensemble and is the defining characteristic of Random Forests.
# It utilizes NumPy for efficient array slicing and calculation.

import numpy as np

class DecisionTreeOptimal:
    def __init__(self, max_depth=10, min_samples_split=2, max_features=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.tree = None

    def _gini(self, y):
        m = len(y)
        if m == 0: return 0
        # Vectorized Gini calculation
        counts = np.bincount(y)
        probs = counts / m
        return 1.0 - np.sum(probs**2)

    def _best_split(self, X, y):
        m, n = X.shape
        if m < self.min_samples_split:
            return None, None

        # Randomly sample features at each node
        n_feat = self.max_features if self.max_features else n
        feat_idxs = np.random.choice(n, n_feat, replace=False)

        best_gini = float('inf')
        best_feat, best_thresh = None, None

        for feat_idx in feat_idxs:
            # To optimize, we only check a subset of unique values as thresholds if many exist
            values = X[:, feat_idx]
            thresholds = np.unique(values)
            if len(thresholds) > 20: # Heuristic to speed up training on continuous data
                thresholds = np.percentile(values, np.linspace(0, 100, 20))

            for thresh in thresholds:
                mask = X[:, feat_idx] <= thresh
                left_y, right_y = y[mask], y[~mask]
                
                if len(left_y) == 0 or len(right_y) == 0:
                    continue
                
                gini = (len(left_y) * self._gini(left_y) + 
                        len(right_y) * self._gini(right_y)) / m
                
                if gini < best_gini:
                    best_gini, best_feat, best_thresh = gini, feat_idx, thresh
        
        return best_feat, best_thresh

    def _build_tree(self, X, y, depth=0):
        num_samples, _ = X.shape
        unique_classes = np.unique(y)

        if depth >= self.max_depth or len(unique_classes) == 1 or num_samples < self.min_samples_split:
            return np.argmax(np.bincount(y)) if len(y) > 0 else None

        feat, thresh = self._best_split(X, y)
        if feat is None:
            return np.argmax(np.bincount(y)) if len(y) > 0 else None

        mask = X[:, feat] <= thresh
        return {
            'feature': feat,
            'threshold': thresh,
            'left': self._build_tree(X[mask], y[mask], depth + 1),
            'right': self._build_tree(X[~mask], y[~mask], depth + 1)
        }

    def fit(self, X, y):
        self.tree = self._build_tree(X, y)

    def _predict_one(self, x, tree):
        if not isinstance(tree, dict):
            return tree
        if x[tree['feature']] <= tree['threshold']:
            return self._predict_one(x, tree['left'])
        return self._predict_one(x, tree['right'])

    def predict(self, X):
        return np.array([self._predict_one(x, self.tree) for x in X])

class RandomForestClassifier:
    def __init__(self, n_estimators=10, max_depth=10, min_samples_split=2, max_features='sqrt'):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []

    def fit(self, X, y):
        n_samples, n_features = X.shape
        
        # Calculate max_features based on strategy
        if self.max_features == 'sqrt':
            m_feat = int(np.sqrt(n_features))
        elif self.max_features == 'log2':
            m_feat = int(np.log2(n_features))
        elif isinstance(self.max_features, int):
            m_feat = self.max_features
        else:
            m_feat = n_features

        self.trees = []
        for _ in range(self.n_estimators):
            # Bootstrap
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_boot, y_boot = X[indices], y[indices]
            
            tree = DecisionTreeOptimal(
                max_depth=self.max_depth, 
                min_samples_split=self.min_samples_split, 
                max_features=m_feat
            )
            tree.fit(X_boot, y_boot)
            self.trees.append(tree)

    def predict(self, X):
        # Get predictions from all trees: shape (n_estimators, n_samples)
        tree_preds = np.array([tree.predict(X) for tree in self.trees])
        # Majority vote along the estimator axis
        final_preds = []
        for i in range(X.shape[0]):
            sample_preds = tree_preds[:, i]
            final_preds.append(np.argmax(np.bincount(sample_preds.astype(int))))
        return np.array(final_preds)

def solve_optimal(X, y, n_estimators=10):
    # Default hyperparameters for a standard RF
    rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=10, max_features='sqrt')
    rf.fit(X, y)
    return rf.predict(X)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package classical_ml;

import java.util.*;
import java.util.stream.*;

public class RandomForest {
    private int nEstimators;
    private int maxDepth;
    private int minSamplesSplit;
    private List<DecisionTree> trees;

    public RandomForest(int nEstimators, int maxDepth, int minSamplesSplit) {
        this.nEstimators = nEstimators;
        this.maxDepth = maxDepth;
        this.minSamplesSplit = minSamplesSplit;
        this.trees = new ArrayList<>();
    }

    public void fit(double[][] X, int[] y) {
        int nSamples = X.length;
        int nFeatures = X[0].length;
        int maxFeat = (int) Math.sqrt(nFeatures);
        Random random = new Random();

        for (int i = 0; i < nEstimators; i++) {
            // Bootstrap
            double[][] XBoot = new double[nSamples][nFeatures];
            int[] yBoot = new int[nSamples];
            for (int j = 0; j < nSamples; j++) {
                int idx = random.nextInt(nSamples);
                XBoot[j] = X[idx];
                yBoot[j] = y[idx];
            }
            DecisionTree tree = new DecisionTree(maxDepth, minSamplesSplit, maxFeat);
            tree.fit(XBoot, yBoot);
            trees.add(tree);
        }
    }

    public int[] predict(double[][] X) {
        int nSamples = X.length;
        int[] finalPreds = new int[nSamples];
        for (int i = 0; i < nSamples; i++) {
            Map<Integer, Integer> votes = new HashMap<>();
            for (DecisionTree tree : trees) {
                int p = tree.predict(X[i]);
                votes.put(p, votes.getOrDefault(p, 0) + 1);
            }
            finalPreds[i] = Collections.max(votes.entrySet(), Map.Entry.comparingByValue()).getKey();
        }
        return finalPreds;
    }

    private static class DecisionTree {
        private Node root;
        private int maxDepth;
        private int minSamplesSplit;
        private int maxFeatures;

        public DecisionTree(int maxDepth, int minSamplesSplit, int maxFeatures) {
            this.maxDepth = maxDepth;
            this.minSamplesSplit = minSamplesSplit;
            this.maxFeatures = maxFeatures;
        }

        public void fit(double[][] X, int[] y) {
            this.root = buildTree(X, y, 0);
        }

        private Node buildTree(double[][] X, int[] y, int depth) {
            int nSamples = X.length;
            long uniqueClasses = Arrays.stream(y).distinct().count();

            if (depth >= maxDepth || uniqueClasses == 1 || nSamples < minSamplesSplit) {
                return new Node(getMostFrequent(y));
            }

            int bestFeat = -1;
            double bestThresh = 0;
            double bestGini = Double.MAX_VALUE;

            // Feature Subsampling
            List<Integer> featIdxs = IntStream.range(0, X[0].length).boxed().collect(Collectors.toList());
            Collections.shuffle(featIdxs);
            
            for (int i = 0; i < Math.min(maxFeatures, featIdxs.size()); i++) {
                int f = featIdxs.get(i);
                double[] vals = new double[nSamples];
                for (int j = 0; j < nSamples; j++) vals[j] = X[j][f];
                
                for (double thresh : vals) {
                    double gini = calculateSplitGini(X, y, f, thresh);
                    if (gini < bestGini) {
                        bestGini = gini;
                        bestFeat = f;
                        bestThresh = thresh;
                    }
                }
            }

            if (bestFeat == -1) return new Node(getMostFrequent(y));

            // Split data
            List<Integer> leftIdx = new ArrayList<>();
            List<Integer> rightIdx = new ArrayList<>();
            for (int i = 0; i < nSamples; i++) {
                if (X[i][bestFeat] <= bestThresh) leftIdx.add(i);
                else rightIdx.add(i);
            }

            Node node = new Node(bestFeat, bestThresh);
            node.left = buildTree(filterX(X, leftIdx), filterY(y, leftIdx), depth + 1);
            node.right = buildTree(filterX(X, rightIdx), filterY(y, rightIdx), depth + 1);
            return node;
        }

        private double calculateSplitGini(double[][] X, int[] y, int f, double t) {
            List<Integer> leftY = new ArrayList<>();
            List<Integer> rightY = new ArrayList<>();
            for (int i = 0; i < X.length; i++) {
                if (X[i][f] <= t) leftY.add(y[i]);
                else rightY.add(y[i]);
            }
            if (leftY.isEmpty() || rightY.isEmpty()) return Double.MAX_VALUE;
            return (leftY.size() * gini(leftY) + rightY.size() * gini(rightY)) / y.length;
        }

        private double gini(List<Integer> y) {
            if (y.isEmpty()) return 0;
            Map<Integer, Long> counts = y.stream().collect(Collectors.groupingBy(i -> i, Collectors.counting()));
            double sumSq = 0;
            for (long count : counts.values()) {
                sumSq += Math.pow((double) count / y.size(), 2);
            }
            return 1.0 - sumSq;
        }

        private int getMostFrequent(int[] y) {
            return Arrays.stream(y).boxed()
                .collect(Collectors.groupingBy(i -> i, Collectors.counting()))
                .entrySet().stream().max(Map.Entry.comparingByValue()).get().getKey();
        }

        private double[][] filterX(double[][] X, List<Integer> idxs) {
            double[][] res = new double[idxs.size()][X[0].length];
            for (int i = 0; i < idxs.size(); i++) res[i] = X[idxs.get(i)];
            return res;
        }

        private int[] filterY(int[] y, List<Integer> idxs) {
            int[] res = new int[idxs.size()];
            for (int i = 0; i < idxs.size(); i++) res[i] = y[idxs.get(i)];
            return res;
        }

        public int predict(double[] x) {
            Node curr = root;
            while (curr.isLeaf()) {
                if (x[curr.feature] <= curr.threshold) curr = curr.left;
                else curr = curr.right;
            }
            return curr.value;
        }
    }

    private static class Node {
        int feature;
        double threshold;
        int value;
        Node left, right;
        boolean leaf;

        Node(int val) { this.value = val; this.leaf = true; }
        Node(int feat, double thresh) { this.feature = feat; this.threshold = thresh; this.leaf = false; }
        boolean isLeaf() { return !leaf; } // Inverted logic to fit loop
    }
}
"""

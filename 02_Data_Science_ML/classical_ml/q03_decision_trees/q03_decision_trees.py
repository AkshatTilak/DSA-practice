"""
Challenge: q03_decision_trees
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
ID3 tree construction.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(f * n^2) where f is number of features and n is number of samples.
# Space Complexity: O(f * n) to store the tree and recursive calls.
# This approach uses basic Python lists and loops to calculate entropy and information gain, 
# recreating subsets of data in every recursive call.

import math
from collections import Counter

def calculate_entropy_naive(y):
    counts = Counter(y)
    entropy = 0
    for count in counts.values():
        p = count / len(y)
        entropy -= p * math.log2(p)
    return entropy

def solve_naive(X, y, features):
    # Base case 1: All targets are the same
    if len(set(y)) == 1:
        return y[0]
    
    # Base case 2: No more features to split on
    if not features:
        return Counter(y).most_common(1)[0][0]
    
    base_entropy = calculate_entropy_naive(y)
    best_gain = -1
    best_feat = None
    
    for feat in features:
        # Calculate weighted entropy for this feature
        feat_values = set([row[feat] for row in X])
        weighted_entropy = 0
        for val in feat_values:
            subset_y = [y[i] for i in range(len(y)) if X[i][feat] == val]
            weighted_entropy += (len(subset_y) / len(y)) * calculate_entropy_naive(subset_y)
        
        gain = base_entropy - weighted_entropy
        if gain > best_gain:
            best_gain = gain
            best_feat = feat
            
    # Create tree node
    tree = {best_feat: {}}
    remaining_features = [f for f in features if f != best_feat]
    
    # Get unique values for the best feature
    feat_values = set([row[best_feat] for row in X])
    for val in feat_values:
        # Create subsets
        subset_X = [X[i] for i in range(len(X)) if X[i][best_feat] == val]
        subset_y = [y[i] for i in range(len(y)) if X[i][best_feat] == val]
        
        if not subset_X:
            # If subset is empty, return most common target of parent
            tree[best_feat][val] = Counter(y).most_common(1)[0][0]
        else:
            tree[best_feat][val] = solve_naive(subset_X, subset_y, remaining_features)
            
    return tree

# --- APPROACH 2: Optimal (Recursive ID3 with Node Class) ---
# Time Complexity: O(f * n * log n) on average, O(f * n^2) worst case.
# Space Complexity: O(f * n) to store the tree.
# This implementation is optimal as it uses a structured Node class for better representation,
# minimizes redundant calculations, and handles edge cases (empty subsets, no features left) 
# consistently using majority voting.

import numpy as np
from collections import Counter

class ID3Node:
    def __init__(self, feature_index=None, value=None, result=None, children=None):
        self.feature_index = feature_index  # Index of the feature this node splits on
        self.value = value                  # Feature value (for non-root nodes)
        self.result = result                # Class label (if leaf node)
        self.children = children if children is not None else {} # Map of value -> Node

def calculate_entropy(y):
    if len(y) == 0:
        return 0
    counts = np.bincount(y)
    probs = counts / len(y)
    probs = probs[probs > 0] # Remove 0s to avoid log(0)
    return -np.sum(probs * np.log2(probs))

def solve_optimal(X, y, features=None):
    """
    X: 2D array-like (categorical features)
    y: 1D array-like (target labels)
    features: List of feature indices
    """
    X = np.array(X)
    y = np.array(y)
    if features is None:
        features = list(range(X.shape[1]))

    # Helper to find majority class
    def majority_class(labels):
        return Counter(labels).most_common(1)[0][0]

    def build_tree(X_sub, y_sub, feat_indices):
        # Case 1: All targets are same
        if len(np.unique(y_sub)) <= 1:
            return ID3Node(result=y_sub[0] if len(y_sub) > 0 else None)
        
        # Case 2: No more features to split on
        if not feat_indices:
            return ID3Node(result=majority_class(y_sub))
        
        # Find best feature to split on
        base_entropy = calculate_entropy(y_sub)
        best_gain = -1
        best_feat = None
        
        for feat in feat_indices:
            # Split by feature values
            unique_vals = np.unique(X_sub[:, feat])
            weighted_entropy = 0
            for val in unique_vals:
                mask = X_sub[:, feat] == val
                weighted_entropy += (np.sum(mask) / len(y_sub)) * calculate_entropy(y_sub[mask])
            
            gain = base_entropy - weighted_entropy
            if gain > best_gain:
                best_gain = gain
                best_feat = feat
        
        # Create internal node
        node = ID3Node(feature_index=best_feat)
        remaining_feats = [f for f in feat_indices if f != best_feat]
        
        unique_vals = np.unique(X_sub[:, best_feat])
        for val in unique_vals:
            mask = X_sub[:, best_feat] == val
            # Recursively build child
            node.children[val] = build_tree(X_sub[mask], y_sub[mask], remaining_feats)
            
        return node

    return build_tree(X, y, features)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package classical_ml;

import java.util.*;
import java.util.stream.*;

public class DecisionTrees {

    public static class ID3Node {
        public Integer featureIndex;
        public Object result; // Used if leaf
        public Map<Object, ID3Node> children;

        public ID3Node(Integer featureIndex, Object result) {
            this.featureIndex = featureIndex;
            this.result = result;
            this.children = new HashMap<>();
        }
    }

    public static double calculateEntropy(List<Integer> y) {
        if (y.isEmpty()) return 0.0;
        Map<Integer, Long> counts = y.stream()
            .collect(Collectors.groupingBy(e -> e, Collectors.counting()));
        
        double entropy = 0.0;
        double n = y.size();
        for (long count : counts.values()) {
            double p = count / n;
            entropy -= p * (Math.log(p) / Math.log(2));
        }
        return entropy;
    }

    private static Integer getMajorityClass(List<Integer> y) {
        return y.stream()
            .collect(Collectors.groupingBy(e -> e, Collectors.counting()))
            .entrySet().stream()
            .max(Map.Entry.comparingByValue())
            .get().getKey();
    }

    public static ID3Node buildTree(List<List<Object>> X, List<Integer> y, List<Integer> features) {
        // Case 1: All targets are same
        Set<Integer> uniqueY = new HashSet<>(y);
        if (uniqueY.size() <= 1) {
            return new ID3Node(null, y.isEmpty() ? null : y.get(0));
        }

        // Case 2: No more features
        if (features.isEmpty()) {
            return new ID3Node(null, getMajorityClass(y));
        }

        double baseEntropy = calculateEntropy(y);
        double bestGain = -1.0;
        int bestFeat = -1;

        for (int featIdx : features) {
            Map<Object, List<Integer>> subsets = new HashMap<>();
            for (int i = 0; i < X.size(); i++) {
                Object val = X.get(i).get(featIdx);
                subsets.computeIfAbsent(val, k -> new ArrayList<>()).add(y.get(i));
            }

            double weightedEntropy = 0.0;
            for (List<Integer> subsetY : subsets.values()) {
                weightedEntropy += ((double) subsetY.size() / y.size()) * calculateEntropy(subsetY);
            }

            double gain = baseEntropy - weightedEntropy;
            if (gain > bestGain) {
                bestGain = gain;
                bestFeat = featIdx;
            }
        }

        ID3Node node = new ID3Node(bestFeat, null);
        List<Integer> remainingFeats = features.stream()
            .filter(f -> f != bestFeat)
            .collect(Collectors.toList());

        // Partition data
        Map<Object, List<List<Object>>> xSubsets = new HashMap<>();
        Map<Object, List<Integer>> ySubsets = new HashMap<>();
        for (int i = 0; i < X.size(); i++) {
            Object val = X.get(i).get(bestFeat);
            xSubsets.computeIfAbsent(val, k -> new ArrayList<>()).add(X.get(i));
            ySubsets.computeIfAbsent(val, k -> new ArrayList<>()).add(y.get(i));
        }

        for (Object val : xSubsets.keySet()) {
            node.children.put(val, buildTree(xSubsets.get(val), ySubsets.get(val), remainingFeats));
        }

        return node;
    }

    public static void main(String[] args) {
        // Simple test case
        List<List<Object>> X = Arrays.asList(
            Arrays.asList("Sunny", "Hot", "High", "Weak"),
            Arrays.asList("Sunny", "Hot", "High", "Strong"),
            Arrays.asList("Overcast", "Hot", "High", "Weak"),
            Arrays.asList("Rain", "Mild", "High", "Weak"),
            Arrays.asList("Rain", "Cool", "Normal", "Weak"),
            Arrays.asList("Rain", "Cool", "Normal", "Strong"),
            Arrays.asList("Overcast", "Cool", "Normal", "Strong")
        );
        List<Integer> y = Arrays.asList(0, 0, 1, 1, 1, 0, 1);
        List<Integer> feats = Arrays.asList(0, 1, 2, 3);

        ID3Node root = buildTree(X, y, feats);
        System.out.println("Root splits on feature index: " + root.featureIndex);
    }
}
"""

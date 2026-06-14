INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'ID3 tree construction.',
    'groups': ['Classical ML'],
    'readme_content': """# Decision Tree Construction (ID3 Algorithm)

## 📌 Overview & Concept Card

The **ID3 (Iterative Dichotomizer 3)** algorithm is a foundational machine learning algorithm used to generate a decision tree from a dataset. It is a **greedy, top-down induction** approach that builds a tree by recursively partitioning the data based on the attribute that provides the most "information" about the target class.

### Core Objective
The primary goal of ID3 is to create the **smallest possible tree** that correctly classifies the training data. To achieve this, it minimizes the uncertainty (entropy) of the target variable at each split, ensuring that the resulting child nodes are as "pure" (homogeneous) as possible.

### Key Characteristics
- **Type**: Supervised Learning (Classification).
- **Split Criterion**: Information Gain.
- **Feature Type**: Originally designed for **categorical features**.
- **Strategy**: Recursive Partitioning.

---

## 🧪 Theoretical Foundations & Math

The ID3 algorithm relies on Information Theory, specifically the concepts of **Entropy** and **Information Gain**.

### 1. Entropy
Entropy is a measure of impurity, disorder, or uncertainty in a group of examples. For a binary classification problem, if the data is split 50/50, entropy is at its maximum (1.0). If all examples belong to one class, entropy is 0.

**Mathematical Formula:**
$$H(S) = -\sum_{i=1}^{c} p_i \log_2(p_i)$$

Where:
- $S$: The current set of examples.
- $c$: The number of classes.
- $p_i$: The proportion of examples belonging to class $i$ in set $S$.

### 2. Information Gain (IG)
Information Gain measures the reduction in entropy achieved by partitioning the data according to a specific attribute $A$. ID3 selects the attribute that maximizes this value.

**Mathematical Formula:**
$$IG(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} H(S_v)$$

Where:
- $H(S)$: Entropy of the parent set.
- $\text{Values}(A)$: All possible values the attribute $A$ can take.
- $S_v$: The subset of $S$ where attribute $A$ has value $v$.
- $\frac{|S_v|}{|S|}$: The weight of the subset $S_v$ relative to the parent set.

---

## 🛠️ Step-by-Step Logic

The ID3 algorithm follows a recursive process to build the tree from the root downwards.

### Algorithmic Flow:
1. **Calculate Parent Entropy**: Compute the entropy of the target label for the current dataset.
2. **Evaluate All Features**:
   - For each available feature, split the dataset into subsets based on the feature's values.
   - Calculate the weighted entropy of these subsets.
   - Subtract the weighted entropy from the parent entropy to find the **Information Gain**.
3. **Select the Best Split**: The feature with the **highest Information Gain** is chosen as the decision node.
4. **Partition and Recurse**:
   - Create a branch for each possible value of the chosen feature.
   - Filter the dataset to include only rows matching that value.
   - Repeat the process for each branch using the remaining features.
5. **Base Cases (Stopping Criteria)**:
   - **Pure Node**: All examples in the subset belong to the same class $\rightarrow$ Create a **Leaf Node** with that class label.
   - **No More Features**: If no features are left to split but classes are still mixed $\rightarrow$ Create a **Leaf Node** with the majority class label.
   - **Empty Subset**: If a branch has no examples $\rightarrow$ Create a **Leaf Node** with the majority class of the parent.

### Implementation Strategy

```python
import numpy as np
from collections import Counter

class ID3DecisionTree:
    def __init__(self):
        self.tree = None

    def entropy(self, y):
        \"\"\"Calculate the entropy of a label array.\"\"\"
        hist = np.bincount(y)
        ps = hist / len(y)
        return -np.sum([p * np.log2(p) for p in ps if p > 0])

    def info_gain(self, X, y, idx):
        \"\"\"Calculate Information Gain for a specific feature index.\"\"\"
        parent_entropy = self.entropy(y)
        
        # Get unique values of the feature
        values, counts = np.unique(X[:, idx], return_counts=True)
        
        weighted_entropy = 0
        for v, count in zip(values, counts):
            # Subset where feature idx == value v
            subset_y = y[X[:, idx] == v]
            weighted_entropy += (count / len(y)) * self.entropy(subset_y)
            
        return parent_entropy - weighted_entropy

    def build_tree(self, X, y, features):
        # Base Case 1: All samples have the same class
        if len(np.unique(y)) == 1:
            return np.unique(y)[0]
        
        # Base Case 2: No more features to split on
        if len(features) == 0:
            return Counter(y).most_common(1)[0][0]
        
        # Find the best feature
        gains = [self.info_gain(X, y, f) for f in features]
        best_feat_idx = features[np.argmax(gains)]
        
        # Create tree node
        tree = {best_feat_idx: {}}
        
        # Split the data
        feat_values = np.unique(X[:, best_feat_idx])
        for val in feat_values:
            # Filter X and y for the specific feature value
            mask = X[:, best_feat_idx] == val
            new_X = X[mask]
            new_y = y[mask]
            
            # Remove the used feature from the list
            remaining_feats = [f for f in features if f != best_feat_idx]
            
            # Recursive call
            tree[best_feat_idx][val] = self.build_tree(new_X, new_y, remaining_feats)
            
        return tree

    def fit(self, X, y):
        features = list(range(X.shape[1]))
        self.tree = self.build_tree(X, y, features)

    def predict_single(self, x, tree):
        if not isinstance(tree, dict):
            return tree
        
        feature_idx = list(tree.keys())[0]
        feature_val = x[feature_idx]
        
        if feature_val not in tree[feature_idx]:
            # Return most common label if value not seen during training (simplified)
            return None 
            
        return self.predict_single(x, tree[feature_idx][feature_val])

    def predict(self, X):
        return np.array([self.predict_single(x, self.tree) for x in X])

# --- Example Usage ---
def solve():
    # Features: [Outlook, Temp, Humidity, Windy]
    # Outlook: 0:Sunny, 1:Overcast, 2:Rainy
    # Temp: 0:Hot, 1:Mild, 2:Cool
    # Humidity: 0:High, 1:Normal
    # Windy: 0:False, 1:True
    X = np.array([
        [0, 0, 0, 0], [0, 0, 0, 1], [1, 0, 1, 0], [2, 1, 1, 0],
        [2, 0, 0, 1], [2, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0]
    ])
    y = np.array([0, 0, 1, 1, 1, 0, 1, 0]) # 0: No, 1: Yes

    model = ID3DecisionTree()
    model.fit(X, y)
    print("Constructed Tree:", model.tree)

if __name__ == "__main__":
    solve()
```

---

## 📊 Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Explanation |
| :--- | :--- | :--- | :--- |
| **Training** | $O(F \cdot N \log N)$ | $O(\text{Nodes})$ | $F$ is the number of features, $N$ is the number of samples. At each level, we evaluate $F$ features across $N$ samples. |
| **Inference** | $O(\text{Depth})$ | $O(1)$ | Traversing from root to leaf takes time proportional to the height of the tree. |

### Key Hyperparameters & Limitations
1. **No Pruning**: Standard ID3 does not perform pruning, making it highly susceptible to **overfitting** (it creates a tree that fits the training data perfectly but generalizes poorly).
2. **Categorical Only**: ID3 cannot handle continuous numerical data without discretization (binning).
3. **Bias**: It favors features with a large number of distinct values (which can lead to artificially high Information Gain). This is why **C4.5** uses **Gain Ratio** instead of Information Gain.

---

## 🌍 Real-World Applications

Decision trees (and their evolved versions like Random Forests and XGBoost) are used across various industries:

1. **Medical Diagnosis**: Creating a flowchart of symptoms (Fever $\rightarrow$ Yes $\rightarrow$ Cough $\rightarrow$ Yes) to predict a specific disease.
2. **Credit Scoring**: Banks use tree-based logic to decide loan approvals based on credit score, income brackets, and employment history.
3. **Customer Churn Prediction**: Identifying which customers are likely to cancel a subscription based on usage frequency, contract type, and support tickets.
4. **Fraud Detection**: Detecting anomalous transaction patterns (Transaction Amount $>$ \$10k AND Location $=$ Foreign $\rightarrow$ Flag for Review).""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
    \"\"\"
    X: 2D array-like (categorical features)
    y: 1D array-like (target labels)
    features: List of feature indices
    \"\"\"
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
\"\"\"
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
\"\"\"""",
}

"""
ML Evaluation: Precision, Recall, and F1 Score
Difficulty: Medium
Category: Systems Evaluation

Problem:
Given list of actual labels (binary 0 or 1) and list of predicted labels (binary 0 or 1),
calculate the Precision, Recall, and F1-Score of the predictions.
If the denominator for any metric is zero, return 0.0 for that metric.

Curriculum Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/
"""

# --- STARTER TEMPLATE FOR USER ---
def calculate_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    """
    Calculate precision, recall, and f1-score from lists of ground truth and predictions.
    Should return a dictionary:
    {
        "precision": float,
        "recall": float,
        "f1_score": float
    }
    """
    # Write your solution here
    pass


# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive Iterative Loop ---
# Time Complexity: O(N)
# Space Complexity: O(1)
def calculate_metrics_naive(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = 0
    fp = 0
    fn = 0
    
    for i in range(len(y_true)):
        actual = y_true[i]
        pred = y_pred[i]
        
        if actual == 1 and pred == 1:
            tp += 1
        elif actual == 0 and pred == 1:
            fp += 1
        elif actual == 1 and pred == 0:
            fn += 1
            
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }


# --- APPROACH 2: Optimal Pythonic (Zip & Generator Comprehensions) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# Uses fast zip generators and single-pass counters.
def calculate_metrics_optimal(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }


# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

import java.util.HashMap;
import java.util.Map;

public class ClassificationMetrics {
    public static Map<String, Double> calculateMetrics(int[] yTrue, int[] yPred) {
        int tp = 0, fp = 0, fn = 0;
        
        for (int i = 0; i < yTrue.length; i++) {
            if (yTrue[i] == 1 && yPred[i] == 1) tp++;
            else if (yTrue[i] == 0 && yPred[i] == 1) fp++;
            else if (yTrue[i] == 1 && yPred[i] == 0) fn++;
        }
        
        double precision = (tp + fp > 0) ? (double) tp / (tp + fp) : 0.0;
        double recall = (tp + fn > 0) ? (double) tp / (tp + fn) : 0.0;
        double f1 = (precision + recall > 0) ? 2.0 * (precision * recall) / (precision + recall) : 0.0;
        
        Map<String, Double> metrics = new HashMap<>();
        metrics.put("precision", Math.round(precision * 10000.0) / 10000.0);
        metrics.put("recall", Math.round(recall * 10000.0) / 10000.0);
        metrics.put("f1_score", Math.round(f1 * 10000.0) / 10000.0);
        
        return metrics;
    }
}
"""

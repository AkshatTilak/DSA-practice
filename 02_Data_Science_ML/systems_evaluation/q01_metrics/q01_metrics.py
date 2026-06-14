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

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach uses separate list comprehensions to count True Positives, False Positives, and False Negatives.
# While still linear in time, it performs multiple passes over the input lists.
def calculate_metrics_naive(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }

# --- APPROACH 2: Optimal (Single Pass) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach is optimal because it calculates all necessary counts (TP, FP, FN) in a single 
# pass through the data using a loop and zip, minimizing iterator overhead and memory access.
def calculate_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = 0
    fp = 0
    fn = 0

    for true_val, pred_val in zip(y_true, y_pred):
        if true_val == 1:
            if pred_val == 1:
                tp += 1
            else:
                fn += 1
        elif pred_val == 1:
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

import java.util.HashMap;
import java.util.Map;

public class Metrics {
    /**
     * Calculates precision, recall, and F1 score from true labels and predictions.
     * 
     * @param yTrue Actual binary labels.
     * @param yPred Predicted binary labels.
     * @return A map containing the calculated metrics.
     */
    public static Map<String, Double> calculateMetrics(int[] yTrue, int[] yPred) {
        if (yTrue == null || yPred == null || yTrue.length != yPred.length) {
            throw new IllegalArgumentException("Input arrays must be non-null and have the same length.");
        }

        int tp = 0;
        int fp = 0;
        int fn = 0;

        for (int i = 0; i < yTrue.length; i++) {
            if (yTrue[i] == 1) {
                if (yPred[i] == 1) {
                    tp++;
                } else {
                    fn++;
                }
            } else if (yPred[i] == 1) {
                fp++;
            }
        }

        double precision = (tp + fp > 0) ? (double) tp / (tp + fp) : 0.0;
        double recall = (tp + fn > 0) ? (double) tp / (tp + fn) : 0.0;
        double f1 = (precision + recall > 0) ? 2 * (precision * recall) / (precision + recall) : 0.0;

        Map<String, Double> metrics = new HashMap<>();
        metrics.put("precision", precision);
        metrics.put("recall", recall);
        metrics.put("f1", f1);

        return metrics;
    }

    public static void main(String[] args) {
        int[] yTrue = {1, 0, 1, 1, 0, 1};
        int[] yPred = {1, 1, 0, 1, 0, 1};
        System.out.println(calculateMetrics(yTrue, yPred));
    }
}
"""

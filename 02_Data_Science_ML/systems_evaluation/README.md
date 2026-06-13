# Systems Evaluation: Classification Metrics

In Machine Learning systems, evaluation metrics determine how well models perform under varying operational thresholds. Selecting the right metric balances precision (avoiding false alarms) against recall (capturing all relevant events).

---

## 🗺️ Visual Mind-Map & Equations

### The Confusion Matrix
```text
                  Actual Positive      Actual Negative
Predicted Pos       True Pos (TP)       False Pos (FP)  ──> Precision = TP / (TP + FP)
Predicted Neg       False Neg (FN)      True Neg (TN)   ──> Recall    = TP / (TP + FN)
                                                                       
                                                                F1-Score  = 2 * (Prec * Rec) / (Prec + Rec)
```

### Threshold Sensitivity Flow
```text
Threshold ──> High (0.90) ──> Decreases FP ──> Increases Precision ──> Decreases Recall
Threshold ──> Low  (0.10) ──> Decreases FN ──> Increases Recall    ──> Decreases Precision
```

---

## 🏢 Real-World Production Use-Case

### Netflix: Notification Engine Filtering
When Netflix recommends a new movie, it must decide whether to send a high-intrusiveness push notification.
1. The machine learning model outputs a probability that the user will click and watch the recommended title.
2. Sending too many unclicked notifications drives user unsubscribe rates (fatigue). This requires **high Precision**.
3. Under-notifying misses watch-time opportunities. This requires **sufficient Recall**.
4. The notification engine uses threshold tuning based on the **F1-Score** or **ROC-AUC** metrics, calibrating the threshold individually for different user cohorts to optimize notification engagement without causing fatigue.

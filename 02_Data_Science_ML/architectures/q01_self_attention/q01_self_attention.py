"""
Challenge: q01_self_attention
Difficulty: Hard
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Calculate scaled dot-product self-attention weights and final contextual projections.
"""

# --- STARTER TEMPLATE FOR USER ---
import numpy as np

def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Returns (output, attention_weights)
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

def scaled_dot_product_attention_optimal(Q, K, V):
    dk = Q.shape[-1]
    scores = np.dot(Q, K.T) / np.sqrt(dk)
    # Stable Softmax
    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    output = np.dot(attention_weights, V)
    return output, attention_weights

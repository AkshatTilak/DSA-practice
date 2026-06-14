# Scaled Dot-Product Self-Attention

## 🗂️ Concept Card: Self-Attention
**Self-Attention** is the fundamental building block of the **Transformer architecture**, which has revolutionized Natural Language Processing (NLP) and beyond. Unlike previous sequence models (like RNNs or LSTMs) that process tokens sequentially, self-attention allows a model to look at every other token in a sequence simultaneously to determine which ones are most relevant to the current token.

The core objective is to create **contextualized embeddings**. Instead of a word having a static vector (like Word2Vec), self-attention allows the word "bank" to have a different representation in "river bank" versus "investment bank" by attending to the surrounding context.

---

## 📐 Theoretical Foundations & Math

The "Scaled Dot-Product" variant is the specific implementation used in the original *Attention Is All You Need* paper. It relies on three learned linear projections of the input embeddings: **Query (Q)**, **Key (K)**, and **Value (V)**.

### 1. The Analogy
- **Query ($Q$):** "What I am looking for."
- **Key ($K$):** "What I contain/offer."
- **Value ($V$):** "The actual information I provide once matched."

### 2. The Mathematical Formula
The attention mechanism is defined as:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

### 3. Component Breakdown
*   **The Dot Product ($QK^T$):** We compute the dot product between the query of one token and the keys of all tokens. This measures the **similarity** or "alignment" between tokens.
*   **The Scaling Factor ($\frac{1}{\sqrt{d_k}}$):** As the dimension of the keys $d_k$ grows, the magnitude of the dot products increases. This can push the softmax function into regions where gradients are extremely small (vanishing gradients). Dividing by $\sqrt{d_k}$ stabilizes the gradients.
*   **The Softmax:** This converts the raw similarity scores (logits) into a probability distribution (weights) that sum to 1.
*   **The Weighted Sum ($\dots V$):** The final output is a weighted sum of the Value vectors, where the weights are determined by the softmax output.

---

## ⚙️ Step-by-Step Logic

Following the provided optimal implementation, here is the algorithmic flow:

### Step 1: Calculate Similarity (Attention Scores)
We perform a matrix multiplication between $Q$ and the transpose of $K$.
*   **Code:** `scores = np.dot(Q, K.T)`
*   **Result:** A square matrix of size $(n \times n)$ where $n$ is the sequence length. Each element $(i, j)$ represents how much token $i$ attends to token $j$.

### Step 2: Scale the Scores
We divide the scores by the square root of the head dimension $d_k$.
*   **Code:** `scores / np.sqrt(dk)`
*   **Purpose:** To prevent the "saturation" of the softmax function.

### Step 3: Stable Softmax
Computing $\exp(x)$ for large $x$ leads to numerical overflow (NaNs). We use the **Log-Sum-Exp trick** by subtracting the maximum value in each row before exponentiating.
*   **Code:** 
    ```python
    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    ```
*   **Result:** A probability matrix where each row sums to 1.

### Step 4: Contextual Projection
The final representation is the product of the attention weights and the Value matrix.
*   **Code:** `output = np.dot(attention_weights, V)`
*   **Result:** A matrix of size $(n \times d_v)$ where each token's vector is now a mixture of all other tokens' values based on their relevance.

---

## 🚀 Complexity & Training Details

### Computational Complexity
Given a sequence length $n$ and embedding dimension $d$:

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| $QK^T$ | $O(n^2 \cdot d)$ | $O(n^2)$ | Quadratic with sequence length |
| Softmax | $O(n^2)$ | $O(n^2)$ | Applied over the score matrix |
| Weight $\times V$ | $O(n^2 \cdot d)$ | $O(n \cdot d)$ | Final projection |
| **Total** | **$O(n^2 \cdot d)$** | **$O(n^2)$** | This is the "Transformer Bottleneck" |

### Key Hyperparameters
- **$d_k$ (Dimension of Keys/Queries):** Typically $d_{model} / \text{num\_heads}$ in Multi-Head Attention.
- **Sequence Length ($n$):** The maximum number of tokens the model can process in one window.

---

## 🌍 Real-World Applications

1.  **Large Language Models (LLMs):** GPT-4, Llama, and Claude use multi-head self-attention to maintain long-range dependencies across thousands of tokens.
2.  **Machine Translation:** Google Translate uses attention to align words in the source language (e.g., English) with the target language (e.g., French), handling differing word orders.
3.  **Computer Vision (ViT):** Vision Transformers treat images as a sequence of patches, using self-attention to understand global spatial relationships instead of using local convolutions.
4.  **Protein Folding (AlphaFold):** Uses attention mechanisms to determine which amino acids in a sequence are physically close to each other in a 3D folded structure.

## 💻 Final Implementation Reference

```python
import numpy as np

def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes the scaled dot-product attention.
    
    Args:
        Q: Query matrix of shape (seq_len, d_k)
        K: Key matrix of shape (seq_len, d_k)
        V: Value matrix of shape (seq_len, d_v)
        
    Returns:
        output: The contextualized embeddings (seq_len, d_v)
        attention_weights: The softmax weights (seq_len, seq_len)
    """
    dk = Q.shape[-1]
    
    # 1. Compute dot product of Q and K^T
    scores = np.dot(Q, K.T) / np.sqrt(dk)
    
    # 2. Numerically stable softmax
    # Subtract max for numerical stability to avoid overflow in np.exp
    max_scores = np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(scores - max_scores)
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    
    # 3. Compute final weighted sum of values
    output = np.dot(attention_weights, V)
    
    return output, attention_weights
```
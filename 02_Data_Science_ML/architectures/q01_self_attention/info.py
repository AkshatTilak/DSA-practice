INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Calculate scaled dot-product self-attention weights and final contextual projections.',
    'groups': ['Deep Learning', 'Transformers'],
    'starter_code': """import numpy as np

def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Returns (output, attention_weights)
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n * m * (dk + dv))
# Space Complexity: O(n * m)
# This approach avoids using NumPy's optimized matrix multiplication and instead uses nested loops to calculate the dot products and the final projections. It serves as a conceptual implementation of the attention mechanism.
import numpy as np

def scaled_dot_product_attention_naive(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n, dk = Q.shape
    m, dk_k = K.shape
    m_v, dv = V.shape
    
    if dk != dk_k:
        raise ValueError("Dimension of Q and K must match.")
    if m != m_v:
        raise ValueError("Number of keys must match number of values.")

    # 1. Calculate QK^T manually
    scores = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            dot_product = 0
            for k in range(dk):
                dot_product += Q[i, k] * K[j, k]
            scores[i, j] = dot_product / np.sqrt(dk)

    # 2. Softmax manually (row-wise)
    attention_weights = np.zeros((n, m))
    for i in range(n):
        # Numerical stability: subtract max
        row_max = np.max(scores[i, :])
        exp_sum = 0
        row_exp = np.zeros(m)
        for j in range(m):
            row_exp[j] = np.exp(scores[i, j] - row_max)
            exp_sum += row_exp[j]
        for j in range(m):
            attention_weights[i, j] = row_exp[j] / exp_sum

    # 3. Calculate AttentionWeights * V manually
    output = np.zeros((n, dv))
    for i in range(n):
        for j in range(dv):
            val_sum = 0
            for k in range(m):
                val_sum += attention_weights[i, k] * V[k, j]
            output[i, j] = val_sum

    return output, attention_weights

# --- APPROACH 2: Optimal (Vectorized NumPy) ---
# Time Complexity: O(n * m * (dk + dv))
# Space Complexity: O(n * m)
# This approach uses NumPy's highly optimized BLAS-backed matrix multiplication (@ operator) and vectorized operations. It is optimal because it minimizes Python overhead and leverages SIMD instructions for floating-point calculations.
def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # d_k is the dimensionality of the query/key vectors
    dk = Q.shape[-1]
    
    # Step 1: Compute scaled dot-product scores
    # Q: (n, dk), K: (m, dk) -> scores: (n, m)
    # Using np.matmul or @ for efficient matrix multiplication
    scores = (Q @ K.T) / np.sqrt(dk)
    
    # Step 2: Apply softmax to get attention weights
    # For numerical stability, subtract the maximum value in each row
    # softmax(x) = exp(x - max(x)) / sum(exp(x - max(x)))
    # axis=-1 ensures softmax is computed across the key dimension (m)
    max_scores = np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(scores - max_scores)
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    
    # Step 3: Compute final contextual projections
    # weights: (n, m), V: (m, dv) -> output: (n, dv)
    output = attention_weights @ V
    
    return output, attention_weights

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package architectures;

import java.util.Arrays;

public class SelfAttention {

    /**
     * Calculates scaled dot-product attention.
     * 
     * @param Q Query matrix [n][dk]
     * @param K Key matrix [m][dk]
     * @param V Value matrix [m][dv]
     * @return An array containing [outputMatrix, weightsMatrix]
     */
    public static double[][][] scaledDotProductAttention(double[][] Q, double[][] K, double[][] V) {
        int n = Q.length;
        int dk = Q[0].length;
        int m = K.length;
        int dv = V[0].length;

        // 1. Q * K^T / sqrt(dk)
        double[][] scores = new double[n][m];
        double scale = Math.sqrt(dk);
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                double dot = 0;
                for (int k = 0; k < dk; k++) {
                    dot += Q[i][k] * K[j][k];
                }
                scores[i][j] = dot / scale;
            }
        }

        // 2. Softmax (Row-wise)
        double[][] weights = new double[n][m];
        for (int i = 0; i < n; i++) {
            double maxVal = Double.NEGATIVE_INFINITY;
            for (int j = 0; j < m; j++) {
                if (scores[i][j] > maxVal) maxVal = scores[i][j];
            }

            double sumExp = 0;
            for (int j = 0; j < m; j++) {
                weights[i][j] = Math.exp(scores[i][j] - maxVal);
                sumExp += weights[i][j];
            }

            for (int j = 0; j < m; j++) {
                weights[i][j] /= sumExp;
            }
        }

        // 3. Weights * V
        double[][] output = new double[n][dv];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < dv; j++) {
                double sum = 0;
                for (int k = 0; k < m; k++) {
                    sum += weights[i][k] * V[k][j];
                }
                output[i][j] = sum;
            }
        }

        return new double[][][]{output, weights};
    }

    public static void main(String[] args) {
        double[][] Q = {{1.0, 0.0, 1.0}, {0.0, 1.0, 0.0}};
        double[][] K = {{1.0, 0.0, 1.0}, {0.0, 1.0, 0.0}, {1.0, 1.0, 1.0}};
        double[][] V = {{10.0, 0.0}, {0.0, 5.0}, {2.0, 2.0}};

        double[][][] result = scaledDotProductAttention(Q, K, V);
        double[][] output = result[0];
        double[][] weights = result[1];

        System.out.println("Output: " + Arrays.deepToString(output));
        System.out.println("Weights: " + Arrays.deepToString(weights));
    }
}
\"\"\"""",
    'test_code': """def test_attention():
    pass""",
    'readme_content': """# Scaled Dot-Product Self-Attention

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
    \"\"\"
    Computes the scaled dot-product attention.
    
    Args:
        Q: Query matrix of shape (seq_len, d_k)
        K: Key matrix of shape (seq_len, d_k)
        V: Value matrix of shape (seq_len, d_v)
        
    Returns:
        output: The contextualized embeddings (seq_len, d_v)
        attention_weights: The softmax weights (seq_len, seq_len)
    \"\"\"
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
```""",
}

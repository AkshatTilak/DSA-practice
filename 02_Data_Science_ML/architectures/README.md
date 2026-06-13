# Deep Learning Architectures

Deep Learning architectures process complex, high-dimensional data by learning hierarchical representations across neural layers. Primary building blocks include sequential networks (Recurrent Neural Networks - RNNs), spatial filters (Convolutional Neural Networks - CNNs), neighborhood message aggregators (Graph Neural Networks - GNNs), and attention-driven architectures (Transformers).

---

## 🗺️ ASCII Execution Flow: Scaled Dot-Product Attention

Below is the computational pipeline of the core **Self-Attention** mechanism in Transformers, mapping Queries ($Q$), Keys ($K$), and Values ($V$):

```text
Inputs: Q (Query Matrix), K (Key Matrix), V (Value Matrix)

1. Compute dot-product similarity:   [ Q ] x [ K^T ] ──> Raw Scores Matrix
2. Scale scores by dimension size:   Scores / sqrt(d_k)
3. Apply Softmax row-wise:           Softmax(Scaled Scores) ──> Attention Weights
4. Weight Value vectors:             [ Attention Weights ] x [ V ] ──> Output Matrix

Matrix Dimension Flow:
Q: [SeqLen, d_k]  x  K^T: [d_k, SeqLen]  ──>  Scores: [SeqLen, SeqLen]
Softmax(Scores)   x  V:   [SeqLen, d_v]  ──>  Output: [SeqLen, d_v]
```

---

## 📊 Structural Comparison & Complexities

| Architecture | Forward Pass Complexity | Spatial / Temporal Alignment | Primary Application |
| :--- | :--- | :--- | :--- |
| CNN Layer | $O(H \cdot W \cdot K^2 \cdot C_{in} \cdot C_{out})$ | Grid-bound local translation | Image Classification, OCR |
| RNN Step | $O(SeqLen \cdot D^2)$ | Sequential causal ordering | Time-Series Forecasting |
| Transformer | $O(SeqLen^2 \cdot D + SeqLen \cdot D^2)$ | Global position-agnostic token correlation | Language Generation, Code Completion |

---

## 🏢 Real-World Production Use-Case

### AI Engineering: Large Language Models Text Generation
Systems like chat applications and search assistants generate context-appropriate text answers.
1. The user input prompt is converted to dense vector embeddings.
2. The model routes tokens through multiple **Transformer blocks**, utilizing **Self-Attention** layers to let tokens attend to the entire prefix history.
3. This attention mechanism allows the system to resolve pronoun referents and capture complex logical dependencies across long spans of text.
4. The final softmax layer selects the highest probability next token, updating the generation cache incrementally.
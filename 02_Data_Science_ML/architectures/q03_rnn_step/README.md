# RNN Step: Recurrent State Update

## 1. Overview & Concept Card

The **RNN Step** refers to the fundamental computational unit of a Recurrent Neural Network (RNN). Unlike traditional feedforward neural networks that process inputs independently, RNNs are designed to handle **sequential data** (time series, text, audio) by maintaining a "memory" of previous inputs.

The core objective of the RNN step is to update the **hidden state** ($h_t$) based on the current input ($x_t$) and the previous hidden state ($h_{t-1}$). This hidden state acts as a compressed representation of all information seen by the network up to time $t$, allowing the model to capture temporal dependencies and patterns over time.

### Core Concept Summary
| Feature | Description |
| :--- | :--- |
| **Input** | Current sequence element $x_t$ and previous state $h_{t-1}$. |
| **Output** | Updated hidden state $h_t$ (and optionally a prediction $y_t$). |
| **Memory** | The hidden state $h$ is the mechanism for "remembering" the past. |
| **Architecture** | A looped structure where the output of one step is fed back as input to the next. |

---

## 2. Theoretical Foundations & Math

The recurrent step is defined by a specific mathematical transformation. To compute the state at time $t$, the network performs a linear combination of the current input and the previous state, adds a bias term, and passes the result through a non-linear activation function.

### The State Update Equation
The standard mathematical formulation for a single RNN step is:

$$h_t = \sigma(W_{xh} x_t + W_{hh} h_{t-1} + b_h)$$

**Where:**
*   $x_t \in \mathbb{R}^{d}$ : The input vector at time step $t$ (dimension $d$).
*   $h_{t-1} \in \mathbb{R}^{h}$ : The hidden state from the previous time step (dimension $h$).
*   $W_{xh} \in \mathbb{R}^{h \times d}$ : The **Input-to-Hidden** weight matrix. It transforms the input into the hidden space.
*   $W_{hh} \in \mathbb{R}^{h \times h}$ : The **Hidden-to-Hidden** (recurrent) weight matrix. It defines how the previous memory influences the current state.
*   $b_h \in \mathbb{R}^{h}$ : The bias vector.
*   $\sigma$ : A non-linear activation function, most commonly $\tanh$ (hyperbolic tangent) or $\text{ReLU}$.

### Why $\tanh$?
The $\tanh$ function is typically used because its output range is $(-1, 1)$, which helps regulate the values flowing through the network over many time steps. Without a squashing function, the hidden state values could grow exponentially (explode) or shrink to zero (vanish) during repeated matrix multiplications.

---

## 3. Step-by-Step Logic

To implement the RNN step programmatically, we follow a strict sequence of linear algebra operations.

### Algorithmic Flow
1.  **Linear Projection of Input**: Multiply the current input vector $x_t$ by the weight matrix $W_{xh}$. This maps the raw input into the latent feature space of the hidden state.
2.  **Linear Projection of State**: Multiply the previous hidden state $h_{t-1}$ by the recurrent weight matrix $W_{hh}$. This extracts relevant information from the "memory."
3.  **Aggregation**: Sum the results of the two projections and add the bias vector $b_h$.
4.  **Non-Linear Activation**: Pass the summed vector through $\tanh$ to produce the final updated hidden state $h_t$.

### Implementation
Below is the optimal implementation using `numpy` to simulate one step of a recurrent cell.

```python
import numpy as np

def solve_optimal(x_t, h_prev, W_xh, W_hh, b_h):
    """
    Performs a single RNN step state update.
    
    Args:
        x_t (np.ndarray): Input vector at time t (shape: input_dim,)
        h_prev (np.ndarray): Hidden state from time t-1 (shape: hidden_dim,)
        W_xh (np.ndarray): Weight matrix for input (shape: hidden_dim, input_dim)
        W_hh (np.ndarray): Weight matrix for recurrent state (shape: hidden_dim, hidden_dim)
        b_h (np.ndarray): Bias vector (shape: hidden_dim,)
        
    Returns:
        np.ndarray: The updated hidden state h_t
    """
    # 1. Compute the contribution of the current input: W_xh * x_t
    input_contribution = np.dot(W_xh, x_t)
    
    # 2. Compute the contribution of the previous state: W_hh * h_prev
    recurrent_contribution = np.dot(W_hh, h_prev)
    
    # 3. Sum contributions and add bias
    z = input_contribution + recurrent_contribution + b_h
    
    # 4. Apply non-linear activation function (tanh)
    h_t = np.tanh(z)
    
    return h_t

# Example Usage
if __name__ == "__main__":
    # Dimensions
    input_dim = 3
    hidden_dim = 5
    
    # Random initialization
    x_t = np.random.randn(input_dim)
    h_prev = np.zeros(hidden_dim) # Initial state is usually zeros
    W_xh = np.random.randn(hidden_dim, input_dim)
    W_hh = np.random.randn(hidden_dim, hidden_dim)
    b_h = np.zeros(hidden_dim)
    
    h_t = solve_optimal(x_t, h_prev, W_xh, W_hh, b_h)
    print(f"Updated Hidden State h_t:\n{h_t}")
```

---

## 4. Complexity & Training Details

### Computational Complexity
The complexity of a single RNN step is dominated by matrix-vector multiplications.

| Operation | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| $W_{xh} x_t$ | $O(h \cdot d)$ | $O(h \cdot d)$ for weights |
| $W_{hh} h_{t-1}$ | $O(h^2)$ | $O(h^2)$ for weights |
| $\tanh$ activation | $O(h)$ | $O(h)$ |
| **Total (per step)** | **$O(h^2 + hd)$** | **$O(h^2 + hd)$** |

*Where $h$ is the hidden dimension and $d$ is the input dimension.*

### Training Challenges
While the forward step is simple, training RNNs via **Backpropagation Through Time (BPTT)** introduces two major issues:
1.  **Vanishing Gradients**: As the gradient is propagated back through many steps, the repeated multiplication by $W_{hh}$ (if eigenvalues $< 1$) causes the gradient to decay exponentially, preventing the model from learning long-term dependencies.
2.  **Exploding Gradients**: If the eigenvalues of $W_{hh}$ are $> 1$, the gradients can grow exponentially. This is typically mitigated using **Gradient Clipping**.

---

## 5. Real-World Applications

The recurrent step is the "atomic" operation for several higher-level sequence architectures:

*   **Sentiment Analysis**: An RNN processes a sentence word-by-word. The final hidden state $h_T$ serves as a summary of the entire sentence, which is then passed to a softmax layer to predict "Positive" or "Negative."
*   **Time-Series Forecasting**: In stock price or weather prediction, the RNN step updates the state based on the current measurement and the trend established in previous steps.
*   **Language Modeling**: Predicting the next character or word in a sequence. The hidden state tracks the grammatical context of the sentence.
*   **Foundation for Advanced Cells**: The basic RNN step's limitations led to the development of **LSTM (Long Short-Term Memory)** and **GRU (Gated Recurrent Units)**, which replace the simple $\tanh$ update with "gates" to better control what information is forgotten or remembered.
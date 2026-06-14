"""
Challenge: q03_rnn_step
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Recurrent step state update.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
    # Time Complexity: O(H*I + H^2)
    # Space Complexity: O(H)
    # [Explanation]
    def solve_naive(...):

    # --- APPROACH 2: Optimal (Vectorized NumPy) ---
    # Time Complexity: O(H*I + H^2)
    # Space Complexity: O(H)
    # [Explanation]
    def solve_optimal(...):

    # --- APPROACH 3: Secondary Language (Java Variant) ---
    """ ... """

    I will define $H$ as hidden size and $I$ as input size in the explanation.

    Wait, just double-checking if there are any other RNN variants. The "recurrent step state update" is the most fundamental one. LSTMs or GRUs have multiple gates and are much more complex. Usually, "rnn_step" refers to the basic RNN cell.

    For the naive Python approach, I'll avoid using `sum()` with a generator if I want it to be absolutely "naive", but `sum()` is standard Python. I'll use a basic loop to be safe.

    ```python
    def solve_naive(x, h_prev, W_xh, W_hh, b, activation):
        h_size = len(W_xh)
        i_size = len(x)
        h_next = [0.0] * h_size
        for i in range(h_size):
            acc = 0.0
            for j in range(i_size):
                acc += W_xh[i][j] * x[j]
            for j in range(h_size):
                acc += W_hh[i][j] * h_prev[j]
            h_next[i] = activation(acc + b[i])
        return h_next
    ```

    Check if `activation` should be applied to the vector in `solve_optimal`.
    If `activation` is `np.tanh`, `np.tanh(z)` works on the array.
    If `activation` is `lambda x: 1/(1+math.exp(-x))`, it fails.
    To make it truly production-grade, I should probably ensure `activation` is applied element-wise.
    Actually, in most ML frameworks, activations are designed to be vectorized. I'll leave it as `activation(z)`. If the user wants to use a non-vectorized function, they can wrap it.

    Final check on Java:
    The `DoubleUnaryOperator` is available since Java 8. It's perfect for the `activation` function.# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(H * I + H^2)
# Space Complexity: O(H)
# This approach implements the RNN state update using nested loops to perform matrix-vector multiplication. 
# H is the hidden state dimension and I is the input vector dimension.
def solve_naive(x, h_prev, W_xh, W_hh, b, activation):
    """
    Computes the next hidden state of a basic RNN cell.
    x: Input vector (list)
    h_prev: Previous hidden state vector (list)
    W_xh: Input-to-hidden weight matrix (list of lists)
    W_hh: Hidden-to-hidden weight matrix (list of lists)
    b: Bias vector (list)
    activation: Activation function (callable)
    """
    hidden_size = len(W_xh)
    input_size = len(x)
    h_next = [0.0] * hidden_size
    
    for i in range(hidden_size):
        # Compute W_xh * x
        sum_x = 0.0
        for j in range(input_size):
            sum_x += W_xh[i][j] * x[j]
        
        # Compute W_hh * h_prev
        sum_h = 0.0
        for j in range(hidden_size):
            sum_h += W_hh[i][j] * h_prev[j]
        
        # Final update: h_t = activation(W_xh*x + W_hh*h_{t-1} + b)
        h_next[i] = activation(sum_x + sum_h + b[i])
        
    return h_next

# --- APPROACH 2: Optimal (Vectorized NumPy) ---
# Time Complexity: O(H * I + H^2)
# Space Complexity: O(H)
# This approach utilizes NumPy's vectorized operations (BLAS), which are highly optimized 
# for matrix-vector multiplication. While the theoretical time complexity is the same as 
# the naive approach, the constant factors are significantly lower due to SIMD 
# instructions and efficient memory access patterns.
import numpy as np

def solve_optimal(x, h_prev, W_xh, W_hh, b, activation):
    """
    Computes the next hidden state of a basic RNN cell using vectorized operations.
    x: Input vector (array-like)
    h_prev: Previous hidden state vector (array-like)
    W_xh: Input-to-hidden weight matrix (array-like)
    W_hh: Hidden-to-hidden weight matrix (array-like)
    b: Bias vector (array-like)
    activation: Vectorized activation function (callable, e.g., np.tanh)
    """
    # Ensure inputs are numpy arrays for vectorized computation
    x = np.asarray(x)
    h_prev = np.asarray(h_prev)
    W_xh = np.asarray(W_xh)
    W_hh = np.asarray(W_hh)
    b = np.asarray(b)
    
    # Linear transformation: z = W_xh * x + W_hh * h_prev + b
    # Using the @ operator for matrix-vector multiplication
    z = W_xh @ x + W_hh @ h_prev + b
    
    # Apply the activation function element-wise
    return activation(z)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package architectures;

import java.util.function.DoubleUnaryOperator;

/**
 * RnnStep provides the implementation for a single step state update of a 
 * recurrent neural network cell.
 */
public class RnnStep {

    /**
     * Computes the next hidden state of a basic RNN cell.
     *
     * @param x          The input vector at time t.
     * @param hPrev      The hidden state vector from time t-1.
     * @param Wxh        The weight matrix for the input-to-hidden connection.
     * @param Whh        The weight matrix for the hidden-to-hidden connection.
     * @param b          The bias vector.
     * @param activation The activation function (e.g., Math::tanh).
     * @return           The updated hidden state vector at time t.
     */
    public static double[] solve(double[] x, double[] hPrev, double[][] Wxh, 
                                 double[][] Whh, double[] b, DoubleUnaryOperator activation) {
        int hiddenSize = Wxh.length;
        int inputSize = x.length;
        double[] hNext = new double[hiddenSize];

        for (int i = 0; i < hiddenSize; i++) {
            double sum = 0.0;

            // Dot product of i-th row of Wxh and x
            for (int j = 0; j < inputSize; j++) {
                sum += Wxh[i][j] * x[j];
            }

            // Dot product of i-th row of Whh and hPrev
            for (int j = 0; j < hiddenSize; j++) {
                sum += Whh[i][j] * hPrev[j];
            }

            // Add bias and apply the activation function
            hNext[i] = activation.applyAsDouble(sum + b[i]);
        }

        return hNext;
    }

    public static void main(String[] args) {
        // Example usage
        double[] x = {1.0, 0.5};
        double[] hPrev = {0.1, -0.2};
        double[][] Wxh = {{0.1, 0.2}, {0.3, 0.4}};
        double[][] Whh = {{0.5, 0.6}, {0.7, 0.8}};
        double[] b = {0.1, 0.1};
        
        double[] result = solve(x, hPrev, Wxh, Whh, b, Math::tanh);
        
        for (double val : result) {
            System.out.println(val);
        }
    }
}
"""

"""
Challenge: q02_cnn_layer
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Forward pass CNN filter convolution.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(H * W * kH * kW)
# Space Complexity: O((H - kH + 1) * (W - kW + 1))
# This approach uses four nested loops to perform the 2D convolution (specifically, cross-correlation as is standard in CNNs). 
# It iterates through every possible top-left corner of the image where the filter can fit, 
# and for each position, it computes the dot product of the filter and the local image window.
def solve_naive(image, kernel):
    if not image or not image[0] or not kernel or not kernel[0]:
        return []

    h, w = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])
    
    # Calculate output dimensions for 'valid' convolution (no padding, stride 1)
    oh = h - kh + 1
    ow = w - kw + 1
    
    if oh <= 0 or ow <= 0:
        return []

    # Initialize output matrix with zeros
    output = [[0.0 for _ in range(ow)] for _ in range(oh)]
    
    for i in range(oh):
        for j in range(ow):
            # Compute the sum of element-wise multiplications for the current window
            current_sum = 0.0
            for m in range(kh):
                for n in range(kw):
                    current_sum += image[i + m][j + n] * kernel[m][n]
            output[i][j] = current_sum
            
    return output

# --- APPROACH 2: Optimal (NumPy Vectorization) ---
# Time Complexity: O(H * W * kH * kW)
# Space Complexity: O((H - kH + 1) * (W - kW + 1))
# While the asymptotic time complexity remains the same, this approach is optimal in Python 
# because it leverages NumPy's vectorized array operations. By using slicing and the `np.sum` 
# function, we push the innermost loops into highly optimized C/Fortran code, 
# significantly reducing the Python interpreter overhead.
import numpy as np

def solve_optimal(image, kernel):
    if not image or not image[0] or not kernel or not kernel[0]:
        return []

    # Convert inputs to numpy arrays for vectorized operations
    img = np.array(image, dtype=float)
    ker = np.array(kernel, dtype=float)
    
    h, w = img.shape
    kh, kw = ker.shape
    
    oh = h - kh + 1
    ow = w - kw + 1
    
    if oh <= 0 or ow <= 0:
        return []
    
    # Initialize output array
    out = np.zeros((oh, ow))
    
    # Iterate over the output dimensions and use NumPy slicing for the window operation
    for i in range(oh):
        for j in range(ow):
            # Extract the window and perform element-wise multiplication and summation
            out[i, j] = np.sum(img[i : i + kh, j : j + kw] * ker)
            
    return out.tolist()

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package architectures;

import java.util.ArrayList;
import java.util.List;

public class CnnLayer {
    /**
     * Performs the forward pass of a CNN convolution layer.
     * 
     * @param image  The input 2D image matrix.
     * @param kernel The 2D filter kernel.
     * @return The resulting 2D feature map after convolution.
     */
    public double[][] solve(double[][] image, double[][] kernel) {
        if (image == null || image.length == 0 || image[0].length == 0 || 
            kernel == null || kernel.length == 0 || kernel[0].length == 0) {
            return new double[0][0];
        }

        int h = image.length;
        int w = image[0].length;
        int kh = kernel.length;
        int kw = kernel[0].length;

        int oh = h - kh + 1;
        int ow = w - kw + 1;

        if (oh <= 0 || ow <= 0) {
            return new double[0][0];
        }

        double[][] output = new double[oh][ow];

        for (int i = 0; i < oh; i++) {
            for (int j = 0; j < ow; j++) {
                double sum = 0.0;
                for (int m = 0; m < kh; m++) {
                    for (int n = 0; n < kw; n++) {
                        sum += image[i + m][j + n] * kernel[m][n];
                    }
                }
                output[i][j] = sum;
            }
        }

        return output;
    }

    public static void main(String[] args) {
        CnnLayer cnn = new CnnLayer();
        double[][] image = {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9}
        };
        double[][] kernel = {
            {1, 0},
            {0, -1}
        };
        double[][] result = cnn.solve(image, kernel);
        // Expected output: [[1-5, 2-6], [4-8, 5-9]] = [[-4, -4], [-4, -4]]
        for (double[] row : result) {
            for (double val : row) {
                System.out.print(val + " ");
            }
            System.out.println();
        }
    }
}
"""

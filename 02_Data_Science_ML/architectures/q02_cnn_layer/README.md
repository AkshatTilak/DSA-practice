# CNN Layer: Forward Pass Convolution

## 🌟 Overview & Concept Card

At its core, a **Convolutional Neural Network (CNN) Layer** is designed to automatically and adaptively learn spatial hierarchies of features from input data (typically images). Unlike a fully connected layer that treats an image as a flat vector—destroying the spatial relationship between pixels—the CNN layer uses a **sliding window (filter/kernel)** to maintain local connectivity and translation invariance.

### Core Objective
The primary goal of the forward pass in a CNN layer is to produce **feature maps**. A feature map is a processed version of the input that highlights specific characteristics (such as edges, textures, or complex shapes) depending on the weights of the filters.

**Key Terminology:**
- **Kernel/Filter**: A small matrix of weights that slides across the input to detect specific patterns.
- **Stride**: The number of pixels the filter shifts at each step.
- **Padding**: Adding zeros around the border of the input to control the spatial size of the output.
- **Channel**: The depth of the input (e.g., RGB images have 3 channels).

---

## 📐 Theoretical Foundations & Math

### 1. Output Dimension Calculation
The size of the output feature map is determined by the input size, padding, kernel size, and stride. For a single dimension (height or width), the formula is:

$$O = \lfloor \frac{I + 2P - K}{S} \rfloor + 1$$

Where:
- $O$: Output dimension
- $I$: Input dimension
- $P$: Padding
- $K$: Kernel size
- $S$: Stride

### 2. The Convolution Operation (Cross-Correlation)
In deep learning, what is called "convolution" is technically **cross-correlation**. For a single output pixel at position $(i, j)$ in the $k$-th feature map, the value is calculated as the sum of element-wise multiplications between the filter and the local input window:

$$Y_{i,j,k} = \sum_{c=0}^{C_{in}-1} \sum_{m=0}^{K_h-1} \sum_{n=0}^{K_w-1} (X_{i \cdot S + m, j \cdot S + n, c} \cdot W_{m, n, c, k}) + b_k$$

**Variable Definitions:**
- $X$: Input tensor of shape $(H, W, C_{in})$
- $W$: Filter tensor of shape $(K_h, K_w, C_{in}, C_{out})$
- $b$: Bias vector of shape $(C_{out})$
- $Y$: Output tensor of shape $(H_{out}, W_{out}, C_{out})$
- $C_{in}/C_{out}$: Number of input and output channels.

---

## 🛠️ Step-by-Step Logic

To implement the forward pass of a CNN layer, follow these algorithmic steps:

1. **Padding Application**: If $P > 0$, wrap the input tensor with zeros to ensure the filter can center on edge pixels.
2. **Output Initialization**: Calculate the output dimensions $(H_{out}, W_{out})$ and create a zero-initialized tensor of shape $(H_{out}, W_{out}, C_{out})$.
3. **Sliding Window Iteration**:
   - Loop through each output channel $k \in [0, C_{out}-1]$.
   - Loop through the output height $i$ and width $j$.
   - Define the current window in the input tensor: 
     - Start row: $i \times S$
     - End row: $(i \times S) + K_h$
     - Start col: $j \times S$
     - End col: $(j \times S) + K_w$
4. **Dot Product & Summation**:
   - Extract the $K_h \times K_w \times C_{in}$ slice of the input.
   - Perform element-wise multiplication with the corresponding filter $W_k$.
   - Sum all values across height, width, and input channels.
5. **Bias Addition**: Add the bias $b_k$ to the resulting sum to get the final scalar value for $Y_{i,j,k}$.

### Implementation

```python
import numpy as np

def solve(input_tensor, filters, bias, stride=1, padding=0):
    """
    Performs the forward pass of a CNN convolution layer.
    
    Args:
        input_tensor: np.array of shape (H, W, C_in)
        filters: np.array of shape (K_h, K_w, C_in, C_out)
        bias: np.array of shape (C_out,)
        stride: int
        padding: int
        
    Returns:
        output: np.array of shape (H_out, W_out, C_out)
    """
    # 1. Extract dimensions
    h_in, w_in, c_in = input_tensor.shape
    kh, kw, _, c_out = filters.shape
    
    # 2. Apply Padding
    if padding > 0:
        padded_input = np.pad(input_tensor, 
                              ((padding, padding), (padding, padding), (0, 0)), 
                              mode='constant')
    else:
        padded_input = input_tensor
        
    # 3. Calculate output dimensions
    h_out = (h_in + 2 * padding - kh) // stride + 1
    w_out = (w_in + 2 * padding - kw) // stride + 1
    
    # Initialize output tensor
    output = np.zeros((h_out, w_out, c_out))
    
    # 4. Convolution Process
    for k in range(c_out):
        for i in range(h_out):
            for j in range(w_out):
                # Define the window slicing boundaries
                h_start = i * stride
                h_end = h_start + kh
                w_start = j * stride
                w_end = w_start + kw
                
                # Extract slice: shape (kh, kw, c_in)
                window = padded_input[h_start:h_end, w_start:w_end, :]
                
                # Element-wise multiply and sum + bias
                # filters[:, :, :, k] has shape (kh, kw, c_in)
                output[i, j, k] = np.sum(window * filters[:, :, :, k]) + bias[k]
                
    return output
```

---

## 📈 Complexity & Training Details

### Computational Complexity

| Phase | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Forward Pass** | $O(C_{out} \cdot H_{out} \cdot W_{out} \cdot C_{in} \cdot K_h \cdot K_w)$ | $O(H_{out} \cdot W_{out} \cdot C_{out})$ | The most expensive part is the 6-nested loop (effectively). |
| **Inference** | Same as Forward Pass | $O(\text{Weights} + \text{Activations})$ | Weights are fixed during inference. |

### Key Hyperparameters
- **Kernel Size**: Smaller kernels (e.g., $3 \times 3$) are preferred to capture fine-grained features and reduce parameters.
- **Stride**: Higher stride reduces the output resolution (downsampling).
- **Padding**: "Same" padding ensures output size equals input size (when $S=1$).

---

## 🌍 Real-World Applications

1. **Image Classification**: In architectures like **ResNet** or **VGG**, convolution layers extract features (edges $\rightarrow$ textures $\rightarrow$ objects) to classify an image into a category.
2. **Object Detection**: Frameworks like **YOLO (You Only Look Once)** use convolutions to predict bounding boxes and class probabilities simultaneously across a grid.
3. **Medical Imaging**: CNNs are used to detect tumors in MRI scans or anomalies in X-rays by identifying localized spatial patterns that differ from healthy tissue.
4. **Autonomous Driving**: Used in real-time segmentation to distinguish between the road, pedestrians, and other vehicles.
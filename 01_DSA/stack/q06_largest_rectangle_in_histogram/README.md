# Largest Rectangle in Histogram

## 1. Overview & Problem Explanation

The **Largest Rectangle in Histogram** problem asks us to find the area of the largest rectangle that can be formed within a histogram. The histogram is represented as an array of integers where each element denotes the height of a bar, and each bar has a fixed width of **1**.

### The Problem Statement
Given an array of integers `heights`, we need to identify a contiguous range of bars such that the rectangle formed by the minimum height in that range multiplied by the width of the range is maximized.

**Example:**
- **Input:** `heights = [2, 1, 5, 6, 2, 3]`
- **Output:** `10`
- **Explanation:** The largest rectangle is formed by the bars at indices 2 and 3 (heights 5 and 6). The limiting height is `min(5, 6) = 5`. The width is `2`. Area = $5 \times 2 = 10$.

### Constraints & Edge Cases
- **Empty Input:** If `heights` is empty, the area is `0`.
- **Single Element:** The area is simply the height of that single bar.
- **Sorted Heights (Increasing):** The area grows as we move right; the "limiting" bars are handled at the very end.
- **Sorted Heights (Decreasing):** Each new bar triggers a calculation for the previous bar.
- **Uniform Heights:** The area is `height * len(heights)`.
- **Zero Heights:** Bars with height `0` act as boundaries that reset the possible width.

---

## 2. Core Concepts & Data Structures

### The Monotonic Stack
The optimal solution utilizes a **Monotonic Increasing Stack**. A monotonic stack is a stack where elements are always kept in a specific order (in this case, increasing).

#### Why a Monotonic Stack?
To calculate the area of a rectangle using a specific bar $i$ as the **shortest bar** (the height), we need to find two boundaries:
1. **Left Boundary:** The first bar to the left of $i$ that is shorter than `heights[i]`.
2. **Right Boundary:** The first bar to the right of $i$ that is shorter than `heights[i]`.

The width of the rectangle would then be: `(right_index - left_index - 1)`.

A monotonic stack allows us to find these boundaries in a single pass. When we encounter a bar that is **shorter** than the bar at the top of the stack, it means we have found the **right boundary** for the bar at the top. The element currently below it in the stack is its **left boundary**.

---

## 3. Step-by-Step Logic

### Brute Force Approach ($O(N^2)$)
1. Iterate through every possible pair of indices $(i, j)$.
2. For each pair, find the minimum height between index $i$ and $j$.
3. Calculate `area = min_height * (j - i + 1)`.
4. Keep track of the maximum area found.
*This is inefficient for large inputs.*

### Optimal Approach: Monotonic Stack ($O(N)$)

#### The Algorithm
1. **Initialize** an empty stack to store indices and a variable `max_area = 0`.
2. **Append a dummy zero** to the end of the `heights` list. This ensures that at the end of the iteration, all remaining bars in the stack are popped and processed.
3. **Iterate** through the `heights` array using index `i`:
   - While the stack is not empty AND the current height `heights[i]` is **less than** the height of the bar at the stack's top index:
     - **Pop** the top index from the stack; let this be `h_index`. This bar is the "height" of the rectangle we are currently calculating.
     - **Determine the width**:
       - The **right boundary** is the current index `i`.
       - The **left boundary** is the new top of the stack (if the stack is empty, the left boundary is effectively `-1`).
       - `width = i - stack[-1] - 1` (or `i` if stack is empty).
     - **Update** `max_area = max(max_area, heights[h_index] * width)`.
   - **Push** the current index `i` onto the stack.
4. **Return** `max_area`.

#### Dry Run Example: `heights = [2, 1, 5, 6, 2, 3]`
(Adding dummy 0 $\rightarrow$ `[2, 1, 5, 6, 2, 3, 0]`)

| Index `i` | Height | Action | Stack | Calculation | Max Area |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | 2 | Push 0 | `[0]` | - | 0 |
| 1 | 1 | Pop 0 | `[]` | $h=2, w=1- (-1)-1 = 1 \rightarrow 2$ | 2 |
| 1 | 1 | Push 1 | `[1]` | - | 2 |
| 2 | 5 | Push 2 | `[1, 2]` | - | 2 |
| 3 | 6 | Push 3 | `[1, 2, 3]` | - | 2 |
| 4 | 2 | Pop 3 | `[1, 2]` | $h=6, w=4-2-1 = 1 \rightarrow 6$ | 6 |
| 4 | 2 | Pop 2 | `[1]` | $h=5, w=4-1-1 = 2 \rightarrow 10$ | 10 |
| 4 | 2 | Push 4 | `[1, 4]` | - | 10 |
| 5 | 3 | Push 5 | `[1, 4, 5]` | - | 10 |
| 6 | 0 | Pop 5 | `[1, 4]` | $h=3, w=6-4-1 = 1 \rightarrow 3$ | 10 |
| 6 | 0 | Pop 4 | `[1]` | $h=2, w=6-1-1 = 4 \rightarrow 8$ | 10 |
| 6 | 0 | Pop 1 | `[]` | $h=1, w=6- (-1)-1 = 6 \rightarrow 6$ | 10 |

---

## 4. Implementation

```python
def largest_rectangle_area(heights: list[int]) -> int:
    """
    Finds the area of the largest rectangle in a histogram using a 
    monotonic increasing stack.
    """
    # Adding a zero height at the end to flush out all remaining elements in the stack
    heights.append(0)
    stack = [] # Stores indices
    max_area = 0
    
    for i in range(len(heights)):
        # While current height is smaller than the height at the top of the stack,
        # we have found the right boundary for the bar at stack[-1].
        while stack and heights[i] < heights[stack[-1]]:
            h_index = stack.pop()
            h = heights[h_index]
            
            # The left boundary is the index of the element now at the top of the stack.
            # If the stack is empty, the bar at h_index was the shortest seen so far.
            width = i if not stack else i - stack[-1] - 1
            
            max_area = max(max_area, h * width)
            
        stack.append(i)
    
    # Restore heights list to original state (optional, but good practice)
    heights.pop()
    
    return max_area
```

---

## 5. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(N^2)$ | $O(1)$ | Checks every pair of indices; no extra space. |
| **Monotonic Stack** | $O(N)$ | $O(N)$ | Each element is pushed and popped from the stack exactly once. Stack space grows linearly with $N$. |

---

## 6. Real-World Applications

The "Largest Rectangle in Histogram" pattern (and the Monotonic Stack in general) is widely used in systems engineering:

1. **Image Processing & Computer Vision:** Used in algorithms that detect the largest contiguous block of a certain color or intensity in a binary image (e.g., identifying the largest rectangular object in a scan).
2. **UI Layout Engines:** When calculating how to distribute dynamic space in a grid or flexible layout where elements have varying minimum/maximum heights.
3. **Data Visualization:** Tools that automatically calculate bounding boxes for chart elements or tooltips in complex data histograms.
4. **Resource Scheduling:** In some OS scheduling or memory allocation problems, finding the largest contiguous "block" of available time or space across multiple resources.
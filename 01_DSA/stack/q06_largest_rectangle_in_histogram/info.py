INFO = {
    'difficulty': 'Hard',
    'link': 'https://leetcode.com/problems/largest-rectangle-in-histogram/',
    'description': 'Find the area of largest rectangle in histogram.',
    'groups': ['Array', 'Stack & Queue'],
    'starter_code': """def largest_rectangle_area(heights: list[int]) -> int:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2)
# Space Complexity: O(1)
# For every bar, we treat it as the minimum height of a potential rectangle and 
# expand outwards to the left and right as long as the adjacent bars are 
# greater than or equal to the current bar's height.
def largest_rectangle_area_naive(heights: list[int]) -> int:
    if not heights:
        return 0
    
    max_area = 0
    n = len(heights)
    
    for i in range(n):
        # Current bar is the shortest bar in the rectangle
        min_h = heights[i]
        
        # Expand to the left
        left = i
        while left > 0 and heights[left - 1] >= min_h:
            left -= 1
            
        # Expand to the right
        right = i
        while right < n - 1 and heights[right + 1] >= min_h:
            right += 1
            
        width = right - left + 1
        max_area = max(max_area, width * min_h)
        
    return max_area

# --- APPROACH 2: Optimal (Monotonic Stack) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# The optimal approach uses a monotonic increasing stack to keep track of indices of heights.
# When we encounter a height smaller than the top of the stack, we know the rectangle 
# rooted at the top index cannot extend further right. We pop it and calculate the area 
# using the current index as the right boundary and the index below it in the stack 
# as the left boundary. This ensures each element is pushed and popped exactly once.
def largest_rectangle_area_optimal(heights: list[int]) -> int:
    if not heights:
        return 0
    
    stack = [] # Stores indices
    max_area = 0
    # Append a 0 height to the end to ensure all remaining elements in the stack 
    # are processed at the end of the loop.
    heights_extended = heights + [0]
    
    for i, h in enumerate(heights_extended):
        # Maintain a monotonic increasing stack
        while stack and heights_extended[stack[-1]] >= h:
            # The bar at stack[-1] is the height of the rectangle
            height = heights_extended[stack.pop()]
            # The width is determined by the current index i (right boundary)
            # and the new top of the stack (left boundary)
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        
        stack.append(i)
        
    return max_area

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package stack;

import java.util.Stack;

public class LargestRectangleInHistogram {
    /**
     * Calculates the area of the largest rectangle in a histogram.
     * Time Complexity: O(N)
     * Space Complexity: O(N)
     */
    public int largestRectangleArea(int[] heights) {
        if (heights == null || heights.length == 0) {
            return 0;
        }

        Stack<Integer> stack = new Stack<>();
        int maxArea = 0;
        int n = heights.length;

        for (int i = 0; i <= n; i++) {
            // Use 0 as the height for the virtual element at index n to clear the stack
            int currentHeight = (i == n) ? 0 : heights[i];

            while (!stack.isEmpty() && heights[stack.peek()] >= currentHeight) {
                int h = heights[stack.pop()];
                int width = stack.isEmpty() ? i : i - stack.peek() - 1;
                maxArea = Math.max(maxArea, h * width);
            }
            stack.push(i);
        }

        return maxArea;
    }

    public static void main(String[] args) {
        LargestRectangleInHistogram solver = new LargestRectangleInHistogram();
        int[] test1 = {2, 1, 5, 6, 2, 3};
        System.out.println("Test 1: " + solver.largestRectangleArea(test1)); // Expected: 10
        
        int[] test2 = {2, 4};
        System.out.println("Test 2: " + solver.largestRectangleArea(test2)); // Expected: 4
    }
}
\"\"\"

# To maintain consistency with the starter code's required function name:
def largest_rectangle_area(heights: list[int]) -> int:
    return largest_rectangle_area_optimal(heights)""",
    'test_code': """def test_histogram():
    assert largest_rectangle_area([2,1,5,6,2,3]) == 10""",
    'readme_content': """# Largest Rectangle in Histogram

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
    \"\"\"
    Finds the area of the largest rectangle in a histogram using a 
    monotonic increasing stack.
    \"\"\"
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
4. **Resource Scheduling:** In some OS scheduling or memory allocation problems, finding the largest contiguous "block" of available time or space across multiple resources.""",
}

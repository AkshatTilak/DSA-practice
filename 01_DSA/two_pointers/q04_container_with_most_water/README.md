# Container With Most Water

## 📌 Overview & Problem Explanation

The **Container With Most Water** problem asks us to find two vertical lines on a 2D plane that, together with the x-axis, form a container that holds the maximum amount of water.

### The Problem Statement
Given an integer array `height` of length $n$, there are $n$ vertical lines drawn such that the two endpoints of the $i^{th}$ line are $(i, 0)$ and $(i, height[i])$. You need to find two lines that together with the x-axis form a container, such that the container contains the most water.

### Mathematical Intuition
The amount of water a container can hold is determined by the **Area of a Rectangle**. The formula for the area is:
$$\text{Area} = \text{width} \times \text{height}$$

In this specific problem:
- **Width**: The distance between the two indices $i$ and $j$, calculated as $(j - i)$.
- **Height**: The water level is limited by the **shorter** of the two lines (because water would overflow the shorter side). Thus, $\text{height} = \min(\text{height}[i], \text{height}[j])$.

$$\text{Area} = (j - i) \times \min(\text{height}[i], \text{height}[j])$$

### Constraints & Edge Cases
- **Input Size**: The array can be quite large, meaning an $O(n^2)$ solution will likely result in a **Time Limit Exceeded (TLE)**.
- **Minimum Elements**: The array will have at least 2 elements.
- **Height Values**: Heights are non-negative integers.
- **Edge Case**: All lines having the same height; heights being in strictly increasing or decreasing order.

---

## 💡 Core Concepts & Algorithms

### The Two-Pointer Technique
The optimal way to solve this problem is using the **Two-Pointer Technique**. This pattern is used to process linear data structures (like arrays) by maintaining two indices that move toward each other or in the same direction.

#### Why Two Pointers?
A brute-force approach would check every single pair of lines, which takes $O(n^2)$ time. However, we can observe a critical property:
1. We start with the maximum possible **width** (pointers at the extreme ends).
2. To find a larger area while the width is decreasing, we **must** find a larger **height**.
3. If we move the pointer pointing to the taller line, the height of the container will either stay the same (limited by the shorter line) or decrease. The width definitely decreases. Therefore, the area can only decrease.
4. If we move the pointer pointing to the **shorter line**, we open the possibility of finding a taller line that might compensate for the loss in width.

**This is a greedy strategy**: we always discard the line that limits our current height.

---

## 🚶 Step-by-Step Logic

### 1. Brute Force Approach (Naive)
- Initialize `max_area = 0`.
- Use a nested loop to iterate through every pair $(i, j)$.
- Calculate the area for each pair and update `max_area`.
- **Result**: Correct, but inefficient ($O(n^2)$).

### 2. Optimal Two-Pointer Approach
1. **Initialize**: Place one pointer `left` at the start (index `0`) and one pointer `right` at the end (index `len(height) - 1`). Initialize `max_area = 0`.
2. **Loop**: While `left < right`:
    - Calculate the current area using the formula: $\text{current\_area} = (right - left) \times \min(height[left], height[right])$.
    - Update `max_area` if `current_area` is larger.
    - **Move the Pointers**:
        - If `height[left] < height[right]`, increment `left` (`left += 1`).
        - Else, decrement `right` (`right -= 1`).
3. **Return**: Once the pointers meet, return `max_area`.

### 🔍 Dry Run Example
**Input**: `height = [1, 8, 6, 2, 5, 4, 8, 3, 7]`

| Step | Left (idx, val) | Right (idx, val) | Width | Min Height | Area | Max Area | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 0, **1** | 8, **7** | 8 | 1 | 8 | 8 | `left++` |
| 2 | 1, **8** | 8, **7** | 7 | 7 | 49 | 49 | `right--` |
| 3 | 1, **8** | 7, **3** | 6 | 3 | 18 | 49 | `right--` |
| 4 | 1, **8** | 6, **8** | 5 | 8 | 40 | 49 | `right--` |
| 5 | 1, **8** | 5, **4** | 4 | 4 | 16 | 49 | `right--` |
| 6 | 1, **8** | 4, **5** | 3 | 5 | 15 | 49 | `right--` |
| 7 | 1, **8** | 3, **2** | 2 | 2 | 4 | 49 | `right--` |
| 8 | 1, **8** | 2, **6** | 1 | 6 | 6 | 49 | `right--` |
| 9 | 1, 8 | 1, 8 | 0 | - | - | 49 | **Stop** |

**Final Result: 49**

---

## 💻 Implementation

```python
def max_area(height: list[int]) -> int:
    """
    Calculates the maximum area of water a container can store.
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    left = 0
    right = len(height) - 1
    max_water = 0
    
    while left < right:
        # Calculate current width
        width = right - left
        
        # Determine the limiting height (the shorter of the two lines)
        current_height = min(height[left], height[right])
        
        # Calculate area and update maximum
        current_area = width * current_height
        max_water = max(max_water, current_area)
        
        # Move the pointer pointing to the shorter line to potentially find a taller one
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
            
    return max_water
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(n^2)$ | $O(1)$ | Nested loops iterating through all possible pairs. |
| **Two Pointers** | $O(n)$ | $O(1)$ | Each element is visited at most once as pointers converge. |

- **Time Complexity $O(n)$**: We use a single `while` loop that runs until the two pointers meet. Since each step moves one pointer closer to the other, the loop executes at most $n$ times.
- **Space Complexity $O(1)$**: We only store a few integer variables (`left`, `right`, `max_water`), regardless of the input size.

---

## 🌍 Real-World Applications

While "water containers" are an abstraction, the **Two-Pointer technique** and the **Greedy Shrinking** logic are used extensively in software engineering:

1. **Signal Processing**: Finding the maximum distance between two peaks of a certain threshold in a time-series signal.
2. **Resource Allocation**: In cloud computing, finding a pair of resources (e.g., a server and a client) that satisfy a minimum latency/bandwidth requirement while maximizing a specific distance or capacity metric.
3. **Data Analysis (Sliding Window variants)**: The logic of adjusting boundaries to optimize a specific value is the foundation for sliding window algorithms used in network packet analysis and text processing (e.g., finding the longest substring).
4. **Computational Geometry**: Solving problems related to bounding boxes or calculating the largest area rectangle within a set of constraints.
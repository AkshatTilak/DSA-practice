INFO = {
    'difficulty': 'Hard',
    'link': 'https://leetcode.com/problems/trapping-rain-water/',
    'description': 'Compute how much water can be trapped after raining.',
    'groups': ['Array', 'Two Pointers', 'Dynamic Programming'],
    'starter_code': """def trap(height: list[int]) -> int:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# For each element in the array, we iterate through the entire array to the left to find the 
# maximum height and the entire array to the right to find the maximum height. 
# The water trapped at the current index is the minimum of these two maximums minus the current height.
def trap_naive(height: list[int]) -> int:
    if not height:
        return 0
    
    n = len(height)
    total_water = 0
    
    for i in range(n):
        left_max = 0
        right_max = 0
        
        # Find the maximum height to the left of index i
        for j in range(i, -1, -1):
            left_max = max(left_max, height[j])
            
        # Find the maximum height to the right of index i
        for j in range(i, n):
            right_max = max(right_max, height[j])
            
        # The water trapped at index i is determined by the shorter of the two boundaries
        total_water += min(left_max, right_max) - height[i]
        
    return total_water

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses two pointers moving towards each other. We maintain the maximum height 
# encountered so far from the left and the right. Since the amount of water trapped 
# depends on the minimum of the two boundaries, we can process the side with the smaller 
# current height, knowing that the other side is guaranteed to be at least as tall as 
# the current boundary. This allows us to compute the trapped water in a single pass without 
# extra space for arrays.
def trap_optimal(height: list[int]) -> int:
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    total_water = 0
    
    while left < right:
        if height[left] < height[right]:
            # The bottleneck is on the left side
            if height[left] >= left_max:
                left_max = height[left]
            else:
                total_water += left_max - height[left]
            left += 1
        else:
            # The bottleneck is on the right side
            if height[right] >= right_max:
                right_max = height[right]
            else:
                total_water += right_max - height[right]
            right -= 1
            
    return total_water

# Using the optimal implementation for the required 'trap' signature
def trap(height: list[int]) -> int:
    return trap_optimal(height)

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package two_pointers;

public class TrappingRainWater {
    /**
     * Computes the amount of trapped rain water using the two-pointer technique.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int trap(int[] height) {
        if (height == null || height.length == 0) {
            return 0;
        }
        
        int left = 0;
        int right = height.length - 1;
        int leftMax = 0;
        int rightMax = 0;
        int totalWater = 0;
        
        while (left < right) {
            if (height[left] < height[right]) {
                if (height[left] >= leftMax) {
                    leftMax = height[left];
                } else {
                    totalWater += leftMax - height[left];
                }
                left++;
            } else {
                if (height[right] >= rightMax) {
                    rightMax = height[right];
                } else {
                    totalWater += rightMax - height[right];
                }
                right--;
            }
        }
        
        return totalWater;
    }

    public static void main(String[] args) {
        TrappingRainWater solution = new TrappingRainWater();
        int[] height = {0,1,0,2,1,0,1,3,2,1,2,1};
        System.out.println("Trapped Water: " + solution.trap(height)); // Output: 6
    }
}
\"\"\"""",
    'test_code': """def test_trap():
    assert trap([0,1,0,2,1,0,1,3,2,1,2,1]) == 6""",
    'readme_content': """# Trapping Rain Water

## 📌 Overview & Problem Explanation
The **Trapping Rain Water** problem is a classic algorithmic challenge that asks us to calculate the total volume of water that can be contained between "bars" of varying heights after a rainstorm. 

Imagine a 2D elevation map represented by an array of non-negative integers. Each element in the array represents the height of a bar with a width of 1. Water is trapped in the "valleys" created by these bars.

### The Core Intuition
For water to be trapped at any specific index $i$, there must be a boundary to its **left** and a boundary to its **right** that are both taller than the height at index $i$. The amount of water trapped at index $i$ is determined by the **shorter** of these two boundaries (the "bottleneck"), minus the height of the bar itself.

**Mathematical Formula:**
$$\text{Water at index } i = \max(0, \min(\text{max\_left}, \text{max\_right}) - \text{height}[i])$$

### Inputs, Outputs & Constraints
- **Input**: A list of non-negative integers `height`.
- **Output**: A single integer representing the total units of trapped water.
- **Constraints**:
    - $n == \text{height.length}$
    - $1 \le n \le 2 \cdot 10^4$
    - $0 \le \text{height}[i] \le 10^5$
- **Edge Cases**:
    - **Empty or Small Arrays**: Arrays with fewer than 3 elements cannot trap any water.
    - **Monotonic Arrays**: Strictly increasing or decreasing heights result in 0 trapped water.
    - **Flat Terrain**: All heights equal results in 0 trapped water.
    - **Single Peak**: A "mountain" shape traps no water.

---

## ⚙️ Core Concepts & Algorithms

### 1. The Two-Pointer Pattern (Optimal)
The most efficient way to solve this problem is using the **Two-Pointer Technique**. Instead of pre-calculating the maximums for every index, we maintain two pointers (`left` and `right`) and two variables (`left_max` and `right_max`).

**Why Two Pointers?**
The amount of water at any index is limited by the **minimum** of the maximum height to the left and the maximum height to the right. By moving the pointer that currently points to the smaller height, we can guarantee that the "bottleneck" is known, allowing us to calculate the water for that specific index without knowing the exact maximum on the opposite side.

### 2. Dynamic Programming (Alternative)
A DP approach involves creating two auxiliary arrays:
- `left_max[i]`: The maximum height encountered from index $0$ to $i$.
- `right_max[i]`: The maximum height encountered from index $n-1$ down to $i$.
This trades space ($O(N)$) for a simpler conceptual flow.

---

## 🚶 Step-by-Step Logic

### The Optimal Two-Pointer Approach

1. **Initialization**:
   - Place `left` at index `0` and `right` at index `n-1`.
   - Initialize `left_max = 0`, `right_max = 0`, and `total_water = 0`.

2. **Iterative Process**:
   - While `left < right`:
     - **Compare heights**: Check if `height[left]` is smaller than `height[right]`.
     - **If `height[left]` is smaller**:
       - The bottleneck is on the left side.
       - If `height[left] >= left_max`, update `left_max` (no water trapped here).
       - Else, add `left_max - height[left]` to `total_water`.
       - Increment `left`.
     - **If `height[right]` is smaller (or equal)**:
       - The bottleneck is on the right side.
       - If `height[right] >= right_max`, update `right_max`.
       - Else, add `right_max - height[right]` to `total_water`.
       - Decrement `right`.

3. **Termination**: Once `left` and `right` meet, return the `total_water`.

### Dry Run Example
**Input**: `height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]`

- `left=0, right=11`: `h[0]=0 < h[11]=1`. `left_max` becomes 0. Water += 0. `left` becomes 1.
- `left=1, right=11`: `h[1]=1 == h[11]=1`. `right_max` becomes 1. Water += 0. `right` becomes 10.
- ...
- When `left` is at index 2 (`h[2]=0`) and `left_max` is 1, and `right` is at some index where `h[right] >= 1`, the logic calculates `1 - 0 = 1` unit of water.

### Implementation

```python
def trap(height: list[int]) -> int:
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    total_water = 0
    
    while left < right:
        # The smaller height determines the water level
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                total_water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                total_water += right_max - height[right]
            right -= 1
            
    return total_water
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(N^2)$ | $O(1)$ | For every element, we scan the entire array to find the max left and max right. |
| **Dynamic Programming** | $O(N)$ | $O(N)$ | We traverse the array 3 times (left-max, right-max, and final sum) and store two arrays. |
| **Two Pointers** | $O(N)$ | $O(1)$ | We traverse the array exactly once with two pointers and use only a few variables. |

---

## 🚀 Real-World Applications

While "trapping rain water" sounds like a puzzle, the underlying pattern—**identifying boundaries to calculate containment or capacity**—is used in several engineering fields:

1. **Geographic Information Systems (GIS)**: Used in hydrology and topography software to simulate flood zones, calculate watershed basins, and predict how water will pool in mountainous terrain.
2. **Digital Signal Processing (DSP)**: Finding local minima between two peaks to identify "valleys" in a waveform, which is useful for peak detection and signal normalization.
3. **Memory Management**: In some low-level memory allocators, similar logic is used to find the largest contiguous free block of memory between allocated segments.
4. **Financial Analysis**: Identifying "drawdowns" (the peak-to-trough decline during a specific period) in stock market charts to calculate risk and volatility.""",
}

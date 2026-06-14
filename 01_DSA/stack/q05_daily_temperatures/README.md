# Daily Temperatures

## 📌 Overview & Problem Explanation

The **Daily Temperatures** problem asks us to calculate the number of days one must wait until a warmer temperature occurs for every single day in a given list. If no future day is warmer, the result for that day should be `0`.

### Problem Statement
Given an array of integers `temperatures`, return an array `answer` such that `answer[i]` is the number of days you have to wait after the $i^{th}$ day to get a warmer temperature.

**Example:**
- **Input:** `temperatures = [73, 74, 75, 71, 69, 72, 76, 73]`
- **Output:** `[1, 1, 4, 2, 1, 1, 0, 0]`
- **Explanation:** 
    - For day 0 (73), day 1 (74) is warmer $\rightarrow$ wait **1** day.
    - For day 2 (75), day 6 (76) is the next warmer $\rightarrow$ wait **4** days.
    - For day 6 (76), there are no warmer days ahead $\rightarrow$ wait **0** days.

### Constraints & Edge Cases
- **Input Size:** $1 \le temperatures.length \le 10^5$. This implies an $O(N^2)$ solution will likely exceed the time limit (TLE).
- **Temperature Range:** $30 \le temperatures[i] \le 100$.
- **Edge Cases:**
    - **Strictly Increasing:** `[30, 40, 50]` $\rightarrow$ `[1, 1, 0]`.
    - **Strictly Decreasing:** `[50, 40, 30]` $\rightarrow$ `[0, 0, 0]`.
    - **All Same Temperatures:** `[70, 70, 70]` $\rightarrow$ `[0, 0, 0]`.
    - **Single Element:** `[70]` $\rightarrow$ `[0]`.

---

## 🛠️ Core Concepts: Monotonic Stack

The core of the optimal solution is the **Monotonic Stack**. A monotonic stack is a standard stack that maintains its elements in a specific order (either strictly increasing or strictly decreasing).

### Why a Monotonic Stack?
This problem is a classic variation of the **"Next Greater Element"** problem. When we are at day $i$, we don't know when the next warmer day will be. However, we know that day $i$ might be the "warmer day" for several previous days that are still waiting for a warmer temperature.

By using a **monotonic decreasing stack**, we store the indices of days whose warmer temperature has not yet been found. 
1. We push indices onto the stack as long as the current temperature is colder than or equal to the temperature at the top of the stack.
2. As soon as we encounter a temperature **warmer** than the one at the top of the stack, we have found the "next warmer day" for that index.
3. We pop the index and calculate the difference in days (`current_index - popped_index`).

### Properties
- **Order:** The temperatures corresponding to the indices in the stack are always in non-increasing order.
- **Efficiency:** Each index is pushed onto the stack once and popped once, ensuring linear time complexity.

---

## 🚶 Step-by-Step Logic

### 1. Brute Force Approach (Naive)
The simplest way is to use nested loops. For every day $i$, iterate through every day $j$ (where $j > i$) until you find a temperature higher than `temperatures[i]`.
- **Logic:** `for i in range(n): for j in range(i + 1, n): if temp[j] > temp[i]: res[i] = j - i; break`.
- **Drawback:** In the worst case (decreasing temperatures), this takes $O(N^2)$ time.

### 2. Optimal Approach (Monotonic Stack)
We use a stack to keep track of the indices of the days we are still monitoring.

**The Algorithm:**
1. Initialize an array `res` of the same length as `temperatures` filled with `0`.
2. Initialize an empty stack to store indices.
3. Iterate through the `temperatures` array using index `i`:
   - While the stack is not empty AND the current temperature `temperatures[i]` is greater than the temperature at the index on top of the stack (`temperatures[stack[-1]]`):
     - Pop the index from the stack: `prev_index = stack.pop()`.
     - Calculate the distance: `res[prev_index] = i - prev_index`.
   - Push the current index `i` onto the stack.
4. Return `res`.

### 🔍 Dry Run Example
**Input:** `[73, 74, 75, 71, 72]`

| Step | Temp | Stack (indices) | Action | `res` Array |
| :--- | :--- | :--- | :--- | :--- |
| 0 | 73 | `[0]` | Push index 0 | `[0, 0, 0, 0, 0]` |
| 1 | 74 | `[]` $\rightarrow$ `[1]` | 74 > 73. Pop 0, `res[0] = 1-0 = 1`. Push 1. | `[1, 0, 0, 0, 0]` |
| 2 | 75 | `[]` $\rightarrow$ `[2]` | 75 > 74. Pop 1, `res[1] = 2-1 = 1`. Push 2. | `[1, 1, 0, 0, 0]` |
| 3 | 71 | `[2, 3]` | 71 < 75. Push index 3. | `[1, 1, 0, 0, 0]` |
| 4 | 72 | `[2]` $\rightarrow$ `[2, 4]` | 72 > 71. Pop 3, `res[3] = 4-3 = 1`. Push 4. | `[1, 1, 0, 1, 0]` |

**Final Result:** `[1, 1, 0, 1, 0]` (Note: index 2 remains 0 because no temp > 75 appeared).

---

## 🚀 Implementation

```python
def daily_temperatures(temperatures: list[int]) -> list[int]:
    # Initialize result array with 0s
    # If no warmer day is found, it naturally stays 0
    n = len(temperatures)
    res = [0] * n
    stack = [] # Stores indices of temperatures
    
    for i in range(n):
        current_temp = temperatures[i]
        
        # While the current temperature is warmer than the temperature 
        # at the index stored at the top of the stack
        while stack and current_temp > temperatures[stack[-1]]:
            prev_index = stack.pop()
            res[prev_index] = i - prev_index
            
        # Always push the current index onto the stack
        stack.append(i)
        
    return res
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(N^2)$ | $O(1)$ | Nested loops iterate through the array for every element. |
| **Monotonic Stack** | $O(N)$ | $O(N)$ | Each element is pushed and popped from the stack exactly once. |

- **Time Complexity $O(N)$**: Although there is a `while` loop inside a `for` loop, each index is pushed onto the stack once and popped once. The total number of operations is proportional to $2N$.
- **Space Complexity $O(N)$**: In the worst case (e.g., temperatures in strictly decreasing order), the stack will grow to size $N$.

---

## 🌍 Real-World Applications

The **Monotonic Stack** pattern is highly useful in software engineering for problems involving "nearest boundaries" or "range limits":

1. **Histogram Problems:** Finding the largest rectangle in a histogram (finding the nearest smaller bar to the left and right).
2. **Price Analysis:** In financial software, identifying the "next peak" or "next trough" in stock price data for technical analysis.
3. **Compiler Design:** Expression parsing (e.g., matching parentheses or evaluating postfix expressions) often utilizes stack-based logic to maintain precedence.
4. **UI Rendering:** Determining which window is "on top" or calculating the visible area of overlapping elements (Z-index management).
5. **Network Routing:** Finding the nearest node with a higher capacity or priority in certain graph-based routing algorithms.
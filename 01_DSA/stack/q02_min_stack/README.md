# Min Stack (q02_min_stack)

## 1. Overview & Problem Explanation

The **Min Stack** challenge asks us to design a specialized data structure that functions exactly like a standard **Stack** (Last-In-First-Out), but with one critical enhancement: it must be able to retrieve the minimum element currently present in the stack in **constant time $O(1)$**.

### The Challenge
In a standard stack, you can `push` and `pop` elements in $O(1)$. However, if you want to find the minimum value, you would typically have to iterate through the entire stack, resulting in $O(n)$ time complexity. The goal here is to eliminate that linear scan.

### Requirements
- `push(val)`: Push element `val` onto the stack.
- `pop()`: Remove the element on the top of the stack.
- `top()`: Get the top element of the stack.
- `getMin()`: Retrieve the minimum element in the stack.
- **Constraint**: All operations must run in $O(1)$ time.

### Edge Cases to Consider
- **Empty Stack**: What happens if `pop`, `top`, or `getMin` is called on an empty stack? (Though LeetCode usually guarantees operations are valid, in production, we must handle `IndexError`).
- **Duplicate Minimums**: If the minimum value is pushed multiple times, popping one instance should not remove the knowledge that the value is still the minimum.
- **Negative Numbers**: The solution must handle negative integers correctly.

---

## 2. Core Concepts & Data Structures

### The Trade-off: Space for Time
To achieve $O(1)$ for `getMin()`, we cannot search for the minimum at runtime. We must **pre-calculate** and **store** the minimum state at every single level of the stack. This is a classic architectural trade-off: we increase our **Space Complexity** to decrease our **Time Complexity**.

### The "State Tracking" Pattern
The key insight is that the minimum value of a stack only changes when:
1. A value smaller than or equal to the current minimum is pushed.
2. The current minimum value is popped off the stack.

By associating each element pushed onto the stack with the "minimum value known at that point in time," we create a history of minimums. When we pop an element, we effectively "roll back" to the previous minimum state.

### Chosen Data Structure: Auxiliary Stack
The most robust way to implement this is using an **Auxiliary Stack** (or a stack of pairs). 
- **Main Stack**: Stores all the actual values.
- **Min Stack**: Stores the minimum value encountered up to that depth.

---

## 3. Step-by-Step Logic

### Naive Approach (Brute Force)
1. Use a standard list as a stack.
2. For `push`, `pop`, and `top`, use standard list operations.
3. For `getMin`, call `min(stack)`.
- **Flaw**: `min()` iterates through the entire list, making the time complexity $O(n)$. This fails the requirement.

### Optimal Approach (Dual Stack)

#### 1. Initialization
Create two empty lists: `self.stack` and `self.min_stack`.

#### 2. Push Operation (`push(val)`)
- Push `val` onto `self.stack`.
- If `self.min_stack` is empty, push `val` onto `self.min_stack`.
- If `self.min_stack` is not empty, compare `val` with the current top of `self.min_stack`. Push the **smaller** of the two onto `self.min_stack`.
- *Result*: `self.min_stack` always has the same height as `self.stack`, and its top always represents the minimum of all elements below it.

#### 3. Pop Operation (`pop()`)
- Pop from `self.stack`.
- Pop from `self.min_stack`.
- *Result*: We remove the value and the minimum state associated with that value simultaneously.

#### 4. Top and GetMin Operations
- `top()`: Return the last element of `self.stack`.
- `getMin()`: Return the last element of `self.min_stack`.

### Dry Run Example
**Operations**: `push(-2)`, `push(0)`, `push(-3)`, `getMin()`, `pop()`, `top()`, `getMin()`

| Operation | Main Stack | Min Stack | Return Value | Logic |
| :--- | :--- | :--- | :--- | :--- |
| `push(-2)` | `[-2]` | `[-2]` | - | Min is -2 |
| `push(0)` | `[-2, 0]` | `[-2, -2]` | - | $\min(0, -2) = -2$ |
| `push(-3)` | `[-2, 0, -3]` | `[-2, -2, -3]` | - | $\min(-3, -2) = -3$ |
| `getMin()` | `[-2, 0, -3]` | `[-2, -2, -3]` | **-3** | Top of min\_stack |
| `pop()` | `[-2, 0]` | `[-2, -2]` | - | Both popped |
| `top()` | `[-2, 0]` | `[-2, -2]` | **0** | Top of main\_stack |
| `getMin()` | `[-2, 0]` | `[-2, -2]` | **-2** | Top of min\_stack |

---

## 4. Implementation

```python
class MinStack:
    def __init__(self):
        """
        Initialize two stacks: 
        - 'stack' to keep track of all elements.
        - 'min_stack' to keep track of the minimum at each state.
        """
        self.stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        """
        Push the value onto the main stack.
        Push the current minimum onto the min_stack.
        """
        self.stack.append(val)
        
        # If min_stack is empty, the first value is the minimum.
        # Otherwise, push the minimum of the new value and the current min.
        if not self.min_stack:
            self.min_stack.append(val)
        else:
            current_min = self.min_stack[-1]
            self.min_stack.append(min(val, current_min))

    def pop(self) -> None:
        """
        Remove the top element from both stacks to maintain synchronicity.
        """
        if self.stack:
            self.stack.pop()
            self.min_stack.pop()

    def top(self) -> int:
        """
        Return the top element of the main stack.
        """
        return self.stack[-1]

    def getMin(self) -> int:
        """
        Return the top element of the min_stack, which is the current minimum.
        """
        return self.min_stack[-1]
```

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| `push(val)` | $O(1)$ | $O(1)$ | Appending to a list is amortized constant time. |
| `pop()` | $O(1)$ | $O(1)$ | Popping from the end of a list is constant time. |
| `top()` | $O(1)$ | $O(1)$ | Accessing a list by index is constant time. |
| `getMin()` | $O(1)$ | $O(1)$ | Accessing the top of the auxiliary stack is constant time. |
| **Overall** | **$O(1)$** | **$O(n)$** | We store two values for every one input (Main + Min). |

**Space Complexity Note**: The space complexity is $O(n)$ because in the worst case (e.g., elements pushed in strictly decreasing order), the `min_stack` will grow linearly with the number of elements pushed.

---

## 6. Real-World Applications

The pattern of maintaining a "state history" or "monotonic tracking" is widely used in software engineering:

1. **Undo/Redo Mechanisms**: Many editors maintain a stack of states. If the state includes a summary (like the "min" in this problem), the application can revert to a previous state instantly without recalculating the entire document's properties.
2. **Expression Parsing (Compilers)**: When parsing nested parentheses or mathematical expressions, compilers use stacks to keep track of the most recent open bracket or operator priority.
3. **Memory Management**: The CPU's **Call Stack** manages return addresses and local variables. While it doesn't track a "minimum," the LIFO property is fundamental to how functions are executed and returned from.
4. **Browser History**: The "Back" and "Forward" buttons are essentially two stacks managing the state of your navigation history.
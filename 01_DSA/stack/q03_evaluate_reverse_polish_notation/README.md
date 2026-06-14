# Evaluate Reverse Polish Notation

## 📌 Overview & Problem Explanation

**Reverse Polish Notation (RPN)**, also known as **Postfix Notation**, is a mathematical notation in which every operator follows all of its operands. Unlike the standard **Infix Notation** we learn in school (e.g., `3 + 4`), RPN removes the need for parentheses to define precedence.

### The Problem
Given an array of strings `tokens` that represent an arithmetic expression in Reverse Polish Notation, you must evaluate the expression and return the integer result.

**Example:**
- **Infix:** `(2 + 1) * 3`
- **RPN:** `["2", "1", "+", "3", "*"]`
- **Evaluation:** 
    1. See `2`, see `1`.
    2. See `+` $\rightarrow$ add the last two numbers: $2 + 1 = 3$.
    3. See `3`.
    4. See `*` $\rightarrow$ multiply the last two numbers: $3 * 3 = 9$.
- **Result:** `9`

### Constraints & Edge Cases
- **Input:** A list of strings containing integers and operators (`+`, `-`, `*`, `/`).
- **Division:** Division between two integers should **truncate toward zero**. 
    - *Crucial Python Note:* In Python, `//` is floor division (rounds down). For example, `-1 // 10` results in `-1`. To truncate toward zero, use `int(a / b)`.
- **Valid Expression:** The input is guaranteed to be a valid RPN expression.
- **Operands:** Numbers can be negative.

---

## ⚙️ Core Concepts & Data Structures

### The Stack (LIFO)
The optimal data structure for this problem is a **Stack**. 

**Why a Stack?**
RPN is designed to be processed linearly. The most recently encountered numbers (the "top" of the stack) are the ones that the next operator will act upon. This "Last-In, First-Out" (LIFO) property perfectly matches the requirements of postfix evaluation.

**Theoretical Workflow:**
1. **Operand encountered:** Push it onto the stack.
2. **Operator encountered:** 
    - Pop the top two elements from the stack.
    - Apply the operator to these elements.
    - Push the resulting value back onto the stack.
3. **End of expression:** The final value remaining on the stack is the result.

---

## 🚶 Step-by-Step Logic

### The Optimal Algorithm
1. **Initialize** an empty stack.
2. **Iterate** through each `token` in the `tokens` list:
    - **If the token is a number:** Convert it to an integer and `push` it onto the stack.
    - **If the token is an operator (`+`, `-`, `*`, `/`):**
        - `Pop` the top element as the **right operand** ($b$).
        - `Pop` the next element as the **left operand** ($a$).
        - *Note: Order matters for subtraction and division!*
        - Perform the operation ($a \text{ op } b$).
        - `Push` the result back onto the stack.
3. **Return** the only remaining element in the stack.

### Dry Run Example
**Input:** `tokens = ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]`

| Token | Action | Stack State | Calculation |
| :--- | :--- | :--- | :--- |
| `"10"` | Push | `[10]` | - |
| `"6"` | Push | `[10, 6]` | - |
| `"9"` | Push | `[10, 6, 9]` | - |
| `"3"` | Push | `[10, 6, 9, 3]` | - |
| `"+"` | Pop 3, 9 | `[10, 6, 12]` | $9 + 3 = 12$ |
| `"-11"`| Push | `[10, 6, 12, -11]`| - |
| `"*"` | Pop -11, 12| `[10, 6, -132]` | $12 \times -11 = -132$ |
| `"/"` | Pop -132, 6 | `[10, 0]` | $6 / -132 = 0$ (trunc) |
| `"*"` | Pop 0, 10 | `[0]` | $10 \times 0 = 0$ |
| `"17"` | Push | `[0, 17]` | - |
| `"+"` | Pop 17, 0 | `[17]` | $0 + 17 = 17$ |
| `"5"` | Push | `[17, 5]` | - |
| `"+"` | Pop 5, 17 | `[22]` | $17 + 5 = 22$ |

**Final Result:** `22`

---

## 💻 Implementation

```python
def eval_rpn(tokens: list[str]) -> int:
    stack = []
    
    # Define operator mapping for cleaner logic
    # We use a lambda for division to handle truncation toward zero in Python
    operators = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: int(a / b) 
    }
    
    for token in tokens:
        if token in operators:
            # The first element popped is the second operand (right side)
            right = stack.pop()
            # The second element popped is the first operand (left side)
            left = stack.pop()
            
            # Calculate result and push back to stack
            result = operators[token](left, right)
            stack.append(result)
        else:
            # Token is a number
            stack.append(int(token))
            
    return stack[0]
```

---

## 📊 Complexity Analysis

| Complexity | Analysis | Reasoning |
| :--- | :--- | :--- |
| **Time Complexity** | $O(N)$ | We iterate through the list of tokens exactly once. Each stack operation (`push`, `pop`) takes $O(1)$ time. |
| **Space Complexity** | $O(N)$ | In the worst case (e.g., all numbers followed by all operators), the stack will store up to $N$ elements. |

---

## 🌍 Real-World Applications

The logic used to evaluate RPN is fundamental to computer science and is used in several critical areas:

1. **Compiler Design:** Compilers often convert human-readable infix expressions into postfix (RPN) or prefix notation during the parsing phase. This simplifies the process of generating machine code because it eliminates the need to manage operator precedence and parentheses.
2. **Virtual Machines (JVM/CPython):** The Java Virtual Machine (JVM) and the Python bytecode interpreter are **stack-based architectures**. They use a stack to perform arithmetic operations exactly like the RPN evaluation algorithm.
3. **Calculator Implementation:** Many early Hewlett-Packard (HP) calculators used RPN to reduce the number of keystrokes and memory required to calculate complex formulas.
4. **PostScript:** The page description language used by printers (PostScript) is based on a stack-oriented language, utilizing postfix notation to describe graphics and text layout.
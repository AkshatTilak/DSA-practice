# Stack

A Stack is a linear, Last-In-First-Out (LIFO) data structure where elements are added (pushed) and removed (popped) from the same end, called the "top". It is highly efficient for recursive tracking, matching structures, and maintaining historical execution context (e.g. call stacks). A specialized variant, the Monotonic Stack, maintains elements in sorted order to solve range/next-greater queries.

---

## 🗺️ ASCII Execution Flow: Valid Parentheses

Below is a flow diagram mapping validation of brackets in `s = "([{}])"` using an in-memory LIFO stack:

```text
Input brackets: [ ( , [ , { , } , ] , ) ]

1. Character '(' ── Push ── Stack: [ '(' ]
2. Character '[' ── Push ── Stack: [ '(', '[' ]
3. Character '{' ── Push ── Stack: [ '(', '[', '{' ]
4. Character '}' ── Peek matching '{' on Top? Yes! ── Pop ── Stack: [ '(', '[' ]
5. Character ']' ── Peek matching '[' on Top? Yes! ── Pop ── Stack: [ '(' ]
6. Character ')' ── Peek matching '(' on Top? Yes! ── Pop ── Stack: []

Validation Complete: Stack is empty ──> True
```

---

## 📊 Complexity Analysis

| Operations | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Push / Pop / Peek | $O(1)$ | $O(1)$ |
| Matching Sequence / Monotonic Search | $O(N)$ | $O(N)$ |

---

## 🏢 Real-World Production Use-Case

### Web Browsers: Forward/Backward History State Engine
Modern browsers allow users to navigate back and forward through visited URLs.
1. The navigation history is managed using **two stacks**: the back-stack and the forward-stack.
2. When visiting a new page, it is pushed onto the back-stack, and the forward-stack is cleared.
3. Clicking "Back" pops the current URL from the back-stack and pushes it onto the forward-stack.
4. Because stack operations occur in $O(1)$ time, navigation state transitions are instantaneous and memory-efficient.
INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/valid-parentheses/',
    'description': 'Given a string containing brackets, determine if the input string is valid.',
    'groups': ['String', 'Stack & Queue'],
    'starter_code': """def is_valid(s: str) -> bool:
    # Write your solution here
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(n)
# This approach repeatedly searches for and removes adjacent matching pairs of brackets.
# In the worst case, such as deeply nested brackets, it performs O(n) scans of the string.
def is_valid_naive(s: str) -> bool:
    if not s:
        return True
    
    prev_length = -1
    while prev_length != len(s):
        prev_length = len(s)
        s = s.replace('()', '').replace('[]', '').replace('{}', '')
        
    return len(s) == 0

# --- APPROACH 2: Optimal (Stack) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach uses a stack to keep track of opening brackets. When a closing bracket
# is encountered, it is matched with the most recent opening bracket. This is optimal
# because it processes the string in a single pass and uses the minimum necessary space 
# to ensure correct nesting order.
def is_valid_optimal(s: str) -> bool:
    stack = []
    # Mapping of closing brackets to their corresponding opening brackets
    mapping = {")": "(", "}": "{", "]": "["}
    
    for char in s:
        if char in mapping:
            # Pop the top element if stack is not empty, otherwise use a dummy character
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            # It is an opening bracket, push it onto the stack
            stack.append(char)
            
    # If the stack is empty, all brackets were matched correctly
    return not stack

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package stack;

import java.util.Stack;
import java.util.HashMap;
import java.util.Map;

public class ValidParentheses {
    /**
     * Determines if the input string containing brackets is valid.
     * Time Complexity: O(n)
     * Space Complexity: O(n)
     */
    public boolean isValid(String s) {
        if (s == null) return false;
        
        Stack<Character> stack = new Stack<>();
        Map<Character, Character> mapping = new HashMap<>();
        mapping.put(')', '(');
        mapping.put('}', '{');
        mapping.put(']', '[');

        for (char c : s.toCharArray()) {
            if (mapping.containsKey(c)) {
                // If stack is empty, use a dummy character that won't match
                char topElement = stack.isEmpty() ? '#' : stack.pop();
                if (topElement != mapping.get(c)) {
                    return false;
                }
            } else {
                // Character is an opening bracket
                stack.push(c);
            }
        }
        
        return stack.isEmpty();
    }

    public static void main(String[] args) {
        ValidParentheses vp = new ValidParentheses();
        System.out.println(vp.isValid("()[]{}")); // true
        System.out.println(vp.isValid("([)]"));   // false
        System.out.println(vp.isValid("{[]}"));   // true
    }
}
\"\"\"""",
    'test_code': """def test_parentheses():
    assert is_valid('()[]{}') is True
    assert is_valid('(]') is False
    assert is_valid('([)]') is False""",
    'readme_content': """# Valid Parentheses

## 📌 Overview & Problem Explanation

The **Valid Parentheses** problem is a classic challenge that tests your understanding of linear data structures and the concept of "nesting." The goal is to determine if a given string of brackets—consisting of parentheses `()`, square brackets `[]`, and curly braces `{}`—is logically balanced.

### What makes a string "Valid"?
A string is considered valid if:
1. **Open brackets must be closed by the same type of brackets.** (e.g., `(` must be closed by `)`).
2. **Open brackets must be closed in the correct order.** (e.g., `([)]` is **invalid** because the `[` should be closed before the `(` is closed).
3. **Every closing bracket has a corresponding opening bracket of the same type.**

### Input & Output
- **Input**: A string `s` containing only the characters `'('`, `')'`, `'{'`, `'}'`, `'['`, and `']'`.
- **Output**: A boolean value (`True` if valid, `False` otherwise).

### Constraints & Edge Cases
- **Time Complexity Target**: $O(N)$, where $N$ is the length of the string.
- **Space Complexity Target**: $O(N)$ in the worst case.
- **Edge Cases**:
    - **Empty String**: Usually considered valid (though check constraints; if length $\ge 1$, this is moot).
    - **Single Character**: Always invalid (e.g., `"["` is unbalanced).
    - **Only Closing Brackets**: Invalid (e.g., `")]]"`).
    - **Only Opening Brackets**: Invalid (e.g., `"{{("`).
    - **Wrong Order**: Invalid (e.g., `"(]"`).

---

## 🧠 Core Concepts & Data Structures

### The Stack (LIFO)
The primary data structure used to solve this problem is the **Stack**. A stack follows the **Last-In, First-Out (LIFO)** principle. 

**Why a Stack?**
In a balanced bracket sequence, the **last** bracket opened must be the **first** one closed. This mirrors the exact behavior of a stack:
- When we encounter an **opening bracket**, we "push" it onto the stack to remember that it needs to be closed later.
- When we encounter a **closing bracket**, we "pop" the most recent opening bracket from the top of the stack to see if they match.

### Hash Map (Dictionary)
To avoid writing multiple `if/elif` statements for every bracket type, we use a **Hash Map** to store the relationship between closing and opening brackets. This allows for $O(1)$ lookup to verify if a closing bracket matches the popped opening bracket.

---

## ⚙️ Step-by-Step Logic

### Approach 1: Naive (Recursive Replacement)
The naive approach treats the string as a set of nested pairs and repeatedly "peels" the inner-most valid pairs away.

1. Search the string for the substrings `()`, `[]`, or `{}`.
2. Replace all occurrences of these pairs with an empty string `""`.
3. Repeat this process until no more replacements can be made.
4. If the final string is empty, it was valid. Otherwise, it is invalid.

**Dry Run: `s = "{[()]}"`**
- Pass 1: Find `()`, replace $\rightarrow$ `"{[]}"`
- Pass 2: Find `[]`, replace $\rightarrow$ `"{}"`
- Pass 3: Find `{}`, replace $\rightarrow$ `""`
- Result: **Valid**

---

### Approach 2: Optimal (LIFO Stack)
This is the industry-standard approach, utilizing a stack to track pending closures.

1. **Initialize** an empty stack and a mapping dictionary: `mapping = {')': '(', '}': '{', ']': '['}`.
2. **Iterate** through each character `char` in the string:
   - **If `char` is a closing bracket** (exists as a key in `mapping`):
     - Check if the stack is empty. If it is, we have a closing bracket without a preceding opening bracket $\rightarrow$ **Return `False`**.
     - Pop the top element from the stack.
     - Check if the popped element matches the corresponding opening bracket in the mapping. If not $\rightarrow$ **Return `False`**.
   - **If `char` is an opening bracket**:
     - Push it onto the stack.
3. **Final Check**: After the loop, if the stack still contains elements, it means some opening brackets were never closed $\rightarrow$ **Return `False`**. Otherwise, **Return `True`**.

**Dry Run: `s = "([)]"`**
1. `char = '('`: Push to stack $\rightarrow$ `stack = ['(']`
2. `char = '['`: Push to stack $\rightarrow$ `stack = ['(', '[']`
3. `char = ')'`: Closing bracket! Pop stack $\rightarrow$ `top = '['`. 
   - Does `mapping[')']` (which is `'('`) equal `top` (`'['`)? **No**.
   - **Return `False`**.

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Naive** | $O(N^2)$ | $O(N)$ | In the worst case (e.g., `((((()))))`), we perform $N/2$ iterations, and each `.replace()` call scans the string $O(N)$. |
| **Optimal** | $O(N)$ | $O(N)$ | We traverse the string exactly once. The space is $O(N)$ because, in the worst case, we push all characters onto the stack. |

---

## 💻 Implementation

### Python Optimal
```python
def is_valid(s: str) -> bool:
    stack = []
    # Map closing brackets to their corresponding opening brackets
    mapping = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in mapping:
            # Pop the top element if stack is not empty, otherwise use a dummy value
            top_element = stack.pop() if stack else '#'
            # If the popped element doesn't match the required opening bracket, it's invalid
            if mapping[char] != top_element:
                return False
        else:
            # It's an opening bracket, push it onto the stack
            stack.append(char)
            
    # If the stack is empty, all brackets were matched correctly
    return not stack
```

### Java Optimal
```java
public boolean isValid(String s) {
    Stack<Character> stack = new Stack<>();
    for (char c : s.toCharArray()) {
        // Push the expected closing bracket onto the stack
        if (c == '(') stack.push(')');
        else if (c == '[') stack.push(']');
        else if (c == '{') stack.push('}');
        // If stack is empty or the popped bracket doesn't match the current char
        else if (stack.isEmpty() || stack.pop() != c) return false;
    }
    return stack.isEmpty();
}
```

---

## 🌍 Real-World Applications

The "Valid Parentheses" pattern is not just a LeetCode puzzle; it is fundamental to how software processes structured data:

1. **Compilers & Interpreters**: Every time you write code in Python, Java, or C++, the compiler uses a stack-based parser to ensure your parentheses, curly braces, and brackets are balanced. A `SyntaxError: unexpected EOF while parsing` is often just a failed "Valid Parentheses" check.
2. **JSON/XML Parsing**: Data interchange formats like JSON and XML rely on matching tags (`<tag>...</tag>`) or braces (`{...}`). Parsers use stacks to ensure the nested structure is hierarchical and correct.
3. **IDE Feature: Bracket Matching**: When you click next to a brace in VS Code or IntelliJ and the corresponding brace is highlighted, the editor is using a stack to find the matching pair.
4. **Mathematical Expression Evaluation**: Calculators use this logic (often via the Shunting-yard algorithm) to determine the order of operations in expressions like `(2 + 3) * [10 / (2 + 3)]`.""",
}

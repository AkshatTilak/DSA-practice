INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/generate-parentheses/',
    'description': 'Generate all combinations of n pairs of valid parentheses.',
    'groups': ['String', 'Stack & Queue', 'Backtracking'],
    'starter_code': """def generate_parenthesis(n: int) -> list[str]:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(2^(2n) * n)
# Space Complexity: O(2^(2n) * n)
# This approach generates every possible sequence of length 2n containing '(' and ')'.
# It then validates each sequence using a balance counter to ensure it is a valid parentheses string.
import itertools

def generate_parenthesis_naive(n: int) -> list[str]:
    if n == 0:
        return []
    
    def is_valid(s):
        balance = 0
        for char in s:
            if char == '(':
                balance += 1
            else:
                balance -= 1
            if balance < 0:
                return False
        return balance == 0

    # Generate all permutations of length 2n using '(' and ')'
    all_combinations = itertools.product(['(', ')'], repeat=2*n)
    result = []
    for combo in all_combinations:
        s = "".join(combo)
        if is_valid(s):
            result.append(s)
            
    return result

# --- APPROACH 2: Optimal (Backtracking) ---
# Time Complexity: O(4^n / (n^(3/2)))
# Space Complexity: O(n)
# This approach uses backtracking to build only valid sequences.
# We maintain counts of open and closed parentheses. An open parenthesis is added if 
# we haven't exceeded n. A closed parenthesis is added only if it doesn't exceed 
# the number of open parentheses currently in the string. This prunes the search 
# space significantly, resulting in a complexity related to the n-th Catalan number.
def generate_parenthesis_optimal(n: int) -> list[str]:
    result = []
    
    def backtrack(current_string: str, open_count: int, close_count: int):
        # Base case: if the current string length reaches 2n, it is a valid combination
        if len(current_string) == 2 * n:
            result.append(current_string)
            return
        
        # If we can still add an opening parenthesis, do so
        if open_count < n:
            backtrack(current_string + '(', open_count + 1, close_count)
            
        # If we can add a closing parenthesis without making the string invalid
        if close_count < open_count:
            backtrack(current_string + ')', open_count, close_count + 1)
            
    backtrack("", 0, 0)
    return result

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package stack;

import java.util.ArrayList;
import java.util.List;

public class GenerateParentheses {
    /**
     * Generates all combinations of n pairs of valid parentheses.
     * This implementation uses the optimal backtracking approach.
     */
    public List<String> generateParenthesis(int n) {
        List<String> result = new ArrayList<>();
        backtrack(result, new StringBuilder(), 0, 0, n);
        return result;
    }

    private void backtrack(List<String> result, StringBuilder current, int open, int close, int max) {
        // Base case: valid string of length 2n reached
        if (current.length() == max * 2) {
            result.add(current.toString());
            return;
        }

        // Add open parenthesis if we have not reached the limit n
        if (open < max) {
            current.append('(');
            backtrack(result, current, open + 1, close, max);
            current.deleteCharAt(current.length() - 1); // Backtrack
        }

        // Add close parenthesis if it doesn't exceed the number of open ones
        if (close < open) {
            current.append(')');
            backtrack(result, current, open, close + 1, max);
            current.deleteCharAt(current.length() - 1); // Backtrack
        }
    }

    public static void main(String[] args) {
        GenerateParentheses sol = new GenerateParentheses();
        System.out.println(sol.generateParenthesis(3)); 
        // Expected: ["((()))", "(()())", "(())()", "()(())", "()()()"]
    }
}
\"\"\"""",
    'test_code': """def test_generate():
    assert len(generate_parenthesis(3)) == 5""",
    'readme_content': """# Generate Parentheses

## 1. Overview & Problem Explanation
The **Generate Parentheses** challenge asks us to produce every possible combination of $n$ pairs of parentheses such that the resulting strings are **valid**.

### What constitutes "Valid" Parentheses?
A sequence of parentheses is considered valid if:
1. Every opening parenthesis `(` has a corresponding closing parenthesis `)`.
2. At any point while reading the string from left to right, the number of closing parentheses **never exceeds** the number of opening parentheses.
3. The total number of opening parentheses equals the total number of closing parentheses.

### Inputs, Outputs, and Constraints
- **Input**: An integer `n` (e.g., `n = 3`).
- **Output**: A list of strings containing all valid combinations (e.g., `["((()))", "(()())", "(())()", "()(())", "()()()"]`).
- **Constraints**: 
    - $1 \le n \le 8$.
    - The small constraint on $n$ suggests that an exponential time complexity (inherent to combinatorial problems) is acceptable, but we must avoid redundant computations.

### Edge Cases
- **$n = 1$**: The only valid output is `["()"]`.
- **$n = 0$**: Though constraints say $n \ge 1$, mathematically this would be an empty string `[""]`.
- **Invalid State**: If we ever place a `)` before a `(`, the string can never become valid; we must prune that path immediately.

---

## 2. Core Concepts & Data Structures

### Backtracking
The primary algorithmic pattern used here is **Backtracking**. Backtracking is a refined version of recursion used to explore all possible configurations of a solution. Instead of generating all possible $2^{2n}$ permutations and checking them (Brute Force), backtracking allows us to **prune** the search tree. If a partial solution is already invalid, we stop exploring that path.

### The "Balance" Principle
To ensure validity without needing a separate validation function, we track two variables:
1. `open_count`: How many `(` have been placed.
2. `close_count`: How many `)` have been placed.

**The Rules of Placement:**
- **Can we add `(`?** Yes, if `open_count < n`.
- **Can we add `)`?** Yes, if `close_count < open_count`. This rule is the "secret sauce" that prevents invalid sequences like `())`.

### Why this approach?
A Brute Force approach would generate $2^{2n}$ strings. For $n=8$, that's $2^{16} = 65,536$ strings. While small for $n=8$, this grows explosively. By using the balance principle, we only visit states that are guaranteed to lead to a valid solution.

---

## 3. Step-by-Step Logic

### The Recursive Process
1. **Initialize**: Start with an empty string `""`, `open_count = 0`, and `close_count = 0`.
2. **Base Case**: If the length of the current string reaches $2n$, we have successfully built a valid combination. Add it to our result list.
3. **Recursive Step A (Add Open)**: If `open_count < n`, append `(` and recurse.
4. **Recursive Step B (Add Close)**: If `close_count < open_count`, append `)` and recurse.
5. **Backtrack**: Because we are passing the string by value (or using a list that we pop from), the state naturally resets as the recursion unwinds, allowing us to explore other branches.

### Dry Run: $n = 2$
- Start: `""` (open: 0, close: 0)
    - $\rightarrow$ Add `(`: `"("` (open: 1, close: 0)
        - $\rightarrow$ Add `(`: `"(("` (open: 2, close: 0)
            - $\rightarrow$ Add `)`: `"(()"` (open: 2, close: 1)
                - $\rightarrow$ Add `)`: `"(())"` $\rightarrow$ **Valid!**
        - $\rightarrow$ Add `)`: `"()"` (open: 1, close: 1)
            - $\rightarrow$ Add `(`: `"()("` (open: 2, close: 1)
                - $\rightarrow$ Add `)`: `"()()"` $\rightarrow$ **Valid!**

### Implementation

```python
def generate_parenthesis(n: int) -> list[str]:
    result = []
    
    def backtrack(current_string, open_count, close_count):
        # Base case: the string has reached the maximum length
        if len(current_string) == 2 * n:
            result.append(current_string)
            return
        
        # Rule 1: We can add an opening parenthesis if we haven't reached n
        if open_count < n:
            backtrack(current_string + "(", open_count + 1, close_count)
            
        # Rule 2: We can add a closing parenthesis if it won't violate validity
        if close_count < open_count:
            backtrack(current_string + ")", open_count, close_count + 1)
            
    backtrack("", 0, 0)
    return result
```

---

## 4. Complexity Analysis

The complexity of this problem is tied to the **Catalan Number**. The number of valid parentheses sequences for $n$ is given by $C_n = \frac{1}{n+1}\binom{2n}{n}$.

| Complexity | Notation | Reasoning |
| :--- | :--- | :--- |
| **Time Complexity** | $O(\frac{4^n}{\sqrt{n}})$ | The number of valid combinations is the $n$-th Catalan number. Asymptotically, $C_n$ grows at a rate of $\frac{4^n}{n^{1.5}}$. Each valid string takes $O(n)$ to construct. |
| **Space Complexity** | $O(n)$ | The recursion stack depth is $2n$ (the length of the string), and the space for the current string being built is $O(n)$. (Excluding the output list). |

---

## 5. Real-World Applications

While this looks like a brain teaser, the logic of tracking "open/close" balances is fundamental in several software domains:

1. **Compiler Design & Lexing**: Compilers use this exact logic to ensure that brackets, braces, and parentheses in code are balanced. If you get a "Syntax Error: Unexpected `}`", the compiler's internal stack found a `close_count > open_count` state.
2. **JSON/XML Validation**: Parsers verify that every `<tag>` has a corresponding `</tag>` using a stack-based approach mirroring this backtracking logic.
3. **Mathematical Expression Evaluation**: When evaluating expressions like `(a + (b * c))`, the system uses a stack to determine the order of operations based on parenthesis depth.
4. **Linting Tools**: Tools like ESLint or Prettier use these algorithms to auto-format code and identify missing closing brackets.""",
}

"""
Challenge: q01_valid_parentheses
Difficulty: Easy
Link: https://leetcode.com/problems/valid-parentheses/

Problem:
Given a string containing brackets, determine if the input string is valid.
"""

# --- STARTER TEMPLATE FOR USER ---
def is_valid(s: str) -> bool:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Approach 1: Naive (Replace pairs recursively) O(N^2) time, O(1) space
def is_valid_naive(s: str) -> bool:
    old_len = -1
    while len(s) != old_len:
        old_len = len(s)
        s = s.replace('()', '').replace('[]', '').replace('{}', '')
    return len(s) == 0

# Approach 2: Optimal (LIFO Stack) O(N) time, O(N) space
def is_valid_optimal(s: str) -> bool:
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top: return False
        else:
            stack.append(char)
    return not stack

# Approach 3: Java
'''
public boolean isValid(String s) {
    Stack<Character> stack = new Stack<>();
    for (char c : s.toCharArray()) {
        if (c == '(') stack.push(')');
        else if (c == '[') stack.push(']');
        else if (c == '{') stack.push('}');
        else if (stack.isEmpty() || stack.pop() != c) return false;
    }
    return stack.isEmpty();
}
'''

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

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

"""
Challenge: q04_generate_parentheses
Difficulty: Medium
Link: https://leetcode.com/problems/generate-parentheses/

Problem:
Generate all combinations of n pairs of valid parentheses.
"""

# --- STARTER TEMPLATE FOR USER ---
def generate_parenthesis(n: int) -> list[str]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

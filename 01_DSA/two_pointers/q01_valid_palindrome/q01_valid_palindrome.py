"""
Challenge: q01_valid_palindrome
Difficulty: Easy
Link: https://leetcode.com/problems/valid-palindrome/

Problem:
Check if a string is a palindrome, ignoring non-alphanumeric chars.
"""

# --- STARTER TEMPLATE FOR USER ---
def is_palindrome(s: str) -> bool:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Approach 1: Brute Force (Clean & Reverse) O(N) time, O(N) space
def is_palindrome_naive(s: str) -> bool:
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]

# Approach 2: Optimal (Two Pointers) O(N) time, O(1) space
def is_palindrome_optimal(s: str) -> bool:
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum(): l += 1
        while l < r and not s[r].isalnum(): r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l += 1
        r -= 1
    return True

# Approach 3: Java
'''
public boolean isPalindrome(String s) {
    int l = 0, r = s.length() - 1;
    while(l < r) {
        if (!Character.isLetterOrDigit(s.charAt(l))) l++;
        else if (!Character.isLetterOrDigit(s.charAt(r))) r--;
        else if (Character.toLowerCase(s.charAt(l++)) != Character.toLowerCase(s.charAt(r--))) return false;
    }
    return true;
}
'''

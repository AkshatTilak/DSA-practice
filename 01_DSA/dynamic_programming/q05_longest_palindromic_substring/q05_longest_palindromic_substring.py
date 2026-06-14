"""
Challenge: q05_longest_palindromic_substring
Difficulty: Medium
Link: https://leetcode.com/problems/longest-palindromic-substring/

Problem:
Find longest palindrome.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^3)
# Space Complexity: O(1)
# This approach iterates through every possible substring of the given string, checks if it is a palindrome by comparing it with its reverse, and keeps track of the longest one found.
def solve_naive(s: str) -> str:
    if not s:
        return ""
    
    longest_pal = ""
    n = len(s)
    
    for i in range(n):
        for j in range(i, n):
            # Extract substring
            substring = s[i : j + 1]
            # Check if palindrome
            if substring == substring[::-1]:
                if len(substring) > len(longest_pal):
                    longest_pal = substring
                    
    return longest_pal

# --- APPROACH 2: Optimal (Expand Around Center) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach treats each character (and the gap between characters) as a potential center of a palindrome. 
# It expands outwards as long as the characters match. This is optimal for most production scenarios 
# because it reduces space complexity to O(1) compared to the O(n^2) space required by the standard 
# Dynamic Programming table approach, while maintaining the same O(n^2) time complexity.
def solve_optimal(s: str) -> str:
    if not s or len(s) < 1:
        return ""
    
    start = 0
    end = 0
    
    def expand_around_center(left: int, right: int) -> int:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        # The loop ends when s[left] != s[right] or boundaries are hit.
        # Length is (right - 1) - (left + 1) + 1 = right - left - 1
        return right - left - 1
    
    for i in range(len(s)):
        # Odd length palindromes (single character center)
        len1 = expand_around_center(i, i)
        # Even length palindromes (gap between two characters as center)
        len2 = expand_around_center(i, i + 1)
        
        max_len = max(len1, len2)
        if max_len > (end - start + 1):
            # Calculate new start and end indices
            # For odd: start = i - (max_len-1)//2, end = i + max_len//2
            # For even: start = i - (max_len-1)//2, end = i + max_len//2
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
            
    return s[start : end + 1]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

public class LongestPalindromicSubstring {
    public String solveOptimal(String s) {
        if (s == null || s.length() < 1) {
            return "";
        }
        
        int start = 0;
        int end = 0;
        
        for (int i = 0; i < s.length(); i++) {
            int len1 = expandAroundCenter(s, i, i);
            int len2 = expandAroundCenter(s, i, i + 1);
            int maxLen = Math.max(len1, len2);
            
            if (maxLen > end - start + 1) {
                start = i - (maxLen - 1) / 2;
                end = i + maxLen / 2;
            }
        }
        
        return s.substring(start, end + 1);
    }
    
    private int expandAroundCenter(String s, int left, int right) {
        while (left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right)) {
            left--;
            right++;
        }
        return right - left - 1;
    }

    public static void main(String[] args) {
        LongestPalindromicSubstring solver = new LongestPalindromicSubstring();
        System.out.println(solver.solveOptimal("babad")); // Output: "bab" or "aba"
        System.out.println(solver.solveOptimal("cbbd"));  // Output: "bb"
    }
}
"""

"""
Challenge: q06_decode_ways
Difficulty: Medium
Link: https://leetcode.com/problems/decode-ways/

Problem:
Ways to decode string.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(2^n)
# Space Complexity: O(n)
# A recursive approach that explores all possible decoding combinations. At each step, it attempts to take either one digit (if not '0') or two digits (if the value is between 10 and 26).
def solve_naive(s: str) -> int:
    if not s:
        return 0
    
    def backtrack(index):
        # Base case: reached the end of the string
        if index == len(s):
            return 1
        
        # If the current character is '0', it's an invalid decoding path
        if s[index] == '0':
            return 0
        
        # Option 1: Decode a single character
        ways = backtrack(index + 1)
        
        # Option 2: Decode two characters if they form a number between 10 and 26
        if index + 1 < len(s):
            two_digit = int(s[index : index + 2])
            if 10 <= two_digit <= 26:
                ways += backtrack(index + 2)
        
        return ways

    return backtrack(0)

# --- APPROACH 2: Optimal (Dynamic Programming with Space Optimization) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses bottom-up dynamic programming. We observe that the number of ways to decode a string of length i depends only on the results for lengths i-1 and i-2. 
# By using two variables instead of a full DP array, we reduce the space complexity from O(n) to O(1).
def solve_optimal(s: str) -> int:
    if not s or s[0] == '0':
        return 0
    
    n = len(s)
    # prev2 represents dp[i-2], prev1 represents dp[i-1]
    prev2 = 1  # Ways to decode an empty string
    prev1 = 1  # Ways to decode a string of length 1 (already checked s[0] != '0')
    
    for i in range(2, n + 1):
        current = 0
        # One-digit check: The current digit must not be '0'
        if s[i-1] != '0':
            current += prev1
        
        # Two-digit check: The digits at i-2 and i-1 must form a number between 10 and 26
        two_digit = int(s[i-2 : i])
        if 10 <= two_digit <= 26:
            current += prev2
            
        # Update variables for next iteration
        prev2 = prev1
        prev1 = current
        
        # Optimization: if current ways become 0, the rest of the string cannot be decoded
        if current == 0:
            return 0
            
    return prev1

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package dynamic_programming;

public class DecodeWays {
    /**
     * Calculates the number of ways to decode a string based on the mapping 1->A, ..., 26->Z.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int numDecodings(String s) {
        if (s == null || s.length() == 0 || s.charAt(0) == '0') {
            return 0;
        }

        int n = s.length();
        int prev2 = 1; // Equivalent to dp[i-2]
        int prev1 = 1; // Equivalent to dp[i-1]

        for (int i = 2; i <= n; i++) {
            int current = 0;
            
            // Single digit check
            char oneDigit = s.charAt(i - 1);
            if (oneDigit != '0') {
                current += prev1;
            }

            // Double digit check
            int twoDigits = Integer.parseInt(s.substring(i - 2, i));
            if (twoDigits >= 10 && twoDigits <= 26) {
                current += prev2;
            }

            if (current == 0) {
                return 0;
            }

            prev2 = prev1;
            prev1 = current;
        }

        return prev1;
    }

    public static void main(String[] args) {
        DecodeWays dw = new DecodeWays();
        System.out.println(dw.numDecodings("12"));   // Output: 2
        System.out.println(dw.numDecodings("226"));  // Output: 3
        System.out.println(dw.numDecodings("06"));   // Output: 0
    }
}
"""

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

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach filters the string to include only alphanumeric characters, converts it to lowercase, and compares the resulting string with its reverse.
def is_palindrome_naive(s: str) -> bool:
    filtered_chars = [char.lower() for char in s if char.isalnum()]
    return filtered_chars == filtered_chars[::-1]

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses two pointers starting from both ends of the string, moving inward. It skips non-alphanumeric characters on the fly, avoiding the creation of a new string. This is optimal because it minimizes space usage to constant space while maintaining linear time complexity.
def is_palindrome_optimal(s: str) -> bool:
    left, right = 0, len(s) - 1
    
    while left < right:
        # Skip non-alphanumeric characters from the left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric characters from the right
        while left < right and not s[right].isalnum():
            right -= 1
        
        # Compare characters case-insensitively
        if s[left].lower() != s[right].lower():
            return False
        
        left += 1
        right -= 1
        
    return True

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package two_pointers;

public class ValidPalindrome {
    /**
     * Checks if a string is a palindrome, ignoring non-alphanumeric characters and case.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public boolean isPalindrome(String s) {
        if (s == null) return false;
        
        int left = 0;
        int right = s.length() - 1;
        
        while (left < right) {
            char leftChar = s.charAt(left);
            char rightChar = s.charAt(right);
            
            if (!Character.isLetterOrDigit(leftChar)) {
                left++;
            } else if (!Character.isLetterOrDigit(rightChar)) {
                right--;
            } else {
                if (Character.toLowerCase(leftChar) != Character.toLowerCase(rightChar)) {
                    return false;
                }
                left++;
                right--;
            }
        }
        
        return true;
    }

    public static void main(String[] args) {
        ValidPalindrome vp = new ValidPalindrome();
        System.out.println(vp.isPalindrome("A man, a plan, a canal: Panama")); // true
        System.out.println(vp.isPalindrome("race a car")); // false
    }
}
"""

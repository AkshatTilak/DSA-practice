"""
Challenge: q02_longest_substring_without_repeating_characters
Difficulty: Medium
Link: https://leetcode.com/problems/longest-substring-without-repeating-characters/

Problem:
Find the length of the longest substring without repeating characters.
"""

# --- STARTER TEMPLATE FOR USER ---
def length_of_longest_substring(s: str) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^3)
# Space Complexity: O(min(N, M)) where M is the size of the character set.
# The naive approach generates every possible substring (O(N^2)) and checks if each 
# substring contains unique characters by using a set (O(N)), resulting in O(N^3).
def length_of_longest_substring_naive(s: str) -> int:
    n = len(s)
    max_length = 0
    for i in range(n):
        for j in range(i + 1, n + 1):
            substring = s[i:j]
            if len(set(substring)) == len(substring):
                max_length = max(max_length, len(substring))
    return max_length

# --- APPROACH 2: Optimal (Sliding Window with HashMap) ---
# Time Complexity: O(N)
# Space Complexity: O(min(N, M)) where M is the size of the character set.
# This approach uses a sliding window defined by two pointers. A dictionary stores 
# the last seen index of each character. When a duplicate is encountered, the 
# left pointer jumps to the position after the previous occurrence of that character, 
# ensuring the window always contains unique characters. It is optimal because it 
# traverses the string only once.
def length_of_longest_substring_optimal(s: str) -> int:
    char_map = {}
    max_length = 0
    start = 0
    
    for end in range(len(s)):
        char = s[end]
        # If character is in map and within the current window, move start
        if char in char_map and char_map[char] >= start:
            start = char_map[char] + 1
        
        # Update last seen index of the character
        char_map[char] = end
        # Calculate window length and update max_length
        max_length = max(max_length, end - start + 1)
        
    return max_length

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package sliding_window;

import java.util.HashMap;
import java.util.Map;

public class LongestSubstringWithoutRepeatingCharacters {
    /**
     * Finds the length of the longest substring without repeating characters.
     * Time Complexity: O(N)
     * Space Complexity: O(min(N, M))
     */
    public int lengthOfLongestSubstring(String s) {
        if (s == null || s.length() == 0) {
            return 0;
        }

        Map<Character, Integer> charMap = new HashMap<>();
        int maxLength = 0;
        int start = 0;

        for (int end = 0; end < s.length(); end++) {
            char currentChar = s.charAt(end);
            
            if (charMap.containsKey(currentChar)) {
                // Ensure the start pointer only moves forward
                start = Math.max(start, charMap.get(currentChar) + 1);
            }
            
            charMap.put(currentChar, end);
            maxLength = Math.max(maxLength, end - start + 1);
        }

        return maxLength;
    }

    public static void main(String[] args) {
        LongestSubstringWithoutRepeatingCharacters solver = new LongestSubstringWithoutRepeatingCharacters();
        System.out.println(solver.lengthOfLongestSubstring("abcabcbb")); // Output: 3
        System.out.println(solver.lengthOfLongestSubstring("bbbbb"));    // Output: 1
        System.out.println(solver.lengthOfLongestSubstring("pwwkew"));   // Output: 3
    }
}
"""

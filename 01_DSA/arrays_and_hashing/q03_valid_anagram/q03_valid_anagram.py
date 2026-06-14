"""
Challenge: q03_valid_anagram
Difficulty: Easy
Link: https://leetcode.com/problems/valid-anagram/

Problem:
Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.
"""

# --- STARTER TEMPLATE FOR USER ---
def is_anagram(s: str, t: str) -> bool:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n log n)
# Space Complexity: O(n)
# This approach sorts both strings and compares them. If two strings are anagrams, their sorted versions must be identical. 
# Sorting takes O(n log n) time and O(n) space in Python due to the sorted() function creating a new list.
def is_anagram_naive(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    return sorted(s) == sorted(t)

# --- APPROACH 2: Optimal (Hash Map/Frequency Counter) ---
# Time Complexity: O(n)
# Space Complexity: O(k)
# This approach uses a frequency map (dictionary) to count occurrences of each character. 
# It is optimal because it traverses the strings only once, resulting in linear time complexity. 
# Space complexity is O(k) where k is the number of unique characters in the alphabet (constant O(1) if limited to English letters).
def is_anagram_optimal(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    
    count = {}
    
    # Increment counts for string s
    for char in s:
        count[char] = count.get(char, 0) + 1
        
    # Decrement counts for string t
    for char in t:
        if char not in count:
            return False
        count[char] -= 1
        if count[char] < 0:
            return False
            
    return True

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.HashMap;
import java.util.Map;

public class ValidAnagram {
    /**
     * Determines if string t is an anagram of string s.
     * This implementation uses a frequency array for optimal performance, 
     * assuming the input consists of lowercase English letters.
     */
    public boolean isAnagram(String s, String t) {
        if (s == null || t == null || s.length() != t.length()) {
            return false;
        }

        // Using an integer array as a fixed-size hash map for lowercase 'a'-'z'
        int[] charCounts = new int[26];

        for (int i = 0; i < s.length(); i++) {
            charCounts[s.charAt(i) - 'a']++;
            charCounts[t.charAt(i) - 'a']--;
        }

        for (int count : charCounts) {
            if (count != 0) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        ValidAnagram va = new ValidAnagram();
        System.out.println(va.isAnagram("anagram", "nagaram")); // true
        System.out.println(va.isAnagram("rat", "car"));         // false
    }
}
"""

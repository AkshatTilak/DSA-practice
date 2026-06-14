"""
Challenge: q03_longest_repeating_character_replacement
Difficulty: Medium
Link: https://leetcode.com/problems/longest-repeating-character-replacement/

Problem:
Find length of longest repeating substring after replacing at most k characters.
"""

# --- STARTER TEMPLATE FOR USER ---
def character_replacement(s: str, k: int) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# The naive approach iterates through all possible substrings. For each substring, 
# it calculates the frequency of the most frequent character. If the number of 
# characters that need to be replaced (length - max_frequency) is less than or 
# equal to k, the substring is valid.
def character_replacement_naive(s: str, k: int) -> int:
    if not s:
        return 0
    
    max_length = 0
    n = len(s)
    
    for i in range(n):
        counts = {}
        max_f = 0
        for j in range(i, n):
            char = s[j]
            counts[char] = counts.get(char, 0) + 1
            max_f = max(max_f, counts[char])
            
            # Window length is (j - i + 1)
            # Characters to replace is (window_length - max_f)
            if (j - i + 1) - max_f <= k:
                max_length = max(max_length, j - i + 1)
            else:
                # Once the condition is violated for a fixed start i, 
                # expanding further will only increase the needed replacements.
                break
                
    return max_length

# --- APPROACH 2: Optimal (Sliding Window) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# We use a sliding window defined by two pointers, left and right. We maintain a 
# frequency map of characters currently in the window. The key insight is that 
# a window is valid if (window_width - max_frequency_in_window <= k).
# We maintain 'max_freq' as the maximum frequency of any single character encountered 
# in any window so far. We only shift the left pointer when the current window 
# becomes invalid. Since we only care about finding a window larger than the 
# previous maximum, 'max_freq' does not need to be decremented when shrinking the 
# window, as a smaller max_freq would not lead to a larger window.
def character_replacement_optimal(s: str, k: int) -> int:
    if not s:
        return 0
    
    count = {}
    max_length = 0
    max_freq = 0
    left = 0
    
    for right in range(len(s)):
        char = s[right]
        count[char] = count.get(char, 0) + 1
        
        # Update the maximum frequency found in any window so far
        max_freq = max(max_freq, count[char])
        
        # Current window size is (right - left + 1)
        # If the number of characters to replace exceeds k, shrink window from left
        while (right - left + 1) - max_freq > k:
            count[s[left]] -= 1
            left += 1
            
        max_length = max(max_length, right - left + 1)
        
    return max_length

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package sliding_window;

import java.util.HashMap;
import java.util.Map;

public class LongestRepeatingCharacterReplacement {
    /**
     * Finds the length of the longest repeating substring after replacing at most k characters.
     * Time Complexity: O(n) where n is the length of the string.
     * Space Complexity: O(1) since the alphabet size is constant (26 characters).
     */
    public int characterReplacement(String s, int k) {
        if (s == null || s.length() == 0) {
            return 0;
        }

        int[] counts = new int[26];
        int left = 0;
        int maxFreq = 0;
        int maxLength = 0;

        for (int right = 0; right < s.length(); right++) {
            char currentRight = s.charAt(right);
            counts[currentRight - 'A']++;
            
            // Update maxFreq to track the most frequent character seen in any window
            maxFreq = Math.max(maxFreq, counts[currentRight - 'A']);

            // If the window is invalid (replacements > k), slide the left pointer
            while ((right - left + 1) - maxFreq > k) {
                char currentLeft = s.charAt(left);
                counts[currentLeft - 'A']--;
                left++;
            }

            maxLength = Math.max(maxLength, right - left + 1);
        }

        return maxLength;
    }

    public static void main(String[] args) {
        LongestRepeatingCharacterReplacement sol = new LongestRepeatingCharacterReplacement();
        System.out.println(sol.characterReplacement("AABABBA", 1)); // Expected: 4
        System.out.println(sol.characterReplacement("ABAB", 2));    // Expected: 4
    }
}
"""

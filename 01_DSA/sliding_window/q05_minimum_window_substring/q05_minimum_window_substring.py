"""
Challenge: q05_minimum_window_substring
Difficulty: Hard
Link: https://leetcode.com/problems/minimum-window-substring/

Problem:
Find the minimum window in s containing all characters of t.
"""

# --- STARTER TEMPLATE FOR USER ---
def min_window(s: str, t: str) -> str:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^3) where n is the length of s. We iterate through all possible substrings (n^2) and for each, we check character counts (n).
# Space Complexity: O(k) where k is the number of unique characters in t.
# This approach checks every possible substring of s to see if it contains all the characters of t, keeping track of the minimum length found.
from collections import Counter

def min_window_naive(s: str, t: str) -> str:
    if not t or not s:
        return ""
    
    t_count = Counter(t)
    min_len = float('inf')
    result = ""
    
    for i in range(len(s)):
        for j in range(i, len(s)):
            substring = s[i:j+1]
            sub_count = Counter(substring)
            
            is_valid = True
            for char, count in t_count.items():
                if sub_count[char] < count:
                    is_valid = False
                    break
            
            if is_valid:
                if len(substring) < min_len:
                    min_len = len(substring)
                    result = substring
                    
    return result

# --- APPROACH 2: Optimal (Sliding Window) ---
# Time Complexity: O(s + t) where s and t are lengths of the respective strings. Each character is visited at most twice (once by right pointer, once by left).
# Space Complexity: O(k) where k is the number of unique characters in s and t.
# This approach uses two pointers to maintain a sliding window. We expand the right pointer to find a valid window and then contract the left pointer to minimize the window size. 
# This is optimal because it avoids redundant checks and processes the string in linear time.
from collections import Counter

def min_window_optimal(s: str, t: str) -> str:
    if not t or not s:
        return ""

    # Frequency map of characters required from t
    dict_t = Counter(t)
    required = len(dict_t)
    
    # Window tracking
    l, r = 0, 0
    # formed is used to keep track of how many unique characters in t are present in the current window in desired frequency.
    formed = 0
    window_counts = {}
    
    # ans tuple of (window length, left, right)
    ans = float("inf"), None, None
    
    while r < len(s):
        char = s[r]
        window_counts[char] = window_counts.get(char, 0) + 1
        
        # If the frequency of the current character matches the desired count in t
        if char in dict_t and window_counts[char] == dict_t[char]:
            formed += 1
            
        # Try and contract the window till the point where it ceases to be 'desirable'.
        while l <= r and formed == required:
            char = s[l]
            
            # Save the smallest window until now.
            if r - l + 1 < ans[0]:
                ans = (r - l + 1, l, r)
            
            # The character at the position pointed by the `left` pointer is no longer a part of the window.
            window_counts[char] -= 1
            if char in dict_t and window_counts[char] < dict_t[char]:
                formed -= 1
                
            l += 1
            
        r += 1
        
    return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]

# Alias to match starter code requirement
def min_window(s: str, t: str) -> str:
    return min_window_optimal(s, t)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package sliding_window;

import java.util.*;

public class MinimumWindowSubstring {
    public String minWindow(String s, String t) {
        if (s == null || t == null || s.length() < t.length()) {
            return "";
        }

        Map<Character, Integer> dictT = new HashMap<>();
        for (char c : t.toCharArray()) {
            dictT.put(c, dictT.getOrDefault(c, 0) + 1);
        }

        int required = dictT.size();
        int l = 0, r = 0;
        int formed = 0;
        Map<Character, Integer> windowCounts = new HashMap<>();

        int minLen = Integer.MAX_VALUE;
        int minLeft = 0;

        while (r < s.length()) {
            char c = s.charAt(r);
            windowCounts.put(c, windowCounts.getOrDefault(c, 0) + 1);

            if (dictT.containsKey(c) && windowCounts.get(c).equals(dictT.get(c))) {
                formed++;
            }

            while (l <= r && formed == required) {
                char leftChar = s.charAt(l);

                if (r - l + 1 < minLen) {
                    minLen = r - l + 1;
                    minLeft = l;
                }

                windowCounts.put(leftChar, windowCounts.get(leftChar) - 1);
                if (dictT.containsKey(leftChar) && windowCounts.get(leftChar) < dictT.get(leftChar)) {
                    formed--;
                }
                l++;
            }
            r++;
        }

        return minLen == Integer.MAX_VALUE ? "" : s.substring(minLeft, minLeft + minLen);
    }
}
"""

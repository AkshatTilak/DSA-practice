"""
Challenge: q04_permutation_in_string
Difficulty: Medium
Link: https://leetcode.com/problems/permutation-in-string/

Problem:
Return true if s2 contains a permutation of s1.
"""

# --- STARTER TEMPLATE FOR USER ---
def check_inclusion(s1: str, s2: str) -> bool:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O((n - m + 1) * m log m)
# Space Complexity: O(m)
# The naive approach iterates through every possible substring of s2 with the same length as s1.
# For each substring, it sorts the characters and compares the result to the sorted version of s1.
def check_inclusion_naive(s1: str, s2: str) -> bool:
    n1, n2 = len(s1), len(s2)
    if n1 > n2:
        return False
    
    sorted_s1 = sorted(s1)
    for i in range(n2 - n1 + 1):
        window = s2[i : i + n1]
        if sorted(window) == sorted_s1:
            return True
    return False

# --- APPROACH 2: Optimal (Sliding Window with Frequency Map) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses a fixed-size sliding window of length len(s1). 
# Instead of sorting, we maintain frequency counts of characters in s1 and the current window of s2.
# Since the character set is limited to 26 lowercase English letters, the space is constant O(1) 
# and comparing two frequency arrays takes O(26), which is also O(1).
def check_inclusion_optimal(s1: str, s2: str) -> bool:
    n1, n2 = len(s1), len(s2)
    if n1 > n2:
        return False

    s1_counts = [0] * 26
    window_counts = [0] * 26

    # Initialize frequencies for s1 and the first window of s2
    for i in range(n1):
        s1_counts[ord(s1[i]) - ord('a')] += 1
        window_counts[ord(s2[i]) - ord('a')] += 1

    if s1_counts == window_counts:
        return True

    # Slide the window across s2
    for i in range(n1, n2):
        # Add the new character on the right
        window_counts[ord(s2[i]) - ord('a')] += 1
        # Remove the character that is no longer in the window on the left
        window_counts[ord(s2[i - n1]) - ord('a')] -= 1
        
        if s1_counts == window_counts:
            return True

    return False

# To match the starter code's function name
def check_inclusion(s1: str, s2: str) -> bool:
    return check_inclusion_optimal(s1, s2)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package sliding_window;

import java.util.Arrays;

public class PermutationInString {
    /**
     * Checks if s2 contains a permutation of s1.
     * Time Complexity: O(n), where n is the length of s2.
     * Space Complexity: O(1), as the frequency array size is constant (26).
     */
    public boolean checkInclusion(String s1, String s2) {
        int n1 = s1.length();
        int n2 = s2.length();
        
        if (n1 > n2) {
            return false;
        }
        
        int[] s1Counts = new int[26];
        int[] windowCounts = new int[26];
        
        // Initialize frequencies for s1 and the first window of s2
        for (int i = 0; i < n1; i++) {
            s1Counts[s1.charAt(i) - 'a']++;
            windowCounts[s2.charAt(i) - 'a']++;
        }
        
        if (Arrays.equals(s1Counts, windowCounts)) {
            return true;
        }
        
        // Slide the window across s2
        for (int i = n1; i < n2; i++) {
            // Add the character on the right of the window
            windowCounts[s2.charAt(i) - 'a']++;
            // Remove the character on the left of the window
            windowCounts[s2.charAt(i - n1) - 'a']--;
            
            if (Arrays.equals(s1Counts, windowCounts)) {
                return true;
            }
        }
        
        return false;
    }

    public static void main(String[] args) {
        PermutationInString solution = new PermutationInString();
        System.out.println(solution.checkInclusion("ab", "eidbaooo")); // Expected: true
        System.out.println(solution.checkInclusion("ab", "eidboaoo")); // Expected: false
    }
}
"""

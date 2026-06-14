"""
Challenge: q04_group_anagrams
Difficulty: Medium
Link: https://leetcode.com/problems/group-anagrams/

Problem:
Group an array of strings together if they are anagrams.
"""

# --- STARTER TEMPLATE FOR USER ---
def group_anagrams(strs: list[str]) -> list[list[str]]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2 * K)
# Space Complexity: O(N * K)
# This approach uses a nested loop to compare every pair of strings. 
# For each pair, it checks if they are anagrams by comparing character frequencies.
def group_anagrams_naive(strs: list[str]) -> list[list[str]]:
    def is_anagram(s1: str, s2: str) -> bool:
        if len(s1) != len(s2):
            return False
        count = {}
        for char in s1:
            count[char] = count.get(char, 0) + 1
        for char in s2:
            if char not in count or count[char] == 0:
                return False
            count[char] -= 1
        return True

    res = []
    used = [False] * len(strs)
    for i in range(len(strs)):
        if used[i]:
            continue
        group = [strs[i]]
        used[i] = True
        for j in range(i + 1, len(strs)):
            if not used[j] and is_anagram(strs[i], strs[j]):
                group.append(strs[j])
                used[j] = True
        res.append(group)
    return res

# --- APPROACH 2: Optimal (Frequency Hash Map) ---
# Time Complexity: O(N * K)
# Space Complexity: O(N * K)
# This approach is optimal because it processes each string exactly once and each character once.
# Instead of sorting the strings (which would take O(N * K log K)), it uses a character count 
# tuple of size 26 as the dictionary key, ensuring linear time complexity relative to the total 
# number of characters across all strings.
from collections import defaultdict

def group_anagrams_optimal(strs: list[str]) -> list[list[str]]:
    # Map of character frequency tuple to list of anagrams
    groups = defaultdict(list)
    
    for s in strs:
        # Initialize frequency array for 'a'-'z'
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1
        
        # Convert list to tuple to be usable as a dictionary key
        groups[tuple(count)].append(s)
        
    return list(groups.values())

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.*;

public class GroupAnagrams {
    /**
     * Groups anagrams using a frequency map strategy.
     * Time Complexity: O(N * K)
     * Space Complexity: O(N * K)
     */
    public List<List<String>> groupAnagrams(String[] strs) {
        if (strs == null || strs.length == 0) {
            return new ArrayList<>();
        }

        Map<String, List<String>> map = new HashMap<>();
        for (String s : strs) {
            int[] count = new int[26];
            for (char c : s.toCharArray()) {
                count[c - 'a']++;
            }
            
            // Create a unique string key based on the frequency array
            // Example: "eat" -> "#1#0#0#0#1#0...#1#0...#0"
            StringBuilder sb = new StringBuilder();
            for (int i : count) {
                sb.append('#');
                sb.append(i);
            }
            String key = sb.toString();
            
            map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }
        
        return new ArrayList<>(map.values());
    }
}
"""

INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/longest-substring-without-repeating-characters/',
    'description': 'Find the length of the longest substring without repeating characters.',
    'groups': ['String', 'Sliding Window', 'Hashing'],
    'starter_code': """def length_of_longest_substring(s: str) -> int:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_longest():
    assert length_of_longest_substring('abcabcbb') == 3""",
    'readme_content': """# Longest Substring Without Repeating Characters

## 📖 Overview & Problem Explanation

The goal of this challenge is to find the length of the **longest contiguous substring** within a given string that contains **no repeating characters**.

### Understanding the Problem
A **substring** is a contiguous sequence of characters within a string. For example, in the string `"abcabcbb"`, `"abc"` is a substring, but `"abb"` (skipping characters) is not. The "without repeating characters" constraint means every character in that substring must be unique.

**Example Scenarios:**
- **Input:** `s = "abcabcbb"` $\rightarrow$ **Output:** `3` (The longest substring is `"abc"`)
- **Input:** `s = "bbbbb"` $\rightarrow$ **Output:** `1` (The longest substring is `"b"`)
- **Input:** `s = "pwwkew"` $\rightarrow$ **Output:** `3` (The longest substring is `"wke"`. Note that `"pwke"` is a *subsequence*, not a *substring*.)
- **Input:** `s = ""` $\rightarrow$ **Output:** `0` (Empty string)

### Constraints & Edge Cases
- **Constraints:** The string length can range from $0$ to $5 \times 10^4$. Characters can be letters, digits, symbols, and spaces.
- **Edge Cases:**
    - **Empty String:** Should return `0`.
    - **All Identical Characters:** Should return `1`.
    - **All Unique Characters:** Should return the total length of the string.
    - **Case Sensitivity:** Usually, 'A' and 'a' are treated as different characters.

---

## ⚙️ Core Concepts & Data Structures

To solve this problem efficiently, we use a combination of the **Sliding Window** pattern and a **Hash Map (or Set)**.

### 1. The Sliding Window Pattern
The sliding window is used to track a "window" of the current substring being evaluated. Instead of re-checking every possible substring (which would be computationally expensive), we maintain two pointers: `left` and `right`.
- The `right` pointer expands the window to explore new characters.
- The `left` pointer shrinks the window from the left to remove duplicates when a repeating character is encountered.

### 2. Hashing for Fast Lookup
We need a way to instantly determine if a character is already present in our current window. 
- A **Hash Set** can tell us *if* a character exists.
- A **Hash Map** can tell us *where* (the index) the character last appeared. This allows us to "jump" the `left` pointer forward rather than incrementing it one by one, further optimizing the process.

**Why this is optimal:** 
The sliding window ensures we only traverse the string once ($O(N)$), and the Hash Map ensures our character checks happen in constant time ($O(1)$).

---

## 🚀 Step-by-Step Logic

### Naive Approach (Brute Force)
1. Generate every possible substring of the input string.
2. For each substring, check if all characters are unique using a set.
3. Keep track of the maximum length found.
- **Downside:** This requires $O(N^2)$ substrings and $O(N)$ to check each, leading to $O(N^3)$ time complexity. This is too slow for large inputs.

### Optimal Approach (Sliding Window with Map)
The optimal approach uses a map to store the **last seen index** of each character.

1. **Initialize:**
   - `char_map = {}` (to store `{character: last_index}`)
   - `left = 0` (the start of the window)
   - `max_length = 0`
2. **Iterate:** Move the `right` pointer from $0$ to $N-1$.
3. **Check for Duplicate:** If the current character `s[right]` is already in the map:
   - We need to move the `left` pointer. However, we only move `left` if the last seen position of `s[right]` is **inside** the current window (`index >= left`).
   - Update `left = char_map[s[right]] + 1`.
4. **Update Map:** Store the current index of the character: `char_map[s[right]] = right`.
5. **Calculate Length:** Calculate the current window size (`right - left + 1`) and update `max_length` if it is larger than the previous maximum.

#### Dry Run: `s = "abba"`
| Step | right | char | map | left | Window | max_len | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 0 | 'a' | `{'a': 0}` | 0 | `"a"` | 1 | New char |
| 2 | 1 | 'b' | `{'a': 0, 'b': 1}` | 0 | `"ab"` | 2 | New char |
| 3 | 2 | 'b' | `{'a': 0, 'b': 2}` | 2 | `"b"` | 2 | Duplicate 'b' at index 1. `left = 1 + 1 = 2` |
| 4 | 3 | 'a' | `{'a': 3, 'b': 2}` | 2 | `"ba"` | 2 | 'a' exists at index 0, but $0 < left(2)$, so ignore. |

**Final Result:** 2

---

## 💻 Implementation

```python
def length_of_longest_substring(s: str) -> int:
    # Map to store the last seen index of each character
    char_map = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        char = s[right]
        
        # If the character is in the map and its index is within the current window
        if char in char_map and char_map[char] >= left:
            # Move the left pointer to the right of the previous occurrence
            left = char_map[char] + 1
            
        # Update the last seen index of the character
        char_map[char] = right
        
        # Calculate the window size and update max_length
        current_window_len = right - left + 1
        max_length = max(max_length, current_window_len)
        
    return max_length
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(N^3)$ | $O(K)$ | Three nested loops: two for substrings, one for uniqueness check. |
| **Optimal Sliding Window** | $O(N)$ | $O(\min(m, n))$ | We traverse the string once. Space is used for the map, limited by the size of the character set $m$. |

- **Time Complexity $O(N)$:** Each pointer (`left` and `right`) travels across the string at most once.
- **Space Complexity $O(\min(m, n))$:** The hash map stores at most $n$ characters (length of string) or $m$ characters (the total number of unique characters in the character set/alphabet), whichever is smaller.

---

## 🌐 Real-World Applications

The "Longest Substring" pattern and the Sliding Window technique are fundamental in many production systems:

1. **Network Packet Analysis:** Detecting repeating patterns or "heartbeat" signals in a stream of data packets to identify potential protocol errors or security threats (DDoS signatures).
2. **Text Processing & NLP:** Used in tokenization algorithms to find unique sequences of characters or words for indexing and search normalization.
3. **Bioinformatics:** Identifying the longest unique sequence of nucleotides (DNA/RNA) in a genomic string to find specific genetic markers.
4. **Data Deduplication:** Implementing algorithms that scan buffers for repeating data chunks to compress files or optimize storage.""",
}

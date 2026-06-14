INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/longest-repeating-character-replacement/',
    'description': 'Find length of longest repeating substring after replacing at most k characters.',
    'groups': ['String', 'Sliding Window'],
    'starter_code': """def character_replacement(s: str, k: int) -> int:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_replacement():
    assert character_replacement('ABAB', 2) == 4""",
    'readme_content': """# Longest Repeating Character Replacement

## 📌 Overview & Problem Explanation

The **Longest Repeating Character Replacement** problem asks us to find the length of the longest possible substring consisting of the same character, given that we are allowed to change up to $k$ characters in the original string to any other uppercase English character.

Essentially, we are looking for a "window" in the string where the number of characters that *differ* from the most frequent character in that window is less than or equal to $k$.

### Input & Output
- **Input**: 
    - `s`: A string consisting of uppercase English letters.
    - `k`: An integer representing the maximum number of characters we can replace.
- **Output**: 
    - An integer representing the length of the longest valid substring.

### Constraints & Edge Cases
- **Constraints**: $1 \le s.length \le 10^5$, $0 \le k \le s.length$.
- **Edge Cases**:
    - $k = 0$: No replacements allowed; the problem becomes finding the longest substring of identical characters.
    - $k \ge s.length$: We can replace every character, so the answer is simply the length of the string.
    - String with all identical characters: The answer is the length of the string.
    - String with all unique characters: The answer is $1 + k$ (capped at string length).

---

## 💡 Core Concepts & Data Structures

### 1. The Sliding Window Pattern
This problem is a classic application of the **Sliding Window** technique. Instead of checking every possible substring (which would be computationally expensive), we maintain a dynamic window defined by two pointers: `left` and `right`. We expand the window to find a potential solution and shrink it only when the current window violates the given constraint.

### 2. The "Validity" Formula
To determine if a window is "valid" (i.e., can be turned into a string of repeating characters using $k$ replacements), we use this logic:
$$\text{Window Length} - \text{Frequency of Most Frequent Character} \le k$$

**Why?** 
If the most frequent character appears $max\_freq$ times in a window of size $L$, then there are $L - max\_freq$ characters that are *not* the most frequent. To make the entire window consist of one repeating character, we must replace all those "other" characters. If this count is $\le k$, the window is valid.

### 3. Frequency Map
We use a **Hash Map** (or an array of size 26) to keep track of the counts of each character currently inside the sliding window. This allows us to update the `max_freq` in constant time as the window slides.

---

## 🛠️ Step-by-Step Logic

### Naive Approach (Brute Force)
1. Generate every possible substring of $s$.
2. For each substring, count the frequency of the most common character.
3. Calculate if `substring_length - max_freq <= k`.
4. Keep track of the maximum length found.
- **Complexity**: $O(N^3)$ or $O(N^2)$, which is too slow for $N = 10^5$.

### Optimal Approach (Sliding Window)

1. **Initialize**: 
   - `left = 0`, `max_len = 0`.
   - `max_freq = 0` (Tracks the highest frequency of any single character ever seen in a window).
   - `count = {}` (A frequency map for characters in the current window).

2. **Expand**:
   - Iterate with a `right` pointer from $0$ to the end of the string.
   - Add the character at `s[right]` to the `count` map.
   - Update `max_freq` to be the maximum of its current value and the count of the character just added.

3. **Validate & Shrink**:
   - Check the condition: `(right - left + 1) - max_freq > k`.
   - If this is true, the current window contains more than $k$ characters that need replacing. It is invalid.
   - Move the `left` pointer to the right, decrementing the count of `s[left]` in the map, until the window becomes valid again.

4. **Update Result**:
   - At each step (after ensuring the window is valid), calculate the current window size `right - left + 1` and update `max_len`.

### Dry Run Example
**Input**: `s = "AABABBA"`, `k = 1`

| Right | Char | Count Map | MaxFreq | Window $[L, R]$ | Valid? ($(R-L+1) - MF \le 1$) | Action | MaxLen |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | A | {A:1} | 1 | [0,0] "A" | $1-1=0 \le 1$ ✅ | Expand | 1 |
| 1 | A | {A:2} | 2 | [0,1] "AA" | $2-2=0 \le 1$ ✅ | Expand | 2 |
| 2 | B | {A:2, B:1} | 2 | [0,2] "AAB" | $3-2=1 \le 1$ ✅ | Expand | 3 |
| 3 | A | {A:3, B:1} | 3 | [0,3] "AABA" | $4-3=1 \le 1$ ✅ | Expand | 4 |
| 4 | B | {A:3, B:2} | 3 | [0,4] "AABAB" | $5-3=2 > 1$ ❌ | Shrink Left $\rightarrow$ [1,4] | 4 |
| 5 | B | {A:2, B:3} | 3 | [1,5] "ABAB B" | $5-3=2 > 1$ ❌ | Shrink Left $\rightarrow$ [2,5] | 4 |
| 6 | A | {A:2, B:3} | 3 | [2,6] "BABBA" | $5-3=2 > 1$ ❌ | Shrink Left $\rightarrow$ [3,6] | 4 |

**Final Result**: 4

---

## 🚀 Implementation

```python
def character_replacement(s: str, k: int) -> int:
    # Frequency map to store counts of characters in the current window
    count = {}
    max_len = 0
    max_freq = 0
    left = 0
    
    for right in range(len(s)):
        # Add the current character to the frequency map
        char = s[right]
        count[char] = count.get(char, 0) + 1
        
        # Update the maximum frequency encountered in any window so far
        max_freq = max(max_freq, count[char])
        
        # The window is invalid if: (total characters - most frequent character) > k
        while (right - left + 1) - max_freq > k:
            # Shrink the window from the left
            left_char = s[left]
            count[left_char] -= 1
            left += 1
            # Note: We don't need to update max_freq here because max_len 
            # only increases when max_freq increases.
            
        # Update the global maximum length
        max_len = max(max_len, right - left + 1)
        
    return max_len
```

---

## 📊 Complexity Analysis

| Complexity | Notation | Reasoning |
| :--- | :--- | :--- |
| **Time Complexity** | $O(N)$ | The `right` pointer iterates $N$ times. The `left` pointer also iterates at most $N$ times across the entire process. Each map operation is $O(1)$. |
| **Space Complexity** | $O(1)$ | The frequency map stores at most 26 uppercase English characters, regardless of the size of the input string. |

---

## 🌍 Real-World Applications

The logic used in this problem (Sliding Window + Frequency Tracking) is widely used in industry:

1. **Bioinformatics**: Identifying "conserved sequences" in DNA. If a researcher allows for $k$ mutations, they are essentially looking for the longest repeating sequence with $k$ replacements.
2. **Signal Processing**: Detecting bursts of noise or consistent patterns in a stream of data where some "flipped bits" (errors) are expected and should be ignored.
3. **Data Cleaning/Normalization**: In search engines, identifying strings that are "almost identical" (clustering) to merge duplicate entries despite small typos.
4. **Network Traffic Analysis**: Identifying DoS (Denial of Service) attacks by finding windows of time with a high frequency of requests from a single IP, allowing for a small amount of "noise" (legitimate requests).""",
}

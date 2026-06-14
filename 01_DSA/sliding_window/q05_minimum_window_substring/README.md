# Minimum Window Substring

## 1. Overview & Problem Explanation

The **Minimum Window Substring** problem is a classic "Hard" challenge that tests your ability to manage two pointers and frequency tracking. The goal is to find the shortest contiguous substring in a string `s` that contains all the characters of another string `t`, including duplicate characters.

### Problem Statement
Given two strings `s` and `t` of lengths `m` and `n` respectively, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string `""`.

### Input / Output Example
- **Input**: `s = "ADOBECODEBANC"`, `t = "ABC"`
- **Output**: `"BANC"`
- **Explanation**: The substring `"BANC"` contains 'A', 'B', and 'C' and is the shortest such window (length 4). Other windows like `"ADOBEC"` also contain all characters but are longer.

### Constraints & Edge Cases
- **Time/Space Constraints**: $1 \le s.length, t.length \le 10^5$. A brute force $O(N^2)$ or $O(N^3)$ approach will result in a Time Limit Exceeded (TLE) error.
- **Case Sensitivity**: Usually, characters are case-sensitive ('a' $\neq$ 'A').
- **Duplicates**: If `t = "AAB"`, the window must contain at least two 'A's and one 'B'.
- **No Solution**: If `s` is shorter than `t` or simply doesn't contain all characters of `t`, return `""`.

---

## 2. Core Concepts & Data Structures

### The Sliding Window Pattern
The most efficient way to solve this is using a **Variable-Size Sliding Window**. Unlike a fixed-size window, a variable window expands to satisfy a condition and shrinks to optimize the result.

### Why Sliding Window?
A brute force approach would check every possible substring. However, we can observe that if a window from index `i` to `j` is valid, any window from `i` to `j+1` is also valid. Conversely, if we have a valid window, we can try to remove characters from the left to see if a smaller valid window exists. This "expand-then-shrink" behavior is the essence of the sliding window.

### Hash Maps (Frequency Counters)
Since we need to track the requirements of `t` and the current state of the window in `s`, we use **Hash Maps** (or frequency arrays):
1. **`target_count`**: Stores the required frequency of each character in `t`.
2. **`window_count`**: Stores the frequency of characters currently inside our sliding window.

### The "Have" vs "Need" Variable
To avoid iterating over the entire hash map every time we move the pointer (which would add an $O(26)$ or $O(52)$ overhead), we use a counter:
- **`need`**: The number of *unique* characters in `t` that must be present with the required frequency.
- **`have`**: The number of *unique* characters currently in the window that meet the required frequency from `t`.

---

## 3. Step-by-Step Logic

### Naive Approach (Brute Force)
1. Generate all possible substrings of `s`.
2. For each substring, count its characters and compare them with `t`.
3. Keep track of the smallest substring that satisfies the condition.
- **Complexity**: $O(S^3)$ — extremely inefficient.

### Optimal Approach (Sliding Window)

#### The Algorithm
1. **Initialization**: 
   - Create a `target_count` map for all characters in `t`.
   - Initialize `left` and `right` pointers at 0.
   - Initialize `have = 0`, `need = len(target_count)`.
   - Keep track of the `min_len` (start with infinity) and the `res` coordinates.

2. **Expansion Phase**:
   - Move the `right` pointer to the right, adding characters to the `window_count`.
   - If the current character's count in `window_count` equals its count in `target_count`, increment `have`.

3. **Contraction Phase**:
   - While `have == need` (the window is valid):
     - Update `min_len` and store the current `left` and `right` indices if the current window is smaller than the previous minimum.
     - Remove the character at the `left` pointer from `window_count`.
     - If removing that character causes its count to drop below the required frequency in `target_count`, decrement `have`.
     - Increment the `left` pointer to shrink the window.

4. **Termination**:
   - Once `right` reaches the end of `s`, return the substring using the stored coordinates.

#### Dry Run Trace
`s = "ADOBECODEBANC"`, `t = "ABC"`
- `target_count = {A:1, B:1, C:1}`, `need = 3`
- `right` moves to index 5 (`"ADOBEC"`): `window_count` has A, B, and C. `have = 3`.
- **Shrink**: `left` moves from 0 to 1. `"DOBEC"` is invalid (`have = 2`).
- `right` moves to index 10 (`"DOBECODEBA"`): Valid.
- **Shrink**: `left` moves until `"CODEBA"` (valid), then `"ODEBA"` (invalid).
- `right` moves to index 12 (`"ODEBANC"`): Valid.
- **Shrink**: `left` moves until `"BANC"`. This is length 4, the smallest found.

### Optimal Implementation

```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not t or not s:
        return ""

    # Dictionary which keeps a count of all the unique characters in t.
    target_count = Counter(t)
    # Number of unique characters in t, which need to be present in the desired window.
    need = len(target_count)
    
    # left and right pointer
    l, r = 0, 0
    # have is used to keep track of how many unique characters in t 
    # are present in the current window in its desired frequency.
    have = 0
    # Dictionary which keeps a count of all the unique characters in the current window.
    window_count = {}
    
    # ans tuple of (window length, left, right)
    ans = float("inf"), None, None

    while r < len(s):
        # Add one character from the right to the window
        char = s[r]
        window_count[char] = window_count.get(char, 0) + 1

        # If the frequency of the current character added equals to the 
        # desired count in t then increment the have count.
        if char in target_count and window_count[char] == target_count[char]:
            have += 1

        # Try and contract the window till the point where it ceases to be 'desirable'.
        while have == need:
            # Update the smallest window found so far
            if (r - l + 1) < ans[0]:
                ans = (r - l + 1, l, r)

            # The character at the position pointed by the `left` pointer is no longer a part of the window.
            char_l = s[l]
            window_count[char_l] = window_count[char_l] - 1
            if char_l in target_count and window_count[char_l] < target_count[char_l]:
                have -= 1
            
            # Move the left pointer ahead, this helps in looking for a new window.
            l += 1    

        # Keep expanding the window once we are done contracting.
        r += 1    
        
    return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]
```

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(S^3)$ | $O(T)$ | Iterating all substrings $O(S^2)$ and checking each against $T$. |
| **Sliding Window** | $O(S + T)$ | $O(K)$ | Each pointer (`l` and `r`) visits each character at most once. $K$ is the size of the character set. |

- **Time Complexity $O(S + T)$**: We process string `t` once to build the target map $O(T)$. Then, the `right` pointer traverses `s` once, and the `left` pointer traverses `s` once. Even though there is a nested `while` loop, each index is visited a maximum of two times.
- **Space Complexity $O(K)$**: We store frequencies in hash maps. The maximum size of the maps is limited by the number of unique characters in the alphabet (e.g., 52 for upper/lowercase English letters), which is constant $O(1)$ or $O(K)$ relative to the input size.

---

## 5. Real-World Applications

The Minimum Window Substring pattern is widely used in systems that require **pattern matching within streams of data**:

1. **Bioinformatics (Genomics)**: Finding the shortest segment of a DNA sequence that contains a specific set of genetic markers or nucleotides.
2. **Network Traffic Analysis**: Detecting the smallest window of packets that contains a specific sequence of flags or signatures to identify a cyber attack (Intrusion Detection Systems).
3. **Log Analysis**: In large-scale distributed systems, searching for the smallest time window in logs that contains all the events required to diagnose a specific race condition or failure.
4. **Search Normalization**: Finding a compact segment of text in a document that contains all the keywords of a user's query to provide a concise "snippet" in search engine results.
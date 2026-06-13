# Longest Palindromic Substring

*   **Module**: `01_DSA`
*   **Topic**: `dynamic_programming`
*   **Difficulty**: Medium
*   **Categorized Groups**: Dynamic Programming, String
*   **Reference Link**: [https://leetcode.com/problems/longest-palindromic-substring/](https://leetcode.com/problems/longest-palindromic-substring/)

---

## 📝 Overview & Problem Explanation

The challenge asks us to find the **longest palindromic substring** within a given input string `s`. A **palindrome** is a sequence of characters that reads the same forwards and backward (e.g., "madam", "racecar", "level"). A **substring** is a contiguous sequence of characters within a string. We need to identify one such substring that is a palindrome and has the maximum possible length.

**Example Scenarios:**

1.  **Input:** `s = "babad"`
    *   **Output:** `"bab"` (or `"aba"`, both are valid longest palindromic substrings of length 3).
2.  **Input:** `s = "cbbd"`
    *   **Output:** `"bb"`

**Inputs:**

*   `s`: A string consisting of digits and English letters.

**Outputs:**

*   The longest palindromic substring found in `s`. If there are multiple longest palindromic substrings, any one of them is acceptable.

**Constraints:**

*   `1 <= s.length <= 1000`

**Edge Cases:**

*   **Single-character string:** If `s` has only one character (e.g., `s = "a"`), it is by definition a palindrome, and it's the longest one. The output should be `s`.
*   **String already a palindrome:** If `s` itself is a palindrome (e.g., `s = "racecar"`), then `s` is the longest palindromic substring.
*   **String with no palindromes other than single characters:** If `s = "abcde"`, the longest palindromic substrings are each individual character (`"a"`, `"b"`, etc.). The output could be any of them, typically the first one encountered.

---

## 💡 Core Concepts & Data Structures/Algorithms

This problem can be approached with several algorithmic patterns, but the most common optimal solutions involve **Dynamic Programming** or the **Expand Around Center** technique.

### 1. Dynamic Programming (DP)

*   **Concept:** Dynamic Programming is an algorithmic technique for solving optimization problems by breaking them down into simpler overlapping subproblems and storing the results of these subproblems to avoid recomputing them.
*   **Applicability:** This problem exhibits **optimal substructure** (the longest palindromic substring can be built from shorter palindromic substrings) and **overlapping subproblems** (checking if `s[i...j]` is a palindrome often requires checking if `s[i+1...j-1]` is a palindrome, which might be computed multiple times).
*   **How it works:** We build a 2D table, `dp[i][j]`, which stores a boolean value indicating whether the substring `s[i...j]` is a palindrome. The state transition depends on previously computed states.

### 2. Expand Around Center

*   **Concept:** This is a more direct and often simpler approach for palindromes. Every palindrome has a "center." This center can be a single character (for odd-length palindromes like "aba", center is 'b') or two characters (for even-length palindromes like "abba", center is 'bb').
*   **Applicability:** We can iterate through every possible center in the string and expand outwards from that center, checking for character equality.
*   **How it works:** For each character `s[i]`, we consider two potential centers:
    1.  `s[i]` itself (to find odd-length palindromes).
    2.  `s[i]` and `s[i+1]` (to find even-length palindromes).
    We then expand left and right from these centers, incrementing the length of the palindrome as long as characters match. We keep track of the longest palindrome found during this process.

### Why these are chosen:

*   **Brute Force (Naive):** Generates all `O(N^2)` substrings and checks each for palindromicity in `O(N)` time, leading to `O(N^3)` total time. This is too slow for `N=1000`.
*   **Dynamic Programming:** Reduces the check for palindromicity from `O(N)` to `O(1)` by using the precomputed `dp` table. Building the `dp` table takes `O(N^2)` time.
*   **Expand Around Center:** This method also achieves `O(N^2)` time complexity. Each character can be a center, and expanding from a center can take up to `O(N)` time. Since there are `2N-1` possible centers (N for odd, N-1 for even), the total time is `O(N * N) = O(N^2)`. It often has better constant factors than the explicit DP table approach and can be more space-efficient (O(1) auxiliary space if we only store the max length and start index).

---

## Walkthrough: Step-by-Step Logic

We will cover three approaches: a conceptual Brute Force, the Dynamic Programming approach, and the more optimized "Expand Around Center" method.

### Approach 1: Brute Force (Conceptual)

1.  **Generate All Substrings:** Iterate through all possible starting indices `i` from `0` to `n-1`. For each `i`, iterate through all possible ending indices `j` from `i` to `n-1`. The substring `s[i...j]` is thus generated.
2.  **Check Palindrome:** For each generated substring, check if it is a palindrome. This involves comparing characters from both ends inwards.
3.  **Track Longest:** Keep track of the longest palindrome found so far.

**Example Trace (s = "babad"):**

*   `s[0...0]` = "b" (Palindrome)
*   `s[0...1]` = "ba" (Not Palindrome)
*   `s[0...2]` = "bab" (Palindrome, current max="bab")
*   `s[0...3]` = "baba" (Not Palindrome)
*   `s[0...4]` = "babad" (Not Palindrome)
*   ... and so on for all `i, j` combinations.

This approach is simple to understand but highly inefficient.

### Approach 2: Dynamic Programming

Let `dp[i][j]` be a boolean value that is `True` if the substring `s[i...j]` is a palindrome, and `False` otherwise.

1.  **Initialization:**
    *   Initialize a 2D boolean array `dp[n][n]` where `n` is the length of `s`.
    *   Every single character is a palindrome: `dp[i][i] = True` for all `i` from `0` to `n-1`.
    *   Initialize `max_len = 1` and `start_index = 0` (for single character palindromes).

2.  **Base Cases for length 2 substrings:**
    *   For `i` from `0` to `n-2`:
        *   If `s[i] == s[i+1]`, then `s[i...i+1]` is a palindrome. Set `dp[i][i+1] = True`.
        *   Update `max_len = 2` and `start_index = i`.

3.  **Fill DP Table for length >= 3:**
    *   Iterate `length` from `3` to `n`. (This represents the current substring length).
    *   Iterate `i` (start index) from `0` to `n - length`.
    *   Calculate `j = i + length - 1` (end index).
    *   **State Transition:** `s[i...j]` is a palindrome if and only if:
        *   `s[i]` is equal to `s[j]`, **AND**
        *   `s[i+1...j-1]` is a palindrome (i.e., `dp[i+1][j-1]` is `True`).
    *   So, `dp[i][j] = (s[i] == s[j]) AND dp[i+1][j-1]`.
    *   If `dp[i][j]` becomes `True` and `length > max_len`, update `max_len = length` and `start_index = i`.

4.  **Result:** The longest palindromic substring is `s[start_index : start_index + max_len]`.

**Dry Run Example: `s = "babad"`**

`n = 5`
Initialize `dp` table (all `False` initially):
```
  0 1 2 3 4
  b a b a d
0 T F F F F
1 F T F F F
2 F F T F F
3 F F F T F
4 F F F F T
```
`max_len = 1`, `start_index = 0` (e.g., "b" at index 0)

**Length 2 substrings:**
*   `i=0, j=1` (`s[0...1]` = "ba"): `s[0] != s[1]`. `dp[0][1] = F`.
*   `i=1, j=2` (`s[1...2]` = "ab"): `s[1] != s[2]`. `dp[1][2] = F`.
*   `i=2, j=3` (`s[2...3]` = "ba"): `s[2] != s[3]`. `dp[2][3] = F`.
*   `i=3, j=4` (`s[3...4]` = "ad"): `s[3] != s[4]`. `dp[3][4] = F`.

*Oops, I made a mistake here in the initial thought process for the dry run. Let's correct it based on the algorithm.*

**Corrected Dry Run Example: `s = "babad"`**

`n = 5`
Initialize `dp` table, `max_len = 1`, `start_index = 0` (arbitrarily pick `s[0]` = "b")

1.  **Length 1 (Base Case):**
    *   `dp[0][0]=T`, `dp[1][1]=T`, `dp[2][2]=T`, `dp[3][3]=T`, `dp[4][4]=T`.
    *   `max_len = 1`, `start_index = 0` (e.g., from `dp[0][0]`)

2.  **Length 2 (Base Case):**
    *   `i=0, j=1`: `s[0]='b'`, `s[1]='a'`. Not equal. `dp[0][1]=F`.
    *   `i=1, j=2`: `s[1]='a'`, `s[2]='b'`. Not equal. `dp[1][2]=F`.
    *   `i=2, j=3`: `s[2]='b'`, `s[3]='a'`. Not equal. `dp[2][3]=F`.
    *   `i=3, j=4`: `s[3]='a'`, `s[4]='d'`. Not equal. `dp[3][4]=F`.
    *   *Correction*: If `s = "bb"`, then `s[0]==s[1]`, `dp[0][1]=T`, `max_len=2`, `start_index=0`. For "babad", no length-2 palindromes.

3.  **Length 3:**
    *   `i=0, j=2` (`s[0...2]` = "bab"):
        *   `s[0] == s[2]` (`'b' == 'b'`) is True.
        *   `dp[0+1][2-1]` = `dp[1][1]` is True (from base case).
        *   So, `dp[0][2] = True`.
        *   `length (3) > max_len (1)`. Update `max_len = 3`, `start_index = 0`. Current longest: "bab".
    *   `i=1, j=3` (`s[1...3]` = "aba"):
        *   `s[1] == s[3]` (`'a' == 'a'`) is True.
        *   `dp[1+1][3-1]` = `dp[2][2]` is True.
        *   So, `dp[1][3] = True`.
        *   `length (3) > max_len (3)`. Update `max_len = 3`, `start_index = 1`. Current longest: "aba".
    *   `i=2, j=4` (`s[2...4]` = "bad"):
        *   `s[2] == s[4]` (`'b' == 'd'`) is False. `dp[2][4] = F`.

4.  **Length 4:**
    *   `i=0, j=3` (`s[0...3]` = "baba"):
        *   `s[0] == s[3]` (`'b' == 'a'`) is False. `dp[0][3] = F`.
    *   `i=1, j=4` (`s[1...4]` = "abad"):
        *   `s[1] == s[4]` (`'a' == 'd'`) is False. `dp[1][4] = F`.

5.  **Length 5:**
    *   `i=0, j=4` (`s[0...4]` = "babad"):
        *   `s[0] == s[4]` (`'b' == 'd'`) is False. `dp[0][4] = F`.

Final result: `s[start_index : start_index + max_len]` = `s[1 : 1 + 3]` = `s[1:4]` = `"aba"`.

```python
# DP Approach Implementation Sketch
def solve_dp(s: str) -> str:
    n = len(s)
    if n < 2:
        return s

    dp = [[False] * n for _ in range(n)]
    
    max_len = 1
    start_index = 0

    # All single characters are palindromes
    for i in range(n):
        dp[i][i] = True

    # Check for palindromes of length 2
    for i in range(n - 1):
        if s[i] == s[i+1]:
            dp[i][i+1] = True
            max_len = 2
            start_index = i
            
    # Check for palindromes of length >= 3
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            # s[i...j] is a palindrome if s[i] == s[j] AND s[i+1...j-1] is a palindrome
            if s[i] == s[j] and dp[i+1][j-1]:
                dp[i][j] = True
                if length > max_len:
                    max_len = length
                    start_index = i
                    
    return s[start_index : start_index + max_len]

```

### Approach 3: Expand Around Center

This approach is generally more intuitive and often has better constant factors than the explicit DP approach.

1.  **Helper Function `expand_around_center(s, left, right)`:**
    *   This function takes the string `s` and two indices, `left` and `right`, representing the potential center(s) of a palindrome.
    *   It expands outwards from `left` and `right` as long as `left >= 0`, `right < len(s)`, and `s[left] == s[right]`.
    *   It returns the length of the palindrome found and its `left` (start) index.

2.  **Main Logic:**
    *   Initialize `max_len = 0` and `start_index = 0`.
    *   Iterate through each character `i` from `0` to `n-1` (where `n` is `len(s)`).
    *   For each `i`, consider two types of palindromes:
        *   **Odd-length palindromes:** Center is `s[i]`. Call `expand_around_center(s, i, i)`. Let `len1` be the length returned.
        *   **Even-length palindromes:** Center is `s[i]` and `s[i+1]`. Call `expand_around_center(s, i, i+1)`. Let `len2` be the length returned.
    *   Determine the `current_max_len = max(len1, len2)`.
    *   If `current_max_len > max_len`:
        *   Update `max_len = current_max_len`.
        *   Calculate the new `start_index`. If `len1` was greater, `start_index = i - (len1 - 1) // 2`. If `len2` was greater, `start_index = i - (len2 // 2) + 1`. A simpler way to calculate start index is `i - (max_len - 1) // 2`. (The `max_len - 1` is because `max_len` is the total length, but we are expanding `(max_len - 1)/2` steps to the left/right from the center.)

3.  **Return Result:** `s[start_index : start_index + max_len]`. Handle the edge case of an empty string or single char string returning itself.

**Dry Run Example: `s = "babad"`**

`n = 5`
`max_len = 0`, `start_index = 0` (or `max_len = 1` and `start_index = 0` for `s[0]`, pre-initializing for single char edge case)

Let's refine `expand_around_center`:
```python
def get_palindrome_from_center(s: str, left: int, right: int) -> (int, int):
    # Expands from center(s) (left, right) to find max palindrome length and its start index
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    # At this point, s[left+1 ... right-1] is the palindrome
    # Length is (right-1) - (left+1) + 1 = right - left - 1
    # Start index is left + 1
    return right - left - 1, left + 1
```

**Main Loop Trace for `s = "babad"`:**

*   **`i = 0` (`s[0] = 'b'`):**
    *   `len_odd, start_odd = get_palindrome_from_center(s, 0, 0)` -> (`1`, `0`) (for "b")
    *   `len_even, start_even = get_palindrome_from_center(s, 0, 1)` -> (`0`, `1`) (for "" or "b" with error in function - for "ba" no palindrome)
    *   `current_max = max(1, 0) = 1`. Update `max_len = 1`, `start_index = 0`.
*   **`i = 1` (`s[1] = 'a'`):**
    *   `len_odd, start_odd = get_palindrome_from_center(s, 1, 1)` -> (`1`, `1`) (for "a")
    *   `len_even, start_even = get_palindrome_from_center(s, 1, 2)` -> (`0`, `2`) (for "ab" no palindrome)
    *   `current_max = max(1, 0) = 1`. No update to `max_len` or `start_index`.
*   **`i = 2` (`s[2] = 'b'`):**
    *   `len_odd, start_odd = get_palindrome_from_center(s, 2, 2)` -> (`1`, `2`) (for "b")
    *   `len_even, start_even = get_palindrome_from_center(s, 2, 3)` -> (`0`, `3`) (for "ba" no palindrome)
    *   `current_max = max(1, 0) = 1`. No update.
    *   *Correction here*: Let's check `len_odd, start_odd = get_palindrome_from_center(s, 2, 2)` for "babad".
        *   `left=2, right=2`: `s[2]=='b'`, `s[2]=='b'`. `left=1, right=3`.
        *   `left=1, right=3`: `s[1]=='a'`, `s[3]=='a'`. `left=0, right=4`.
        *   `left=0, right=4`: `s[0]=='b'`, `s[4]=='d'`. Not equal. Stop.
        *   Palindrome is `s[left+1...right-1]` which is `s[1...3]` = "aba".
        *   Length: `right - left - 1` = `4 - 0 - 1 = 3`. Start index: `left+1 = 1`.
        *   So, `len_odd = 3`, `start_odd = 1`.
    *   For `i=2`, for odd-length palindrome: length `3`, start `1` ("aba").
    *   For `i=2`, for even-length palindrome: `s[2], s[3]` = "ba". Not equal. Length `0`.
    *   `current_max = max(3, 0) = 3`. Update `max_len = 3`, `start_index = 1`. Longest: "aba".
*   **`i = 3` (`s[3] = 'a'`):**
    *   `len_odd, start_odd = get_palindrome_from_center(s, 3, 3)` -> (`1`, `3`) (for "a")
    *   `len_even, start_even = get_palindrome_from_center(s, 3, 4)` -> (`0`, `4`) (for "ad" no palindrome)
    *   `current_max = max(1, 0) = 1`. No update.
*   **`i = 4` (`s[4] = 'd'`):**
    *   `len_odd, start_odd = get_palindrome_from_center(s, 4, 4)` -> (`1`, `4`) (for "d")
    *   `len_even` (out of bounds for `i+1`).
    *   `current_max = 1`. No update.

Final result: `s[start_index : start_index + max_len]` = `s[1 : 1 + 3]` = `s[1:4]` = `"aba"`.

```python
# Expand Around Center Implementation Sketch
def solve_expand_around_center(s: str) -> str:
    n = len(s)
    if n < 2:
        return s

    max_len = 1
    start_index = 0

    def expand_around_center(left: int, right: int) -> (int, int):
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1, left + 1 # (length, actual_start_index)

    for i in range(n):
        # Odd length palindromes, e.g., "aba"
        len1, current_start1 = expand_around_center(i, i)
        
        # Even length palindromes, e.g., "abba"
        len2, current_start2 = expand_around_center(i, i + 1)

        if len1 > max_len:
            max_len = len1
            start_index = current_start1
        
        if len2 > max_len: # Note: This handles updating max_len and start_index if len2 is greater
            max_len = len2
            start_index = current_start2
            
    return s[start_index : start_index + max_len]

```

---

## ⏱️ Complexity Analysis

| Approach                | Time Complexity        | Space Complexity        | Notes                                                              |
| :---------------------- | :--------------------- | :---------------------- | :----------------------------------------------------------------- |
| **Brute Force**         | `O(N^3)`               | `O(1)`                  | Generating `N^2` substrings, each `O(N)` to check palindrome.     |
| **Dynamic Programming** | `O(N^2)`               | `O(N^2)`                | `N^2` states in DP table, each state `O(1)` computation.          |
| **Expand Around Center**| `O(N^2)`               | `O(1)`                  | `N` centers, each expansion `O(N)` in worst case. `O(1)` auxiliary space not counting output string. |

**Reasoning:**

*   **Brute Force:**
    *   **Time:** We have `N` choices for the starting character, `N` choices for the ending character. This gives `N^2` substrings. For each substring of length `k`, checking if it's a palindrome takes `O(k)` time. In the worst case, `k` is `N`, leading to `O(N^2 * N) = O(N^3)`.
    *   **Space:** We only store the current longest palindrome, which is `O(1)` (not counting the space for the output string itself, which is `O(N)`).
*   **Dynamic Programming:**
    *   **Time:** The `dp` table has `N * N` cells. Each cell is computed in `O(1)` time (checking `s[i] == s[j]` and looking up `dp[i+1][j-1]`). Thus, the total time is `O(N^2)`.
    *   **Space:** We use a `N * N` 2D boolean array to store `dp` states, leading to `O(N^2)` space.
*   **Expand Around Center:**
    *   **Time:** There are `2N-1` possible centers (N single-character centers `(i, i)` and `N-1` two-character centers `(i, i+1)`). For each center, the `expand_around_center` function might expand up to `N/2` times in each direction. Thus, for each center, it takes `O(N)` time. Total time complexity is `O(N * N) = O(N^2)`.
    *   **Space:** We only need a few variables to store `max_len` and `start_index`. This is constant extra space, `O(1)`.

---

## 🌐 Real-World Applications

Finding palindromic substrings, or pattern matching in general, has several practical applications:

1.  **Bioinformatics:**
    *   Identifying palindromic sequences in DNA or RNA strands is crucial. These sequences often play a role in gene regulation, enzyme recognition sites, and structural formation (e.g., hairpin loops).
    *   Algorithms for finding palindromes are fundamental for analyzing genetic data.
2.  **Text Processing and Natural Language Processing (NLP):**
    *   **Spell Checkers and Autocorrect:** While not directly for palindromes, the underlying string matching and substring analysis techniques are critical.
    *   **Data Compression:** Some compression algorithms exploit repeating patterns, including palindromic ones, to reduce storage size.
    *   **Lexical Analysis:** In tokenizing text or code, identifying specific patterns (which could include palindromic-like structures in more complex patterns) is essential.
    *   **Plagiarism Detection:** Finding long matching substrings (though not necessarily palindromic) is a core component.
3.  **String Searching and Pattern Recognition:**
    *   Many advanced string search algorithms (e.g., Manacher's Algorithm, which solves this problem in O(N)) build upon concepts of finding repeating or symmetric patterns.
    *   Used in database query optimization, log analysis, and searching large datasets.
4.  **Cryptography (Theoretical):**
    *   The study of symmetric patterns can sometimes appear in theoretical cryptographic constructions or cryptanalysis, though direct use of palindromic substrings is rare.
5.  **Recreational Mathematics and Puzzles:**
    *   Beyond practical applications, palindromes are popular in recreational mathematics, puzzles, and linguistic games, often serving as a gateway problem to introduce algorithmic thinking.
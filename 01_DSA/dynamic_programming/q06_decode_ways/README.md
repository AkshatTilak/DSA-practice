# Decode Ways (q06_decode_ways)

## 📝 Overview & Problem Explanation

The "Decode Ways" challenge asks us to determine the total number of ways a given string of digits can be decoded. We're provided with a simple mapping: 'A' corresponds to '1', 'B' to '2', and so on, up to 'Z' corresponding to '26'. Each digit or pair of digits must map to a letter from 'A' to 'Z'.

Essentially, we need to partition the input digit string `s` into valid numbers (between 1 and 26, inclusive) and count how many unique ways such a partition can be formed.

**Example:**
If `s = "12"`, it can be decoded in two ways:
1.  "1" (A) + "2" (B) -> "AB"
2.  "12" (L) -> "L"
So, the output should be `2`.

---

**Inputs:**
*   `s`: A string consisting only of digits.

**Outputs:**
*   An integer representing the total number of ways to decode `s`.

**Constraints:**
*   `1 <= s.length <= 100`
*   `s` contains only digits and may contain leading zeros.

**Edge Cases & Important Rules:**
1.  **'0' is special**: A '0' by itself cannot be decoded (there's no letter for '0').
2.  **Two-digit numbers**: A two-digit number must be between '10' and '26' (inclusive) to be a valid decoding. For instance, "06" is invalid (cannot start with 0 if it's a two-digit number, and '0' is invalid alone). "30" is also invalid as a two-digit number (greater than 26), and since '0' cannot be decoded alone, if '3' is taken, '0' is left invalid.
3.  **Empty string**: Not possible per constraints (`s.length >= 1`).
4.  **Valid single digits**: Any digit from '1' to '9' can be decoded as a single character.

## 💡 Core Concepts & Data Structures/Algorithms

This problem exhibits characteristics perfectly suited for **Dynamic Programming (DP)**:

1.  **Optimal Substructure**: The solution to the main problem (decoding `s`) depends on solutions to smaller subproblems (decoding suffixes of `s`). For example, the number of ways to decode `s[i:]` depends on the number of ways to decode `s[i+1:]` (if `s[i]` is a valid single digit) and `s[i+2:]` (if `s[i:i+2]` is a valid two-digit number).
2.  **Overlapping Subproblems**: Without memoization or tabulation, a recursive solution would repeatedly compute the number of ways for the same substrings, leading to exponential time complexity.

The general approach will be **Tabulation (Bottom-Up DP)**, where we build up the solution from the smallest subproblems to the complete problem.

## 🧠 Step-by-Step Logic

Let `n` be the length of the string `s`. We'll define `dp[i]` as the number of ways to decode the substring `s[i:]` (from index `i` to the end of the string).

### Approach 1: Brute Force (Recursive without Memoization) - Intuition for DP

A recursive function `solve(index)` could calculate the number of ways to decode `s[index:]`.

1.  **Base Cases:**
    *   If `index == n`: We've successfully decoded the entire string. Return `1` (one way to decode an empty string).
    *   If `s[index] == '0'`: A '0' cannot be decoded by itself. This path is invalid. Return `0`.

2.  **Recursive Steps:**
    *   Initialize `ways = 0`.
    *   **Consider single digit `s[index]`**: If `s[index]` is a valid digit (1-9), we can decode it and add the ways from the rest of the string: `ways += solve(index + 1)`.
    *   **Consider two digits `s[index:index+2]`**:
        *   If `index + 1 < n` (there are at least two digits remaining) AND the number formed by `s[index:index+2]` is between 10 and 26 (inclusive):
        *   We can decode these two digits together and add the ways from the rest of the string: `ways += solve(index + 2)`.

3.  **Return `ways`**.

This approach suffers from **exponential time complexity** `O(2^N)` because of repeated calculations for overlapping subproblems.

### Approach 2: Optimal - Dynamic Programming (Tabulation)

We'll use a `dp` array where `dp[i]` stores the number of ways to decode `s[i:]`. We build this array from right to left (from `n` down to `0`).

1.  **Initialization:**
    *   Create a `dp` array of size `n + 1`.
    *   `dp[n] = 1`: There is one way to decode an empty string (the base case for successful decoding).

2.  **Iterate from `i = n-1` down to `0`:**
    *   For each index `i`:
        *   **Check for '0'**: If `s[i] == '0'`, then `dp[i] = 0`. A '0' cannot be a valid single digit and also cannot be the first digit of a two-digit number (e.g., "06" is invalid).
        *   **If `s[i] != '0'` (valid single digit):**
            *   `dp[i]` will at least be equal to `dp[i+1]` (decoding `s[i]` as a single digit).
            *   **Check for two-digit decoding**:
                *   If `i + 1 < n` (meaning there's a second digit `s[i+1]`) AND
                *   The two-digit number formed by `s[i]` and `s[i+1]` is between 10 and 26 (inclusive).
                *   Then, we can also decode `s[i:i+2]` as a two-digit number. Add the ways from `dp[i+2]` to `dp[i]`.
            *   So, `dp[i] = dp[i+1]` (if valid) + `dp[i+2]` (if valid).

3.  **Result:**
    *   The final answer is `dp[0]`.

#### **Dry Run Example: `s = "226"`**
`n = 3`
`dp` array of size 4: `[?, ?, ?, ?]`

1.  **Initialize**: `dp[3] = 1`
    `dp = [?, ?, ?, 1]`

2.  **`i = 2` (character `s[2] = '6'`)**:
    *   `s[2] = '6'` is not '0'.
    *   Single digit: `dp[2] = dp[3] = 1`.
    *   Two digits: `i+1=3`, which is not `< n`. No two-digit check.
    `dp = [?, ?, 1, 1]`

3.  **`i = 1` (character `s[1] = '2'`)**:
    *   `s[1] = '2'` is not '0'.
    *   Single digit: `dp[1] = dp[2] = 1`.
    *   Two digits: `i+1=2 < n=3`. Form "26". `int("26")` is 26, which is `10 <= 26 <= 26`. Valid.
        *   Add `dp[i+2]` which is `dp[3] = 1`.
    *   `dp[1] = dp[2] + dp[3] = 1 + 1 = 2`.
    `dp = [?, 2, 1, 1]`

4.  **`i = 0` (character `s[0] = '2'`)**:
    *   `s[0] = '2'` is not '0'.
    *   Single digit: `dp[0] = dp[1] = 2`.
    *   Two digits: `i+1=1 < n=3`. Form "22". `int("22")` is 22, which is `10 <= 22 <= 26`. Valid.
        *   Add `dp[i+2]` which is `dp[2] = 1`.
    *   `dp[0] = dp[1] + dp[2] = 2 + 1 = 3`.
    `dp = [3, 2, 1, 1]`

**Final Answer:** `dp[0] = 3`.

### Approach 3: Space-Optimized Dynamic Programming (Optimal)

Notice that `dp[i]` only depends on `dp[i+1]` and `dp[i+2]`. This means we don't need the entire `dp` array. We can keep track of just the last two (or three, if you count `dp[n]`) values.

Let's rename:
*   `dp_current` (or `dp[i]`)
*   `dp_next` (or `dp[i+1]`)
*   `dp_next_next` (or `dp[i+2]`)

1.  **Initialization:**
    *   `dp_next_next = 1` (corresponds to `dp[n]`)
    *   `dp_next = 0` (Placeholder for `dp[n-1]`. Will be computed based on `s[n-1]`)
    *   Handle `s[n-1]` specifically:
        *   If `s[n-1] == '0'`, `dp_next = 0`.
        *   Else, `dp_next = 1` (one way to decode the last character).

2.  **Iterate from `i = n-2` down to `0`:**
    *   Store `dp_next` into a temporary variable, say `temp_dp_next`, because `dp_next` will become `dp_next_next` in the next iteration.
    *   Calculate `dp_current`:
        *   If `s[i] == '0'`, `dp_current = 0`.
        *   Else (`s[i] != '0'`):
            *   `dp_current = dp_next` (decoding `s[i]` as a single digit).
            *   Check two digits:
                *   `two_digit_num = int(s[i:i+2])`
                *   If `10 <= two_digit_num <= 26`:
                    *   `dp_current += dp_next_next`
    *   Update for the next iteration:
        *   `dp_next_next = temp_dp_next` (This effectively shifts `dp[i+1]` to `dp[i+2]` for the *next* iteration `i-1`)
        *   `dp_next = dp_current` (This becomes `dp[i+1]` for the *next* iteration `i-1`)

3.  **Result:**
    *   The final answer is `dp_next` (which holds the value for `dp[0]` after the loop finishes).

## 📊 Complexity Analysis

| Approach                       | Time Complexity | Space Complexity | Reasoning                                                                       |
| :----------------------------- | :-------------- | :--------------- | :------------------------------------------------------------------------------ |
| **Brute Force (Recursion)**    | O(2^N)          | O(N)             | Each character can be grouped in two ways, leading to exponential branching.   |
| **DP (Tabulation)**            | O(N)            | O(N)             | Each state `dp[i]` is computed once. Linear pass through the string.          |
| **DP (Space-Optimized)**       | O(N)            | O(1)             | Each state is computed once. Only a constant number of variables are stored.   |

## 🌍 Real-World Applications

The "Decode Ways" problem, and its underlying dynamic programming pattern, has several parallels in real-world software engineering:

1.  **Compiler Design & Parsing**: When a compiler or interpreter parses source code, it often needs to determine if a sequence of characters forms a valid token or expression. Ambiguous grammars might lead to multiple valid parse trees, similar to how a digit string can have multiple decodings. DP can be used to count or find all valid parses.
2.  **Natural Language Processing (NLP)**: In tasks like word segmentation or understanding ambiguous sentences, a sequence of characters or words might have multiple interpretations. DP helps in finding the most probable or all possible segmentations/interpretations. For example, decoding a sequence of phonemes into words.
3.  **Bioinformatics**:
    *   **Codon Decoding**: In genetics, a sequence of three nucleotides (a codon) maps to a specific amino acid. A long RNA sequence needs to be decoded into a protein sequence. Dynamic programming can be used to find valid reading frames and protein sequences, especially if there are alternative start/stop codons or "wobble" base pairing leading to ambiguous decodings.
    *   **Sequence Alignment**: Algorithms like Smith-Waterman or Needleman-Wunsch (which are DP-based) find the best alignment between two DNA or protein sequences, where "decoding" the optimal alignment involves choosing between matches, mismatches, and gaps.
4.  **Network Routing & Pathfinding**: In some network scenarios, a sequence of hops might have multiple valid interpretations or paths. DP can be used to count or find optimal paths under certain constraints.
5.  **Data Compression / Encoding Schemes**: Designing or analyzing encoding schemes where a sequence of bits or symbols can be grouped in multiple ways to represent data. DP can help analyze the efficiency or ambiguity of such schemes.

---

## 🐍 Solutions Implemented in Codebase

```python
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Optimal (Space-Optimized Dynamic Programming) ---
def solve_optimal(s: str) -> int:
    """
    Calculates the number of ways to decode a digit string using space-optimized Dynamic Programming.

    Args:
        s: The input string containing only digits.

    Returns:
        The total number of ways to decode the string.
    """
    n = len(s)

    # Base case: an empty string has one way to decode (no operations needed).
    # This corresponds to dp[n] = 1 in the full DP table.
    # dp_next_next will represent dp[i+2]
    dp_next_next = 1 

    # dp_next will represent dp[i+1]
    # Handle the last character (s[n-1]):
    # If s[n-1] is '0', it cannot be decoded, so 0 ways.
    # Otherwise, it can be decoded as a single digit, so 1 way (dp[n]).
    dp_next = 0 if s[n-1] == '0' else 1

    # Iterate from the second-to-last character down to the first.
    # dp_current will represent dp[i]
    for i in range(n - 2, -1, -1):
        dp_current = 0

        # Case 1: Decode s[i] as a single digit.
        # This is only possible if s[i] is not '0'.
        if s[i] != '0':
            dp_current = dp_next # Add ways from decoding s[i+1:]

        # Case 2: Decode s[i] and s[i+1] as a two-digit number.
        # This is possible if the number formed by s[i:i+2] is between 10 and 26.
        two_digit_num = int(s[i:i+2])
        if 10 <= two_digit_num <= 26:
            dp_current += dp_next_next # Add ways from decoding s[i+2:]

        # Update dp_next and dp_next_next for the next iteration (moving left).
        # The previous dp_next becomes dp_next_next for the current 'i'.
        dp_next_next = dp_next 
        # The current dp_current becomes dp_next for the current 'i'.
        dp_next = dp_current

    # The result for s[0:] is stored in dp_next after the loop.
    return dp_next


# --- APPROACH 2: Dynamic Programming (Tabulation) ---
def solve_dp_tabulation(s: str) -> int:
    """
    Calculates the number of ways to decode a digit string using Dynamic Programming (tabulation).

    Args:
        s: The input string containing only digits.

    Returns:
        The total number of ways to decode the string.
    """
    n = len(s)
    if n == 0:
        return 0

    # dp[i] stores the number of ways to decode the substring s[i:]
    dp = [0] * (n + 1)

    # Base case: An empty string has one way to decode (no operations needed).
    dp[n] = 1

    # Handle the last character (s[n-1]):
    # If s[n-1] is '0', it cannot be decoded, so dp[n-1] = 0.
    # Otherwise, it can be decoded as a single digit, so dp[n-1] = dp[n] = 1.
    dp[n-1] = 0 if s[n-1] == '0' else 1

    # Iterate from the second-to-last character down to the first.
    for i in range(n - 2, -1, -1):
        # If s[i] is '0', it cannot be decoded as a single digit.
        # Also, it cannot start a two-digit number (e.g., "06" is invalid).
        # So, if s[i] is '0', there are 0 ways to decode starting from this position.
        if s[i] == '0':
            dp[i] = 0
            continue # Move to the next iteration

        # Case 1: Decode s[i] as a single digit.
        # If s[i] is 1-9 (which we've already checked by s[i] != '0'),
        # we can always decode it as a single digit.
        # The number of ways is then the number of ways to decode the rest of the string s[i+1:].
        dp[i] = dp[i+1]

        # Case 2: Decode s[i] and s[i+1] as a two-digit number.
        # This is possible if the two-digit number is between 10 and 26.
        two_digit_num = int(s[i:i+2])
        if 10 <= two_digit_num <= 26:
            # Add the number of ways to decode the rest of the string s[i+2:].
            dp[i] += dp[i+2]

    # The result for the entire string s[0:] is stored in dp[0].
    return dp[0]


# Starter template solution (will point to the optimal one)
def solve():
    """
    Placeholder for the main solution entry point, typically used in competitive programming.
    Should call the desired optimal solution function.
    """
    # Example usage:
    # s = "12"
    # return solve_optimal(s)
    pass # This would be replaced by actual logic in a real competitive programming setup.

```
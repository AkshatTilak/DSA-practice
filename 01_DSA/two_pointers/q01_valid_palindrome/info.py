INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/valid-palindrome/',
    'description': 'Check if a string is a palindrome, ignoring non-alphanumeric chars.',
    'groups': ['String', 'Two Pointers'],
    'starter_code': """def is_palindrome(s: str) -> bool:
    # Write your solution here
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach filters the string to include only alphanumeric characters, converts it to lowercase, and compares the resulting string with its reverse.
def is_palindrome_naive(s: str) -> bool:
    filtered_chars = [char.lower() for char in s if char.isalnum()]
    return filtered_chars == filtered_chars[::-1]

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses two pointers starting from both ends of the string, moving inward. It skips non-alphanumeric characters on the fly, avoiding the creation of a new string. This is optimal because it minimizes space usage to constant space while maintaining linear time complexity.
def is_palindrome_optimal(s: str) -> bool:
    left, right = 0, len(s) - 1
    
    while left < right:
        # Skip non-alphanumeric characters from the left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric characters from the right
        while left < right and not s[right].isalnum():
            right -= 1
        
        # Compare characters case-insensitively
        if s[left].lower() != s[right].lower():
            return False
        
        left += 1
        right -= 1
        
    return True

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package two_pointers;

public class ValidPalindrome {
    /**
     * Checks if a string is a palindrome, ignoring non-alphanumeric characters and case.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public boolean isPalindrome(String s) {
        if (s == null) return false;
        
        int left = 0;
        int right = s.length() - 1;
        
        while (left < right) {
            char leftChar = s.charAt(left);
            char rightChar = s.charAt(right);
            
            if (!Character.isLetterOrDigit(leftChar)) {
                left++;
            } else if (!Character.isLetterOrDigit(rightChar)) {
                right--;
            } else {
                if (Character.toLowerCase(leftChar) != Character.toLowerCase(rightChar)) {
                    return false;
                }
                left++;
                right--;
            }
        }
        
        return true;
    }

    public static void main(String[] args) {
        ValidPalindrome vp = new ValidPalindrome();
        System.out.println(vp.isPalindrome("A man, a plan, a canal: Panama")); // true
        System.out.println(vp.isPalindrome("race a car")); // false
    }
}
\"\"\"""",
    'test_code': """def test_palindrome():
    assert is_palindrome('A man, a plan, a canal: Panama') is True
    assert is_palindrome('race a car') is False
    assert is_palindrome(' ') is True""",
    'readme_content': """# Valid Palindrome

## 📌 Overview & Problem Explanation
The **Valid Palindrome** challenge asks us to determine if a given string is a palindrome. A palindrome is a sequence that reads the same backward as forward. However, this problem adds two critical constraints to make it more realistic:
1. **Ignore Case**: 'A' and 'a' should be treated as the same character.
2. **Ignore Non-Alphanumeric Characters**: Only letters and numbers count; spaces, commas, colons, and other symbols should be skipped.

### Input/Output
- **Input**: A string `s` consisting of alphanumeric characters and symbols.
- **Output**: A boolean value (`True` if the cleaned string is a palindrome, `False` otherwise).

### Constraints & Edge Cases
- **Empty String**: An empty string or a string containing only non-alphanumeric characters is technically a palindrome (reads the same forwards and backwards).
- **Single Character**: A single alphanumeric character is always a palindrome.
- **Mixed Case/Symbols**: "Race Car" $\rightarrow$ `true`, "A man, a plan, a canal: Panama" $\rightarrow$ `true`.
- **Complexity**: The solution must handle strings up to $2 \cdot 10^5$ characters, making an $O(N^2)$ solution inefficient.

---

## 🧠 Core Concepts & Algorithmic Patterns

### 1. The Two-Pointer Pattern
The most efficient way to solve palindrome problems is the **Two-Pointer Technique**. 
- **How it works**: We place one pointer at the very beginning (`left`) and one at the very end (`right`) of the string. We move them toward the center, comparing the characters at each step.
- **Why it's optimal**: It allows us to validate the string in a single pass without allocating extra memory for a reversed copy of the string.

### 2. String Filtering (Alphanumeric Check)
Since the problem requires ignoring symbols, we utilize the `isalnum()` method (in Python) or `Character.isLetterOrDigit()` (in Java). This allows us to "skip" noise characters dynamically during the pointer movement.

### 3. Case Normalization
To handle case-insensitivity, we convert characters to lowercase using `.lower()` before comparison.

---

## 🛠️ Step-by-Step Logic

### Approach 1: Brute Force (Clean & Reverse)
This approach prioritizes readability and simplicity over memory efficiency.
1. **Filter**: Create a new list/string containing only alphanumeric characters from `s`, converted to lowercase.
2. **Reverse**: Create a reversed version of this filtered string.
3. **Compare**: If the filtered string equals its reverse, return `True`.

**Dry Run (`s = "Race Car"`)**:
- Filtered: `"racecar"`
- Reversed: `"racecar"`
- Comparison: `"racecar" == "racecar"` $\rightarrow$ `True`.

### Approach 2: Optimal (Two Pointers)
This approach prioritizes memory efficiency by operating "in-place."
1. **Initialization**: Set `l = 0` and `r = len(s) - 1`.
2. **Iterative Comparison**: While `l < r`:
    - **Skip Left**: If `s[l]` is not alphanumeric, increment `l`.
    - **Skip Right**: If `s[r]` is not alphanumeric, decrement `r`.
    - **Verify**: Once both pointers land on alphanumeric characters, compare them (lowercase).
    - **Mismatch**: If they differ, return `False` immediately.
    - **Match**: Increment `l` and decrement `r` to check the next pair.
3. **Completion**: If the pointers meet or cross, all checks passed $\rightarrow$ return `True`.

**Dry Run (`s = "A man, a plan..."`)**:
- `l` at 'A', `r` at 'a' $\rightarrow$ Match.
- `l` moves to ' ', skips it $\rightarrow$ `l` moves to 'm'.
- `r` moves to 'm' $\rightarrow$ Match.
- Process continues until the center is reached.

---

## 💻 Implementation

```python
def is_palindrome_naive(s: str) -> bool:
    \"\"\"
    Approach 1: Brute Force
    Time: O(N), Space: O(N)
    \"\"\"
    # Filter alphanumeric characters and normalize to lowercase
    clean = [c.lower() for c in s if c.isalnum()]
    # Compare list with its reverse
    return clean == clean[::-1]

def is_palindrome_optimal(s: str) -> bool:
    \"\"\"
    Approach 2: Two Pointers
    Time: O(N), Space: O(1)
    \"\"\"
    l, r = 0, len(s) - 1
    
    while l < r:
        # Skip non-alphanumeric characters from the left
        while l < r and not s[l].isalnum(): 
            l += 1
        # Skip non-alphanumeric characters from the right
        while l < r and not s[r].isalnum(): 
            r -= 1
        
        # Case-insensitive comparison
        if s[l].lower() != s[r].lower():
            return False
            
        l += 1
        r -= 1
        
    return True
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Naive** | $O(N)$ | $O(N)$ | We traverse the string to filter it and create a new list of size $N$. |
| **Optimal** | $O(N)$ | $O(1)$ | We traverse the string once with pointers; no extra storage proportional to $N$ is used. |

- **Time Complexity $O(N)$**: In the worst case, we visit every character in the string exactly once.
- **Space Complexity $O(1)$**: The optimal approach only uses two integer variables (`l` and `r`), regardless of the input string size.

---

## 🚀 Real-World Applications

1. **Data Normalization**: This pattern is used in search engines to normalize queries (removing punctuation and case) before searching a database.
2. **Bioinformatics**: In genetics, "inverted repeats" or palindromic sequences in DNA are crucial for understanding how restriction enzymes cut DNA.
3. **Compiler Design**: Lexical analyzers often use similar pointer-based scanning to identify tokens while ignoring whitespace and comments.
4. **Data Validation**: Used in creating "fuzzy match" algorithms where a system needs to check if two strings are equivalent despite formatting differences.""",
}

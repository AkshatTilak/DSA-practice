INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/group-anagrams/',
    'description': 'Group an array of strings together if they are anagrams.',
    'groups': ['String', 'Hashing'],
    'starter_code': """def group_anagrams(strs: list[str]) -> list[list[str]]:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_group_anagrams():
    assert len(group_anagrams(['eat', 'tea'])) == 1""",
    'readme_content': """The following study guide provides a comprehensive overview of the "Group Anagrams" challenge, covering problem explanation, core concepts, step-by-step logic for optimal solutions, complexity analysis, and real-world applications.

---

# Group Anagrams (q04_group_anagrams)

## 1. Overview & Problem Explanation

### Description / Problem Statement
The "Group Anagrams" challenge requires you to take an array of strings and organize them into groups, where each group contains strings that are anagrams of each other. Anagrams are words or phrases formed by rearranging the letters of another, using all the original letters exactly once. For example, "eat", "tea", and "ate" are anagrams because they all consist of the letters 'e', 'a', and 't'.

### Inputs
A list of strings (`strs: list[str]`).

### Outputs
A list of lists of strings (`list[list[str]]`), where each inner list represents a group of anagrams. The order of the output groups and the order of strings within each group do not matter.

### Constraints
*   `1 <= strs.length <= 10^4`
*   `0 <= strs[i].length <= 100`
*   `strs[i]` consists of lowercase English letters only.

### Edge Cases
*   **Empty input list**: If `strs` is empty, the output should likely be an empty list.
*   **List with single string**: A single string will form a group by itself (e.g., `["a"]` -> `[["a"]]`).
*   **List with empty strings**: Multiple empty strings `["", "", ""]` are considered anagrams of each other and should be grouped `[["", "", ""]]`.
*   **All strings are anagrams**: All input strings could belong to a single anagram group.
*   **No strings are anagrams**: Each string could be unique, resulting in each string forming its own group.

## 2. Core Concepts & Data Structures/Algorithms

The core concept for solving this problem efficiently revolves around the property of anagrams: **they contain the exact same characters with the same frequencies, just in a different order**. This insight leads to the use of a **hash map (dictionary)** to group strings based on a "canonical representation" or "signature" of their characters.

### Hashing
A hash map (or dictionary in Python) is a data structure that stores key-value pairs, allowing for average O(1) time complexity for insertion, deletion, and lookup operations. This makes it ideal for grouping items.

### Canonical Representation of Anagrams
To use a hash map, we need a way to generate a unique, consistent key for all strings that are anagrams of each other. Two primary methods achieve this:

1.  **Sorted String as Key**: The most intuitive approach is to sort the characters of each string alphabetically. For example, "eat", "tea", and "ate" all become "aet" when sorted. This sorted string acts as a unique key for the anagram group. Since strings are immutable in Python, a sorted string can directly serve as a dictionary key.
2.  **Character Count Tuple as Key**: An alternative is to count the frequency of each character (e.g., using an array of size 26 for lowercase English letters). For "eat", the count would be `[1,0,0,0,1,0,... (e at index 4), ... (a at index 0), ... (t at index 19)]`. This frequency array (converted to an immutable tuple to be used as a dictionary key) serves as the canonical representation. This approach avoids the O(K log K) sorting time per string, reducing it to O(K) for counting.

We choose hashing because it allows us to process each string once, compute its canonical key, and then efficiently store it with other anagrams. Without hashing, a brute-force approach would involve comparing every string with every other string, leading to much higher time complexity.

## 3. Step-by-Step Logic

### Brute-Force Approach (Implicit)
A naive approach would be to iterate through the input array, and for each string, compare it with all previously ungroupe strings to check if they are anagrams. If they are, group them. To check if two strings are anagrams, one would sort both strings and compare the sorted versions. This method involves many redundant comparisons and is highly inefficient for large inputs.

### Optimal Solution: Hashing with Sorted String Keys

This approach leverages a hash map to group anagrams efficiently.

1.  **Initialize a Hash Map**: Create an empty hash map (e.g., `defaultdict(list)` in Python, which automatically initializes a new list for a key if it doesn't exist). This map will store sorted strings as keys and lists of original strings (which are anagrams) as values.
    ```python
    from collections import defaultdict
    anagram_groups = defaultdict(list)
    ```
2.  **Iterate Through Input Strings**: Loop through each string `s` in the input list `strs`.
    ```python
    for s in strs:
        # ...
    ```
3.  **Generate Canonical Key**: For each string `s`, convert it into its canonical form. The most straightforward way is to sort its characters alphabetically and then join them back into a string.
    *   Example: For `s = "eat"`
        *   `sorted(s)` returns `['a', 'e', 't']`.
        *   `"".join(sorted(s))` returns `"aet"`.
    This sorted string, `"aet"`, will be our key.
    ```python
    sorted_s = "".join(sorted(s))
    ```
4.  **Group Strings in Hash Map**: Use the `sorted_s` (the canonical key) to access the hash map. Append the *original* string `s` to the list associated with that key. If the key doesn't exist yet, `defaultdict(list)` will automatically create an empty list before appending.
    ```python
    anagram_groups[sorted_s].append(s)
    ```
5.  **Collect Results**: After iterating through all input strings, the `anagram_groups` hash map will contain all the grouped anagrams. The values of this hash map are the lists of grouped anagrams. Convert these values into a list of lists and return it.
    ```python
    return list(anagram_groups.values())
    ```

#### Example Walkthrough: `strs = ["eat", "tea", "tan", "ate", "nat", "bat"]`

1.  Initialize `anagram_groups = defaultdict(list)`
2.  **Processing "eat"**:
    *   `sorted("eat")` -> `"aet"`
    *   `anagram_groups["aet"].append("eat")` -> `anagram_groups = {"aet": ["eat"]}`
3.  **Processing "tea"**:
    *   `sorted("tea")` -> `"aet"`
    *   `anagram_groups["aet"].append("tea")` -> `anagram_groups = {"aet": ["eat", "tea"]}`
4.  **Processing "tan"**:
    *   `sorted("tan")` -> `"ant"`
    *   `anagram_groups["ant"].append("tan")` -> `anagram_groups = {"aet": ["eat", "tea"], "ant": ["tan"]}`
5.  **Processing "ate"**:
    *   `sorted("ate")` -> `"aet"`
    *   `anagram_groups["aet"].append("ate")` -> `anagram_groups = {"aet": ["eat", "tea", "ate"], "ant": ["tan"]}`
6.  **Processing "nat"**:
    *   `sorted("nat")` -> `"ant"`
    *   `anagram_groups["ant"].append("nat")` -> `anagram_groups = {"aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"]}`
7.  **Processing "bat"**:
    *   `sorted("bat")` -> `"abt"`
    *   `anagram_groups["abt"].append("bat")` -> `anagram_groups = {"aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"], "abt": ["bat"]}`
8.  **Return**: `list(anagram_groups.values())` will yield `[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]` (order of inner lists and elements within them may vary).

## 4. Complexity Analysis

Let:
*   `N` be the number of strings in the input array (`strs.length`).
*   `K` be the maximum length of a string in the input array (`max(strs[i].length)`).

| Approach                      | Time Complexity   | Space Complexity     | Reasoning                                                                                                                                                                                                                                                                                                              |
| :---------------------------- | :---------------- | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Brute Force (Pairwise Comparison)** | O(N² \* K log K)  | O(N \* K)            | **Time**: Comparing `N` strings with `N` other strings (`N²`). Each comparison involves sorting two strings of length up to `K`, which takes `O(K log K)` time. <br> **Space**: Storing the results will, in the worst case, involve storing all `N` strings, each up to `K` length. |
| **Optimal (Hashing Sorted String Keys)** | O(N \* K log K)   | O(N \* K)            | **Time**: We iterate through `N` strings. For each string of length `K`, sorting takes `O(K log K)` time. Hash map operations (insertion, lookup) are amortized `O(K)` on average for string keys (due to string hashing and comparison, which depends on string length) but practically considered `O(1)` for small fixed-length keys. However, the `K log K` from sorting dominates. <br> **Space**: In the worst case, all `N` strings are unique or form unique anagram groups, and they are all stored in the hash map. This requires `O(N * K)` space to store all original strings. The sorted keys also take `O(K)` space each.                                                                                                 |
| **Optimal (Hashing Character Count Tuple Keys)** | O(N \* K)         | O(N \* K)            | **Time**: We iterate through `N` strings. For each string of length `K`, creating a character count array takes `O(K)` time. Converting the array to a tuple is `O(26)` or `O(1)` as the alphabet size is constant. Hash map operations are amortized `O(1)` as the tuple key length is constant (26). Thus, `O(N * K)`. <br> **Space**: Similar to the sorted string approach, all `N` strings are stored in the hash map, requiring `O(N * K)` space. The character count tuples are of constant size (26) and add `O(N * 26)` which simplifies to `O(N)` auxiliary space. So overall `O(N * K)`.                                                                                                                   |

The optimal solution using character count tuples as keys is generally considered more efficient in terms of time complexity, as it avoids the logarithmic factor of sorting each string.

## 5. Real-World Applications

The "Group Anagrams" problem, or the underlying techniques it employs, has several practical applications in various domains:

1.  **Text Processing and Natural Language Processing (NLP)**:
    *   **Spell Checkers and Autocorrect**: Identifying anagrams can help in suggesting corrections for misspelled words or variations of words.
    *   **Search Normalization**: In search engines, grouping anagrams can help in returning relevant results even if the user types a rearranged version of a word. For instance, searching for "listen" might also surface documents containing "silent".
    *   **Data Analysis**: Analyzing text data to find relationships between words or to normalize vocabulary.

2.  **Data Compression and Indexing**:
    *   **Database Systems**: In databases, similar to search normalization, grouping anagrams could be part of an indexing strategy to find permutations of a term more quickly.
    *   **Data Deduplication**: Reducing redundant storage by identifying and grouping identical "canonical forms" of data, even if their raw representation differs slightly (like anagrams).

3.  **Password Security and Encryption**:
    *   **Password Strength**: Anagram grouping can be used to assess password strength by identifying easy permutations.
    *   **Encryption**: While not direct, the concept of character permutations is fundamental in certain cryptographic algorithms.

4.  **Word Games and Puzzles**:
    *   Many word games (e.g., Scrabble, Anagram puzzles) rely on identifying anagrams. Algorithms to solve such puzzles often involve grouping anagrams.

5.  **Bioinformatics**:
    *   Identifying common sequences in DNA or protein strings, where the order might be permuted but the constituent elements are the same.

This problem teaches fundamental skills in using hash maps for efficient data aggregation and transforming data into canonical forms, which are invaluable techniques across many software engineering challenges.""",
}

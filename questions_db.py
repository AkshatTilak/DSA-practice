# Master Challenges Database - 110 Core Topics
# Each challenge has a "groups" list for cross-cutting category filtering.

CHALLENGES_DB = {
    "01_DSA": {
        "arrays_and_hashing": {
            "q01_two_sum": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/two-sum/",
                "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
                "groups": ["Array", "Hashing"],
                "starter_code": "def two_sum(nums: list[int], target: int) -> list[int]:\n    # Write your solution here\n    pass",
                "solutions": "# Approach 1: Naive (O(N^2))\n# ...",
                "test_code": "",
                "readme_content": ""
            },
            "q02_contains_duplicate": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/contains-duplicate/",
                "description": "Given an integer array `nums`, return `true` if any value appears at least twice in the array, and return `false` if every element is distinct.",
                "groups": ["Array", "Hashing"],
                "starter_code": "def contains_duplicate(nums: list[int]) -> bool:\n    # Write your solution here\n    pass",
                "solutions": "# Approach 1: Naive (Sort) O(N log N)\ndef contains_duplicate_naive(nums: list[int]) -> bool:\n    nums.sort()\n    for i in range(len(nums) - 1):\n        if nums[i] == nums[i+1]:\n            return True\n    return False\n\n# Approach 2: Optimal (Hash Set) O(N)\ndef contains_duplicate_optimal(nums: list[int]) -> bool:\n    seen = set()\n    for num in nums:\n        if num in seen:\n            return True\n        seen.add(num)\n    return False\n\n# Approach 3: Java\n'''\npublic boolean containsDuplicate(int[] nums) {\n    Set<Integer> set = new HashSet<>();\n    for (int n : nums) {\n        if (!set.add(n)) return true;\n    }\n    return false;\n}\n'''",
                "test_code": "def test_contains_duplicate():\n    assert contains_duplicate([1, 2, 3, 1]) is True\n    assert contains_duplicate([1, 2, 3, 4]) is False\n    assert contains_duplicate([]) is False",
                "readme_content": "# Contains Duplicate\nCheck for duplicate values in an array. Utilizes a Hash Set for O(1) average lookups.\nReal-world: Deduplicating log message IDs."
            },
            "q03_valid_anagram": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/valid-anagram/",
                "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.",
                "groups": ["String", "Hashing"],
                "starter_code": "def is_anagram(s: str, t: str) -> bool:\n    pass",
                "solutions": "# Optimal: count dictionary O(N)",
                "test_code": "def test_anagram():\n    assert is_anagram('anagram', 'nagaram') is True",
                "readme_content": "# Valid Anagram\nCompare character frequencies."
            },
            "q04_group_anagrams": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/group-anagrams/",
                "description": "Group an array of strings together if they are anagrams.",
                "groups": ["String", "Hashing"],
                "starter_code": "def group_anagrams(strs: list[str]) -> list[list[str]]:\n    pass",
                "solutions": "# Optimal: Hashing sorted tuple keys",
                "test_code": "def test_group_anagrams():\n    assert len(group_anagrams(['eat', 'tea'])) == 1",
                "readme_content": "# Group Anagrams\nGroup words by character count."
            },
            "q05_top_k_frequent_elements": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/top-k-frequent-elements/",
                "description": "Return the k most frequent elements.",
                "groups": ["Array", "Hashing", "Heap / Priority Queue"],
                "starter_code": "def top_k_frequent(nums: list[int], k: int) -> list[int]:\n    pass",
                "solutions": "# Optimal: Bucket Sort O(N) or Heap O(N log K)",
                "test_code": "def test_top_k():\n    assert set(top_k_frequent([1,1,1,2,2,3], 2)) == {1, 2}",
                "readme_content": "# Top K Frequent Elements\nBucket sort frequency mapping."
            },
            "q06_product_of_array_except_self": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/product-of-array-except-self/",
                "description": "Return an array where each index is the product of all elements except the one at that index, without using division.",
                "groups": ["Array"],
                "starter_code": "def product_except_self(nums: list[int]) -> list[int]:\n    pass",
                "solutions": "# Optimal: Prefix and Suffix products",
                "test_code": "def test_product():\n    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]",
                "readme_content": "# Product of Array Except Self\nAccumulate left products and right products."
            },
            "q07_longest_consecutive_sequence": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/longest-consecutive-sequence/",
                "description": "Find the length of the longest consecutive elements sequence in O(N).",
                "groups": ["Array", "Hashing"],
                "starter_code": "def longest_consecutive(nums: list[int]) -> int: \n    pass",
                "solutions": "# Optimal: Hash Set checking sequence starts",
                "test_code": "def test_consecutive():\n    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4",
                "readme_content": "# Longest Consecutive Sequence\nSearch sequence starting elements in Set."
            }
        },
        "two_pointers": {
            "q01_valid_palindrome": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/valid-palindrome/",
                "description": "Check if a string is a palindrome, ignoring non-alphanumeric chars.",
                "groups": ["String", "Two Pointers"],
                "starter_code": "def is_palindrome(s: str) -> bool:\n    # Write your solution here\n    pass",
                "solutions": "# Approach 1: Brute Force (Clean & Reverse) O(N) time, O(N) space\ndef is_palindrome_naive(s: str) -> bool:\n    clean = [c.lower() for c in s if c.isalnum()]\n    return clean == clean[::-1]\n\n# Approach 2: Optimal (Two Pointers) O(N) time, O(1) space\ndef is_palindrome_optimal(s: str) -> bool:\n    l, r = 0, len(s) - 1\n    while l < r:\n        while l < r and not s[l].isalnum(): l += 1\n        while l < r and not s[r].isalnum(): r -= 1\n        if s[l].lower() != s[r].lower():\n            return False\n        l += 1\n        r -= 1\n    return True\n\n# Approach 3: Java\n'''\npublic boolean isPalindrome(String s) {\n    int l = 0, r = s.length() - 1;\n    while(l < r) {\n        if (!Character.isLetterOrDigit(s.charAt(l))) l++;\n        else if (!Character.isLetterOrDigit(s.charAt(r))) r--;\n        else if (Character.toLowerCase(s.charAt(l++)) != Character.toLowerCase(s.charAt(r--))) return false;\n    }\n    return true;\n}\n'''",
                "test_code": "def test_palindrome():\n    assert is_palindrome('A man, a plan, a canal: Panama') is True\n    assert is_palindrome('race a car') is False\n    assert is_palindrome(' ') is True",
                "readme_content": "# Two Pointers: Valid Palindrome\nUsing two boundaries shrinking inwards.\nReal-world: Log validation, search string normalization."
            },
            "q02_two_sum_ii": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/",
                "description": "Find two numbers in a sorted array that add up to target.",
                "groups": ["Array", "Two Pointers"],
                "starter_code": "def two_sum_sorted(numbers: list[int], target: int) -> list[int]:\n    pass",
                "solutions": "# Optimal: Left & Right pointers narrowing down",
                "test_code": "def test_two_sum_ii():\n    assert two_sum_sorted([2,7,11,15], 9) == [1, 2]",
                "readme_content": "# Two Sum II\nShrinking pointer window on sorted data."
            },
            "q03_3sum": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/3sum/",
                "description": "Find all unique triplets that sum to zero.",
                "groups": ["Array", "Two Pointers"],
                "starter_code": "def three_sum(nums: list[int]) -> list[list[int]]:\n    pass",
                "solutions": "# Optimal: Sort then loop with two-pointers",
                "test_code": "def test_3sum():\n    assert len(three_sum([-1,0,1,2,-1,-4])) > 0",
                "readme_content": "# 3Sum\nReduce problem to Two Sum II in a loop."
            },
            "q04_container_with_most_water": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/container-with-most-water/",
                "description": "Find two lines that contain the most water.",
                "groups": ["Array", "Two Pointers"],
                "starter_code": "def max_area(height: list[int]) -> int:\n    pass",
                "solutions": "# Optimal: Shrink pointers keeping maximum height",
                "test_code": "def test_water():\n    assert max_area([1,8,6,2,5,4,8,3,7]) == 49",
                "readme_content": "# Container With Most Water\nMaximize width * min(height)."
            },
            "q05_trapping_rain_water": {
                "difficulty": "Hard",
                "link": "https://leetcode.com/problems/trapping-rain-water/",
                "description": "Compute how much water can be trapped after raining.",
                "groups": ["Array", "Two Pointers", "Dynamic Programming"],
                "starter_code": "def trap(height: list[int]) -> int:\n    pass",
                "solutions": "# Optimal: Two pointers tracking max walls O(N)",
                "test_code": "def test_trap():\n    assert trap([0,1,0,2,1,0,1,3,2,1,2,1]) == 6",
                "readme_content": "# Trapping Rain Water\nTrack max boundaries left and right."
            }
        },
        "sliding_window": {
            "q01_best_time_to_buy_and_sell_stock": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
                "description": "Find the maximum profit you can achieve buying one day and selling another.",
                "groups": ["Array", "Sliding Window"],
                "starter_code": "def max_profit(prices: list[int]) -> int:\n    # Write your solution here\n    pass",
                "solutions": "# Approach 1: Naive (O(N^2))\ndef max_profit_naive(prices: list[int]) -> int:\n    max_p = 0\n    for i in range(len(prices)):\n        for j in range(i + 1, len(prices)):\n            max_p = max(max_p, prices[j] - prices[i])\n    return max_p\n\n# Approach 2: Optimal (Sliding Window / Min Tracker) O(N)\ndef max_profit_optimal(prices: list[int]) -> int:\n    min_p = float('inf')\n    max_p = 0\n    for p in prices:\n        if p < min_p: min_p = p\n        elif p - min_p > max_p: max_p = p - min_p\n    return max_p\n\n# Approach 3: Java\n'''\npublic int maxProfit(int[] prices) {\n    int min = Integer.MAX_VALUE, max = 0;\n    for(int p : prices) {\n        if(p < min) min = p;\n        else if(p - min > max) max = p - min;\n    }\n    return max;\n}\n'''",
                "test_code": "def test_stock():\n    assert max_profit([7,1,5,3,6,4]) == 5\n    assert max_profit([7,6,4,3,1]) == 0",
                "readme_content": "# Sliding Window: Stock Profit\nDynamic window boundaries sliding to track profit margins."
            },
            "q02_longest_substring_without_repeating_characters": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
                "description": "Find the length of the longest substring without repeating characters.",
                "groups": ["String", "Sliding Window", "Hashing"],
                "starter_code": "def length_of_longest_substring(s: str) -> int:\n    pass",
                "solutions": "# Optimal: Set sliding window O(N)",
                "test_code": "def test_longest():\n    assert length_of_longest_substring('abcabcbb') == 3",
                "readme_content": "# Longest Substring Without Repeating Characters\nSlide window start forward when duplicates hit."
            },
            "q03_longest_repeating_character_replacement": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/longest-repeating-character-replacement/",
                "description": "Find length of longest repeating substring after replacing at most k characters.",
                "groups": ["String", "Sliding Window"],
                "starter_code": "def character_replacement(s: str, k: int) -> int:\n    pass",
                "solutions": "# Optimal: Slide window checking counts",
                "test_code": "def test_replacement():\n    assert character_replacement('ABAB', 2) == 4",
                "readme_content": "# Longest Repeating Character Replacement\nWindow size - max character count <= k."
            },
            "q04_permutation_in_string": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/permutation-in-string/",
                "description": "Return true if s2 contains a permutation of s1.",
                "groups": ["String", "Sliding Window", "Hashing"],
                "starter_code": "def check_inclusion(s1: str, s2: str) -> bool:\n    pass",
                "solutions": "# Optimal: Fixed window character frequency match",
                "test_code": "def test_permutation():\n    assert check_inclusion('ab', 'eidbaooo') is True",
                "readme_content": "# Permutation in String\nSliding match window of length s1."
            },
            "q05_minimum_window_substring": {
                "difficulty": "Hard",
                "link": "https://leetcode.com/problems/minimum-window-substring/",
                "description": "Find the minimum window in s containing all characters of t.",
                "groups": ["String", "Sliding Window", "Hashing"],
                "starter_code": "def min_window(s: str, t: str) -> str:\n    pass",
                "solutions": "# Optimal: Dynamic window shrinking to check coverage",
                "test_code": "def test_min_window():\n    assert min_window('ADOBECODEBANC', 'ABC') == 'BANC'",
                "readme_content": "# Minimum Window Substring\nTrack characters matching constraints."
            }
        },
        "stack": {
            "q01_valid_parentheses": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/valid-parentheses/",
                "description": "Given a string containing brackets, determine if the input string is valid.",
                "groups": ["String", "Stack & Queue"],
                "starter_code": "def is_valid(s: str) -> bool:\n    # Write your solution here\n    pass",
                "solutions": "# Approach 1: Naive (Replace pairs recursively) O(N^2) time, O(1) space\ndef is_valid_naive(s: str) -> bool:\n    old_len = -1\n    while len(s) != old_len:\n        old_len = len(s)\n        s = s.replace('()', '').replace('[]', '').replace('{}', '')\n    return len(s) == 0\n\n# Approach 2: Optimal (LIFO Stack) O(N) time, O(N) space\ndef is_valid_optimal(s: str) -> bool:\n    stack = []\n    mapping = {')': '(', ']': '[', '}': '{'}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack\n\n# Approach 3: Java\n'''\npublic boolean isValid(String s) {\n    Stack<Character> stack = new Stack<>();\n    for (char c : s.toCharArray()) {\n        if (c == '(') stack.push(')');\n        else if (c == '[') stack.push(']');\n        else if (c == '{') stack.push('}');\n        else if (stack.isEmpty() || stack.pop() != c) return false;\n    }\n    return stack.isEmpty();\n}\n'''",
                "test_code": "def test_parentheses():\n    assert is_valid('()[]{}') is True\n    assert is_valid('(]') is False\n    assert is_valid('([)]') is False",
                "readme_content": "# Stack: Valid Parentheses\nLast-in First-out matching structures.\nReal-world: Compiler syntax parsers, matching parentheses."
            },
            "q02_min_stack": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/min-stack/",
                "description": "Design a stack that supports push, pop, top, and retrieving the minimum element in O(1).",
                "groups": ["Stack & Queue"],
                "starter_code": "class MinStack:\n    def __init__(self):\n        pass\n    def push(self, val: int) -> None:\n        pass\n    def pop(self) -> None:\n        pass\n    def top(self) -> int:\n        pass\n    def getMin(self) -> int:\n        pass",
                "solutions": "# Optimal: Dual stacks tracking min state O(1)",
                "test_code": "def test_min_stack():\n    ms = MinStack()\n    # test sequence...",
                "readme_content": "# Min Stack\nTrack running minimums in companion stack."
            },
            "q03_evaluate_reverse_polish_notation": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/evaluate-reverse-polish-notation/",
                "description": "Evaluate RPN mathematical expression.",
                "groups": ["Stack & Queue"],
                "starter_code": "def eval_rpn(tokens: list[str]) -> int:\n    pass",
                "solutions": "# Optimal: Stack evaluations",
                "test_code": "def test_rpn():\n    assert eval_rpn(['2', '1', '+', '3', '*']) == 9",
                "readme_content": "# Evaluate RPN\nStore operands on stack, execute when operators show."
            },
            "q04_generate_parentheses": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/generate-parentheses/",
                "description": "Generate all combinations of n pairs of valid parentheses.",
                "groups": ["String", "Stack & Queue", "Backtracking"],
                "starter_code": "def generate_parenthesis(n: int) -> list[str]:\n    pass",
                "solutions": "# Optimal: Backtracking using open/close balances",
                "test_code": "def test_generate():\n    assert len(generate_parenthesis(3)) == 5",
                "readme_content": "# Generate Parentheses\nAdd open bracket if open < n, close bracket if close < open."
            },
            "q05_daily_temperatures": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/daily-temperatures/",
                "description": "Return an array showing days to wait for a warmer temperature.",
                "groups": ["Array", "Stack & Queue"],
                "starter_code": "def daily_temperatures(temperatures: list[int]) -> list[int]:\n    pass",
                "solutions": "# Optimal: Monotonic decreasing stack O(N)",
                "test_code": "def test_temp():\n    assert daily_temperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]",
                "readme_content": "# Daily Temperatures\nMonotonic stack maintaining un-updated index values."
            },
            "q06_largest_rectangle_in_histogram": {
                "difficulty": "Hard",
                "link": "https://leetcode.com/problems/largest-rectangle-in-histogram/",
                "description": "Find the area of largest rectangle in histogram.",
                "groups": ["Array", "Stack & Queue"],
                "starter_code": "def largest_rectangle_area(heights: list[int]) -> int:\n    pass",
                "solutions": "# Optimal: Monotonic increasing stack",
                "test_code": "def test_histogram():\n    assert largest_rectangle_area([2,1,5,6,2,3]) == 10",
                "readme_content": "# Largest Rectangle\nTrigger boundaries using monotonic stack indexes."
            }
        },
        "binary_search": {
            "q01_binary_search": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/binary-search/",
                "description": "Search for a target value in a sorted array, returning index or -1.",
                "groups": ["Array", "Binary Search"],
                "starter_code": "def search(nums: list[int], target: int) -> int:\n    # Write your solution here\n    pass",
                "solutions": "# Approach 1: Naive (Linear search) O(N)\ndef search_naive(nums: list[int], target: int) -> int:\n    for i in range(len(nums)):\n        if nums[i] == target: return i\n    return -1\n\n# Approach 2: Optimal (Split-interval) O(log N)\ndef search_optimal(nums: list[int], target: int) -> int:\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        m = l + (r - l) // 2\n        if nums[m] == target: return m\n        elif nums[m] < target: l = m + 1\n        else: r = m - 1\n    return -1",
                "test_code": "def test_binary_search():\n    assert search([-1,0,3,5,9,12], 9) == 4\n    assert search([-1,0,3,5,9,12], 2) == -1",
                "readme_content": "# Binary Search\nInterval splitting on sorted collections.\nReal-world: Index search, routing tables, databases."
            },
            "q02_search_a_2d_matrix": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/search-a-2d-matrix/",
                "description": "Search target in 2D sorted matrix.",
                "groups": ["Array", "Binary Search", "Matrix"],
                "starter_code": "def search_matrix(matrix: list[list[int]], target: int) -> bool:\n    pass",
                "solutions": "# Optimal: Logarithmic virtual 1D array search",
                "test_code": "def test_matrix():\n    assert search_matrix([[1,3,5,7],[10,11,16,20]], 3) is True",
                "readme_content": "# Search 2D Matrix\nMap index virtual_1d to row/col indexes."
            },
            "q03_koko_eating_bananas": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/koko-eating-bananas/",
                "description": "Find the minimum rate to eat all piles within H hours.",
                "groups": ["Array", "Binary Search"],
                "starter_code": "def min_eating_speed(piles: list[int], h: int) -> int:\n    pass",
                "solutions": "# Optimal: Binary search on rates [1, max(piles)]",
                "test_code": "def test_koko():\n    assert min_eating_speed([3,6,7,11], 8) == 4",
                "readme_content": "# Koko Eating Bananas\nSearch range of speeds using binary validation."
            },
            "q04_find_minimum_in_rotated_sorted_array": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/",
                "description": "Find minimum element in a sorted array that was rotated.",
                "groups": ["Array", "Binary Search"],
                "starter_code": "def find_min(nums: list[int]) -> int:\n    pass",
                "solutions": "# Optimal: Binary search tracking inflection point",
                "test_code": "def test_min_rotated():\n    assert find_min([3,4,5,1,2]) == 1",
                "readme_content": "# Find Minimum Rotated\nCompare mid value against right boundary."
            },
            "q05_search_in_rotated_sorted_array": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
                "description": "Find index of target in rotated sorted array.",
                "groups": ["Array", "Binary Search"],
                "starter_code": "def search_rotated(nums: list[int], target: int) -> int:\n    pass",
                "solutions": "# Optimal: Binary search finding sorted side",
                "test_code": "def test_search_rotated():\n    assert search_rotated([4,5,6,7,0,1,2], 0) == 4",
                "readme_content": "# Search in Rotated Array\nValidate target inside the sorted partition."
            }
        },
        "linked_list": {
            "q01_reverse_linked_list": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/reverse-linked-list/",
                "description": "Reverse a singly linked list.",
                "groups": ["Linked List"],
                "starter_code": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head: ListNode) -> ListNode:\n    # Write your solution here\n    pass",
                "solutions": "# Iterative pointer swapping O(N)\ndef reverse_list_optimal(head):\n    prev, curr = None, head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev",
                "test_code": "def test_reverse():\n    # Setup simple list 1->2 and reverse\n    pass",
                "readme_content": "# Reverse Linked List\nSwapping pointers sequentially."
            },
            "q02_merge_two_sorted_lists": { "difficulty": "Easy", "link": "https://leetcode.com/problems/merge-two-sorted-lists/", "description": "Merge two sorted lists.", "groups": ["Linked List"] },
            "q03_reorder_list": { "difficulty": "Medium", "link": "https://leetcode.com/problems/reorder-list/", "description": "Reorder list in-place.", "groups": ["Linked List"] },
            "q04_remove_nth_node": { "difficulty": "Medium", "link": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/", "description": "Remove Nth node.", "groups": ["Linked List", "Two Pointers"] },
            "q05_copy_list_with_random_pointer": { "difficulty": "Medium", "link": "https://leetcode.com/problems/copy-list-with-random-pointer/", "description": "Copy list.", "groups": ["Linked List", "Hashing"] },
            "q06_add_two_numbers": { "difficulty": "Medium", "link": "https://leetcode.com/problems/add-two-numbers/", "description": "Add two numbers list representation.", "groups": ["Linked List", "Math"] },
            "q07_linked_list_cycle": { "difficulty": "Easy", "link": "https://leetcode.com/problems/linked-list-cycle/", "description": "Detect cycle.", "groups": ["Linked List", "Two Pointers"] },
            "q08_find_duplicate": { "difficulty": "Medium", "link": "https://leetcode.com/problems/find-the-duplicate-number/", "description": "Find duplicate using cycle detection.", "groups": ["Array", "Linked List", "Two Pointers"] }
        },
        "trees": {
            "q01_invert_binary_tree": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/invert-binary-tree/",
                "description": "Invert a binary tree (swap left and right child recursively).",
                "groups": ["Tree"],
                "starter_code": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef invert_tree(root: TreeNode) -> TreeNode:\n    # Write your solution here\n    pass",
                "solutions": "def invert_tree_optimal(root):\n    if not root: return None\n    root.left, root.right = invert_tree_optimal(root.right), invert_tree_optimal(root.left)\n    return root",
                "test_code": "def test_invert():\n    pass",
                "readme_content": "# Invert Binary Tree\nRecursive traversal swaps."
            },
            "q02_max_depth": { "difficulty": "Easy", "link": "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "description": "Max depth.", "groups": ["Tree"] },
            "q03_diameter": { "difficulty": "Easy", "link": "https://leetcode.com/problems/diameter-of-binary-tree/", "description": "Tree diameter.", "groups": ["Tree"] },
            "q04_balanced_tree": { "difficulty": "Easy", "link": "https://leetcode.com/problems/balanced-binary-tree/", "description": "Check balance.", "groups": ["Tree"] },
            "q05_same_tree": { "difficulty": "Easy", "link": "https://leetcode.com/problems/same-tree/", "description": "Verify same tree.", "groups": ["Tree"] },
            "q06_subtree": { "difficulty": "Easy", "link": "https://leetcode.com/problems/subtree-of-another-tree/", "description": "Subtree match.", "groups": ["Tree"] },
            "q07_lowest_common_ancestor": { "difficulty": "Easy", "link": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/", "description": "LCA BST.", "groups": ["Tree", "Binary Search"] },
            "q08_level_order": { "difficulty": "Medium", "link": "https://leetcode.com/problems/binary-tree-level-order-traversal/", "description": "BFS traversal.", "groups": ["Tree", "Graph"] },
            "q09_validate_bst": { "difficulty": "Medium", "link": "https://leetcode.com/problems/validate-binary-search-tree/", "description": "Validate BST values.", "groups": ["Tree", "Binary Search"] },
            "q10_kth_smallest": { "difficulty": "Medium", "link": "https://leetcode.com/problems/kth-smallest-element-in-a-bst/", "description": "Find Kth smallest.", "groups": ["Tree", "Binary Search"] }
        },
        "heap": {
            "q01_kth_largest": { "difficulty": "Easy", "link": "https://leetcode.com/problems/kth-largest-element-in-a-stream/", "description": "Kth largest element in stream.", "groups": ["Heap / Priority Queue"] },
            "q02_last_stone_weight": { "difficulty": "Easy", "link": "https://leetcode.com/problems/last-stone-weight/", "description": "Last stone weight using max heap.", "groups": ["Heap / Priority Queue"] },
            "q03_k_closest_points": { "difficulty": "Medium", "link": "https://leetcode.com/problems/k-closest-points-to-origin/", "description": "Find K closest points.", "groups": ["Heap / Priority Queue", "Math"] },
            "q04_kth_largest_array": { "difficulty": "Medium", "link": "https://leetcode.com/problems/kth-largest-element-in-an-array/", "description": "Kth largest array.", "groups": ["Heap / Priority Queue", "Array"] },
            "q05_median_stream": { "difficulty": "Hard", "link": "https://leetcode.com/problems/find-median-from-data-stream/", "description": "Find median from dynamic stream.", "groups": ["Heap / Priority Queue"] }
        },
        "graphs": {
            "q01_number_of_islands": {
                "difficulty": "Medium",
                "link": "https://leetcode.com/problems/number-of-islands/",
                "description": "Given a 2D grid of '1's (land) and '0's (water), return the number of islands.",
                "groups": ["Graph", "Matrix"],
                "starter_code": "def num_islands(grid: list[list[str]]) -> int:\n    # Write your solution here\n    pass",
                "solutions": "def num_islands_optimal(grid):\n    if not grid: return 0\n    rows, cols = len(grid), len(grid[0])\n    visited = set()\n    islands = 0\n    \n    def dfs(r, c):\n        if r<0 or r>=rows or c<0 or c>=cols or grid[r][c]=='0' or (r,c) in visited:\n            return\n        visited.add((r,c))\n        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n            dfs(r+dr, c+dc)\n            \n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1' and (r,c) not in visited:\n                dfs(r, c)\n                islands += 1\n    return islands",
                "test_code": "def test_islands():\n    pass",
                "readme_content": "# Number of Islands\nDFS/BFS connected components traversal."
            },
            "q02_clone_graph": { "difficulty": "Medium", "link": "https://leetcode.com/problems/clone-graph/", "description": "Clone deep copy graph.", "groups": ["Graph", "Hashing"] },
            "q03_max_area": { "difficulty": "Medium", "link": "https://leetcode.com/problems/max-area-of-island/", "description": "Max area island.", "groups": ["Graph", "Matrix"] },
            "q04_pacific_atlantic": { "difficulty": "Medium", "link": "https://leetcode.com/problems/pacific-atlantic-water-flow/", "description": "Water flow maps.", "groups": ["Graph", "Matrix"] },
            "q05_surrounded_regions": { "difficulty": "Medium", "link": "https://leetcode.com/problems/surrounded-regions/", "description": "Capture border-trapped regions.", "groups": ["Graph", "Matrix"] },
            "q06_rotting_oranges": { "difficulty": "Medium", "link": "https://leetcode.com/problems/rotting-oranges/", "description": "Multi-source BFS decay.", "groups": ["Graph", "Matrix"] },
            "q07_course_schedule": { "difficulty": "Medium", "link": "https://leetcode.com/problems/course-schedule/", "description": "Topological sort course check.", "groups": ["Graph"] },
            "q08_redundant_connection": { "difficulty": "Medium", "link": "https://leetcode.com/problems/redundant-connection/", "description": "Union-find cycle detection.", "groups": ["Graph"] }
        },
        "dynamic_programming": {
            "q01_climbing_stairs": {
                "difficulty": "Easy",
                "link": "https://leetcode.com/problems/climbing-stairs/",
                "description": "Calculate distinct ways to climb n steps if you take 1 or 2 steps each time.",
                "groups": ["Dynamic Programming", "Math"],
                "starter_code": "def climb_stairs(n: int) -> int:\n    # Write your solution here\n    pass",
                "solutions": "def climb_stairs_optimal(n):\n    if n <= 2: return n\n    one, two = 1, 2\n    for i in range(3, n+1):\n        one, two = two, one + two\n    return two",
                "test_code": "def test_climb():\n    pass",
                "readme_content": "# Climbing Stairs\nTabulation dynamic planning."
            },
            "q02_min_cost_climbing": { "difficulty": "Easy", "link": "https://leetcode.com/problems/min-cost-climbing-stairs/", "description": "Min cost stairs.", "groups": ["Dynamic Programming", "Array"] },
            "q03_house_robber": { "difficulty": "Medium", "link": "https://leetcode.com/problems/house-robber/", "description": "Rob non-adjacent houses.", "groups": ["Dynamic Programming", "Array"] },
            "q04_house_robber_ii": { "difficulty": "Medium", "link": "https://leetcode.com/problems/house-robber-ii/", "description": "Circular robber.", "groups": ["Dynamic Programming", "Array"] },
            "q05_longest_palindromic_substring": { "difficulty": "Medium", "link": "https://leetcode.com/problems/longest-palindromic-substring/", "description": "Find longest palindrome.", "groups": ["Dynamic Programming", "String"] },
            "q06_decode_ways": { "difficulty": "Medium", "link": "https://leetcode.com/problems/decode-ways/", "description": "Ways to decode string.", "groups": ["Dynamic Programming", "String"] },
            "q07_coin_change": { "difficulty": "Medium", "link": "https://leetcode.com/problems/coin-change/", "description": "Fewest coins to sum.", "groups": ["Dynamic Programming"] },
            "q08_longest_increasing_subsequence": { "difficulty": "Medium", "link": "https://leetcode.com/problems/longest-increasing-subsequence/", "description": "LIS length.", "groups": ["Dynamic Programming", "Array", "Binary Search"] },
            "q09_partition_subset_sum": { "difficulty": "Medium", "link": "https://leetcode.com/problems/partition-equal-subset-sum/", "description": "Partition equal sum check.", "groups": ["Dynamic Programming", "Array"] }
        }
    },
    "02_Data_Science_ML": {
        "classical_ml": {
            "q01_linear_regression": {
                "difficulty": "Medium",
                "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/",
                "description": "Implement linear regression fitting using gradient descent from scratch.",
                "groups": ["Classical ML", "Optimization"],
                "starter_code": "import numpy as np\n\ndef fit_linear_regression(X: np.ndarray, y: np.ndarray, lr=0.01, epochs=100) -> tuple[np.ndarray, float]:\n    # Return weights (np.ndarray) and bias (float)\n    pass",
                "solutions": "def fit_linear_regression_optimal(X, y, lr=0.01, epochs=100):\n    n_samples, n_features = X.shape\n    w = np.zeros(n_features)\n    b = 0.0\n    for _ in range(epochs):\n        predictions = np.dot(X, w) + b\n        dw = (1/n_samples) * np.dot(X.T, (predictions - y))\n        db = (1/n_samples) * np.sum(predictions - y)\n        w -= lr * dw\n        b -= lr * db\n    return w, b",
                "test_code": "def test_linear():\n    pass",
                "readme_content": "# Linear Regression\nGradient descent optimization."
            },
            "q02_logistic_regression": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Logistic regression classification.", "groups": ["Classical ML", "Optimization"] },
            "q03_decision_trees": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "ID3 tree construction.", "groups": ["Classical ML"] },
            "q04_k_means": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Cluster iterative centroids.", "groups": ["Classical ML", "Unsupervised Learning"] },
            "q05_random_forest": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Ensemble bagging trees.", "groups": ["Classical ML", "Ensemble Methods"] },
            "q06_support_vector_machines": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Hyperplane margins.", "groups": ["Classical ML", "Optimization"] },
            "q07_naive_bayes": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Bayesian probability classification.", "groups": ["Classical ML", "Probabilistic Models"] },
            "q08_pca": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Eigenvalue dimension reduction.", "groups": ["Classical ML", "Dimensionality Reduction"] }
        },
        "architectures": {
            "q01_self_attention": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/",
                "description": "Calculate scaled dot-product self-attention weights and final contextual projections.",
                "groups": ["Deep Learning", "Transformers"],
                "starter_code": "import numpy as np\n\ndef scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:\n    # Returns (output, attention_weights)\n    pass",
                "solutions": "def scaled_dot_product_attention_optimal(Q, K, V):\n    dk = Q.shape[-1]\n    scores = np.dot(Q, K.T) / np.sqrt(dk)\n    # Stable Softmax\n    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))\n    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)\n    output = np.dot(attention_weights, V)\n    return output, attention_weights",
                "test_code": "def test_attention():\n    pass",
                "readme_content": "# Self-Attention\nScaled Query Key interactions matrix weights."
            },
            "q02_cnn_layer": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Forward pass CNN filter convolution.", "groups": ["Deep Learning", "Computer Vision"] },
            "q03_rnn_step": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Recurrent step state update.", "groups": ["Deep Learning", "Sequence Models"] },
            "q04_gnn_aggregation": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Graph neighborhood feature aggregator.", "groups": ["Deep Learning", "Graph Neural Networks"] },
            "q05_backpropagation": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Gradient backprop neural layer.", "groups": ["Deep Learning", "Optimization"] }
        },
        "systems_evaluation": {
            "q01_metrics": {
                "difficulty": "Medium",
                "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/",
                "description": "Calculate precision, recall, and F1 from predictions.",
                "groups": ["Evaluation & Metrics"],
                "starter_code": "def calculate_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:\n    pass",
                "solutions": "",
                "test_code": ""
            },
            "q02_roc_auc": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Approximate Area Under ROC.", "groups": ["Evaluation & Metrics"] },
            "q03_mean_squared_error": { "difficulty": "Easy", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "MSE calculator.", "groups": ["Evaluation & Metrics"] },
            "q04_log_loss": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Binary cross-entropy loss.", "groups": ["Evaluation & Metrics", "Deep Learning"] },
            "q05_mape": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Mean Absolute Percentage Error.", "groups": ["Evaluation & Metrics"] },
            "q06_r_squared": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/", "description": "Coefficient of determination.", "groups": ["Evaluation & Metrics"] }
        }
    },
    "03_LLD": {
        "design_patterns": {
            "q01_singleton": {
                "difficulty": "Medium",
                "link": "https://refactoring.guru/design-patterns/singleton",
                "description": "Implement double-checked locking thread-safe singleton metaclass.",
                "groups": ["Creational Patterns"],
                "starter_code": "class SingletonMeta(type):\n    pass",
                "solutions": "",
                "test_code": ""
            },
            "q02_strategy_pattern": {
                "difficulty": "Medium",
                "link": "https://refactoring.guru/design-patterns/strategy",
                "description": "Implement Strategy pattern for dynamic payment billing integrations.",
                "groups": ["Behavioral Patterns"],
                "starter_code": "class PaymentStrategy:\n    def pay(self, amount: float) -> str:\n        pass\n\nclass CreditCardPayment(PaymentStrategy):\n    def pay(self, amount: float) -> str:\n        return f'Paid {amount} using Credit Card'\n\nclass PayPalPayment(PaymentStrategy):\n    def pay(self, amount: float) -> str:\n        return f'Paid {amount} using PayPal'\n\nclass OrderProcessor:\n    def __init__(self, strategy: PaymentStrategy):\n        self.strategy = strategy\n    def process(self, amount: float) -> str:\n        return self.strategy.pay(amount)",
                "solutions": "# Strategy pattern bindings",
                "test_code": "def test_strategy():\n    pass",
                "readme_content": "# Strategy Pattern\nBehavioral encapsulation."
            },
            "q03_observer_pattern": {
                "difficulty": "Medium",
                "link": "https://refactoring.guru/design-patterns/observer",
                "description": "Implement Publish-Subscribe dynamic messaging engine via Observer Pattern.",
                "groups": ["Behavioral Patterns"],
                "starter_code": "class Subject:\n    def __init__(self):\n        self._observers = []\n    def register(self, obs):\n        self._observers.append(obs)\n    def notify(self, event: str):\n        for o in self._observers: o.update(event)\n\nclass Observer:\n    def update(self, event: str):\n        pass",
                "solutions": "# Observer implementations",
                "test_code": "def test_observer():\n    pass",
                "readme_content": "# Observer Pattern\nDecoupled event bindings."
            },
            "q04_factory_pattern": { "difficulty": "Medium", "link": "https://refactoring.guru/design-patterns/factory-method", "description": "Factory method class instantiations.", "groups": ["Creational Patterns"] },
            "q05_decorator_pattern": { "difficulty": "Medium", "link": "https://refactoring.guru/design-patterns/decorator", "description": "Wrapper pattern dynamic additions.", "groups": ["Structural Patterns"] },
            "q06_adapter_pattern": { "difficulty": "Medium", "link": "https://refactoring.guru/design-patterns/adapter", "description": "Translate interface adapter.", "groups": ["Structural Patterns"] },
            "q07_command_pattern": { "difficulty": "Medium", "link": "https://refactoring.guru/design-patterns/command", "description": "Encapsulate executable operations.", "groups": ["Behavioral Patterns"] }
        },
        "case_studies": {
            "q01_parking_lot": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/design-parking-lot-low-level-design/",
                "description": "Design object models for multi-level parking lot including spot size constraints, ticket calculations.",
                "groups": ["OOP Case Studies"],
                "starter_code": "class SpotType:\n    SMALL, COMPACT, LARGE = 1, 2, 3\n\nclass ParkingSpot:\n    def __init__(self, id, spot_type):\n        self.id = id\n        self.spot_type = spot_type\n        self.is_free = True",
                "solutions": "# Parking lot designs",
                "test_code": "def test_parking():\n    pass",
                "readme_content": "# Parking Lot LLD\nObject relationships allocation."
            },
            "q02_movie_booking": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/design-movie-ticket-booking-system-online-bookmyshow-lld/", "description": "Design online ticket booker.", "type": "design", "groups": ["OOP Case Studies"] },
            "q03_elevator_system": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/design-elevator-system-low-level-design/", "description": "Elevator dispatch constraints.", "type": "design", "groups": ["OOP Case Studies", "Concurrency"] },
            "q04_splitwise_expense": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/design-splitwise-low-level-design/", "description": "Expense share calculations.", "type": "design", "groups": ["OOP Case Studies"] },
            "q05_vending_machine": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/design-vending-machine-lld/", "description": "Vending state pattern machine.", "type": "design", "groups": ["OOP Case Studies", "Behavioral Patterns"] },
            "q06_tic_tac_toe": { "difficulty": "Medium", "type": "design", "description": "Design Tic-Tac-Toe game.", "groups": ["OOP Case Studies", "Game Design"] },
            "q07_snake_ladder": { "difficulty": "Medium", "type": "design", "description": "Design Snake & Ladder game.", "groups": ["OOP Case Studies", "Game Design"] },
            "q08_chess_game": { "difficulty": "Hard", "type": "design", "description": "Design Chess Game.", "groups": ["OOP Case Studies", "Game Design"] },
            "q09_library_management": { "difficulty": "Medium", "type": "design", "description": "Design Library Management System.", "groups": ["OOP Case Studies"] },
            "q10_hotel_management": { "difficulty": "Medium", "type": "design", "description": "Design Hotel Management System.", "groups": ["OOP Case Studies"] },
            "q11_coffee_vending": { "difficulty": "Medium", "type": "design", "description": "Design Coffee Vending Machine.", "groups": ["OOP Case Studies", "Behavioral Patterns"] },
            "q12_text_editor": { "difficulty": "Hard", "type": "design", "description": "Design Text Editor / Word Processor.", "groups": ["OOP Case Studies"] },
            "q13_food_ordering": { "difficulty": "Hard", "type": "design", "description": "Design Food Ordering and Ratings (Zomato/Swiggy).", "groups": ["OOP Case Studies"] },
            "q14_logger_framework": { "difficulty": "Medium", "type": "design", "description": "Design a Logger Framework (Chain of Responsibility).", "groups": ["OOP Case Studies", "Behavioral Patterns"] },
            "q15_notification_service": { "difficulty": "Medium", "type": "design", "description": "Design Notification Service (Observer Pattern).", "groups": ["OOP Case Studies", "Behavioral Patterns"] },
            "q16_caching_framework": { "difficulty": "Hard", "type": "design", "description": "Design Caching Framework (LRU/LFU, Thread-safe).", "groups": ["OOP Case Studies", "Caching & Storage"] },
            "q17_rate_limiter": { "difficulty": "Hard", "type": "design", "description": "Design Distributed Rate Limiter (Token Bucket / Sliding Window).", "groups": ["OOP Case Studies", "Concurrency"] },
            "q18_kv_store": { "difficulty": "Hard", "type": "design", "description": "Design Key-Value Store like Redis (LLD).", "groups": ["OOP Case Studies", "Caching & Storage"] },
            "q19_blocking_queue": { "difficulty": "Medium", "type": "design", "description": "Design Thread-safe Blocking Queue.", "groups": ["OOP Case Studies", "Concurrency"] },
            "q20_rw_lock": { "difficulty": "Medium", "type": "design", "description": "Design Readers-Writers Lock.", "groups": ["OOP Case Studies", "Concurrency"] },
            "q21_pub_sub": { "difficulty": "Hard", "type": "design", "description": "Design Pub-Sub System.", "groups": ["OOP Case Studies", "Messaging"] },
            "q22_web_crawler": { "difficulty": "Hard", "type": "design", "description": "Design Web Crawler (Extensible design).", "groups": ["OOP Case Studies", "Concurrency"] },
            "q23_collaborative_editor": { "difficulty": "Hard", "type": "design", "description": "Design Collaborative Document Editor (like Google Docs).", "groups": ["OOP Case Studies", "Concurrency"] },
            "q24_atm_system": { "difficulty": "Medium", "type": "design", "description": "Design ATM / Banking System.", "groups": ["OOP Case Studies"] },
            "q25_undo_redo": { "difficulty": "Medium", "type": "design", "description": "Design Undo-Redo Framework (Command Pattern).", "groups": ["OOP Case Studies", "Behavioral Patterns"] },
            "q26_airline_reservation": { "difficulty": "Hard", "type": "design", "description": "Design Airline Reservation System.", "groups": ["OOP Case Studies"] },
            "q27_spotify_playlist": { "difficulty": "Medium", "type": "design", "description": "Design Spotify Playlist Manager.", "groups": ["OOP Case Studies"] },
            "q28_url_shortener_lld": { "difficulty": "Medium", "type": "design", "description": "Design URL Shortener (bit.ly) - LLD focus.", "groups": ["OOP Case Studies", "Hashing"] },
            "q29_elevator_group": { "difficulty": "Hard", "type": "design", "description": "Design Advanced Elevator Group Control.", "groups": ["OOP Case Studies", "Concurrency"] },
            "q30_ticket_resolution": { "difficulty": "Medium", "type": "design", "description": "Design Ticket Resolution System (Support/Tickets).", "groups": ["OOP Case Studies"] },
            "q31_file_system": { "difficulty": "Medium", "type": "design", "description": "Design File System (Composite Pattern).", "groups": ["OOP Case Studies", "Structural Patterns"] },
            "q32_multiplayer_lobby": { "difficulty": "Hard", "type": "design", "description": "Design Online Multiplayer Game Lobby.", "groups": ["OOP Case Studies", "Game Design", "Concurrency"] }
        }
    },
    "04_HLD": {
        "system_components": {
            "q01_consistent_hashing": {
                "difficulty": "Hard",
                "link": "https://www.systemdesignprimer.com/consistent-hashing",
                "description": "Implement consistent hashing ring with virtual nodes configuration.",
                "groups": ["Distributed Systems", "Hashing"],
                "starter_code": "import hashlib\n\nclass ConsistentHashRing:\n    def __init__(self, replicas=3):\n        self.replicas = replicas\n        self.ring = {} # hash -> node\n        self.sorted_keys = []\n\n    def add_node(self, node: str) -> None:\n        pass\n    def remove_node(self, node: str) -> None:\n        pass\n    def get_node(self, key: str) -> str:\n        pass",
                "solutions": "# Consistent hashing allocations",
                "test_code": "def test_hashing():\n    pass",
                "readme_content": "# Consistent Hashing\nNode rings virtual configurations."
            },
            "q02_load_balancers": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/load-balancers-system-design/", "description": "LB routing logic.", "type": "design", "groups": ["Distributed Systems", "Networking"] },
            "q03_redis_caching": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/redis-caching-system-design/", "description": "Cache invalidation write policies.", "type": "design", "groups": ["Caching & Storage", "Databases"] },
            "q04_kafka_messaging": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/kafka-system-design/", "description": "Topic partition consumer lags.", "type": "design", "groups": ["Messaging", "Distributed Systems"] },
            "q05_cdn_distributions": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/content-delivery-networks-cdn-system-design/", "description": "Static content edge validation.", "type": "design", "groups": ["Networking", "Distributed Systems"] },
            "q06_database_sharding": { "difficulty": "Hard", "link": "https://www.geeksforgeeks.org/database-sharding-system-design/", "description": "Horizontal databases partitioning schemes.", "type": "design", "groups": ["Databases", "Distributed Systems"] }
        },
        "real_world_cases": {
            "q01_vehicle_damage": {
                "difficulty": "Hard",
                "link": "",
                "description": "Design an Automated Vehicle Damage Auto-Penalty Pipeline.",
                "type": "design",
                "groups": ["Real-World Systems", "Data Pipelines"]
            },
            "q02_url_shortener": {
                "difficulty": "Medium",
                "link": "https://www.geeksforgeeks.org/design-url-shortener-tinyurl/",
                "description": "Design a high-scale TinyURL redirection engine.",
                "type": "design",
                "groups": ["Real-World Systems", "Hashing"]
            },
            "q03_ride_sharing": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/design-ride-sharing-service-like-uber-lyft-system-design/",
                "description": "Design Uber dispatch driver passenger matching service.",
                "type": "design",
                "groups": ["Real-World Systems", "Distributed Systems"]
            },
            "q04_news_feed": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/design-news-feed-system-system-design/",
                "description": "Design Twitter feed timeline aggregation.",
                "type": "design",
                "groups": ["Real-World Systems", "Distributed Systems"]
            },
            "q05_video_streaming": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/design-video-streaming-system-like-netflix-youtube/",
                "description": "Design Netflix transcoding video delivery CDN pipeline.",
                "type": "design",
                "groups": ["Real-World Systems", "Data Pipelines"]
            },
            "q06_whatsapp": { "difficulty": "Hard", "type": "design", "description": "Design WhatsApp / Messenger - Chat + E2E encryption.", "groups": ["Real-World Systems", "Messaging"] },
            "q07_instagram": { "difficulty": "Hard", "type": "design", "description": "Design Instagram - Stories, feed, reels.", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q08_swiggy_doordash": { "difficulty": "Hard", "type": "design", "description": "Design Swiggy / DoorDash - Food delivery logistics.", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q09_google_docs": { "difficulty": "Hard", "type": "design", "description": "Design Google Docs - Real-time collaboration.", "groups": ["Real-World Systems", "Concurrency"] },
            "q10_dropbox": { "difficulty": "Hard", "type": "design", "description": "Design Dropbox / Google Drive - File storage/sync.", "groups": ["Real-World Systems", "Caching & Storage"] },
            "q11_replit": { "difficulty": "Hard", "type": "design", "description": "Design Replit / Online IDE - Real-time code collaboration.", "groups": ["Real-World Systems", "Concurrency"] },
            "q12_distributed_cache": { "difficulty": "Hard", "type": "design", "description": "Design Distributed Cache (Redis-like).", "groups": ["Real-World Systems", "Caching & Storage"] },
            "q13_rate_limiter_hld": { "difficulty": "Medium", "type": "design", "description": "Design Distributed Rate Limiter.", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q14_search_engine": { "difficulty": "Hard", "type": "design", "description": "Design Search Engine (Google-scale).", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q15_notification_system": { "difficulty": "Medium", "type": "design", "description": "Design Notification System (Push/Email/SMS).", "groups": ["Real-World Systems", "Messaging"] },
            "q16_api_gateway": { "difficulty": "Medium", "type": "design", "description": "Design API Gateway and Load Balancer.", "groups": ["Real-World Systems", "Networking"] },
            "q17_workflow_orchestrator": { "difficulty": "Hard", "type": "design", "description": "Design Workflow Orchestrator (Airflow style).", "groups": ["Real-World Systems", "Data Pipelines"] },
            "q18_distributed_scheduler": { "difficulty": "Hard", "type": "design", "description": "Design Distributed Job Scheduler.", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q19_analytics_platform": { "difficulty": "Hard", "type": "design", "description": "Design Analytics Platform (Batch + Real-time).", "groups": ["Real-World Systems", "Data Pipelines"] },
            "q20_cdn": { "difficulty": "Medium", "type": "design", "description": "Design CDN (Content Delivery Network).", "groups": ["Real-World Systems", "Networking"] },
            "q21_event_streaming": { "difficulty": "Hard", "type": "design", "description": "Design Event Streaming Platform (Kafka style).", "groups": ["Real-World Systems", "Messaging"] },
            "q22_payment_gateway": { "difficulty": "Hard", "type": "design", "description": "Design Payment Gateway (Stripe, Razorpay).", "groups": ["Real-World Systems"] },
            "q23_stock_trading": { "difficulty": "Hard", "type": "design", "description": "Design Stock Trading Platform / Exchange.", "groups": ["Real-World Systems", "Concurrency"] },
            "q24_rtb_ad_system": { "difficulty": "Hard", "type": "design", "description": "Design Real-Time Bidding Ad System.", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q25_monitoring_alerting": { "difficulty": "Medium", "type": "design", "description": "Design Monitoring & Alerting (Prometheus/Grafana).", "groups": ["Real-World Systems", "Data Pipelines"] },
            "q26_recommendation_engine": { "difficulty": "Hard", "type": "design", "description": "Design Recommendation Engine (Netflix-style).", "groups": ["Real-World Systems", "Deep Learning"] },
            "q27_leaderboard": { "difficulty": "Medium", "type": "design", "description": "Design Leaderboard & Ranking System (Top K Problem).", "groups": ["Real-World Systems", "Caching & Storage"] },
            "q28_chatbot_platform": { "difficulty": "Medium", "type": "design", "description": "Design Chatbot Platform.", "groups": ["Real-World Systems"] },
            "q29_ecommerce": { "difficulty": "Hard", "type": "design", "description": "Design E-commerce Platform (Amazon/Flipkart).", "groups": ["Real-World Systems", "Distributed Systems"] },
            "q30_multiplayer_backend": { "difficulty": "Hard", "type": "design", "description": "Design Multiplayer Game Backend.", "groups": ["Real-World Systems", "Concurrency", "Game Design"] },
            "q31_zoom": { "difficulty": "Hard", "type": "design", "description": "Design Zoom-like Video Conferencing System.", "groups": ["Real-World Systems", "Networking"] }
        }
    }
}

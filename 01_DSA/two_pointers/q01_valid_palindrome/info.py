INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/valid-palindrome/',
    'description': 'Check if a string is a palindrome, ignoring non-alphanumeric chars.',
    'groups': ['String', 'Two Pointers'],
    'starter_code': 'def is_palindrome(s: str) -> bool:\n    # Write your solution here\n    pass',
    'solutions': "# Approach 1: Brute Force (Clean & Reverse) O(N) time, O(N) space\ndef is_palindrome_naive(s: str) -> bool:\n    clean = [c.lower() for c in s if c.isalnum()]\n    return clean == clean[::-1]\n\n# Approach 2: Optimal (Two Pointers) O(N) time, O(1) space\ndef is_palindrome_optimal(s: str) -> bool:\n    l, r = 0, len(s) - 1\n    while l < r:\n        while l < r and not s[l].isalnum(): l += 1\n        while l < r and not s[r].isalnum(): r -= 1\n        if s[l].lower() != s[r].lower():\n            return False\n        l += 1\n        r -= 1\n    return True\n\n# Approach 3: Java\n'''\npublic boolean isPalindrome(String s) {\n    int l = 0, r = s.length() - 1;\n    while(l < r) {\n        if (!Character.isLetterOrDigit(s.charAt(l))) l++;\n        else if (!Character.isLetterOrDigit(s.charAt(r))) r--;\n        else if (Character.toLowerCase(s.charAt(l++)) != Character.toLowerCase(s.charAt(r--))) return false;\n    }\n    return true;\n}\n'''",
    'test_code': "def test_palindrome():\n    assert is_palindrome('A man, a plan, a canal: Panama') is True\n    assert is_palindrome('race a car') is False\n    assert is_palindrome(' ') is True",
    'readme_content': '# Two Pointers: Valid Palindrome\nUsing two boundaries shrinking inwards.\nReal-world: Log validation, search string normalization.',
}

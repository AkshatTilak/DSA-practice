INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/valid-parentheses/',
    'description': 'Given a string containing brackets, determine if the input string is valid.',
    'groups': ['String', 'Stack & Queue'],
    'starter_code': 'def is_valid(s: str) -> bool:\n    # Write your solution here\n    pass',
    'solutions': "# Approach 1: Naive (Replace pairs recursively) O(N^2) time, O(1) space\ndef is_valid_naive(s: str) -> bool:\n    old_len = -1\n    while len(s) != old_len:\n        old_len = len(s)\n        s = s.replace('()', '').replace('[]', '').replace('{}', '')\n    return len(s) == 0\n\n# Approach 2: Optimal (LIFO Stack) O(N) time, O(N) space\ndef is_valid_optimal(s: str) -> bool:\n    stack = []\n    mapping = {')': '(', ']': '[', '}': '{'}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack\n\n# Approach 3: Java\n'''\npublic boolean isValid(String s) {\n    Stack<Character> stack = new Stack<>();\n    for (char c : s.toCharArray()) {\n        if (c == '(') stack.push(')');\n        else if (c == '[') stack.push(']');\n        else if (c == '{') stack.push('}');\n        else if (stack.isEmpty() || stack.pop() != c) return false;\n    }\n    return stack.isEmpty();\n}\n'''",
    'test_code': "def test_parentheses():\n    assert is_valid('()[]{}') is True\n    assert is_valid('(]') is False\n    assert is_valid('([)]') is False",
    'readme_content': '# Stack: Valid Parentheses\nLast-in First-out matching structures.\nReal-world: Compiler syntax parsers, matching parentheses.',
}

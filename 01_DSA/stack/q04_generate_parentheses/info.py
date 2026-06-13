INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/generate-parentheses/',
    'description': 'Generate all combinations of n pairs of valid parentheses.',
    'groups': ['String', 'Stack & Queue', 'Backtracking'],
    'starter_code': 'def generate_parenthesis(n: int) -> list[str]:\n    pass',
    'solutions': '# Optimal: Backtracking using open/close balances',
    'test_code': 'def test_generate():\n    assert len(generate_parenthesis(3)) == 5',
    'readme_content': '# Generate Parentheses\nAdd open bracket if open < n, close bracket if close < open.',
}

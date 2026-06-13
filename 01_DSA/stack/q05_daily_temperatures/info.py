INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/daily-temperatures/',
    'description': 'Return an array showing days to wait for a warmer temperature.',
    'groups': ['Array', 'Stack & Queue'],
    'starter_code': 'def daily_temperatures(temperatures: list[int]) -> list[int]:\n    pass',
    'solutions': '# Optimal: Monotonic decreasing stack O(N)',
    'test_code': 'def test_temp():\n    assert daily_temperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]',
    'readme_content': '# Daily Temperatures\nMonotonic stack maintaining un-updated index values.',
}

INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/number-of-islands/',
    'description': "Given a 2D grid of '1's (land) and '0's (water), return the number of islands.",
    'groups': ['Graph', 'Matrix'],
    'starter_code': 'def num_islands(grid: list[list[str]]) -> int:\n    # Write your solution here\n    pass',
    'solutions': "def num_islands_optimal(grid):\n    if not grid: return 0\n    rows, cols = len(grid), len(grid[0])\n    visited = set()\n    islands = 0\n    \n    def dfs(r, c):\n        if r<0 or r>=rows or c<0 or c>=cols or grid[r][c]=='0' or (r,c) in visited:\n            return\n        visited.add((r,c))\n        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n            dfs(r+dr, c+dc)\n            \n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1' and (r,c) not in visited:\n                dfs(r, c)\n                islands += 1\n    return islands",
    'test_code': 'def test_islands():\n    pass',
    'readme_content': '# Number of Islands\nDFS/BFS connected components traversal.',
}

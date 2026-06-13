INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/',
    'description': 'Find the maximum profit you can achieve buying one day and selling another.',
    'groups': ['Array', 'Sliding Window'],
    'starter_code': 'def max_profit(prices: list[int]) -> int:\n    # Write your solution here\n    pass',
    'solutions': "# Approach 1: Naive (O(N^2))\ndef max_profit_naive(prices: list[int]) -> int:\n    max_p = 0\n    for i in range(len(prices)):\n        for j in range(i + 1, len(prices)):\n            max_p = max(max_p, prices[j] - prices[i])\n    return max_p\n\n# Approach 2: Optimal (Sliding Window / Min Tracker) O(N)\ndef max_profit_optimal(prices: list[int]) -> int:\n    min_p = float('inf')\n    max_p = 0\n    for p in prices:\n        if p < min_p: min_p = p\n        elif p - min_p > max_p: max_p = p - min_p\n    return max_p\n\n# Approach 3: Java\n'''\npublic int maxProfit(int[] prices) {\n    int min = Integer.MAX_VALUE, max = 0;\n    for(int p : prices) {\n        if(p < min) min = p;\n        else if(p - min > max) max = p - min;\n    }\n    return max;\n}\n'''",
    'test_code': 'def test_stock():\n    assert max_profit([7,1,5,3,6,4]) == 5\n    assert max_profit([7,6,4,3,1]) == 0',
    'readme_content': '# Sliding Window: Stock Profit\nDynamic window boundaries sliding to track profit margins.',
}

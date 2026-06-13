"""
Challenge: q01_climbing_stairs
Difficulty: Easy
Link: https://leetcode.com/problems/climbing-stairs/

Problem:
Calculate distinct ways to climb n steps if you take 1 or 2 steps each time.
"""

# --- STARTER TEMPLATE FOR USER ---
def climb_stairs(n: int) -> int:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

def climb_stairs_optimal(n):
    if n <= 2: return n
    one, two = 1, 2
    for i in range(3, n+1):
        one, two = two, one + two
    return two

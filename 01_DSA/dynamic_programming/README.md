# Dynamic Programming

Dynamic Programming (DP) is an algorithmic design technique that solves complex problems by breaking them down into simpler, overlapping subproblems. It solves each subproblem exactly once and stores the results (using Memoization for Top-Down recursive strategies or Tabulation for Bottom-Up iterative strategies) to avoid redundant recalculations.

---

## 🗺️ ASCII Execution Flow: Climbing Stairs Tabulation

Below is the state progression for the **Climbing Stairs** problem ($DP[i] = DP[i-1] + DP[i-2]$) calculating ways to climb $n = 5$ steps:

```text
Initialize DP array of size n+1:
  Index:   [ 0,  1,  2,  3,  4,  5 ]
  Value:   [ 0,  1,  2,  0,  0,  0 ]
            (Base cases: DP[1]=1, DP[2]=2)

Step 1: Compute DP[3] = DP[2] + DP[1] = 2 + 1 = 3
  Array:   [ 0,  1,  2,  3,  0,  0 ]

Step 2: Compute DP[4] = DP[3] + DP[2] = 3 + 2 = 5
  Array:   [ 0,  1,  2,  3,  5,  0 ]

Step 3: Compute DP[5] = DP[4] + DP[3] = 5 + 3 = 8
  Array:   [ 0,  1,  2,  3,  5,  8 ]

Result for n=5 ──> 8 ways
```

---

## 📊 Complexity Analysis

| Method | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Brute Force Recursion | $O(2^N)$ | $O(N)$ (recursion stack) |
| Memoization (Top-Down) | $O(N)$ | $O(N)$ (cache + recursion) |
| Tabulation (Bottom-Up) | $O(N)$ | $O(N)$ (array storage) |
| Optimized Bottom-Up | $O(N)$ | $O(1)$ (constant variables) |

---

## 🏢 Real-World Production Use-Case

### Version Control Systems: Git Diff / Levenshtein Distance
File comparisons and change trackers (like Git) identify edits, insertions, and deletions between two file drafts.
1. The difference engine computes the Longest Common Subsequence (LCS) or Levenshtein distance between lines.
2. It constructs a **DP Tabulation Matrix** where indices represent lines in file A and file B.
3. The cell values record the minimal edit costs, utilizing previously calculated values from the top, left, and diagonal cells.
4. Using DP avoids scanning line variations recursively, allowing Git to compare huge codebases and display diffs instantly.
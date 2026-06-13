# Two Pointers

The Two Pointers technique is an algorithmic pattern that uses two pointer references to scan through data collections (usually arrays or linked lists) simultaneously. Pointers can either converge from both ends toward the middle (e.g., palindrome validation) or move forward at different speeds/intervals (e.g., sliding windows, cycle detection). This avoids nested loops and reduces complexity from $O(N^2)$ to $O(N)$.

---

## 🗺️ ASCII Execution Flow: Valid Palindrome

Here is a visual execution mapping of the **Valid Palindrome** problem, validating the string `"A man, a plan, a canal: Panama"` (normalized to lowercase letters: `"amanaplanacanalpanama"`):

```text
Normalized: [ a, m, a, n, a, p, l, a, n, a, c, a, n, a, l, p, a, n, a, m, a ]
              ▲                                                           ▲
              │                                                           │
          Left Pointer (l)                                        Right Pointer (r)

Iteration 1: Compare 'a' (l) vs 'a' (r) ── Matches! ── l++, r--
Iteration 2: Compare 'm' (l) vs 'm' (r) ── Matches! ── l++, r--
Iteration 3: Compare 'a' (l) vs 'a' (r) ── Matches! ── l++, r--
...
Iteration 10: Compare 'c' (l) vs 'c' (r) ── Matches! (pointers meet or cross)
Output ──> True (Valid Palindrome)
```

---

## 📊 Complexity Analysis

| Operations | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Converging Boundary Pointers | $O(N)$ | $O(1)$ |
| Two Pointers on Two Arrays | $O(N + M)$ | $O(1)$ |
| Dynamic Binary Segmentation | $O(\log N)$ | $O(1)$ |

---

## 🏢 Real-World Production Use-Case

### Netflix: Video Stream Temporal Frame Synchronization
When rendering live streams or stitching camera viewpoints together, video pipelines must align separate timestamped video buffers.
1. The engine maintains two buffers (e.g., video frame indexes and telemetry timeline entries).
2. It assigns **two pointers** tracking indices of frames in both buffers.
3. If pointer 1's frame timestamp lags pointer 2's timestamp, pointer 1 is advanced. If it leads, pointer 2 is advanced.
4. This linear synchronization executes in $O(N + M)$ time instead of an $O(N \times M)$ double-loop comparison, preventing dropped frames in high-throughput video pipelines.
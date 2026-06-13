# Sliding Window

The Sliding Window pattern is used to track and perform operations on a contiguous sub-segment (window) of a sequential data structure (like arrays or strings) without recalculating the entire window from scratch. The window size can be fixed (e.g., maximum average subarray of size K) or dynamic (resizing boundaries based on conditions, e.g., longest substring without repeating characters).

---

## 🗺️ ASCII Execution Flow: Longest Substring Without Repeats

Here is the execution mapping for finding the longest substring without duplicate characters in the string `"abcabcbb"`:

```text
Input String: [ a, b, c, a, b, c, b, b ]
Window:       [ L ... R ]

Step 1: L=0, R=0 ── Window: [a] ─────── Unique! Max Length = 1
Step 2: L=0, R=1 ── Window: [a, b] ──── Unique! Max Length = 2
Step 3: L=0, R=2 ── Window: [a, b, c] ── Unique! Max Length = 3
Step 4: L=0, R=3 ── Window: [a, b, c, a] ── Duplicate 'a'!
                   Slide Left: L++ (L=1)
                   Window:    [b, c, a] ── Unique! Max Length = 3
Step 5: L=1, R=4 ── Window: [b, c, a, b] ── Duplicate 'b'!
                   Slide Left: L++ (L=2)
                   Window:    [c, a, b] ── Unique! Max Length = 3
...
Output Max Length ──> 3
```

---

## 📊 Complexity Analysis

| Window Type | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Fixed Size Window ($K$) | $O(N)$ | $O(1)$ |
| Dynamic Window (Set/Map tracking) | $O(N)$ | $O(\min(N, \Sigma))$ |

---

## 🏢 Real-World Production Use-Case

### Network Protocols: TCP Flow Control & Congestion Window
Reliable data transmission over IP networks requires packet flow pacing to avoid buffer overflows at the receiver.
1. The TCP stack maintains a **Sliding Window** of outstanding unacknowledged packet IDs.
2. The right boundary expands as the network capacity allows more sent packets.
3. The left boundary contracts forward when Acknowledgment (ACK) packets arrive from the receiver.
4. By dynamically sliding this window in-memory, TCP optimizes bandwidth utilization and handles congestion control without scanning packet history.
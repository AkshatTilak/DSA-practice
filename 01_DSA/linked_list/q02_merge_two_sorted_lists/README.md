# Merge Two Sorted Lists

## 📌 Overview & Problem Explanation

The goal of this challenge is to take two already **sorted** singly-linked lists and merge them into a single, sorted linked list. The final list should be constructed by "splicing" together the nodes of the original two lists, meaning we should not create entirely new nodes if we can avoid it, but rather rearrange the existing pointers.

### 📥 Inputs & Outputs
- **Input**: Two heads of sorted linked lists, `list1` and `list2`.
- **Output**: The head of the newly merged sorted linked list.

### ⚙️ Constraints & Edge Cases
- **Constraints**:
    - The number of nodes in both lists is in the range $[0, 50]$.
    - Node values are typically in the range $[-100, 100]$.
- **Edge Cases**:
    - **One list is empty**: If `list1` is null, the result is simply `list2` (and vice versa).
    - **Both lists are empty**: Return `null`.
    - **Lists of different lengths**: One list may be exhausted before the other.
    - **Duplicate values**: If both lists contain the same value, either can come first in the merged list.

---

## 🧠 Core Concepts & Data Structures

### Linked Lists
A **Singly Linked List** consists of nodes where each node contains a value and a pointer (`next`) to the next node in the sequence. Unlike arrays, linked lists do not provide random access; we must traverse them sequentially.

### The "Dummy Node" Pattern
One of the most critical patterns used in linked list problems is the **Dummy Node**. 
- **The Problem**: When building a new linked list, the "head" node is unknown until the first comparison is made. This usually leads to messy `if` statements to handle the initialization of the head.
- **The Solution**: Create a "fake" node at the start. You append all merged nodes to this dummy node. At the end, you simply return `dummy.next`, which is the actual start of your merged list.

### Two-Pointer Technique
Since both lists are already sorted, we can use two pointers (starting at the heads of `list1` and `list2`) to compare the current elements and pick the smaller one. This is a linear traversal strategy.

---

## 🛠️ Step-by-Step Logic

### Approach 1: Iterative (Optimal)
The iterative approach uses a loop to traverse both lists until one is exhausted.

1. **Initialize**: Create a `dummy` node and a `current` pointer that starts at the dummy.
2. **Compare**: While both `list1` and `list2` are not null:
   - Compare `list1.val` and `list2.val`.
   - Attach the node with the **smaller** value to `current.next`.
   - Move the pointer of the list from which the node was taken forward by one step.
   - Move the `current` pointer forward by one step.
3. **Cleanup**: Once the loop ends, one of the lists might still have remaining nodes (because it was longer). Since the lists were already sorted, simply attach the remaining part of the non-empty list to `current.next`.
4. **Return**: Return `dummy.next`.

**Dry Run Example:**
`L1: 1 → 2 → 4`
`L2: 1 → 3 → 4`
- `dummy` created. `current` $\rightarrow$ `dummy`.
- Compare `1` (L1) and `1` (L2). Pick L1. `current.next` $\rightarrow$ `1(L1)`. L1 moves to `2`.
- Compare `2` (L1) and `1` (L2). Pick L2. `current.next` $\rightarrow$ `1(L2)`. L2 moves to `3`.
- Compare `2` (L1) and `3` (L2). Pick L1. `current.next` $\rightarrow$ `2(L1)`. L1 moves to `4`.
- Compare `4` (L1) and `3` (L2). Pick L2. `current.next` $\rightarrow$ `3(L2)`. L2 moves to `4`.
- Compare `4` (L1) and `4` (L2). Pick L1. `current.next` $\rightarrow$ `4(L1)`. L1 moves to `null`.
- Loop ends. L2 still has `4`. Attach it: `current.next` $\rightarrow$ `4(L2)`.
- Result: `1 → 1 → 2 → 3 → 4 → 4`.

---

### Approach 2: Recursive (Elegant)
Recursion can solve this problem by breaking it down into the smallest possible sub-problem: *"Which of the two current heads should come first?"*

1. **Base Cases**:
   - If `list1` is null, return `list2`.
   - If `list2` is null, return `list1`.
2. **Recursive Step**:
   - If `list1.val < list2.val`:
     - `list1` is our current head.
     - We now need to find the `.next` for `list1`. We do this by calling the function again with `list1.next` and `list2`.
   - Else:
     - `list2` is our current head.
     - We find the `.next` for `list2` by calling the function with `list1` and `list2.next`.
3. **Return**: Return the node that was chosen as the head for that specific recursive call.

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Iterative** | $O(n + m)$ | $O(1)$ | We traverse each node in both lists exactly once. Only a few pointers are used regardless of input size. |
| **Recursive** | $O(n + m)$ | $O(n + m)$ | We visit every node once, but each recursive call adds a frame to the **call stack**. |

*Where $n$ and $m$ are the lengths of the two linked lists.*

---

## 💻 Implementation

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_optimal(list1: ListNode, list2: ListNode) -> ListNode:
    # 1. Initialize dummy node to simplify head management
    dummy = ListNode(-1)
    current = dummy
    
    # 2. Traverse both lists while neither is exhausted
    while list1 and list2:
        if list1.val <= list2.val:
            current.next = list1
            list1 = list1.next
        else:
            current.next = list2
            list2 = list2.next
        current = current.next
    
    # 3. Attach the remaining part of the non-empty list
    current.next = list1 if list1 else list2
    
    # 4. Return the head of the merged list (skipping the dummy)
    return dummy.next
```

---

## 🚀 Real-World Applications

The logic used in "Merge Two Sorted Lists" is a fundamental building block for several high-scale systems:

1. **Merge Sort Algorithm**: This is the "Merge" step of the Merge Sort algorithm. Divide-and-conquer sorting relies entirely on the ability to merge two sorted subarrays/lists efficiently.
2. **External Sorting**: When datasets are too large to fit into RAM (e.g., sorting a 1TB log file), software engineers use **External Merge Sort**. The system sorts small chunks of the file, saves them to disk, and then merges these sorted chunks together using the exact logic from this problem.
3. **Database Query Optimization**: When a database performs a **Merge Join** (joining two tables on a sorted key), it uses two pointers to step through the sorted indexes of both tables to find matching records in $O(n+m)$ time.
4. **Stream Processing**: In systems like Apache Flink or Kafka Streams, merging sorted event streams (based on timestamps) is common for windowing operations.
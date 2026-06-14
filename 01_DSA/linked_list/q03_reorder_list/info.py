INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/reorder-list/',
    'description': 'Reorder list in-place.',
    'groups': ['Linked List'],
    'readme_content': """# Reorder List

## 1. Overview & Problem Explanation

The **Reorder List** problem asks us to take a singly linked list and rearrange its nodes in a specific zig-zag pattern. Given a list:
$L_0 \to L_1 \to L_2 \to \dots \to L_{n-1} \to L_n$

We need to reorder it to:
$L_0 \to L_n \to L_1 \to L_{n-1} \to L_2 \to L_{n-2} \dots$

Essentially, we are interleaving the first half of the list with the second half, but the second half must be processed in **reverse order**.

### Example
**Input:** `1 -> 2 -> 3 -> 4 -> 5`
**Output:** `1 -> 5 -> 2 -> 4 -> 3`

**Input:** `1 -> 2 -> 3 -> 4`
**Output:** `1 -> 4 -> 2 -> 3`

### Constraints & Edge Cases
- **Constraints:** The number of nodes can range from $0$ to $5 \times 10^4$.
- **In-Place Requirement:** The problem specifically asks to modify the existing list rather than creating a new one.
- **Edge Cases:**
    - **Empty List:** No operation needed.
    - **Single Node:** No operation needed.
    - **Two Nodes:** No operation needed (already in the correct order $L_0 \to L_1$).
    - **Odd vs. Even Length:** The middle node handling differs slightly between odd and even lengths.

---

## 2. Core Concepts & Data Structures

To solve this problem optimally in-place, we combine three fundamental linked list techniques:

### A. Two-Pointer Technique (Slow & Fast)
To split the list into two halves, we use a **slow pointer** (moves one step) and a **fast pointer** (moves two steps). When the fast pointer reaches the end, the slow pointer will be exactly at the middle of the list.
- **Why?** This allows us to find the split point in $O(N)$ time without knowing the length of the list beforehand.

### B. Linked List Reversal
Since we need to access the end of the list and move backwards ($L_n, L_{n-1} \dots$), but singly linked lists only provide forward pointers, we must **reverse the second half** of the list.
- **Why?** Reversing the second half transforms the tail of the list into a head, allowing us to iterate through it linearly.

### C. Interleaving (Merging)
Once we have two lists (the first half and the reversed second half), we merge them by alternating nodes.
- **Why?** This creates the required $L_0 \to L_n \to L_1 \to L_{n-1} \dots$ sequence.

---

## 3. Step-by-Step Logic

### Naive Approach (Using Extra Space)
1. Traverse the linked list and store all node references in an **array**.
2. Use two pointers: `left` at the start of the array and `right` at the end.
3. Iterate through the array, alternating between `left` and `right` nodes and updating the `.next` pointers.
4. Set the `.next` of the final node to `None`.
- **Downside:** Requires $O(N)$ extra space.

### Optimal Approach (In-Place)

#### Step 1: Find the Middle
We use the slow/fast pointer approach. 
- `slow` moves 1 step; `fast` moves 2 steps.
- For `1 -> 2 -> 3 -> 4 -> 5`, `slow` will end at `3`.

#### Step 2: Reverse the Second Half
We split the list into two: `1 -> 2 -> 3` and `4 -> 5`. We then reverse the second part.
- `4 -> 5` becomes `5 -> 4`.
- Now we have:
    - List 1: `1 -> 2 -> 3`
    - List 2: `5 -> 4`

#### Step 3: Merge the Halves
We alternate nodes from List 1 and List 2.
- Take `1` from List 1 $\to$ Point to `5` from List 2.
- Take `5` from List 2 $\to$ Point to `2` from List 1.
- Take `2` from List 1 $\to$ Point to `4` from List 2.
- Take `4` from List 2 $\to$ Point to `3` from List 1.
- Final: `1 -> 5 -> 2 -> 4 -> 3`

### Dry Run Trace (`1 -> 2 -> 3 -> 4`)
1. **Middle:** `slow` reaches `2`. Split into `1 -> 2` and `3 -> 4`.
2. **Reverse:** `3 -> 4` becomes `4 -> 3`.
3. **Merge:**
   - `1` (L1) $\to$ `4` (L2)
   - `4` (L2) $\to$ `2` (L1)
   - `2` (L1) $\to$ `3` (L2)
   - `3` (L2) $\to$ `None`
   - Result: `1 -> 4 -> 2 -> 3`

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Naive (Array)** | $O(N)$ | $O(N)$ | We store all $N$ nodes in an array. |
| **Optimal (In-Place)** | $O(N)$ | $O(1)$ | We traverse the list a constant number of times (3 passes) and use no extra storage. |

- **Time Reasoning:** Finding the middle takes $O(N/2)$, reversing the second half takes $O(N/2)$, and merging takes $O(N/2)$. Total: $O(1.5N) \approx O(N)$.
- **Space Reasoning:** We only use a few pointer variables (`prev`, `curr`, `next`, `slow`, `fast`), regardless of the input size.

---

## 5. Implementation

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_optimal(head: ListNode) -> None:
    \"\"\"
    Do not return anything, modify head in-place instead.
    \"\"\"
    if not head or not head.next:
        return

    # 1. Find the middle of the linked list
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    
    # 2. Reverse the second half of the list
    # slow is the start of the second half
    prev, curr = None, slow.next
    slow.next = None # Break the list into two halves
    
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    
    # prev now points to the head of the reversed second half
    
    # 3. Merge the two halves
    first, second = head, prev
    while second:
        # Save next pointers
        tmp1, tmp2 = first.next, second.next
        
        # Interleave
        first.next = second
        second.next = tmp1
        
        # Move pointers forward
        first = tmp1
        second = tmp2
```

---

## 6. Real-World Applications

While "reordering a list in a zig-zag" seems like a puzzle, the underlying patterns are used extensively in software engineering:

1. **Undo/Redo Stacks:** Reversing portions of a history list is a common requirement when implementing complex "Undo" features where state must be popped and reapplied in reverse order.
2. **Memory Management:** Garbage collection algorithms sometimes involve rearranging pointers or reversing lists of memory blocks to consolidate fragmented memory.
3. **Concurrent Queue Processing:** In some lock-free data structures (like the Michael-Scott queue), pointer manipulation techniques similar to these are used to ensure atomic updates to the head and tail of a list.
4. **Parsing Expression Trees:** When converting certain types of notation (like Infix to Postfix), stacks are used to reverse the order of operators, mirroring the "reverse a segment" logic used here.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
    # Time Complexity: ...
    # Space Complexity: ...
    # [Explanation]
    def solve_naive(...):

    # --- APPROACH 2: Optimal (...) ---
    # Time Complexity: ...
    # Space Complexity: ...
    # [Explanation]
    def solve_optimal(...):

    # --- APPROACH 3: Secondary Language (Java Variant) ---
    \"\"\"
    ...
    \"\"\"

    Ensure the Python functions are defined. Since the `ListNode` class is required for these to work, I will include the `ListNode` definition at the top.

    Wait, the prompt says "Return ONLY the raw Python code."
    If I include the `ListNode` class, it's part of the implementation.

    Let's double-check the reorder logic one more time.
    List: 1->2->3->4
    Slow=2, Fast=4.
    Split: 1->2 (L1), 3->4 (L2).
    Reverse L2: 4->3.
    Merge: 1->4->2->3. Correct.

    List: 1->2->3->4->5
    Slow=3, Fast=5.
    Split: 1->2->3 (L1), 4->5 (L2).
    Reverse L2: 5->4.
    Merge: 1->5->2->4->3. Correct.

    One edge case: 1 node.
    Slow=1, Fast=1. Split: 1 (L1), None (L2). Merge: 1. Correct.
    Two nodes: 1->2.
    Slow=1, Fast=2. Split: 1 (L1), 2 (L2). Reverse L2: 2. Merge: 1->2. Correct.

    Final check on constraints: "Reorder list in-place."
    Approach 1 (List) is not strictly "in-place" in terms of space complexity $O(N)$, but it modifies the existing nodes.
    Approach 2 is $O(1)$ space.class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# We store all node references in a dynamic array (Python list). This allows O(1) random access to nodes, 
# making it trivial to re-link the nodes from the start and end of the list using two pointers.
def solve_naive(head: ListNode) -> None:
    if not head or not head.next:
        return

    # Store all nodes in a list for easy access
    nodes = []
    curr = head
    while curr:
        nodes.append(curr)
        curr = curr.next

    # Use two pointers to re-link nodes
    left, right = 0, len(nodes) - 1
    while left < right:
        nodes[left].next = nodes[right]
        left += 1
        if left == right:
            break
        nodes[right].next = nodes[left]
        right -= 1
    
    # The last node must point to None to avoid cycles
    nodes[left].next = None

# --- APPROACH 2: Optimal (Two Pointers + Reversal) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach is optimal because it modifies the list in-place without requiring extra storage.
# 1. Find the middle of the list using the slow and fast pointer technique.
# 2. Split the list into two halves.
# 3. Reverse the second half of the list.
# 4. Interleave nodes from the first half and the reversed second half.
def solve_optimal(head: ListNode) -> None:
    if not head or not head.next or not head.next.next:
        return

    # 1. Find middle: slow will be the end of the first half
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # 2. Split the list
    second = slow.next
    slow.next = None

    # 3. Reverse the second half
    prev = None
    curr = second
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    
    # 'prev' is now the head of the reversed second half
    reversed_head = prev

    # 4. Merge the two halves
    first = head
    second = reversed_head
    while second:
        tmp1, tmp2 = first.next, second.next
        first.next = second
        second.next = tmp1
        first = tmp1
        second = tmp2

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package linked_list;

class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

public class ReorderList {
    public void reorderList(ListNode head) {
        if (head == null || head.next == null || head.next.next == null) {
            return;
        }

        // 1. Find middle
        ListNode slow = head;
        ListNode fast = head;
        while (fast.next != null && fast.next.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }

        // 2. Split
        ListNode secondHalf = slow.next;
        slow.next = null;

        // 3. Reverse second half
        ListNode prev = null;
        ListNode curr = secondHalf;
        while (curr != null) {
            ListNode nextTemp = curr.next;
            curr.next = prev;
            prev = curr;
            curr = nextTemp;
        }
        ListNode reversedHead = prev;

        // 4. Merge
        ListNode first = head;
        ListNode second = reversedHead;
        while (second != null) {
            ListNode tmp1 = first.next;
            ListNode tmp2 = second.next;
            
            first.next = second;
            second.next = tmp1;
            
            first = tmp1;
            second = tmp2;
        }
    }
}
\"\"\"""",
}

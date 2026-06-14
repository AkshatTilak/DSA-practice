INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/remove-nth-node-from-end-of-list/',
    'description': 'Remove Nth node.',
    'groups': ['Linked List', 'Two Pointers'],
    'readme_content': """# Remove Nth Node from End of List

## 📌 Overview & Problem Explanation

The goal of this challenge is to remove the **$n$-th node from the end** of a singly linked list and return the head of the modified list. 

In a singly linked list, we only have pointers to the *next* node. This means we cannot traverse backward from the tail. To find the $n$-th node from the end, we must either determine the total length of the list first or use a strategy that allows us to "measure" the distance from the end while moving forward.

### 📥 Input & Output
- **Input**: 
    - `head`: The head node of a singly linked list.
    - `n`: An integer representing the position from the end (1-indexed).
- **Output**: The `head` of the linked list after the $n$-th node from the end has been removed.

### ⚠️ Constraints & Edge Cases
- **Constraints**: $1 \le \text{list length} \le 30$, $1 \le n \le \text{list length}$.
- **Edge Case 1: Removing the Head**: If the list has 5 elements and $n=5$, the head itself must be removed.
- **Edge Case 2: Single Element List**: If the list has 1 element and $n=1$, the list becomes empty (`null`).
- **Edge Case 3: Removing the Tail**: If $n=1$, the last node must be removed.

---

## 🧠 Core Concepts & Algorithmic Patterns

### 1. The Two-Pointer Technique (Fast & Slow)
The most efficient way to solve this problem in a single pass is the **Two-Pointer (or Sliding Window)** approach. Instead of calculating the length of the list, we maintain a constant gap of $n$ nodes between two pointers.

**Why this works:**
If pointer `fast` is $n$ steps ahead of pointer `slow`, then when `fast` reaches the end of the list (the `null` termination), `slow` will be exactly $n$ steps behind. This positions `slow` perfectly at the node **immediately preceding** the one we want to delete.

### 2. The Dummy Node Pattern
When dealing with linked lists, removing the head node often requires special `if/else` logic. To avoid this, we use a **Dummy Node** that points to the head.
- The dummy node acts as a permanent "pre-head."
- This ensures that we always have a node before the head, allowing us to use the same deletion logic regardless of whether we are removing the first, middle, or last node.

---

## 🛠️ Step-by-Step Logic

### Approach 1: Two-Pass (Naive)
1. Traverse the entire list to count the total number of nodes $L$.
2. The node to be removed is at position $(L - n + 1)$ from the start.
3. Traverse the list again to the $(L - n)$-th node.
4. Change the `next` pointer of that node to skip the $n$-th node.

### Approach 2: One-Pass (Optimal)
1. **Initialization**: Create a `dummy` node and set `dummy.next = head`. Initialize two pointers, `slow` and `fast`, both pointing to the `dummy` node.
2. **Create the Gap**: Move the `fast` pointer forward $n + 1$ steps. Now, there are exactly $n$ nodes between `slow` and `fast`.
3. **Simultaneous Traversal**: Move both `slow` and `fast` forward one step at a time until `fast` reaches `None`.
4. **Deletion**: Because of the gap, `slow` is now resting on the node **just before** the target node. Update `slow.next = slow.next.next`.
5. **Return**: Return `dummy.next` (the actual head of the list).

### 🔍 Dry Run Example
**Input**: `head = [1, 2, 3, 4, 5], n = 2`

1. **Init**: `Dummy` $\rightarrow 1 \rightarrow 2 \rightarrow 3 \rightarrow 4 \rightarrow 5 \rightarrow \text{None}$. `slow` and `fast` start at `Dummy`.
2. **Gap**: Move `fast` 3 steps ($n+1$): `fast` is now at node `3`.
3. **Slide**: 
    - `fast` at 4, `slow` at 1
    - `fast` at 5, `slow` at 2
    - `fast` at `None`, `slow` at 3
4. **Delete**: `slow` is at 3. The target is 4. Update `slow.next` to point to `slow.next.next` (node 5).
5. **Result**: `[1, 2, 3, 5]`

---

## 💻 Implementation

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_optimal(head: ListNode, n: int) -> ListNode:
    # 1. Initialize a dummy node to handle edge cases like removing the head
    dummy = ListNode(0)
    dummy.next = head
    
    slow = dummy
    fast = dummy
    
    # 2. Advance fast pointer so there is a gap of n nodes between slow and fast
    # We move n + 1 steps to ensure 'slow' stops BEFORE the node to be deleted
    for _ in range(n + 1):
        fast = fast.next
        
    # 3. Move both pointers until fast reaches the end
    while fast is not None:
        slow = slow.next
        fast = fast.next
        
    # 4. slow.next is the node to be removed. Skip it.
    slow.next = slow.next.next
    
    # 5. Return the actual head (which is dummy.next)
    return dummy.next
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Two-Pass** | $O(L)$ | $O(1)$ | Traverses the list twice (once for length, once for deletion). |
| **One-Pass (Optimal)** | $O(L)$ | $O(1)$ | Traverses the list exactly once using two pointers. |

- **Time $O(L)$**: $L$ is the number of nodes in the list. We visit each node at most once.
- **Space $O(1)$**: No extra data structures are used; we only use a few pointer variables.

---

## 🚀 Real-World Applications

The "Two Pointer" and "Fixed Gap" pattern is widely used in systems engineering:

1. **Undo/Redo Buffers**: In text editors, maintaining a limited history (e.g., last 100 actions) often uses a structure similar to a sliding window or linked list where the "oldest" element is pruned.
2. **LRU Cache (Least Recently Used)**: The implementation of an LRU cache relies heavily on a Doubly Linked List. Removing the least recently used item (the tail) is a variation of the "Remove Node" logic.
3. **Network Packet Buffering**: When managing a queue of packets with a specific timeout or size limit, pointers are used to drop packets from the tail or a specific offset.
4. **Browser History**: Moving back and forward through a session history is essentially navigating a linked list of URLs.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(L)
# Space Complexity: O(1)
# This approach performs two passes over the linked list. The first pass calculates the 
# total length of the list. The second pass iterates to the node immediately preceding 
# the target node (L - n) and removes it by updating the next pointer.

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_naive(head: ListNode, n: int) -> ListNode:
    if not head:
        return None
    
    # First pass: calculate length
    length = 0
    current = head
    while current:
        length += 1
        current = current.next
    
    # Target position from start (0-indexed)
    target_idx = length - n
    
    # Edge case: remove the head node
    if target_idx == 0:
        return head.next
    
    # Second pass: move to the node before the target
    current = head
    for _ in range(target_idx - 1):
        current = current.next
    
    # Skip the target node
    if current.next:
        current.next = current.next.next
        
    return head

# --- APPROACH 2: Optimal (Two-Pointer Technique) ---
# Time Complexity: O(L)
# Space Complexity: O(1)
# This approach uses a "fast" and "slow" pointer to find the Nth node from the end in a 
# single pass. A dummy node is used to simplify edge cases, such as removing the head.
# The fast pointer is moved n steps ahead; then both pointers move at the same pace.
# When the fast pointer reaches the end, the slow pointer is positioned exactly before 
# the node to be removed. This is optimal as it minimizes list traversals.

def solve_optimal(head: ListNode, n: int) -> ListNode:
    # Dummy node handles the case where the head needs to be removed
    dummy = ListNode(0)
    dummy.next = head
    fast = dummy
    slow = dummy
    
    # Move fast pointer n steps ahead
    for _ in range(n):
        if fast.next:
            fast = fast.next
        else:
            # This case handles if n is greater than list length, though usually n <= L
            return head
            
    # Move both until fast reaches the last node
    while fast.next:
        fast = fast.next
        slow = slow.next
        
    # slow is now just before the node to be removed
    if slow.next:
        slow.next = slow.next.next
        
    return dummy.next

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

public class RemoveNthNode {
    /**
     * Removes the nth node from the end of the list using the two-pointer approach.
     * Time Complexity: O(L)
     * Space Complexity: O(1)
     */
    public ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode fast = dummy;
        ListNode slow = dummy;

        // Advance fast pointer by n positions
        for (int i = 0; i < n; i++) {
            if (fast.next != null) {
                fast = fast.next;
            }
        }

        // Move both until fast reaches the end
        while (fast.next != null) {
            fast = fast.next;
            slow = slow.next;
        }

        // Remove the target node
        if (slow.next != null) {
            slow.next = slow.next.next;
        }

        return dummy.next;
    }
}
\"\"\"""",
}

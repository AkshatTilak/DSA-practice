"""
Challenge: q03_reorder_list
Difficulty: Medium
Link: https://leetcode.com/problems/reorder-list/

Problem:
Reorder list in-place.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
    """
    ...
    """

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
"""
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
"""

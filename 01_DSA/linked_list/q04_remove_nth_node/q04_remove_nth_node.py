"""
Challenge: q04_remove_nth_node
Difficulty: Medium
Link: https://leetcode.com/problems/remove-nth-node-from-end-of-list/

Problem:
Remove Nth node.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""

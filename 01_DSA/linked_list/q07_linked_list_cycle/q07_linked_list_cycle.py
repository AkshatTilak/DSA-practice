"""
Challenge: q07_linked_list_cycle
Difficulty: Easy
Link: https://leetcode.com/problems/linked-list-cycle/

Problem:
Detect cycle.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# We use a hash set to keep track of all nodes encountered during traversal. 
# If we encounter a node that is already present in the set, a cycle exists.

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def solve_naive(head: ListNode) -> bool:
    visited = set()
    current = head
    while current:
        if current in visited:
            return True
        visited.add(current)
        current = current.next
    return False

# --- APPROACH 2: Optimal (Floyd's Cycle-Finding Algorithm) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach uses two pointers moving at different speeds: a 'slow' pointer (1 step) 
# and a 'fast' pointer (2 steps). If there is a cycle, the fast pointer will eventually 
# lap the slow pointer and they will meet. If the fast pointer reaches the end (None), 
# no cycle exists. This is optimal as it requires constant extra space regardless of list size.

def solve_optimal(head: ListNode) -> bool:
    if not head or not head.next:
        return False
    
    slow = head
    fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:
            return True
            
    return False

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package linked_list;

import java.util.*;

class ListNode {
    int val;
    ListNode next;
    ListNode(int x) {
        val = x;
        next = null;
    }
}

public class LinkedListCycle {
    /**
     * Detects if a linked list has a cycle using Floyd's Cycle-Finding Algorithm.
     * Time Complexity: O(N)
     * Space Complexity: O(1)
     */
    public boolean hasCycle(ListNode head) {
        if (head == null || head.next == null) {
            return false;
        }
        
        ListNode slow = head;
        ListNode fast = head;
        
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            
            if (slow == fast) {
                return true;
            }
        }
        
        return false;
    }

    public static void main(String[] args) {
        LinkedListCycle detector = new LinkedListCycle();
        
        // Test case: Cycle
        ListNode head = new ListNode(3);
        head.next = new ListNode(2);
        head.next.next = new ListNode(0);
        head.next.next.next = head.next; // Cycle back to node 2
        
        System.out.println("Has Cycle: " + detector.hasCycle(head)); // Expected: true
    }
}
"""

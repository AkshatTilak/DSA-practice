"""
Challenge: q02_merge_two_sorted_lists
Difficulty: Easy
Link: https://leetcode.com/problems/merge-two-sorted-lists/

Problem:
Merge two sorted lists.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O((N + M) log (N + M))
# Space Complexity: O(N + M)
# This approach extracts all values from both linked lists into a standard Python list, 
# sorts the resulting list, and then constructs a new linked list from the sorted values.
from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_naive(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    values = []
    
    curr1 = list1
    while curr1:
        values.append(curr1.val)
        curr1 = curr1.next
        
    curr2 = list2
    while curr2:
        values.append(curr2.val)
        curr2 = curr2.next
        
    values.sort()
    
    dummy = ListNode(0)
    curr = dummy
    for val in values:
        curr.next = ListNode(val)
        curr = curr.next
        
    return dummy.next

# --- APPROACH 2: Optimal (Two-Pointer Iterative) ---
# Time Complexity: O(N + M)
# Space Complexity: O(1)
# This approach uses a dummy head node and a pointer to build the merged list in-place.
# It compares the current nodes of both lists and attaches the smaller one to the result.
# It is optimal because it traverses each node exactly once and does not allocate 
# additional space proportional to the size of the input lists.
def solve_optimal(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0)
    tail = dummy
    
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
        
    # Attach the remaining part of the non-empty list
    tail.next = list1 if list1 is not None else list2
    
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

public class MergeTwoSortedLists {
    /**
     * Merges two sorted linked lists iteratively.
     * Time Complexity: O(N + M)
     * Space Complexity: O(1)
     */
    public ListNode mergeTwoLists(ListNode list1, ListNode list2) {
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;

        while (list1 != null && list2 != null) {
            if (list1.val <= list2.val) {
                tail.next = list1;
                list1 = list1.next;
            } else {
                tail.next = list2;
                list2 = list2.next;
            }
            tail = tail.next;
        }

        // Attach remaining nodes
        if (list1 != null) {
            tail.next = list1;
        } else {
            tail.next = list2;
        }

        return dummy.next;
    }
}
"""

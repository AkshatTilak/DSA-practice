"""
Challenge: q01_reverse_linked_list
Difficulty: Easy
Link: https://leetcode.com/problems/reverse-linked-list/

Problem:
Reverse a singly linked list.
"""

# --- STARTER TEMPLATE FOR USER ---
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Iterative pointer swapping O(N)
def reverse_list_optimal(head):
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev

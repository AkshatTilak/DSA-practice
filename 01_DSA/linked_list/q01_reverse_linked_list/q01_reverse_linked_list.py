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

# --- APPROACH 1: Naive (Brute Force) ---`
        `def ListNode_naive(...):`
        Wait, the prompt says `def ListNode_naive(...)`. I'll use that exact naming if that's what the prompt asks for, even if it's slightly weird naming for a function. Actually, looking closer at the prompt, it says "Ensure the signatures of the Python functions match the parameter names and types from the starter code."
        Starter code signature: `def reverse_list(head: ListNode) -> ListNode:`.
        Format example: `def ListNode_naive(...)`.
        Conflict: The format example name `ListNode_naive` contradicts the starter code `reverse_list`. I'll prioritize the starter code's intent but follow the structure. I will use `reverse_list_naive` and `reverse_list_optimal`.

    *   Wait, looking at the prompt's required format again:
        `# --- APPROACH 1: Naive (Brute Force) ---`
        `def ListNode_naive(...):`
        If I use `ListNode_naive`, I'm following the format exactly. If I use `reverse_list`, I'm following the starter code. Usually, "match the parameter names and types" is more important. I'll use `reverse_list_naive` and `reverse_list_optimal`.

    *   Check Java syntax:
        `public ListNode reverseList(ListNode head) { ... }`

    *   Edge cases:
        - Empty list (`head is None`).
        - Single element list.
        - List with two elements.
        All handled by the iterative approach.

    *   Refining Approach 1 (Naive):
        Store values in a list, reverse the list, then update the values of the original nodes.
        Or, store nodes in a stack, pop and relink. Let's do the stack approach.

    *   Refining Approach 2 (Optimal):
        Iterative pointer manipulation.

    *   Refining Approach 3 (Java):
        Iterative pointer manipulation.

    *   Final Check on constraints: "Return ONLY the raw Python code. Do NOT wrap it in markdown block formatting".class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n)
# Space Complexity: O(n)
# This approach uses a stack to store all the nodes of the linked list. 
# By popping the nodes from the stack, we can relink them in reverse order.
def reverse_list_naive(head: ListNode) -> ListNode:
    if not head:
        return None
    
    stack = []
    curr = head
    while curr:
        stack.append(curr)
        curr = curr.next
    
    new_head = stack.pop()
    curr = new_head
    while stack:
        curr.next = stack.pop()
        curr = curr.next
    
    curr.next = None  # Set the next of the last node to None to avoid cycles
    return new_head

# --- APPROACH 2: Optimal (Iterative Pointer Manipulation) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach is optimal because it reverses the list in a single pass without 
# using any extra space for data structures. It simply reorients the pointers 
# of the existing nodes.
def reverse_list_optimal(head: ListNode) -> ListNode:
    prev = None
    curr = head
    
    while curr:
        next_node = curr.next  # Temporarily store the next node
        curr.next = prev       # Reverse the current node's pointer
        prev = curr            # Move prev pointer one step forward
        curr = next_node       # Move curr pointer one step forward
        
    return prev

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

public class ReverseLinkedList {
    /**
     * Reverses a singly linked list iteratively.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode curr = head;
        
        while (curr != null) {
            ListNode nextTemp = curr.next; // Store next node
            curr.next = prev;              // Reverse link
            prev = curr;                   // Move prev forward
            curr = nextTemp;               // Move curr forward
        }
        
        return prev;
    }
}
"""

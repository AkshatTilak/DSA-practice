"""
Challenge: q06_add_two_numbers
Difficulty: Medium
Link: https://leetcode.com/problems/add-two-numbers/

Problem:
Add two numbers list representation.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N + M)
# Space Complexity: O(max(N, M))
# This approach converts the linked lists into integers, adds the integers together, and then converts the resulting sum back into a linked list. While logically simple, it is limited by the maximum integer size in some languages (though Python handles arbitrarily large integers).

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_naive(l1: ListNode, l2: ListNode) -> ListNode:
    def list_to_int(node):
        num_str = ""
        while node:
            num_str += str(node.val)
            node = node.next
        # The list is in reverse order, so we reverse the string to get the number
        return int(num_str[::-1]) if num_str else 0

    # Convert lists to integers
    num1 = list_to_int(l1)
    num2 = list_to_int(l2)
    
    # Sum the numbers
    total = num1 + num2
    
    # Convert the sum back to a reversed linked list
    s_total = str(total)
    dummy = ListNode(0)
    current = dummy
    # The result should be stored in reverse order (ones place first)
    for char in reversed(s_total):
        current.next = ListNode(int(char))
        current = current.next
        
    return dummy.next

# --- APPROACH 2: Optimal (Two-Pointer Simulation) ---
# Time Complexity: O(max(N, M))
# Space Complexity: O(max(N, M))
# This approach simulates elementary school addition. We traverse both lists simultaneously, adding corresponding digits along with a carry. This is optimal because it visits each node exactly once and does not rely on intermediate type conversions, making it efficient and applicable to any language regardless of integer overflow limits.

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_optimal(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    current = dummy
    carry = 0
    
    while l1 or l2 or carry:
        # Get values from the current nodes, or 0 if we've reached the end of a list
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        # Calculate sum and carry
        total = val1 + val2 + carry
        carry = total // 10
        digit = total % 10
        
        # Create new node with the digit and move pointer
        current.next = ListNode(digit)
        current = current.next
        
        # Move to the next nodes in the input lists
        if l1: l1 = l1.next
        if l2: l2 = l2.next
        
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

public class AddTwoNumbers {
    /**
     * Optimal solution for adding two numbers represented as linked lists.
     * Time Complexity: O(max(N, M))
     * Space Complexity: O(max(N, M))
     */
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode dummyHead = new ListNode(0);
        ListNode current = dummyHead;
        int carry = 0;
        
        while (l1 != null || l2 != null || carry != 0) {
            int x = (l1 != null) ? l1.val : 0;
            int y = (l2 != null) ? l2.val : 0;
            
            int sum = carry + x + y;
            carry = sum / 10;
            current.next = new ListNode(sum % 10);
            current = current.next;
            
            if (l1 != null) l1 = l1.next;
            if (l2 != null) l2 = l2.next;
        }
        
        return dummyHead.next;
    }
}
"""

"""
Challenge: q05_copy_list_with_random_pointer
Difficulty: Medium
Link: https://leetcode.com/problems/copy-list-with-random-pointer/

Problem:
Copy list.
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
# This approach uses a hash map to create a 1:1 mapping between each node in the original list 
# and its corresponding newly created node. We traverse the list twice: first to create all 
# nodes and second to wire the next and random pointers.

class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random

def solve_naive(head: 'Node') -> 'Node':
    if not head:
        return None
    
    # Map to store original_node -> cloned_node
    old_to_new = {None: None}
    
    # First pass: create all cloned nodes
    curr = head
    while curr:
        old_to_new[curr] = Node(curr.val)
        curr = curr.next
        
    # Second pass: assign next and random pointers
    curr = head
    while curr:
        copy = old_to_new[curr]
        copy.next = old_to_new[curr.next]
        copy.random = old_to_new[curr.random]
        curr = curr.next
        
    return old_to_new[head]

# --- APPROACH 2: Optimal (Interweaving Nodes) ---
# Time Complexity: O(N)
# Space Complexity: O(1)
# This approach is optimal because it eliminates the need for an external hash map.
# It works by inserting each cloned node immediately after its original node in the list.
# This allows us to find the cloned version of any node's random target by simply 
# looking at the node immediately following the random target in the original list.
def solve_optimal(head: 'Node') -> 'Node':
    if not head:
        return None
    
    # Step 1: Create cloned nodes and interweave them into the original list
    # Original: A -> B -> C
    # Interweaved: A -> A' -> B -> B' -> C -> C'
    curr = head
    while curr:
        new_node = Node(curr.val, curr.next)
        curr.next = new_node
        curr = new_node.next
        
    # Step 2: Assign random pointers for the cloned nodes
    curr = head
    while curr:
        if curr.random:
            # The clone's random is the clone of the original's random
            curr.next.random = curr.random.next
        curr = curr.next.next
        
    # Step 3: Separate the interweaved list into original and cloned lists
    curr = head
    dummy = Node(0)
    copy_curr = dummy
    
    while curr:
        # Identify the clone
        clone = curr.next
        
        # Extract the clone to the new list
        copy_curr.next = clone
        copy_curr = clone
        
        # Restore the original list's next pointer
        curr.next = clone.next
        curr = curr.next
        
    return dummy.next

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package linked_list;

class Node {
    int val;
    Node next;
    Node random;

    public Node(int val) {
        this.val = val;
        this.next = null;
        this.random = null;
    }

    public Node(int val, Node next, Node random) {
        this.val = val;
        this.next = next;
        this.random = random;
    }
}

public class CopyListWithRandomPointer {
    public Node copyRandomList(Node head) {
        if (head == null) return null;

        // Step 1: Interweave
        Node curr = head;
        while (curr != null) {
            Node newNode = new Node(curr.val);
            newNode.next = curr.next;
            curr.next = newNode;
            curr = newNode.next;
        }

        // Step 2: Copy Random Pointers
        curr = head;
        while (curr != null) {
            if (curr.random != null) {
                curr.next.random = curr.random.next;
            }
            curr = curr.next.next;
        }

        // Step 3: Separate Lists
        curr = head;
        Node dummy = new Node(0);
        Node copyCurr = dummy;
        
        while (curr != null) {
            Node clone = curr.next;
            
            copyCurr.next = clone;
            copyCurr = clone;
            
            curr.next = clone.next;
            curr = curr.next;
        }
        
        return dummy.next;
    }
}
"""

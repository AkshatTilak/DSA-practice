INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/reverse-linked-list/',
    'description': 'Reverse a singly linked list.',
    'groups': ['Linked List'],
    'starter_code': """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    # Write your solution here
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---`
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_reverse():
    # Setup simple list 1->2 and reverse
    pass""",
    'readme_content': """# Reverse Linked List (q01_reverse_linked_list)

## 1. Overview & Problem Explanation

The goal of this challenge is to take a **singly linked list** and reverse its direction. In a singly linked list, each node contains a value and a pointer to the *next* node. To reverse the list, we must change every pointer so that it points to the *previous* node instead of the next one.

### Input / Output
- **Input**: The `head` node of a singly linked list (e.g., `1 -> 2 -> 3 -> 4 -> 5 -> None`).
- **Output**: The new `head` node of the reversed list (e.g., `5 -> 4 -> 3 -> 2 -> 1 -> None`).

### Constraints & Edge Cases
- **Time Complexity Target**: $O(N)$
- **Space Complexity Target**: $O(1)$
- **Empty List**: If the input `head` is `None`, the function should return `None`.
- **Single Node**: If the list contains only one node, it is already "reversed"; the function should return the head as is.
- **List Length**: The list can contain up to $5 \times 10^4$ nodes, meaning a recursive solution might risk a `StackOverflowError` in languages with small default stack limits (though Python handles this up to a certain depth).

---

## 2. Core Concepts & Data Structures

### The Singly Linked List
Unlike an array, a linked list does not store elements in contiguous memory. Each node is an object that knows its value and the location of the next object. Because the links are **unidirectional**, we cannot move backward. To reverse the list, we must logically "flip" these arrows.

### The Three-Pointer Technique
To reverse a link without losing the rest of the list, we need three pointers working in tandem:
1. **`prev`**: Keeps track of the node immediately behind the current node (this becomes the new `next`).
2. **`curr`**: The node we are currently processing.
3. **`nxt`**: A temporary pointer to hold the reference to the *original* next node. Without this, once we change `curr.next`, we lose the reference to the remainder of the list.

**Why this is optimal:** 
This approach is **in-place**. We are not creating a new list or using additional data structures (like a stack) to store values; we are simply modifying the existing pointers.

---

## 3. Step-by-Step Logic

### Optimal Iterative Solution
The iterative approach moves through the list once, flipping the pointers as it goes.

#### Logical Flow:
1. Initialize `prev` as `None` (because the original head will become the new tail, and the tail must point to `None`).
2. Initialize `curr` as the `head`.
3. Enter a `while` loop that continues until `curr` becomes `None`:
   - **Step A (Save):** Store the next node: `nxt = curr.next`.
   - **Step B (Reverse):** Change the current node's pointer to point backward: `curr.next = prev`.
   - **Step C (Advance):** Move `prev` forward to the current node: `prev = curr`.
   - **Step D (Advance):** Move `curr` forward to the saved next node: `curr = nxt`.
4. Once the loop finishes, `prev` will be pointing to the last node of the original list, which is the new head. Return `prev`.

#### Dry Run Trace
**Input:** `1 -> 2 -> 3 -> None`

| Step | `prev` | `curr` | `nxt` | Action | List State (Partial) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Init** | `None` | `1` | `None` | Initialize | `1 -> 2 -> 3` |
| **Iter 1** | `1` | `2` | `2` | `1.next = None` | `None <- 1` |
| **Iter 2** | `2` | `3` | `3` | `2.next = 1` | `None <- 1 <- 2` |
| **Iter 3** | `3` | `None` | `None` | `3.next = 2` | `None <- 1 <- 2 <- 3` |
| **End** | `3` | `None` | `None` | Return `prev` | **Head is now 3** |

### Implementation
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list_optimal(head: ListNode) -> ListNode:
    prev = None
    curr = head
    
    while curr:
        # 1. Save the next node so we don't lose the rest of the list
        nxt = curr.next 
        
        # 2. Flip the pointer to the previous node
        curr.next = prev 
        
        # 3. Shift prev and curr forward for the next iteration
        prev = curr 
        curr = nxt
        
    return prev
```

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Iterative** | $O(N)$ | $O(1)$ | We traverse the list exactly once. Only three pointer variables are used regardless of list size. |
| **Recursive** | $O(N)$ | $O(N)$ | We visit every node once, but each recursive call adds a frame to the call stack. |

---

## 5. Real-World Applications

While "reversing a linked list" is a classic interview problem, the underlying patterns are used in professional software engineering:

1. **Undo/Redo Mechanisms**: Many "Undo" systems operate as a stack of states. Reversing a sequence of operations is conceptually similar to traversing a state-linked list in reverse.
2. **Browser History**: The "Back" and "Forward" buttons in a web browser act like a doubly linked list. Implementing a "jump back" to a specific point often involves logic similar to pointer manipulation.
3. **Expression Evaluation**: In compiler design, certain types of expression parsing (like converting infix to postfix or evaluating right-associative operators) require processing elements in reverse order.
4. **LRU Cache (Least Recently Used)**: High-performance caches often use a combination of a Hash Map and a Doubly Linked List. Moving a "recently used" node to the head of the list involves precisely the kind of pointer swapping learned in this challenge.""",
}

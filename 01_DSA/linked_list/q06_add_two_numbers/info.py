INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/add-two-numbers/',
    'description': 'Add two numbers list representation.',
    'groups': ['Linked List', 'Math'],
    'readme_content': """# Add Two Numbers (q06_add_two_numbers)

## 📌 Overview & Problem Explanation

The **Add Two Numbers** challenge asks us to simulate the process of adding two non-negative integers. However, instead of being provided as standard integers or strings, these numbers are represented as **Singly Linked Lists**.

### The Twist: Reverse Order
The numbers are stored in **reverse order**. This means the head of the list is the **least significant digit** (the ones place), and the tail is the **most significant digit**.

**Example:**
- Number $342$ is represented as: `2 -> 4 -> 3`
- Number $465$ is represented as: `5 -> 6 -> 4`
- The sum $342 + 465 = 807$ is represented as: `7 -> 0 -> 8`

### Inputs & Outputs
- **Input:** Two non-empty linked lists `l1` and `l2`.
- **Output:** A linked list representing the sum of the two numbers.

### Constraints & Edge Cases
- **Node Values:** Each node contains a single digit ($0 \le \text{val} \le 9$).
- **List Length:** The number of nodes can vary. One list might be significantly longer than the other.
- **Carry Over:** Adding two digits (e.g., $7 + 8 = 15$) produces a carry that must be added to the next higher place value.
- **Final Carry:** If the addition of the most significant digits results in a carry (e.g., $50 + 50 = 100$), a new node must be created at the end of the list to hold the final `1`.

---

## ⚙️ Core Concepts & Data Structures

### 1. Singly Linked List
A linked list is used here because the number of digits in the sum isn't known upfront. Unlike an array, a linked list allows us to append new digits (nodes) dynamically as we calculate the sum from left to right.

### 2. Elementary Addition (Column Addition)
The problem is a direct implementation of the "carrying" method we learn in primary school:
1. Add the digits in the current column.
2. If the sum is $\ge 10$, keep the last digit and **carry over** the $1$ to the next column.
3. Move to the next column and repeat.

### 3. The "Dummy Head" Pattern
In linked list problems, creating a **Dummy Node** is a professional standard. It acts as a placeholder for the start of the resulting list. This prevents us from having to write redundant `if` statements to handle the initialization of the head node; we simply return `dummy.next` at the end.

---

## 🚀 Step-by-Step Logic

### The Optimal Approach: Single Pass Simulation

The most efficient way to solve this is to traverse both lists simultaneously, maintaining a `carry` variable.

#### Logical Workflow:
1. **Initialization**: 
   - Create a `dummy` node to start the result list.
   - Create a `curr` pointer to keep track of the last node added to the result.
   - Initialize `carry = 0`.
2. **Traversal**:
   - Use a `while` loop that continues as long as `l1` is not null, `l2` is not null, **or** there is a remaining `carry`.
3. **Digit Summation**:
   - Get the value from `l1` (if it exists, otherwise $0$).
   - Get the value from `l2` (if it exists, otherwise $0$).
   - Compute `total = val1 + val2 + carry`.
4. **Update State**:
   - Update `carry = total // 10` (Integer division).
   - Create a new node with `total % 10` and attach it to `curr.next`.
   - Move the `curr` pointer forward.
5. **Pointer Advancement**:
   - Move `l1` and `l2` to their respective next nodes if they are not null.
6. **Final Return**: Return `dummy.next`.

#### Dry Run Example:
`l1: [2, 4, 3]` (342)
`l2: [5, 6, 4]` (465)

| Step | l1 val | l2 val | Carry | Sum | Result Node | New Carry |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 2 | 5 | 0 | 7 | **7** | 0 |
| 2 | 4 | 6 | 0 | 10 | **0** | 1 |
| 3 | 3 | 4 | 1 | 8 | **8** | 0 |
| **End** | - | - | 0 | - | **[7, 0, 8]** | - |

---

## 💻 Implementation

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_optimal(l1: ListNode, l2: ListNode) -> ListNode:
    # Dummy node acts as the anchor for the result list
    dummy = ListNode(0)
    curr = dummy
    carry = 0
    
    # Continue as long as there are digits to process or a carry exists
    while l1 or l2 or carry:
        # Extract values, default to 0 if list is exhausted
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        # Calculate sum and carry
        total = val1 + val2 + carry
        carry = total // 10
        digit = total % 10
        
        # Create new node and advance current pointer
        curr.next = ListNode(digit)
        curr = curr.next
        
        # Advance input lists
        if l1: l1 = l1.next
        if l2: l2 = l2.next
        
    return dummy.next
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Optimal** | $O(\max(N, M))$ | $O(\max(N, M))$ | We traverse both lists once. The result list's length is at most $\max(N, M) + 1$. |

- **Time Complexity**: $O(\max(N, M))$, where $N$ and $M$ are the lengths of the two linked lists. We must visit every node in the longer list at least once.
- **Space Complexity**: $O(\max(N, M))$. We create a new linked list to store the result. Note that the space used for the output is generally required by the problem and not considered "extra" auxiliary space in some contexts, but technically it scales linearly with the input.

---

## 🌍 Real-World Applications

While we rarely add numbers using linked lists in standard application code, the **patterns** used here are critical in systems engineering:

1. **Arbitrary-Precision Arithmetic (BigInt)**:
   Standard 64-bit integers have a maximum value. Libraries that handle "BigInts" (like Python's `int` or Java's `BigInteger`) internally represent numbers as arrays or linked lists of digits to handle numbers with thousands of places (essential for cryptography/RSA).

2. **Stream Processing**:
   The logic of processing data in "chunks" (digits) and carrying state (the carry variable) forward is the foundation of **Reduce/Fold operations** in functional programming and data streaming pipelines (e.g., Apache Flink).

3. **Compiler Lexing/Parsing**:
   When a compiler parses a large numeric literal, it often processes digits one by one, maintaining a running total—very similar to the additive logic used in this challenge.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

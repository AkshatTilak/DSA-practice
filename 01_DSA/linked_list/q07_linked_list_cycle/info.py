INFO = {
    'difficulty': 'Easy',
    'link': 'https://leetcode.com/problems/linked-list-cycle/',
    'description': 'Detect cycle.',
    'groups': ['Linked List', 'Two Pointers'],
    'readme_content': """# Linked List Cycle

## 📌 Overview & Problem Explanation

The **Linked List Cycle** problem asks us to determine if a given singly linked list contains a cycle. A **cycle** occurs if there is a node in the list that can be reached again by continuously following the `next` pointer. In other words, the list does not terminate with a `null` (or `None` in Python) pointer but instead loops back to a previously visited node.

### Input & Output
- **Input**: The `head` node of a singly linked list.
- **Output**: A boolean value: `True` if there is a cycle, `False` otherwise.

### Constraints & Edge Cases
- **Empty List**: If the head is `null`, there is no cycle.
- **Single Node**: A single node with no `next` pointer has no cycle; a single node pointing to itself has a cycle.
- **List Size**: The number of nodes can range from $0$ to $10^4$.
- **Memory Constraints**: The challenge often asks if we can solve this using $O(1)$ (constant) memory.

---

## 🧠 Core Concepts & Algorithms

To solve this problem, we generally look at two primary patterns: **Hashing** and **Two Pointers**.

### 1. Hash Set (The "Memory" Approach)
The most intuitive way to detect a cycle is to remember every node we have already visited. By storing the memory address (or the node object itself) in a **Hash Set**, we can check in $O(1)$ time if the current node has been seen before. If we encounter a node that is already in the set, a cycle exists.

### 2. Floyd's Cycle-Finding Algorithm (The "Tortoise and Hare")
This is the optimal algorithmic pattern for this problem. It uses two pointers moving at different speeds:
- **Slow Pointer (Tortoise)**: Moves one step at a time.
- **Fast Pointer (Hare)**: Moves two steps at a time.

**Why this works:**
Imagine two runners on a circular track. Even if one starts behind the other, the faster runner will eventually lap the slower runner and meet them again. 
- If there is **no cycle**, the fast pointer will reach the end of the list (`None`) quickly.
- If there **is a cycle**, the fast pointer will eventually enter the loop. Once the slow pointer also enters the loop, the distance between them decreases by exactly 1 node per iteration. Eventually, the distance becomes 0, and the pointers meet at the exact same node.

---

## 🛠️ Step-by-Step Logic

### Approach 1: Using a Hash Set (Naive/Intuitive)
1. Initialize an empty set called `visited`.
2. Traverse the linked list using a pointer `current`.
3. At each node:
   - Check if `current` is already in the `visited` set.
   - If **yes**, return `True` (cycle detected).
   - If **no**, add `current` to the `visited` set and move to `current.next`.
4. If the loop finishes (we hit `None`), return `False`.

### Approach 2: Floyd's Two-Pointer (Optimal)
1. Initialize two pointers, `slow` and `fast`, both pointing to the `head`.
2. Enter a loop that continues as long as `fast` and `fast.next` are not `None`.
3. In each iteration:
   - Move `slow` forward by one node: `slow = slow.next`.
   - Move `fast` forward by two nodes: `fast = fast.next.next`.
4. Check if `slow == fast`. If they point to the same memory address, a cycle exists $\rightarrow$ return `True`.
5. If the loop terminates because `fast` reached the end, return `False`.

#### 🔍 Dry Run Example
**Input**: `3 -> 2 -> 0 -> -4` (where `-4` points back to `2`)

| Step | Slow Pointer | Fast Pointer | Match? |
| :--- | :--- | :--- | :--- |
| Start | Node(3) | Node(3) | Yes (Start) |
| 1 | Node(2) | Node(0) | No |
| 2 | Node(0) | Node(2) | No |
| 3 | Node(-4) | Node(-4) | **YES!** $\rightarrow$ Cycle Found |

---

## 💻 Implementation

```python
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def solve_optimal(head: ListNode) -> bool:
    \"\"\"
    Detects a cycle in a linked list using Floyd's Cycle-Finding Algorithm.
    Time Complexity: O(n)
    Space Complexity: O(1)
    \"\"\"
    if not head or not head.next:
        return False
    
    slow = head
    fast = head
    
    while fast and fast.next:
        slow = slow.next          # Move 1 step
        fast = fast.next.next     # Move 2 steps
        
        if slow == fast:          # Pointers met
            return True
            
    return False # Fast pointer reached the end
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Hash Set** | $O(n)$ | $O(n)$ | We visit each node once, but store every node in the set. |
| **Two Pointers** | $O(n)$ | $O(1)$ | We visit nodes linearly; only two pointer variables are used regardless of list size. |

**Time Complexity Note**: In the Two-Pointer approach, if there is a cycle, the fast pointer will catch the slow pointer in at most $N$ iterations (where $N$ is the number of nodes).

---

## 🚀 Real-World Applications

While "detecting cycles in a linked list" seems like a textbook puzzle, the underlying logic is used extensively in software engineering:

1. **Deadlock Detection**: In Operating Systems, Resource Allocation Graphs are used to detect deadlocks. If a cycle exists in the graph (where nodes are processes and edges are resource requests), a deadlock has occurred.
2. **Garbage Collection**: Memory management systems (like Python's `gc` module) use cycle detection to find "unreachable" groups of objects that reference each other but are no longer accessible from the root of the program.
3. **Network Routing**: Routing protocols (like BGP or RIP) use similar logic (TTL - Time to Live) to prevent packets from looping infinitely between routers if a routing loop is accidentally configured.
4. **Compiler Theory**: Detecting circular dependencies in module imports or class inheritance hierarchies to prevent infinite recursion during compilation.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
}

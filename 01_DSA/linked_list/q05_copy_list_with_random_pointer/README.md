# Copy List With Random Pointer

## 📌 Overview & Problem Explanation

The challenge is to create a **deep copy** of a special linked list. In a standard linked list, each node only points to the next node. In this version, each node has two pointers:
1. `next`: Points to the next node in the sequence.
2. `random`: Points to any node in the list, or `null`.

### What is a Deep Copy?
A **shallow copy** would simply copy the head pointer, meaning both the original and the copy point to the same memory addresses. A **deep copy** requires creating entirely new node instances in memory. If you change a value in the original list, the copied list must remain unchanged.

### Constraints & Edge Cases
- **Input**: A linked list where each node contains an integer value and two pointers.
- **Output**: A new linked list that is an exact structural replica of the input.
- **Constraints**:
    - The number of nodes is in the range $[0, 10^3]$.
    - Node values are in the range $[-10^4, 10^4]$.
    - The `random` pointer can point to any node in the list, including itself, or be `null`.
- **Edge Cases**:
    - **Empty List**: The input `head` is `null`.
    - **Single Node**: The list has only one node pointing to itself via the `random` pointer.
    - **Circular Random Pointers**: The `random` pointer creates a cycle.

---

## ⚙️ Core Concepts & Data Structures

To solve this problem, we must overcome one primary hurdle: **Forward Referencing**. When we are at Node A, its `random` pointer might point to Node Z, which we haven't created yet.

### 1. Hashing (The Mapping Strategy)
We can use a **Hash Map (Dictionary)** to create a mapping between the original node and its corresponding copied node. 
- **Key**: Original Node object.
- **Value**: Copied Node object.
This allows us to retrieve the copy of any node in $O(1)$ time, regardless of whether we have processed its `next` pointer yet.

### 2. Interweaving (The Pointer Manipulation Strategy)
To optimize space, we can use the original list as its own "storage" for the copies. By inserting each copied node directly after its original counterpart, we eliminate the need for an external hash map. The relationship becomes:
`Original Node` $\rightarrow$ `Copied Node` $\rightarrow$ `Next Original Node` $\rightarrow$ `Next Copied Node`.

---

## 🚀 Step-by-Step Logic

### Approach 1: The Hash Map Method (Intuitive)
This is the most straightforward approach, utilizing extra space to simplify the logic.

1. **First Pass**: Traverse the original list. For every node encountered, create a new node with the same value and store the pair `{OriginalNode: CopiedNode}` in the hash map.
2. **Second Pass**: Traverse the original list again. For each node:
   - Use the map to find its corresponding copy.
   - Set `Copy.next` to the map's value for `Original.next`.
   - Set `Copy.random` to the map's value for `Original.random`.
3. **Return**: The copy of the original head.

---

### Approach 2: The Interweaving Method (Optimal Space)
This approach is preferred in high-performance systems as it reduces auxiliary space complexity to $O(1)$.

#### Step 1: Create Interwoven Nodes
Iterate through the list and insert a copy of each node immediately after the original.
- **Original**: `A -> B -> C`
- **Interwoven**: `A -> A' -> B -> B' -> C -> C'`

#### Step 2: Assign Random Pointers
Iterate through the interwoven list. Because the copy `A'` is always immediately after `A`, the copy of `A.random` is always `A.random.next`.
- Logic: `curr.next.random = curr.random.next` (handling nulls carefully).

#### Step 3: Separate the Lists
Restore the original list and extract the copy list by decoupling the nodes.
- `A -> A' -> B -> B'` becomes `A -> B` and `A' -> B'`.

### Dry Run Example (Interweaving)
**Input**: `[{"val": 1, "random": null}, {"val": 2, "random": node 1}]`

1. **Interweave**: `1 -> 1' -> 2 -> 2' -> null`
2. **Randoms**: 
   - Node 1 random is null $\rightarrow$ 1' random is null.
   - Node 2 random is Node 1 $\rightarrow$ 2' random is `Node 2.random.next` (which is 1').
3. **Separate**:
   - Original: `1 -> 2 -> null`
   - Copy: `1' -> 2' -> null`

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Hash Map** | $O(N)$ | $O(N)$ | We traverse the list twice and store all $N$ nodes in a map. |
| **Interweaving**| $O(N)$ | $O(1)$ | We traverse the list three times, but use no extra auxiliary space besides the output list. |

> **Note**: In big-O analysis for "Copy" problems, the space required for the output itself is typically not counted as "extra" auxiliary space.

---

## 💻 Implementation

```python
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random

def solve_optimal(head: 'Node') -> 'Node':
    if not head:
        return None

    # Step 1: Interweave
    curr = head
    while curr:
        new_node = Node(curr.val, curr.next)
        curr.next = new_node
        curr = new_node.next

    # Step 2: Assign Random Pointers
    curr = head
    while curr:
        if curr.random:
            curr.next.random = curr.random.next
        curr = curr.next.next

    # Step 3: Separate Lists
    curr = head
    dummy = Node(0) # Helper to track the head of the copy
    copy_curr = dummy
    
    while curr:
        # Extract the copy
        copy_curr.next = curr.next
        copy_curr = copy_curr.next
        
        # Restore the original
        curr.next = curr.next.next
        curr = curr.next
        
    return dummy.next
```

---

## 🌍 Real-World Applications

This pattern of "cloning a graph-like structure" is highly prevalent in software engineering:

1. **Undo/Redo Mechanisms (Memento Pattern)**: When saving a state of a complex object graph (like a document with interconnected elements), a deep copy is required to ensure that modifying the current state doesn't accidentally corrupt the history.
2. **Compiler Design (Abstract Syntax Trees)**: When performing optimizations on an AST, compilers often clone portions of the tree to test different optimization paths without destroying the original source representation.
3. **Game State Serialization**: In gaming, creating "save points" or "snapshots" of the game world involves deep-copying the current state of all entities and their relationships.
4. **Prototype Pattern**: Used in object-oriented design to create new objects by copying an existing "prototype" instance, ensuring that the new object is independent of the original.
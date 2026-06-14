INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/find-the-duplicate-number/',
    'description': 'Find duplicate using cycle detection.',
    'groups': ['Array', 'Linked List', 'Two Pointers'],
    'readme_content': """# Find Duplicate (q08_find_duplicate)

## 📌 Overview & Problem Explanation

The **Find the Duplicate Number** challenge asks us to identify a repeating integer within an array of $n + 1$ integers. The integers in the array are guaranteed to be in the range $[1, n]$. According to the **Pigeonhole Principle**, if you have $n+1$ items to put into $n$ holes, at least one hole must contain more than one item.

### The Constraints
This problem is deceptively simple but becomes challenging due to strict constraints:
1. **Constant Extra Space**: You must solve it using $O(1)$ additional memory.
2. **Read-Only**: You are not allowed to modify the input array (no sorting, no marking elements as negative).
3. **Time Complexity**: The solution should ideally be linear $O(n)$.

### Example Trace
**Input**: `nums = [1, 3, 4, 2, 2]`
- $n = 4$, Array size = 5.
- Values range from $1$ to $4$.
- The number `2` appears twice.
- **Output**: `2`

**Edge Cases**:
- **Minimum size**: `[1, 1]` $\rightarrow$ Output: `1`.
- **Duplicate at ends**: `[2, 1, 2]` $\rightarrow$ Output: `2`.
- **All elements same**: `[1, 1, 1]` $\rightarrow$ Output: `1`.

---

## ⚙️ Core Concepts & Algorithms

While this is categorized under "Linked Lists," the input is an **Array**. The trick is to treat the array as a **Implicit Linked List**.

### The Array-to-List Mapping
If we treat the value at each index as a "pointer" to the next index, we create a directed graph.
- Index $i \rightarrow$ Value $nums[i]$
- Example: `nums = [1, 3, 4, 2, 2]`
  - $0 \rightarrow nums[0] = 1$
  - $1 \rightarrow nums[1] = 3$
  - $3 \rightarrow nums[3] = 2$
  - $2 \rightarrow nums[2] = 4$
  - $4 \rightarrow nums[4] = 2$ (Cycle detected!)

Because there is a duplicate number, multiple indices will point to the same value. In graph terms, this means two different nodes point to the same node, creating a **cycle**. The duplicate number is the **entrance to the cycle**.

### Floyd's Cycle-Finding Algorithm (Tortoise and Hare)
To find the entrance of a cycle in $O(1)$ space, we use two pointers moving at different speeds:
1. **The Tortoise (Slow)**: Moves one step at a time ($slow = nums[slow]$).
2. **The Hare (Fast)**: Moves two steps at a time ($fast = nums[nums[fast]]$).

If a cycle exists, the Hare will eventually lap the Tortoise and they will meet inside the cycle.

---

## 🚶 Step-by-Step Logic

### Approach 1: The Optimal Solution (Floyd's Cycle Detection)

The algorithm is divided into two distinct phases:

#### Phase 1: Detecting the Cycle
1. Initialize `slow` and `fast` pointers at the first index (`0`).
2. Move `slow` by one step and `fast` by two steps.
3. Continue until `slow == fast`.
4. Once they meet, we have confirmed a cycle exists and we have a meeting point inside that cycle.

#### Phase 2: Finding the Entrance (The Duplicate)
1. Leave the `fast` pointer at the meeting point.
2. Reset the `slow` pointer back to the start (`0`).
3. Move **both** pointers one step at a time.
4. The point where they meet again is the **entrance to the cycle**, which corresponds exactly to the duplicate number.

### Dry Run Example: `nums = [1, 3, 4, 2, 2]`

**Phase 1:**
- Start: `slow=0`, `fast=0`
- Step 1: `slow=nums[0]=1`, `fast=nums[nums[0]]=nums[1]=3`
- Step 2: `slow=nums[1]=3`, `fast=nums[nums[3]]=nums[2]=4`
- Step 3: `slow=nums[3]=2`, `fast=nums[nums[4]]=nums[2]=4`
- Step 4: `slow=nums[2]=4`, `fast=nums[nums[4]]=nums[2]=4` 
- **Meeting Point: Index 4 (Value 4)**

**Phase 2:**
- Reset: `slow=0`, `fast=4`
- Step 1: `slow=nums[0]=1`, `fast=nums[4]=2`
- Step 2: `slow=nums[1]=3`, `fast=nums[2]=4` (Wait, trace carefully)
- Let's re-trace carefully:
  - $S=0, F=4$
  - $S=nums[0]=1, F=nums[4]=2$
  - $S=nums[1]=3, F=nums[2]=4$
  - $S=nums[3]=2, F=nums[4]=2$ $\leftarrow$ **They meet at value 2!**

**Result: 2**

---

## 💻 Implementation

```python
def solve_optimal(nums):
    \"\"\"
    Finds the duplicate number using Floyd's Cycle Detection Algorithm.
    Time Complexity: O(n)
    Space Complexity: O(1)
    \"\"\"
    # Phase 1: Find the intersection point in the cycle
    tortoise = nums[0]
    hare = nums[0]
    
    while True:
        tortoise = nums[tortoise]          # Move 1 step
        hare = nums[nums[hare]]           # Move 2 steps
        if tortoise == hare:
            break
            
    # Phase 2: Find the entrance to the cycle (the duplicate)
    tortoise = nums[0]
    while tortoise != hare:
        tortoise = nums[tortoise]         # Move 1 step
        hare = nums[hare]                 # Move 1 step
        
    return hare
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Modifies Input? | Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Brute Force (Sorting)** | $O(n \log n)$ | $O(1)$ or $O(n)$ | Yes | Sorting allows adjacent comparison but violates "Read-Only". |
| **Hash Set** | $O(n)$ | $O(n)$ | No | Stores every visited number; violates $O(1)$ space. |
| **Binary Search (Range)** | $O(n \log n)$ | $O(1)$ | No | Binary search on the *range* $[1, n]$, counting elements in each half. |
| **Floyd's Cycle Detection**| $O(n)$ | $O(1)$ | No | Two-pointer traversal of the implicit linked list. |

---

## 🌍 Real-World Applications

The cycle detection pattern is used extensively in systems programming and security:

1. **Memory Leak Detection**: In garbage collection (like in Java or Python), cycle detection helps identify groups of objects that reference each other but are no longer reachable from the root, allowing them to be reclaimed.
2. **Deadlock Detection**: In Operating Systems, Resource Allocation Graphs (RAG) are used to detect deadlocks. A cycle in the graph indicates that a set of processes are stuck waiting for each other.
3. **Network Routing**: To prevent packets from looping infinitely in a network (Routing Loops), algorithms like TTL (Time To Live) or specific cycle detection mechanisms are used.
4. **Compiler Optimization**: Compilers use cycle detection in Control Flow Graphs (CFGs) to identify loops (like `for` or `while`) for optimization techniques like loop unrolling.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n log n)
# Space Complexity: O(n) or O(1) depending on sorting implementation
# This approach sorts the input list and then iterates through it to find two adjacent elements that are identical.
def solve_naive(nums):
    if not nums:
        return None
    
    # Create a sorted copy to avoid modifying the original input if necessary,
    # though standard naive sorting usually takes O(n log n).
    sorted_nums = sorted(nums)
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i] == sorted_nums[i + 1]:
            return sorted_nums[i]
    return None

# --- APPROACH 2: Optimal (Floyd's Cycle Finding Algorithm) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach treats the array as a linked list where the value at index 'i' points to the index 'nums[i]'.
# Since there is a duplicate, a cycle must exist. Floyd's Tortoise and Hare algorithm is used to:
# 1. Detect the cycle using a slow and fast pointer.
# 2. Find the start of the cycle, which corresponds to the duplicate number.
# It is optimal because it requires no extra space and performs the search in linear time without modifying the input array.
def solve_optimal(nums):
    if not nums:
        return None
        
    # Phase 1: Detecting the cycle
    # Initialize slow and fast pointers.
    # We start from the first element.
    slow = nums[0]
    fast = nums[0]
    
    # Move slow pointer by 1 step and fast pointer by 2 steps until they meet.
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
            
    # Phase 2: Finding the entrance to the cycle (the duplicate)
    # Reset one pointer to the start of the array.
    slow = nums[0]
    # Move both pointers at the same speed until they meet.
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
        
    return slow

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package linked_list;

public class FindDuplicate {
    /**
     * Finds the duplicate number in an array of n+1 integers where each integer is between 1 and n.
     * Implements Floyd's Cycle Finding Algorithm.
     * 
     * @param nums Input array
     * @return The duplicate number
     */
    public int solveOptimal(int[] nums) {
        if (nums == null || nums.length == 0) {
            throw new IllegalArgumentException("Array must not be empty");
        }

        // Phase 1: Find the intersection point of the two pointers.
        int slow = nums[0];
        int fast = nums[0];

        do {
            slow = nums[slow];
            fast = nums[nums[fast]];
        } while (slow != fast);

        // Phase 2: Find the entrance to the cycle.
        slow = nums[0];
        while (slow != fast) {
            slow = nums[slow];
            fast = nums[fast];
        }

        return slow;
    }

    public static void main(String[] args) {
        FindDuplicate fd = new FindDuplicate();
        int[] test1 = {1, 3, 4, 2, 2};
        int[] test2 = {3, 1, 3, 4, 2};
        System.out.println("Duplicate 1: " + fd.solveOptimal(test1)); // Expected: 2
        System.out.println("Duplicate 2: " + fd.solveOptimal(test2)); // Expected: 3
    }
}
\"\"\"""",
}

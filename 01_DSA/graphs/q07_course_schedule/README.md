# Course Schedule

## 📌 Overview & Problem Explanation

The **Course Schedule** problem is a classic graph theory challenge that asks whether it is possible to complete a set of courses given a series of prerequisites. Each prerequisite is represented as a pair `[a, b]`, meaning that to take course `a`, you must first complete course `b`.

In graph terms, this is a problem of **Cycle Detection in a Directed Graph**. If the dependencies form a cycle (e.g., Course 0 requires Course 1, and Course 1 requires Course 0), it is logically impossible to finish the courses. If no cycle exists, the graph is a **Directed Acyclic Graph (DAG)**, and a valid sequence (topological sort) exists.

### 📥 Inputs & 📤 Outputs
- **Input**: 
    - `numCourses`: An integer representing the total number of courses (nodes).
    - `prerequisites`: A list of integer pairs `[course, prerequisite]` (directed edges).
- **Output**: 
    - `Boolean`: `True` if all courses can be finished (no cycles), `False` otherwise.

### ⚠️ Constraints & Edge Cases
- **Constraints**: 
    - $1 \le \text{numCourses} \le 2000$
    - $0 \le \text{prerequisites.length} \le 5000$
- **Edge Cases**:
    - **No Prerequisites**: If the list is empty, return `True` immediately.
    - **Disconnected Components**: The graph might have several isolated clusters of courses; the algorithm must handle all of them.
    - **Self-Loops**: A course requiring itself `[0, 0]` is an immediate cycle.
    - **Multiple Dependencies**: A course might require multiple other courses.

---

## 🧠 Core Concepts & Algorithms

### 1. Directed Acyclic Graph (DAG)
A **Directed Graph** is one where edges have a direction. A **DAG** is a directed graph with no cycles. The ability to complete the courses is exactly equivalent to confirming that the dependency graph is a DAG.

### 2. Topological Sort
Topological sorting is a linear ordering of vertices such that for every directed edge $u \rightarrow v$, vertex $u$ comes before $v$ in the ordering. If a graph can be topologically sorted, it is by definition a DAG.

### 3. Algorithmic Patterns
Two primary patterns are used to solve this:

#### A. Kahn's Algorithm (BFS Approach)
This approach focuses on the **In-Degree** of nodes. The in-degree is the number of incoming edges to a node.
- Nodes with an in-degree of $0$ have no prerequisites and can be completed immediately.
- By repeatedly removing these "ready" nodes and updating their neighbors, we can determine if all nodes can be processed.

#### B. DFS with State Tracking (Recursion Stack)
This approach explores as deep as possible along a path. To detect a cycle, we track whether a node is currently "in-flight" in the current recursion stack.
- **Unvisited**: Not yet processed.
- **Visiting**: Currently in the recursion stack (if we hit a "Visiting" node, a cycle exists).
- **Visited**: Fully processed and confirmed not to be part of a cycle.

---

## 🛠️ Step-by-Step Logic

### Approach 1: Kahn's Algorithm (BFS)
1. **Graph Construction**: Create an adjacency list to represent the graph and an array `in_degree` to store the number of prerequisites for each course.
2. **Initialize Queue**: Find all courses with `in_degree == 0` and push them into a queue.
3. **Process Queue**:
    - While the queue is not empty:
        - Pop a course `u`.
        - Increment a `count` of completed courses.
        - For every course `v` that depends on `u`:
            - Decrement `in_degree[v]`.
            - If `in_degree[v]` becomes $0$, push `v` into the queue.
4. **Final Check**: If `count == numCourses`, return `True`. Otherwise, return `False` (a cycle prevented some nodes from ever reaching in-degree 0).

### Approach 2: Depth First Search (DFS)
1. **Graph Construction**: Create an adjacency list.
2. **State Array**: Initialize a `state` array where `0 = Unvisited`, `1 = Visiting`, and `2 = Visited`.
3. **Recursive Exploration**:
    - For each course, if it is `Unvisited`, start a DFS.
    - Mark the current node as `Visiting`.
    - For each neighbor:
        - If the neighbor is `Visiting` $\rightarrow$ **Cycle detected!** Return `False`.
        - If the neighbor is `Unvisited` $\rightarrow$ Recursively call DFS. If it returns `False`, propagate it up.
    - After visiting all neighbors, mark the current node as `Visited`.
4. **Completion**: If all nodes are processed without finding a cycle, return `True`.

---

## 💻 Implementation

```python
from collections import deque, defaultdict

def solve_optimal_bfs(numCourses, prerequisites):
    # 1. Build Graph and In-Degree array
    adj = defaultdict(list)
    in_degree = [0] * numCourses
    
    for dest, src in prerequisites:
        adj[src].append(dest)
        in_degree[dest] += 1
    
    # 2. Queue all nodes with 0 in-degree
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    
    completed_courses = 0
    
    # 3. Process the queue
    while queue:
        u = queue.popleft()
        completed_courses += 1
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
                
    # 4. If we processed all courses, no cycle exists
    return completed_courses == numCourses

def solve_optimal_dfs(numCourses, prerequisites):
    adj = defaultdict(list)
    for dest, src in prerequisites:
        adj[src].append(dest)
        
    # 0: Unvisited, 1: Visiting, 2: Visited
    state = [0] * numCourses
    
    def has_cycle(u):
        if state[u] == 1: return True  # Found a back-edge
        if state[u] == 2: return False # Already verified
        
        state[u] = 1 # Mark as visiting
        for v in adj[u]:
            if has_cycle(v):
                return True
        
        state[u] = 2 # Mark as visited
        return False

    for i in range(numCourses):
        if state[i] == 0:
            if has_cycle(i):
                return False
                
    return True
```

---

## 📊 Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Kahn's (BFS)** | $O(V + E)$ | $O(V + E)$ | We visit every vertex once and every edge once. Space is used for the adjacency list and in-degree array. |
| **DFS** | $O(V + E)$ | $O(V + E)$ | We visit every vertex and edge once. Space is used for the adjacency list and the recursion stack. |

*Where $V$ = `numCourses` and $E$ = `len(prerequisites)`.*

---

## 🌍 Real-World Applications

The pattern of cycle detection and topological sorting is fundamental to many software engineering systems:

1. **Build Systems (e.g., Make, Gradle, Bazel)**: Determining the order in which source files should be compiled based on their dependencies.
2. **Package Managers (e.g., npm, pip, apt)**: Resolving the installation order of libraries. If Library A depends on B, and B depends on A, the package manager throws a "Circular Dependency" error.
3. **Task Scheduling (e.g., Apache Airflow)**: Defining DAGs for data pipelines where certain tasks must finish before others begin.
4. **Instruction Scheduling in Compilers**: Reordering machine instructions to minimize pipeline stalls while maintaining data dependencies.
5. **Spreadsheet Formula Evaluation**: When cell A1 depends on B1, and B1 depends on C1, the spreadsheet engine uses a similar logic to calculate values in the correct order.
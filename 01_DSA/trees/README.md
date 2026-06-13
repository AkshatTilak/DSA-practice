# Trees

A Tree is a hierarchical, non-linear data structure consisting of nodes connected by edges. The top node is the root. Trees are widely used to represent hierarchical relationships (like folder directories), optimize lookups (Binary Search Trees), and balance structural splits (AVL, Red-Black Trees). Binary Trees restrict each node to at most two children: Left and Right.

---

## 🗺️ ASCII Execution Flow: Invert Binary Tree

Here is the recursive swap mechanism of inverting a binary tree (mirroring it):

```text
Original Tree:
        [ 4 ]
       /     \
    [ 2 ]   [ 7 ]
    /   \   /   \
  [1]   [3][6]  [9]

Step 1: Traverse to bottom leaves recursively.
Step 2: Swap left/right pointers of Node 2:
        [ 2 ] ──> Left becomes [3], Right becomes [1]
Step 3: Swap left/right pointers of Node 7:
        [ 7 ] ──> Left becomes [9], Right becomes [6]
Step 4: Swap left/right pointers of Root Node 4:
        [ 4 ] ──> Left becomes [7], Right becomes [2]

Inverted Tree:
        [ 4 ]
       /     \
    [ 7 ]   [ 2 ]
    /   \   /   \
  [9]   [6][3]  [1]
```

---

## 📊 Complexity Analysis

| Operations | Balanced Tree | Unbalanced (Skewed) Tree |
| :--- | :--- | :--- |
| Lookup / Search | $O(\log N)$ | $O(N)$ |
| Insertion / Deletion | $O(\log N)$ | $O(N)$ |
| Tree Traversal (DFS/BFS) | $O(N)$ time, $O(H)$ space | $O(N)$ time, $O(N)$ space |

---

## 🏢 Real-World Production Use-Case

### Browsers: DOM Tree Construction and Render Reflows
Web browsers parse HTML files into an interactive document structure called the DOM.
1. The DOM parser reads HTML tags sequentially and constructs a hierarchical **Tree** of nodes representing document elements (div, p, span, etc.).
2. When styles or states change, the layout engine traverses this DOM tree (and CSSOM tree) to compute visual coordinates.
3. Using tree structure allows elements to propagate properties (like font inheritance) downward to child nodes.
4. It also enables localized sub-tree updates (using Virtual DOM diffs) to re-render modified sections without recalculating the entire layout.
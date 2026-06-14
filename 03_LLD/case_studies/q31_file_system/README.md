# File System LLD (Composite Pattern)

## 1. Overview & System Requirements
The goal of this Low-Level Design (LLD) is to simulate a hierarchical File System. In a typical operating system, a file system consists of **Files** and **Directories**. The primary challenge is that a directory can contain both files and other directories, creating a recursive, tree-like structure.

### Core Entities
- **File**: A leaf node representing a basic unit of storage with a name and a size.
- **Directory**: A composite node that can contain multiple files or sub-directories.
- **FileSystemNode**: A common interface/abstract base class that allows the system to treat both files and directories uniformly.

### Functional Requirements
- **Create**: Ability to create files and directories.
- **Add/Remove**: Add a file or directory into another directory; remove an entry from a directory.
- **Size Calculation**: Calculate the total size of a file (simple) or a directory (sum of all its contents recursively).
- **Listing**: List the names of all immediate children within a directory.
- **Uniformity**: The client should be able to call `getSize()` or `getName()` on any node without knowing if it is a single file or a folder.

---

## 2. Design Principles & Patterns

### Composite Design Pattern
The **Composite Pattern** is the heart of this design. It is a structural pattern used when you need to treat a group of objects the same way as a single instance of the object.
- **Why?** Without this pattern, the client would need to check `if (node is File)` or `if (node is Directory)` before performing operations, leading to cluttered code and violating the Open/Closed Principle.
- **Problem Solved**: It eliminates the need for type-checking and allows for recursive aggregation.

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: `File` is responsible only for file-level data; `Directory` is responsible only for managing its children.
- **Open/Closed Principle (OCP)**: We can introduce new types of nodes (e.g., `Shortcut`, `SymLink`, `EncryptedFile`) by extending `FileSystemNode` without modifying the existing `Directory` or `File` logic.
- **Liskov Substitution Principle (LSP)**: Since `Directory` and `File` both inherit from `FileSystemNode`, any method expecting a `FileSystemNode` can accept either without breaking the application.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
       +-------------------+
       |  FileSystemNode   | <--- (Abstract Component)
       +-------------------+
       | - name: String    |
       +-------------------+
       | + getName(): Str  |
       | + getSize(): Int  |
       +-------------------+
                ^
                |
      __________|__________
     |                     |
+----+----+           +----+----+
|   File  |           | Directory | <--- (Composite)
+---------+           +-----------+
| - size:Int|         | - children:List|
+---------+           +-----------+
| +getSize()|         | +add(node)    |
+---------+           | +remove(node) |
                      | +getSize()    |
                      +-----------+
```

### Relationships
- **Inheritance**: `File` and `Directory` inherit from `FileSystemNode`.
- **Composition**: `Directory` maintains a collection (List) of `FileSystemNode` references. This creates the recursive tree structure.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List

# 1. Component: The abstract base class
class FileSystemNode(ABC):
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    @abstractmethod
    def get_size(self) -> int:
        """Return the size of the node in bytes/KB."""
        pass

# 2. Leaf: Represents an individual file
class File(FileSystemNode):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size

    def get_size(self) -> int:
        return self.size

# 3. Composite: Represents a directory containing other nodes
class Directory(FileSystemNode):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: List[FileSystemNode] = []

    def add(self, node: FileSystemNode):
        self._children.append(node)

    def remove(self, node_name: str):
        self._children = [node for node in self._children if node.get_name() != node_name]

    def get_size(self) -> int:
        """
        Recursive logic: The size of a directory is the sum 
        of the sizes of all its children.
        """
        total_size = 0
        for child in self._children:
            total_size += child.get_size()
        return total_size

    def list_contents(self) -> List[str]:
        return [node.get_name() for node in self._children]

# --- Client Code ---
if __name__ == "__main__":
    # Creating a structure: 
    # root / { documents / { resume.pdf, photo.jpg }, videos / { movie.mp4 } }
    
    root = Directory("root")
    docs = Directory("documents")
    vids = Directory("videos")
    
    resume = File("resume.pdf", 100)
    photo = File("photo.jpg", 500)
    movie = File("movie.mp4", 2000)
    
    # Building the hierarchy
    docs.add(resume)
    docs.add(photo)
    vids.add(movie)
    
    root.add(docs)
    root.add(vids)
    
    print(f"Root Directory Size: {root.get_size()} KB") # Expected: 2600
    print(f"Documents Size: {docs.get_size()} KB")      # Expected: 600
    print(f"Root Contents: {root.list_contents()}")      # ['documents', 'videos']
```

### Logic Walkthrough
1. **Initialization**: We define `FileSystemNode` as an abstract class. This ensures that every object in our system (whether a file or a folder) is guaranteed to have a `get_size()` method.
2. **Leaf Execution**: When `get_size()` is called on a `File`, it simply returns its own `size` attribute.
3. **Recursive Execution**: When `get_size()` is called on a `Directory`, it iterates through its `_children` list. If a child is a `File`, it returns the size. If a child is another `Directory`, the call triggers another `get_size()` call on that child. This continues until the base case (the leaf/File) is reached.
4. **Uniformity**: The `Directory.add()` method accepts a `FileSystemNode`. This means the directory doesn't care if it is adding a file or another folder.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| `add()` | $O(1)$ | $O(1)$ | Adding to a list is constant time. |
| `remove()` | $O(N)$ | $O(N)$ | Filtering a list requires visiting every child. |
| `getSize()` | $O(N)$ | $O(H)$ | $N$ = total nodes in the subtree; $H$ = height of tree (recursion stack). |
| `listContents()`| $O(K)$ | $O(K)$ | $K$ = number of immediate children in the folder. |

---

## 6. Real-World Applications

The Composite Pattern is ubiquitous in software engineering:
1. **GUI Frameworks**: In Android or iOS development, a `View` (like a Button) is a leaf, and a `ViewGroup` (like a LinearLayout) is a composite. Both inherit from a base `View` class, allowing the system to render the entire UI tree recursively.
2. **DOM (Document Object Model)**: In HTML, an `Element` can be a simple tag (like `<img>`) or a container (like `<div>`) that holds other elements.
3. **Organization Charts**: An `Employee` can be an individual contributor (Leaf) or a `Manager` (Composite) who manages a list of other employees.
4. **Compiler Design**: Abstract Syntax Trees (AST) use this pattern to represent expressions (e.g., a `BinaryExpression` node containing two other expression nodes).
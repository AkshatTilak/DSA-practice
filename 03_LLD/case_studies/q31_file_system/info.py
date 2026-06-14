INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design File System (Composite Pattern).',
    'groups': ['OOP Case Studies', 'Structural Patterns'],
    'readme_content': """# File System LLD (Composite Pattern)

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
        \"\"\"Return the size of the node in bytes/KB.\"\"\"
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
        \"\"\"
        Recursive logic: The size of a directory is the sum 
        of the sizes of all its children.
        \"\"\"
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
4. **Compiler Design**: Abstract Syntax Trees (AST) use this pattern to represent expressions (e.g., a `BinaryExpression` node containing two other expression nodes).""",
    'solutions': """# System Design Document: File System (Composite Pattern)

## 1. Requirements & System Constraints

The goal is to design a hierarchical file system that allows users to manage files and directories. The primary architectural requirement is the use of the **Composite Design Pattern** to treat individual files and directories uniformly.

### 1.1 Functional Requirements
*   **Hierarchical Structure**: Support a tree-like structure where a directory can contain both files and other directories.
*   **File Operations**: 
    *   Create a file.
    *   Delete a file.
    *   Get file size.
*   **Directory Operations**: 
    *   Create a directory.
    *   Delete a directory (recursive deletion).
    *   Add/Remove children (files or sub-directories).
    *   Calculate the total size of a directory (sum of all nested files).
    *   List all contents of a directory.
*   **Global Operations**:
    *   Search for a file by name across the hierarchy.
    *   Rename/Move items.

### 1.2 Non-Functional Requirements
*   **Extensibility**: Easy to add new types of nodes (e.g., Symbolic Links, Compressed Folders) without modifying existing client code.
*   **Consistency**: Ensuring that removing a directory also removes all its descendants to prevent "orphaned" nodes.
*   **Performance**: Efficient directory size calculation (potential for caching).

### 1.3 Constraints
*   The system should handle deeply nested directory structures.
*   Concurrency control is required if multiple users modify the same directory simultaneously.

---

## 2. High-Level Architecture

### 2.1 Design Pattern: The Composite Pattern
The Composite pattern is ideal here because it allows clients to ignore the difference between a "Leaf" (File) and a "Composite" (Directory). Both implement a common interface.

### 2.2 Component Diagram (Mermaid)

```mermaid
classDiagram
    class FileSystemNode {
        <<abstract>>
        - String name
        + getName() String
        + getSize() long
        + delete() void
        + rename(String newName) void
    }

    class File {
        - long size
        + getSize() long
        + delete() void
    }

    class Directory {
        - List~FileSystemNode~ children
        + add(FileSystemNode node) void
        + remove(FileSystemNode node) void
        + getSize() long
        + delete() void
        + listContents() List~String~
    }

    FileSystemNode <|-- File
    FileSystemNode <|-- Directory
    Directory "1" o-- "*" FileSystemNode : contains
```

### 2.3 Interaction Flow
1.  **Client** interacts with the `FileSystemNode` abstraction.
2.  If the node is a **File**, the operation (e.g., `getSize`) is performed directly.
3.  If the node is a **Directory**, the operation is delegated to its children recursively.
4.  The **File System Manager** acts as the orchestrator, maintaining the root directory and providing an API for the user.

---

## 3. Detailed Database Schema Design

While this is an LLD, persistence is required for a real-world system. A **Relational Database (SQL)** is preferred for metadata due to the need for ACID properties and structured relationships.

### 3.1 Table Design: `nodes`

We use the **Adjacency List Model** to represent the hierarchy.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique identifier for the node. |
| `parent_id` | UUID | FOREIGN KEY (nodes.id) | Reference to parent directory (NULL for root). |
| `name` | VARCHAR(255) | NOT NULL | Name of the file or folder. |
| `type` | ENUM | ('FILE', 'DIR') | Distinguishes between File and Directory. |
| `size` | BIGINT | DEFAULT 0 | Actual size for files; cached size for directories. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp. |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last modification timestamp. |

### 3.2 Indexing Strategy
*   **Index on `parent_id`**: Critical for `listContents()` operations (retrieving all children of a folder).
*   **Composite Index on `(parent_id, name)`**: Ensures that two files/folders cannot have the same name within the same directory (Uniqueness constraint).

### 3.3 SQL vs NoSQL Reasoning
*   **SQL (Chosen)**: Strong consistency is required. Moving a directory requires updating the `parent_id` of the root of the subtree, which is a simple atomic update in SQL.
*   **NoSQL**: A Document store (like MongoDB) could store the tree as a nested object, but this would lead to massive document sizes and performance degradation for deep hierarchies (reaching the 16MB BSON limit).

---

## 4. Core API Design

The API interacts with a `FileSystemService` which maps REST calls to the Composite object structure.

### 4.1 Endpoints

| Method | Endpoint | Request Payload | Response | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/nodes` | `{ "name": "str", "type": "FILE/DIR", "parentId": "uuid" }` | `201 Created` | Create a new file or folder. |
| `GET` | `/nodes/{id}` | N/A | `{ "name": "str", "size": 123, "type": "..." }` | Get metadata of a node. |
| `GET` | `/nodes/{id}/contents` | N/A | `[ { "id": "...", "name": "..." }, ... ]` | List children of a directory. |
| `DELETE` | `/nodes/{id}` | N/A | `204 No Content` | Delete a node and its descendants. |
| `PATCH` | `/nodes/{id}` | `{ "name": "newName" }` | `200 OK` | Rename a node. |
| `PUT` | `/nodes/{id}/move` | `{ "newParentId": "uuid" }` | `200 OK` | Move node to a different directory. |

### 4.2 Example Request/Response (List Contents)
**Request:** `GET /nodes/dir-123/contents`

**Response:**
```json
[
  {
    "id": "file-456",
    "name": "resume.pdf",
    "type": "FILE",
    "size": 102400
  },
  {
    "id": "dir-789",
    "name": "Photos",
    "type": "DIR",
    "size": 5048576
  }
]
```

---

## 5. Scalability & Advanced Topics

### 5.1 Caching Strategy
Calculating the size of a directory recursively is an $O(N)$ operation where $N$ is the total number of descendants.
*   **Write-Through Caching**: Store the `size` in the `nodes` table. When a file is created, updated, or deleted, propagate the size change upwards to all parent directories.
*   **LRU Cache**: Use an LRU cache to store the results of `listContents` for frequently accessed directories.

### 5.2 Concurrency Control
To prevent race conditions during directory moves or deletions:
*   **Optimistic Locking**: Use a `version` column in the `nodes` table. If the version changes between read and write, the operation fails.
*   **Pessimistic Locking**: Lock the subtree (from the root of the operation down) to ensure no other process modifies the structure during a move.

### 5.3 Fault Tolerance & Distributed Storage
If this system scales to petabytes:
*   **Metadata vs. Data**: Separate metadata (SQL DB) from actual file content (Object Store like AWS S3 or Azure Blob Storage). The `nodes` table would store a `blob_url`.
*   **Sharding**: Shard the metadata database by `root_folder_id` or `user_id` to distribute the load across multiple DB instances.

---

## 6. Trade-off Analysis

### 6.1 Composite Pattern Trade-offs
*   **Pro**: Uniformity. The client doesn't need to check `if (node instanceof Directory)` before calling `getSize()`.
*   **Con**: Type safety. If we add a method `addNode()` to the base `FileSystemNode` interface, the `File` class (Leaf) must provide a dummy implementation or throw an exception, violating the Interface Segregation Principle.

### 6.2 Storage Trade-offs (Latency vs. Storage)
*   **Pre-calculated Size**: We store the `size` for directories. 
    *   *Trade-off*: Increases write latency (must update all parents) but drastically reduces read latency for `getSize()`. Given that file systems are read-heavy, this is a preferred trade-off.

### 6.3 Consistency Model (CAP Theorem)
*   In a distributed file system, we prioritize **Consistency (C)** and **Partition Tolerance (P)**.
*   It is unacceptable for a user to delete a folder and then find some of its files still exist in a different view. Therefore, we use synchronous updates for metadata changes, accepting a slight hit in Availability (A) during network partitions.""",
}

INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Text Editor / Word Processor.',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Text Editor / Word Processor LLD

Designing a Text Editor is a classic Low-Level Design (LLD) challenge that tests a candidate's ability to handle **state management**, **efficient data structures**, and the implementation of **complex behavioral patterns** like Undo/Redo.

---

## 1. Overview & System Requirements

The goal is to design a system that mimics the core functionality of a professional text editor (like VS Code, Sublime Text, or MS Word). The system must handle text manipulation, cursor management, and a robust history mechanism.

### Functional Requirements
- **Text Manipulation**: 
    - Insert characters or strings at the current cursor position.
    - Delete characters (Backspace/Delete).
- **Cursor Management**: 
    - Move the cursor (Left, Right, Up, Down).
    - Track the current line and column.
- **History Management**: 
    - **Undo**: Revert the last action.
    - **Redo**: Re-apply the last undone action.
- **Document State**:
    - Ability to get the current full text of the document.

### Non-Functional Requirements
- **Efficiency**: Insertions and deletions should be performant even for large documents.
- **Extensibility**: New features (e.g., Bold, Italic, Find/Replace) should be addable without modifying core logic (**Open/Closed Principle**).
- **Consistency**: Undo/Redo must maintain the exact state of the document.

---

## 2. Design Principles & Patterns

To avoid a "God Class" where the Editor handles everything, we apply the following:

### Design Patterns
| Pattern | Application | Why? |
| :--- | :--- | :--- |
| **Command Pattern** | Every edit action (Insert, Delete) is encapsulated as an object. | Decouples the object that invokes the operation from the one that knows how to perform it. This is the industry standard for implementing **Undo/Redo**. |
| **Singleton Pattern** | The `TextEditor` instance. | Ensures only one instance of the editor manages the document state across the application. |
| **Composite Pattern** | For Formatting (Optional/Advanced). | Allows treating a single character and a block of formatted text uniformly. |
| **Strategy Pattern** | For Saving/Exporting. | Allows switching between different save formats (Plain Text, HTML, PDF) at runtime. |

### SOLID Principles Applied
- **Single Responsibility (SRP)**: `Document` manages data, `Cursor` manages position, `UndoManager` manages history, and `Editor` acts as the Facade.
- **Open/Closed (OCP)**: New commands (e.g., `ReplaceCommand`) can be added by extending the `Command` base class without changing the `UndoManager`.
- **Interface Segregation**: The `Command` interface is lean, requiring only `execute()` and `undo()`.

---

## 3. Class Structure & Relationships

### Data Structure Choice: The "Piece Table" vs "Gap Buffer"
In a production system, using a simple `String` or `List` is inefficient ($O(N)$ for inserts).
- **Gap Buffer**: Great for local edits (used in Emacs).
- **Rope**: A tree structure for very large files.
- **Piece Table**: Uses two buffers (Original and Append) and a table of pointers. This allows $O(1)$ insertions and effortless Undo/Redo. 
*For this LLD implementation, we will use a `List of Lines` approach for clarity, while simulating the Command pattern for state.*

### Class Diagram (ASCII)

```text
+----------------+          +-------------------+          +------------------+
|    Editor      | -------->|     Document      | <------- |      Cursor      |
| (Facade/Ctrl)  |          +-------------------+          +------------------+
+-------+--------+          | - content: List    |          | - row: int       |
        |                   | - get_text()       |          | - col: int       |
        |                   +-------------------+          +------------------+
        |                              ^
        |                              |
        v                              |
+----------------+          +-------------------+
|   UndoManager  | -------->|    <<Interface>>  |
| - undoStack     |          |      Command      |
| - redoStack     |          +-------------------+
+----------------+          | + execute()       |
                            | + undo()          |
                            +---------+---------+
                                      ^
                                      |
                      +---------------+---------------+
                      |                               |
            +-------------------+           +-------------------+
            |   InsertCommand   |           |   DeleteCommand   |
            +-------------------+           +-------------------+
```

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List

# --- Domain Entities ---

class Cursor:
    def __init__(self):
        self.row = 0
        self.col = 0

    def move_left(self):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            # Note: Actual col would depend on the length of the previous line
            self.col = 0 

    def move_right(self, line_len):
        if self.col < line_len:
            self.col += 1
        elif self.row < 0: # Simplified logic for brevity
            self.row += 1
            self.col = 0

    def __repr__(self):
        return f"Cursor(row={self.row}, col={self.col})"

class Document:
    def __init__(self):
        self.lines: List[List[str]] = [[]]  # Represent text as list of lines (list of chars)

    def insert(self, row, col, text):
        for char in text:
            self.lines[row].insert(col, char)
            col += 1

    def delete(self, row, col):
        if 0 <= row < len(self.lines) and 0 <= col < len(self.lines[row]):
            return self.lines[row].pop(col)
        return None

    def get_full_text(self):
        return "\n".join(["".join(line) for line in self.lines])

# --- Command Pattern Implementation ---

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class InsertCommand(Command):
    def __init__(self, document, cursor, text):
        self.doc = document
        self.cursor = cursor
        self.text = text
        self.row = cursor.row
        self.col = cursor.col

    def execute(self):
        self.doc.insert(self.row, self.col, self.text)
        self.cursor.col += len(self.text)

    def undo(self):
        # Delete the characters that were inserted
        for _ in range(len(self.text)):
            self.doc.delete(self.row, self.col)
        self.cursor.col -= len(self.text)

class DeleteCommand(Command):
    def __init__(self, document, cursor):
        self.doc = document
        self.cursor = cursor
        self.row = cursor.row
        self.col = cursor.col
        self.deleted_char = None

    def execute(self):
        self.deleted_char = self.doc.delete(self.row, self.col)
        self.cursor.col -= 1 if self.cursor.col > 0 else 0

    def undo(self):
        if self.deleted_char:
            self.doc.insert(self.row, self.col, self.deleted_char)
            self.cursor.col += 1

# --- Controller / Management ---

class UndoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def execute_command(self, command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear() # New action clears redo history

    def undo(self):
        if not self.undo_stack:
            print("Nothing to undo")
            return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self):
        if not self.redo_stack:
            print("Nothing to redo")
            return
        cmd = self.redo_stack.pop()
        cmd.execute()
        self.undo_stack.append(cmd)

class TextEditor:
    \"\"\"Facade class providing the API to the user\"\"\"
    def __init__(self):
        self.document = Document()
        self.cursor = Cursor()
        self.history = UndoManager()

    def type_text(self, text):
        cmd = InsertCommand(self.document, self.cursor, text)
        self.history.execute_command(cmd)

    def backspace(self):
        # Simplified backspace: delete char before cursor
        if self.cursor.col > 0:
            self.cursor.col -= 1
            cmd = DeleteCommand(self.document, self.cursor)
            self.history.execute_command(cmd)

    def undo(self):
        self.history.undo()

    def redo(self):
        self.history.redo()

    def show(self):
        print(f"Text:\n{self.document.get_full_text()}")
        print(f"Cursor: {self.cursor}")
        print("-" * 20)

# --- Testing the Implementation ---
if __name__ == "__main__":
    editor = TextEditor()
    
    editor.type_text("Hello")
    editor.show() # Hello, Cursor(0, 5)
    
    editor.type_text(" World")
    editor.show() # Hello World, Cursor(0, 11)
    
    editor.undo()
    editor.show() # Hello, Cursor(0, 5)
    
    editor.redo()
    editor.show() # Hello World, Cursor(0, 11)
    
    editor.backspace()
    editor.show() # Hello Worl, Cursor(0, 10)
```

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Insert** | $O(L)$ | $O(S)$ | $L$ = line length, $S$ = string size. |
| **Delete** | $O(L)$ | $O(1)$ | Popping from a list of characters. |
| **Undo** | $O(K)$ | $O(1)$ | $K$ = size of the operation being reverted. |
| **Redo** | $O(K)$ | $O(1)$ | Re-executing the command. |
| **Full Text**| $O(N)$ | $O(N)$ | Joining all lines into one string. |

---

## 5. Real-World Applications

1.  **IDEs (VS Code, IntelliJ)**: These use a **Piece Table** or **Rope** structure instead of a list of lines to ensure that adding a single character to a 100MB file doesn't freeze the UI.
2.  **Collaborative Editors (Google Docs)**: These use **Operational Transformation (OT)** or **CRDTs (Conflict-free Replicated Data Types)**. Instead of a simple Undo stack, they treat every edit as a "transformation" that is synchronized across users.
3.  **Version Control (Git)**: Git treats the entire file as a blob and uses "deltas" (diffs), which is conceptually similar to the Command pattern (storing only the change, not the whole file).
4.  **Graphics Software (Photoshop)**: The Command pattern is used extensively here to allow users to undo complex brush strokes or filter applications.""",
    'solutions': """# System Design Document: Professional Text Editor / Word Processor

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Core Editing:** Ability to insert, delete, and replace text at any cursor position.
*   **Rich Text Support:** Support for formatting (Bold, Italic, Underline, Font Size, Colors) and embedded objects (Images, Tables).
*   **Cursor Management:** Support for multiple cursors, text selection, and navigation.
*   **Undo/Redo:** Comprehensive history management to revert or re-apply changes.
*   **Document Persistence:** Ability to save, load, and version documents.
*   **Real-time Collaboration:** Multiple users editing the same document simultaneously with conflict resolution.
*   **Search & Replace:** Efficient searching and bulk replacement of text patterns.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** Local typing must be instantaneous (sub-10ms latency).
*   **High Availability:** The document service must be available for retrieval and editing.
*   **Strong Eventual Consistency:** In a collaborative environment, all users must eventually converge to the same document state.
*   **Scalability:** Support for documents ranging from a few KB to several MBs without performance degradation.
*   **Fault Tolerance:** Auto-save mechanisms to prevent data loss during crashes.

### 1.3 Scale Estimations
*   **Concurrency:** Support for 10,000+ concurrent users per document cluster.
*   **Document Size:** Up to 100MB per document.
*   **Operation Rate:** Hundreds of keystrokes per second per active user.

---

## 2. High-Level Architecture

The system follows a **Client-Server Architecture** with a heavy emphasis on the **Client-side Engine** to ensure zero-latency typing.

### 2.1 Core Components
1.  **Editor Engine (Client):** Manages the local representation of the document using an efficient data structure (Piece Table).
2.  **Rendering Engine (Client):** Converts the internal document model into a visual representation (DOM/Canvas).
3.  **Command Manager:** Implements the Command Pattern to handle Undo/Redo logic.
4.  **Collaboration Manager:** Handles synchronization between the client and server using **CRDTs (Conflict-free Replicated Data Types)** or **OT (Operational Transformation)**.
5.  **Document Service (Server):** Manages document metadata, permissions, and persistence.
6.  **Synchronization Service (Server):** A WebSocket-based service that broadcasts operations to collaborating peers.

### 2.2 Architecture Diagram

```mermaid
graph TD
    subgraph Client_Browser
        UI[UI Layer / Renderer] --> Engine[Editor Engine / Piece Table]
        Engine --> CmdMgr[Command Manager / Undo-Redo]
        Engine --> CollabMgr[Collaboration Manager / CRDT]
    end

    CollabMgr <-->|WebSockets / Protobuf| SyncSvc[Synchronization Service]
    
    subgraph Backend_Cloud
        SyncSvc --> DocSvc[Document Service]
        DocSvc --> MetaDB[(Metadata SQL DB)]
        DocSvc --> BlobStore[(Document Blob Store / S3)]
        SyncSvc --> Redis[(Op Log Cache / Redis)]
    end
```

---

## 3. Detailed Design

### 3.1 Internal Data Structure: The Piece Table
Standard strings or arrays are inefficient for large documents ($O(N)$ for insertions). We utilize a **Piece Table**.

*   **Original Buffer:** A read-only string containing the document as it was when opened.
*   **Add Buffer:** An append-only string containing all new text typed by the user.
*   **Piece Table:** A list of "Pieces" (descriptors). Each piece contains:
    *   `Buffer Source` (Original or Add)
    *   `Start Offset`
    *   `Length`

**Complexity:**
*   **Insertion:** $O(1)$ to append to Add Buffer, $O(P)$ to split a piece (where $P$ is the number of pieces, much smaller than $N$ characters).
*   **Deletion:** $O(P)$ to split and remove references to pieces.
*   **Undo/Redo:** Extremely efficient as the Original and Add buffers are never modified; only the Piece Table descriptors are rolled back.

### 3.2 Database Schema Design

We use a polyglot persistence approach: SQL for metadata and NoSQL/Blob for content.

#### Table: `Documents` (SQL - PostgreSQL)
Used for ownership, permissions, and metadata.
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `doc_id` | UUID | PK | Unique Document ID |
| `title` | VARCHAR(255) | NOT NULL | Document Title |
| `owner_id` | UUID | FK | Reference to User Table |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation date |
| `updated_at` | TIMESTAMP | INDEX | Last modification date |
| `version` | BIGINT | NOT NULL | Sequence number for OT/CRDT |

#### Table: `Document_Content` (Blob Store / S3)
Since a word processor document can be large and contains rich text/binary objects:
*   **Storage:** S3 or Google Cloud Storage.
*   **Format:** Compressed JSON or Protobuf representing the Piece Table state and metadata.
*   **Key:** `documents/{doc_id}/current_version.bin`

#### Table: `Operation_Log` (NoSQL - Cassandra/DynamoDB)
Used for real-time synchronization and version history.
| Field | Type | Index | Description |
| :--- | :--- | :--- | :--- |
| `doc_id` | UUID | Partition Key | Document ID |
| `seq_num` | BIGINT | Sort Key | Monotonically increasing version |
| `user_id` | UUID | - | Who made the change |
| `operation` | JSON/Binary | - | The actual delta (Insert/Delete/Format) |

---

## 4. Core API Design

### 4.1 REST APIs (Management)
**Create Document**
`POST /v1/documents`
*   Request: `{ "title": "Project Spec" }`
*   Response: `{ "doc_id": "uuid-123", "status": "created" }`

**Fetch Document**
`GET /v1/documents/{doc_id}`
*   Response: `{ "title": "...", "content_url": "s3://...", "version": 450 }`

### 4.2 WebSocket Events (Real-time)
To minimize overhead, we use **Protocol Buffers (Protobuf)** over WebSockets.

**Client $\rightarrow$ Server: `SEND_OP`**
```json
{
  "doc_id": "uuid-123",
  "seq_num": 451,
  "op": {
    "type": "INSERT",
    "position": 1024,
    "text": "Hello",
    "attributes": { "bold": true }
  },
  "user_id": "user-789"
}
```

**Server $\rightarrow$ Client: `BROADCAST_OP`**
The server validates the `seq_num`, applies the operation to the log, and broadcasts it to all other connected clients.

---

## 5. Scalability & Advanced Topics

### 5.1 Real-time Collaboration: CRDT vs OT
To handle concurrent edits without a central locking mechanism:
*   **Choice: CRDT (Conflict-free Replicated Data Types).** Specifically, a sequence CRDT like **LSEQ** or **Automerge**.
*   **Reasoning:** CRDTs are mathematically guaranteed to converge regardless of the order of operations received, making them superior for offline-first capabilities and peer-to-peer syncing.
*   **Mechanism:** Every character is assigned a unique, immutable identifier (a fractional index). Deleting a character marks it as a "tombstone" rather than shifting indices, avoiding the coordinate shift problem.

### 5.2 Rich Text Formatting (Composite Pattern)
To support varied content, the document model is treated as a tree:
*   **Root (Document)** $\rightarrow$ **Block (Paragraph/Table)** $\rightarrow$ **Inline (Text/Image)**.
*   Formatting is applied as "spans" (e.g., `Range(10, 20): {bold: true}`).

### 5.3 Caching & Performance
*   **Redis for Op-Logs:** The last $N$ operations of a document are cached in Redis to allow fast synchronization for users joining a session.
*   **Snapshotting:** Periodically, the server collapses the `Operation_Log` into a new base snapshot in S3 to prevent clients from having to replay millions of operations.
*   **Debounced Auto-save:** Client-side changes are buffered and flushed to the server every few seconds or upon idle.

---

## 6. Trade-off Analysis

| Trade-off | Selection | Justification |
| :--- | :--- | :--- |
| **Data Structure** | Piece Table vs Rope | Piece Table is chosen because it offers superior Undo/Redo performance by preserving the original file and all additions in append-only buffers. |
| **Sync Strategy** | CRDT vs OT | CRDT is chosen over OT for better support of asynchronous/offline editing and easier scaling (no need for a single central sequencer for all operations). |
| **Consistency** | Eventual vs Strong | Eventual Consistency is accepted for the content. Local updates are optimistic to ensure zero typing lag; the system converges in the background. |
| **Storage** | SQL vs NoSQL | Polyglot: SQL for relational metadata (who owns what) and NoSQL/Blob for the high-volume, unstructured operation logs and document bodies. |
| **Transport** | JSON vs Protobuf | Protobuf is used for WebSocket traffic to reduce payload size and serialization CPU overhead, critical for high-frequency keystroke events. |""",
}

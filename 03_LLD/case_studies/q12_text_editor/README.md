# Text Editor / Word Processor LLD

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
    """Facade class providing the API to the user"""
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
4.  **Graphics Software (Photoshop)**: The Command pattern is used extensively here to allow users to undo complex brush strokes or filter applications.
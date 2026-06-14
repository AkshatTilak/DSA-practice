# Undo-Redo Framework LLD

## 1. Overview & System Requirements
The **Undo-Redo Framework** is a classic Low-Level Design (LLD) challenge that focuses on managing the state of an application by recording actions. The primary goal is to allow users to reverse their previous actions (Undo) and re-apply actions that were previously undone (Redo).

The most efficient way to implement this is via the **Command Design Pattern**, which encapsulates a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

### Functional Requirements
- **Execute Action**: Perform a specific operation on a target object (Receiver).
- **Undo Action**: Reverse the most recently executed operation.
- **Redo Action**: Re-apply the most recently undone operation.
- **State Consistency**: Ensure that undoing and redoing maintains the integrity of the system's state.
- **History Management**: Maintain a history of actions (typically using stacks).

### Core Entities
- **Receiver**: The object that contains the actual business logic (e.g., a `Document` class).
- **Command**: An interface or abstract class that defines the `execute()` and `undo()` methods.
- **Concrete Command**: Specific implementations of the Command interface (e.g., `InsertTextCommand`).
- **Invoker (CommandManager)**: The entity that triggers the commands and maintains the undo/redo stacks.
- **Client**: The part of the application that creates the Command objects and associates them with the Receiver.

---

## 2. Design Principles & Patterns

### Design Patterns Applied
1. **Command Pattern (Behavioral)**: 
   - **Why**: It decouples the object that invokes the operation from the object that knows how to perform it. By turning a "request" into a stand-alone object, we can store it in a stack to facilitate undo/redo logic.
   - **Problem Solved**: Prevents the Invoker from needing to know the internal details of every possible operation in the system.

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: The `Document` (Receiver) handles data, the `Command` handles the operation logic, and the `CommandManager` (Invoker) handles history.
- **Open/Closed Principle (OCP)**: The system is open for extension. You can add new commands (e.g., `ChangeFontCommand`, `DeleteImageCommand`) without modifying the `CommandManager` or existing commands.
- **Liskov Substitution Principle (LSP)**: The `CommandManager` treats all commands as the base `Command` type, ensuring any concrete command can be executed or undone without breaking the system.
- **Dependency Inversion Principle (DIP)**: The `CommandManager` depends on the `Command` abstraction, not on concrete command implementations.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-----------------------+           +-----------------------+
|     CommandManager    |           |        Command        |
|-----------------------|           |-----------------------|
| - undoStack: Stack    |---------->| + execute(): void     |
| - redoStack: Stack    |           | + undo(): void        |
|-----------------------|           +-----------^-----------+
| + execute(cmd)        |                       |
| + undo()              |                       | (Inheritance)
| + redo()              |                       |
+-----------------------+           +-----------+-----------+
                                    |                       |
                          +-------------------+   +--------------------+
                          |  InsertTextCmd    |   |   DeleteTextCmd    |
                          |-------------------|   |--------------------|
                          | - receiver: Doc   |   | - receiver: Doc    |
                          | - text: String    |   | - deletedText: Str |
                          | - position: int   |   | - position: int    |
                          +-------------------+   +--------------------+
                                    |                       |
                                    +-----------+-----------+
                                                |
                                                v
                                    +-----------------------+
                                    |        Document       |
                                    |-----------------------|
                                    | - content: String     |
                                    |-----------------------|
                                    | + insert(pos, text)   |
                                    | + delete(pos, length) |
                                    | + getText(): String   |
                                    +-----------------------+
```

### Relationships
- **Composition**: `CommandManager` contains two stacks of `Command` objects.
- **Aggregation**: `ConcreteCommand` holds a reference to the `Document` (Receiver).
- **Inheritance**: All concrete actions inherit from the `Command` interface.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List

# --- Receiver ---
class Document:
    """The Receiver: Knows how to perform the actual operations."""
    def __init__(self):
        self.content = ""

    def insert(self, position: int, text: str):
        self.content = self.content[:position] + text + self.content[position:]
        print(f"Inserted '{text}' at {position}. Content: {self.content}")

    def delete(self, position: int, length: int):
        removed_text = self.content[position : position + length]
        self.content = self.content[:position] + self.content[position + length:]
        print(f"Deleted '{removed_text}' from {position}. Content: {self.content}")
        return removed_text

    def __str__(self):
        return self.content

# --- Command Interface ---
class Command(ABC):
    """The Command interface declares a method for executing an operation."""
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

# --- Concrete Commands ---
class InsertTextCommand(Command):
    def __init__(self, document: Document, text: str, position: int):
        self.document = document
        self.text = text
        self.position = position

    def execute(self):
        self.document.insert(self.position, self.text)

    def undo(self):
        # To undo an insertion, we delete the text we just added
        self.document.delete(self.position, len(self.text))

class DeleteTextCommand(Command):
    def __init__(self, document: Document, position: int, length: int):
        self.document = document
        self.position = position
        self.length = length
        self.deleted_text = ""

    def execute(self):
        # Save the text being deleted so we can restore it during undo
        self.deleted_text = self.document.delete(self.position, self.length)

    def undo(self):
        # To undo a deletion, we re-insert the saved text
        self.document.insert(self.position, self.deleted_text)

# --- Invoker ---
class CommandManager:
    """The Invoker: Manages the history of commands."""
    def __init__(self):
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute_command(self, command: Command):
        command.execute()
        self._undo_stack.append(command)
        # Clear redo stack whenever a new action is performed
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            print("Nothing to undo.")
            return
        
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        if not self._redo_stack:
            print("Nothing to redo.")
            return
        
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)

# --- Client Code ---
if __name__ == "__main__":
    doc = Document()
    manager = CommandManager()

    # Action 1: Insert "Hello "
    cmd1 = InsertTextCommand(doc, "Hello ", 0)
    manager.execute_command(cmd1)

    # Action 2: Insert "World"
    cmd2 = InsertTextCommand(doc, "World", 6)
    manager.execute_command(cmd2)

    # Action 3: Delete "Hello "
    cmd3 = DeleteTextCommand(doc, 0, 6)
    manager.execute_command(cmd3)

    print(f"Current State: {doc}") # Expected: World

    manager.undo() # Undoes delete "Hello " -> Expected: Hello World
    print(f"After Undo: {doc}")

    manager.undo() # Undoes insert "World" -> Expected: Hello 
    print(f"After Undo: {doc}")

    manager.redo() # Redoes insert "World" -> Expected: Hello World
    print(f"After Redo: {doc}")
```

### Logic Walkthrough
1.  **Execution**: When `manager.execute_command(cmd)` is called, the command's `execute()` method is triggered. The command object is then pushed onto the `undo_stack`. Crucially, the `redo_stack` is cleared because a new divergent timeline of actions has started.
2.  **Undo**: The `manager.undo()` pops the last command from the `undo_stack` and calls its `undo()` method. The command is then pushed to the `redo_stack` so it can be reapplied.
3.  **Redo**: The `manager.redo()` pops the last command from the `redo_stack`, calls `execute()` again, and pushes it back to the `undo_stack`.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| `execute_command` | $O(1)$ | $O(1)$ | Constant time to push to stack. |
| `undo` | $O(1)$ | $O(1)$ | Constant time to pop and push. |
| `redo` | $O(1)$ | $O(1)$ | Constant time to pop and push. |
| **Total History** | - | $O(N)$ | $N$ is the number of commands performed. |

*Note: The time complexity of the operation itself (e.g., string manipulation in `Document`) may vary, but the Command framework overhead is $O(1)$.*

---

## 6. Real-World Applications

- **Text Editors (MS Word, VS Code)**: Every keystroke or formatting change is wrapped in a command object.
- **Graphic Software (Adobe Photoshop, Figma)**: Complex operations like "Gaussian Blur" or "Layer Move" are stored as commands to allow multi-step reversals.
- **Database Transactions**: The **Write-Ahead Log (WAL)** acts similarly to a command history, allowing the database to "redo" committed transactions or "undo" uncommitted ones during recovery.
- **Web Browsers**: The Back and Forward buttons are essentially a Redo/Undo implementation for URL navigation history.
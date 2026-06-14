# Logger Framework LLD (Chain of Responsibility)

This study guide provides a comprehensive deep-dive into designing a **Logger Framework** using the **Chain of Responsibility (CoR)** behavioral design pattern. This pattern is quintessential for creating decoupled systems where a request can be passed along a chain of potential handlers.

---

## 1. Overview & System Requirements

### Core Objective
The goal is to build a logging system that can process log messages based on their **severity level**. Instead of using a massive `if-else` or `switch` block to determine where a message should go, the system delegates the responsibility to a chain of logger objects.

### Functional Requirements
- **Support Multiple Log Levels**: The system must support at least `INFO`, `DEBUG`, and `ERROR`.
- **Hierarchical Handling**: A message should be processed by the handler corresponding to its level. In many implementations, a high-severity message (e.g., ERROR) may also be processed by lower-severity handlers (e.g., INFO) to ensure comprehensive auditing.
- **Dynamic Chain Configuration**: The order of the loggers in the chain should be configurable at runtime.
- **Decoupling**: The client sending the log message should not need to know which specific logger handles the request.

### Actors
- **Client**: The application code that triggers a log event (e.g., `logger.log(LogLevel.ERROR, "Database connection failed")`).
- **Logger Handler**: The components responsible for writing the log to a specific destination (Console, File, Database).

---

## 2. Design Principles & Patterns

### The Chain of Responsibility Pattern
The **Chain of Responsibility** is a behavioral pattern that lets you pass requests along a chain of handlers. Upon receiving a request, each handler decides either to process the request or to pass it to the next handler in the chain.

**Why apply it here?**
- **Reduced Coupling**: The sender of the log doesn't need to know the internal logic of which logger handles which level.
- **Flexibility**: You can add, remove, or reorder loggers (e.g., adding a `SentryLogger` for production errors) without changing the client code.

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: Each concrete logger (e.g., `ErrorLogger`) is only responsible for one thing: handling logs of its specific severity.
- **Open/Closed Principle (OCP)**: The system is open for extension (we can add a `CriticalLogger` by extending the base class) but closed for modification (we don't need to change the `AbstractLogger` or existing handlers).
- **Dependency Inversion Principle (DIP)**: The client interacts with the `AbstractLogger` interface rather than concrete implementations.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
+------------------+
|    LogLevel      | <--- (Enum: INFO, DEBUG, ERROR)
+------------------+
         ^
         |
+-----------------------+
|    AbstractLogger     | <--- (Abstract Base Class)
+-----------------------+
| - next_logger: Logger |
+-----------------------+
| + set_next(logger)    |
| + log(level, message) |
+-----------------------+
         ^
         |
  ---------------------------------------
  |                  |                  |
+--------------+  +--------------+  +--------------+
|  InfoLogger  |  |  DebugLogger |  |  ErrorLogger |
+--------------+  +--------------+  +--------------+
| + write()    |  | + write()    |  | + write()    |
+--------------+  +--------------+  +--------------+
```

### Relationships
- **Inheritance**: `InfoLogger`, `DebugLogger`, and `ErrorLogger` inherit from `AbstractLogger`.
- **Composition/Association**: `AbstractLogger` maintains a reference to another `AbstractLogger` (the `next_logger`), forming a linked list structure.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from enum import IntEnum
from abc import ABC, abstractmethod

# 1. Define Log Levels
class LogLevel(IntEnum):
    INFO = 1
    DEBUG = 2
    ERROR = 3

# 2. Abstract Handler
class AbstractLogger(ABC):
    def __init__(self):
        self._next_logger = None

    def set_next(self, logger):
        self._next_logger = logger
        return logger  # Returning logger allows for chaining: l1.set_next(l2).set_next(l3)

    def log(self, level: LogLevel, message: str):
        # If this handler can handle the level, it writes the log
        if self._should_handle(level):
            self.write(message)
        
        # Pass the request to the next logger in the chain
        if self._next_logger:
            self._next_logger.log(level, message)

    @abstractmethod
    def _should_handle(self, level: LogLevel) -> bool:
        pass

    @abstractmethod
    def write(self, message: str):
        pass

# 3. Concrete Handlers
class InfoLogger(AbstractLogger):
    def _should_handle(self, level: LogLevel) -> bool:
        return level == LogLevel.INFO

    def write(self, message: str):
        print(f"[INFO]: {message}")

class DebugLogger(AbstractLogger):
    def _should_handle(self, level: LogLevel) -> bool:
        return level == LogLevel.DEBUG

    def write(self, message: str):
        print(f"[DEBUG]: {message}")

class ErrorLogger(AbstractLogger):
    def _should_handle(self, level: LogLevel) -> bool:
        return level == LogLevel.ERROR

    def write(self, message: str):
        print(f"[ERROR]: {message}")

# --- Client Code ---
if __name__ == "__main__":
    # Initialize loggers
    info = InfoLogger()
    debug = DebugLogger()
    error = ErrorLogger()

    # Build the chain: Info -> Debug -> Error
    info.set_next(debug).set_next(error)

    # Test cases
    print("Test 1: Logging INFO")
    info.log(LogLevel.INFO, "This is an informational message.") 
    
    print("\nTest 2: Logging ERROR")
    info.log(LogLevel.ERROR, "A critical system error occurred!") 
    
    print("\nTest 3: Logging DEBUG")
    info.log(LogLevel.DEBUG, "Debugging the variable x=10.")
```

### Logic Walkthrough
1.  **Chain Initialization**: We create three logger objects. By calling `info.set_next(debug).set_next(error)`, we create a pointer sequence: `InfoLogger` $\rightarrow$ `DebugLogger` $\rightarrow$ `ErrorLogger` $\rightarrow$ `None`.
2.  **Request Entry**: The client calls `info.log()`. The request always enters at the start of the chain.
3.  **The Processing Loop**:
    -   `InfoLogger` checks if the level is `INFO`. If yes, it prints. Regardless of whether it printed or not, it calls `self._next_logger.log()`.
    -   `DebugLogger` checks if the level is `DEBUG`. If yes, it prints. It then passes the request to the `ErrorLogger`.
    -   `ErrorLogger` checks if the level is `ERROR`. If yes, it prints. It then sees `_next_logger` is `None` and terminates the chain.
4.  **Result**: If `LogLevel.ERROR` is passed, only the `ErrorLogger` will execute its `write` method, but the request traveled through the entire chain.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Explanation |
| :--- | :--- | :--- | :--- |
| **Logging a Message** | $O(N)$ | $O(1)$ | $N$ is the number of handlers in the chain. We traverse the list once. |
| **Configuring Chain** | $O(1)$ | $O(N)$ | Setting the next pointer is constant time; storing the chain takes linear space. |

---

## 6. Real-World Applications

The Chain of Responsibility pattern is widely used in professional software engineering:

1.  **Java Servlet Filters**: In Java EE, `FilterChain` is used to process HTTP requests. Each filter (AuthFilter, LoggingFilter, CompressionFilter) decides whether to process the request and whether to pass it to the next filter in the chain.
2.  **GUI Event Bubbling**: In JavaScript/DOM events, an event (like a click) starts at the target element and "bubbles up" through its parents. Each parent has the chance to handle the event or let it propagate further up the DOM tree.
3.  **Middleware in Express.js/Django**: Web frameworks use middleware chains to handle requests. For example, a request passes through `BodyParser` $\rightarrow$ `SessionMiddleware` $\rightarrow$ `AuthMiddleware` $\rightarrow$ `RouteHandler`.
4.  **Spring Security**: The security filter chain in Spring evaluates a request against multiple security filters to determine if the user is authenticated and authorized before reaching the controller.
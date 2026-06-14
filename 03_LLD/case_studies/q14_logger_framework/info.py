INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design a Logger Framework (Chain of Responsibility).',
    'groups': ['OOP Case Studies', 'Behavioral Patterns'],
    'readme_content': """# Logger Framework LLD (Chain of Responsibility)

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
4.  **Spring Security**: The security filter chain in Spring evaluates a request against multiple security filters to determine if the user is authenticated and authorized before reaching the controller.""",
    'solutions': """# Design Document: Extensible Logger Framework

## 1. Requirements & System Constraints

The goal is to design a flexible, extensible logging framework that allows developers to log messages at various severity levels. The framework must employ the **Chain of Responsibility** pattern to ensure that log messages are handled by the appropriate sinks based on their severity.

### 1.1 Functional Requirements
*   **Log Levels**: Support standard log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `FATAL`.
*   **Pluggable Sinks**: Ability to route logs to different destinations (Console, File, Database, Remote API, Email/PagerDuty).
*   **Configurable Routing**: A specific log level should be handled by its corresponding logger and potentially passed down to loggers of higher severity (e.g., a `FATAL` log should likely be logged to the Console, written to a File, and sent via Email).
*   **Custom Formatting**: Support for customizable log formats (e.g., JSON, Plain Text).
*   **Asynchronous Processing**: Logging should not block the main application execution thread.

### 1.2 Non-Functional Requirements
*   **Low Latency**: The overhead added to the application's critical path must be minimal.
*   **Extensibility**: Adding a new logging sink (e.g., Slack integration) should require minimal code changes (Open/Closed Principle).
*   **Thread Safety**: The framework must be thread-safe to handle concurrent log requests from multiple application threads.
*   **Reliability**: Failure of a non-critical sink (e.g., a remote API timeout) should not crash the application.

---

## 2. High-Level Architecture

The system is designed as a library integrated into an application, which can optionally push logs to a centralized logging server.

### 2.1 Core Components
1.  **Logger Facade**: The entry point for the application. It hides the complexity of the chain from the client.
2.  **Log Message**: A Data Transfer Object (DTO) containing the message, timestamp, log level, and thread ID.
3.  **Abstract Log Handler**: The base class for the Chain of Responsibility. It defines the `setNext()` method and the `handle()` logic.
4.  **Concrete Handlers**: Specific implementations (e.g., `ConsoleLogger`, `FileLogger`, `RemoteLogger`) that process the log if the level matches.
5.  **Log Dispatcher (Async Buffer)**: An internal queue (e.g., Ring Buffer/LMAX Disruptor) that decouples the application thread from the I/O-heavy logging sinks.

### 2.2 Architecture Diagram

```mermaid
graph TD
    Client[Application Code] --> Facade[Logger Facade]
    Facade --> Queue[Async Log Queue/Buffer]
    Queue --> Chain[Chain of Responsibility]
    
    subgraph ChainOfResponsibility [Log Handler Chain]
        Chain --> DebugH[Debug Handler]
        DebugH --> InfoH[Info Handler]
        InfoH --> WarnH[Warn Handler]
        WarnH --> ErrorH[Error Handler]
        ErrorH --> FatalH[Fatal Handler]
    end
    
    DebugH --> Console[Console Sink]
    InfoH --> Console
    WarnH --> File[File Sink]
    ErrorH --> DB[Database/Remote Sink]
    FatalH --> Alert[Email/SMS Alert Sink]
```

---

## 3. Detailed Design

### 3.1 Class Design (LLD)
The core of the framework is the `AbstractLogger`.

*   **`LogLevel` (Enum)**: `DEBUG(1), INFO(2), WARNING(3), ERROR(4), FATAL(5)`.
*   **`LogMessage` (Class)**: Contains `timestamp`, `level`, `message`, `contextMap`.
*   **`AbstractLogger` (Abstract Class)**:
    *   `protected AbstractLogger nextLogger;`
    *   `public void setNext(AbstractLogger next)`
    *   `public void logMessage(LogLevel level, String msg)` $\rightarrow$ Checks if `level >= this.level`. If yes, calls `write()` and then calls `nextLogger.logMessage()`.

### 3.2 Database Schema Design (Centralized Logging Backend)
When logs are sent to a remote sink, they are stored in a time-series optimized database. For high-volume logs, **ClickHouse** or **Elasticsearch** is preferred over SQL.

**Table: `application_logs`**

| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `log_id` | UUID | PK | Unique identifier for the log entry |
| `timestamp` | DateTime64 | Indexed | Precision timestamp of the event |
| `level` | Enum/String | Indexed | DEBUG, INFO, etc. |
| `service_id` | String | Indexed | Identifier for the microservice |
| `trace_id` | String | Indexed | For distributed tracing (Correlation ID) |
| `message` | Text | - | The actual log message |
| `payload` | JSON/BSON | - | Structured context (e.g., user_id, request_params) |
| `host` | String | - | Server hostname where log originated |

**Indexing Strategy**:
*   **Partitioning**: Partition by `timestamp` (daily or monthly) to allow efficient TTL (Time-to-Live) deletion of old logs.
*   **Primary Key**: `(service_id, timestamp, level)` to optimize common queries (e.g., "Show me all ERRORs for Service A in the last hour").

---

## 4. Core API Design

### 4.1 Application Interface (Internal API)
```java
Logger logger = LoggerFactory.getLogger();
logger.info("User logged in", Map.of("userId", "123"));
logger.error("Database connection failed", exception);
```

### 4.2 Remote Ingestion API (External API)
If the framework pushes logs to a remote collector (like Logstash or a custom collector), the following REST/gRPC API is used:

**Endpoint**: `POST /v1/logs/ingest`

**Request Payload**:
```json
{
  "batch_id": "batch-998877",
  "logs": [
    {
      "timestamp": "2023-10-27T10:00:00.123Z",
      "level": "ERROR",
      "service_id": "payment-gateway",
      "trace_id": "a1-b2-c3-d4",
      "message": "Timeout connecting to Bank API",
      "payload": {
        "endpoint": "/v1/charge",
        "timeout_ms": 5000
      },
      "host": "pod-payment-01"
    }
  ]
}
```

**Response**:
```json
{
  "status": "success",
  "processed_count": 1
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Asynchronous Logging (The Performance Key)
To prevent the application from slowing down during I/O spikes, the framework implements an **Async Appender**:
*   **Internal Queue**: Use a `BlockingQueue` or a `RingBuffer` (LMAX Disruptor).
*   **Worker Thread**: A background daemon thread consumes the queue and traverses the Chain of Responsibility.
*   **Backpressure Strategy**: If the queue is full, the framework can either:
    *   *Drop logs* (preferable for DEBUG/INFO).
    *   *Block the caller* (preferable for FATAL).
    *   *Spill to a local temporary file*.

### 5.2 Log Aggregation & Distribution
*   **Batching**: Instead of sending one HTTP request per log, the `RemoteLogger` buffers logs and sends them in batches (e.g., every 5 seconds or 1000 logs).
*   **Compression**: Use GZip or Zstd compression for batch uploads to reduce network bandwidth.
*   **Sidecar Pattern**: In Kubernetes, the framework writes to `stdout` or a local file, and a sidecar container (like FluentBit) ships the logs to the backend.

### 5.3 Fault Tolerance
*   **Circuit Breaker**: If the Remote API is down, the `RemoteLogger` should open the circuit and fallback to local file logging to prevent memory buildup in the queue.
*   **Retry Logic**: Implement exponential backoff for transient network failures.

---

## 6. Trade-off Analysis

| Trade-off | Decision | Reasoning |
| :--- | :--- | :--- |
| **Sync vs Async** | **Asynchronous** | Logging is a cross-cutting concern; it should never be the bottleneck of the primary business logic. |
| **SQL vs NoSQL** | **NoSQL/TSDB** | Logs are write-heavy and read-infrequent. ClickHouse/Elasticsearch provide superior write throughput and full-text search compared to PostgreSQL/MySQL. |
| **Chain vs Map** | **Chain of Responsibility** | While a Map of handlers is faster ($O(1)$), the Chain allows for "cascading" logs (e.g., an Error is both logged to file AND sent to an alert system) without duplicating calls. |
| **Latency vs Reliability** | **Latency Priority** | In high-throughput systems, dropping a few DEBUG logs is acceptable to ensure the application remains responsive. |

### CAP Theorem Application
The logging backend prioritizes **Availability** and **Partition Tolerance** (AP). It is acceptable if a log entry takes a few seconds to appear in the dashboard (Eventual Consistency), but it is unacceptable for the ingestion API to reject logs because it is waiting for a global synchronous write across all replicas.""",
}

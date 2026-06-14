# Factory Method Design Pattern LLD

The **Factory Method** is a creational design pattern that provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created. It solves the problem of creating objects without specifying the exact class of object that will be created.

---

## 1. Overview & System Requirements

### Core Objective
The primary goal of the Factory Method is to decouple the **client code** (which uses the object) from the **concrete classes** (which implement the behavior). This ensures that the system is flexible and can introduce new product types without breaking existing code.

### System Requirements
- **Abstraction of Creation**: The system must be able to request an object of a certain "type" without knowing the specific class name.
- **Extensibility**: Adding a new product type should not require modifying the existing client logic (Open/Closed Principle).
- **Consistency**: All objects created by the factory must follow a common interface to ensure they are interchangeable.

### Actors
- **Product**: Defines the interface of objects the factory method creates.
- **Concrete Product**: The actual implementation of the Product interface.
- **Creator**: Declares the factory method, which returns an object of type Product.
- **Concrete Creator**: Overrides the factory method to return an instance of a Concrete Product.

---

## 2. Design Principles & Patterns

### SOLID Principles Applied
| Principle | Application in Factory Method |
| :--- | :--- |
| **Single Responsibility Principle (SRP)** | The creation logic is isolated in the Creator classes, separating it from the business logic of the Product. |
| **Open/Closed Principle (OCP)** | You can introduce new product types (extension) without changing the existing creator or client code (modification). |
| **Dependency Inversion Principle (DIP)** | The client depends on the `Product` abstraction rather than specific `ConcreteProduct` classes. |

### Design Coupling Problem Solved
Without the Factory Method, a developer would use the `new` keyword (or direct class instantiation in Python) throughout the codebase:
`notification = EmailNotification()` $\rightarrow$ **Tight Coupling**.

If the requirement changes to `SMSNotification`, every single line of instantiation must be found and changed. The Factory Method replaces this with:
`notification = factory.create_notification()` $\rightarrow$ **Loose Coupling**.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
       +-----------------+              +---------------------+
       |    Product      |<-------------|   ConcreteProduct A |
       | (Interface/ABC) |              | (e.g., EmailNotify)  |
       +-----------------+              +---------------------+
       | + operation()   |              | + operation()       |
       +-------^---------+              +---------------------+
               |
               | (Returns)
               |
       +-------+---------+              +---------------------+
       |     Creator     |<-------------|   ConcreteCreator A |
       |   (Abstract)    |              |  (e.g., EmailFact)  |
       +-----------------+              +---------------------+
       | + factory_method()|            | + factory_method()  |
       | + some_operation()|            |   returns Product A |
       +-------^---------+              +---------------------+
               |
               | (Inherits)
               |
       +-------+---------+
       | ConcreteCreator B|
       | (e.g., SMSFact)  |
       +------------------+
       | + factory_method()|
       |   returns Product B|
       +------------------+
```

### Relationships
- **Inheritance**: `ConcreteCreator` inherits from `Creator`.
- **Realization**: `ConcreteProduct` implements the `Product` interface.
- **Dependency**: `Creator` depends on the `Product` interface to return the object.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod

# 1. Product Interface
class Notification(ABC):
    @abstractmethod
    def notify(self, message: str):
        pass

# 2. Concrete Products
class EmailNotification(Notification):
    def notify(self, message: str):
        return f"Sending Email: {message}"

class SMSNotification(Notification):
    def notify(self, message: str):
        return f"Sending SMS: {message}"

# 3. Creator Abstract Class
class NotificationFactory(ABC):
    @abstractmethod
    def create_notification(self) -> Notification:
        """The Factory Method"""
        pass

    def send_notification(self, message: str):
        """
        Note: The Creator's primary responsibility isn't just creating.
        It often contains core business logic that relies on the Product.
        """
        notification = self.create_notification()
        return notification.notify(message)

# 4. Concrete Creators
class EmailFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return EmailNotification()

class SMSFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return SMSNotification()

# --- Execution ---
def solve():
    # The client code works with an instance of a concrete creator, 
    # although it may be unaware of the concrete class if it's passed as an interface.
    
    factories = [EmailFactory(), SMSFactory()]
    
    for factory in factories:
        print(factory.send_notification("Hello LLD World!"))

if __name__ == "__main__":
    solve()
```

### Logic Walkthrough
1. **Interface Definition**: We define `Notification` as an abstract base class (ABC). This ensures any notification type (Email, SMS, Slack) has a `.notify()` method.
2. **Product Implementation**: `EmailNotification` and `SMSNotification` provide the specific logic for sending messages.
3. **The Creator Logic**: `NotificationFactory` defines the `create_notification` method. Crucially, it also contains `send_notification`, which shows how the factory method is used within the creator to perform an action without knowing the product's concrete type.
4. **Specialization**: `EmailFactory` ensures that when `create_notification` is called, an `EmailNotification` object is returned.
5. **Client Execution**: The client iterates through various factories. The client doesn't care *how* the notification is sent or *which* class is instantiated; it only cares that the object conforms to the `Notification` interface.

### Complexity Analysis
| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| Object Creation | $O(1)$ | $O(1)$ | Creating a single instance is a constant time operation. |
| Extending System | $O(1)$ | $O(1)$ | Adding a new product requires creating two new classes but 0 changes to existing logic. |

---

## 5. Real-World Applications

### 1. Database Drivers (e.g., JDBC, SQLAlchemy)
Different databases (MySQL, PostgreSQL, Oracle) have different connection logic. A `DatabaseConnectionFactory` allows the application to switch between database engines by changing a configuration string without rewriting the data access layer.

### 2. UI Toolkits (e.g., Java Swing, Flutter)
A cross-platform UI library uses the Factory Method to render buttons. On Windows, the `ButtonFactory` returns a `WindowsButton`; on macOS, it returns a `MacButton`. The main application logic simply calls `factory.createButton()`.

### 3. Logging Frameworks
Logging can be sent to a Console, a File, or a Remote Server. A `LogFactory` creates the appropriate `Logger` implementation based on the environment (Development vs. Production).

### 4. Document Converters
A system that exports files to PDF, JSON, or XML. The `ExporterFactory` determines which converter to instantiate based on the user's selected file extension.
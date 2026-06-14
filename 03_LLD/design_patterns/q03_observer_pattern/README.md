# Observer Pattern LLD

The **Observer Pattern** is a behavioral design pattern that defines a one-to-many dependency between objects. When the state of one object (the **Subject**) changes, all its dependents (**Observers**) are notified and updated automatically. This pattern is the backbone of event-driven programming and the "Publish-Subscribe" mechanism.

---

## 1. Overview & System Requirements

### Core Concept
In a dynamic messaging engine, we often have a central source of truth (e.g., a News Feed, a Stock Ticker, or a System Event Logger) and multiple components that need to react to changes in that source. Instead of the observers constantly polling the subject for updates (which is inefficient), the subject "pushes" updates to the observers.

### Functional Requirements
- **Subscription Management**: The system must allow observers to register (subscribe) and unregister (unsubscribe) dynamically at runtime.
- **Automatic Notification**: Whenever a specific event occurs or state changes in the Subject, all registered observers must be notified.
- **Decoupling**: The Subject should not need to know the internal implementation details of the Observers; it should only know that they implement a specific interface.
- **Consistency**: All observers should receive the update signal to ensure their local state remains synchronized with the subject.

---

## 2. Design Principles & Patterns

### SOLID Principles Applied
- **Open/Closed Principle (OCP)**: The system is open for extension but closed for modification. You can introduce new types of observers (e.g., an `EmailNotificationObserver`, a `LoggingObserver`) without changing the `Subject` class code.
- **Single Responsibility Principle (SRP)**: The `Subject` is responsible only for managing the list of subscribers and broadcasting messages. The `Observer` is responsible only for defining how to react to those messages.
- **Dependency Inversion Principle (DIP)**: The `Subject` does not depend on concrete observer classes. Instead, it depends on the `Observer` abstract base class (interface), ensuring high-level modules are not coupled to low-level modules.

### Design Coupling Problem Solved
Without the Observer pattern, the Subject would need a hard-coded list of every object that needs an update. This creates **Tight Coupling**. If you added a new feature that required a notification, you would have to modify the Subject's core logic. The Observer pattern transforms this into **Loose Coupling**, where the Subject only knows that its observers possess an `update()` method.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
       +-------------------+             +-------------------+
       |      Subject      |             |     Observer      |
       +-------------------+             +-------------------+
       | - _observers: List| <---------- | + update(event)   |
       +-------------------+  (notifies) +-------------------+
       | + register(obs)   |                           ^
       | + unregister(obs) |                           |
       | + notify(event)   |                           |
       +-------------------+                           |
                ^                                      |
                | (inherits)                           | (implements)
       +-------------------+                  +-------------------------+
       |  ConcreteSubject  |                  |   ConcreteObserver A    |
       +-------------------+                  +-------------------------+
       | + state_change()  |                  | + update(event) { ... } |
       +-------------------+                  +-------------------------+
                                              |   ConcreteObserver B    |
                                              +-------------------------+
                                              | + update(event) { ... } |
                                              +-------------------------+
```

### Relationships
- **Association (One-to-Many)**: The `Subject` maintains a collection of `Observer` objects.
- **Inheritance/Interface**: Concrete Observers inherit from the `Observer` base class to guarantee the existence of the `update` method.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod

# 1. The Observer Interface
class Observer(ABC):
    @abstractmethod
    def update(self, event: str):
        """Method called by the subject to notify the observer of an event."""
        pass

# 2. The Subject (The "Publisher")
class Subject:
    def __init__(self):
        # Maintains a list of all subscribed observers
        self._observers = []

    def register(self, obs: Observer):
        """Adds an observer to the subscription list."""
        if obs not in self._observers:
            self._observers.append(obs)

    def unregister(self, obs: Observer):
        """Removes an observer from the subscription list."""
        try:
            self._observers.remove(obs)
        except ValueError:
            pass

    def notify(self, event: str):
        """Broadcasts the event to all registered observers."""
        for o in self._observers:
            o.update(event)

# 3. Concrete Observers (The "Subscribers")
class EmailNotificationService(Observer):
    def update(self, event: str):
        print(f"[Email Service] Sending email notification for event: {event}")

class SMSNotificationService(Observer):
    def update(self, event: str):
        print(f"[SMS Service] Sending text alert for event: {event}")

class LoggerService(Observer):
    def update(self, event: str):
        print(f"[Logger] Logging event to file: {event}")

# --- Execution Flow ---
if __name__ == "__main__":
    # Create the Subject (Messaging Engine)
    messaging_engine = Subject()

    # Instantiate Concrete Observers
    email_service = EmailNotificationService()
    sms_service = SMSNotificationService()
    logger_service = LoggerService()

    # Dynamic registration
    messaging_engine.register(email_service)
    messaging_engine.register(sms_service)
    messaging_engine.register(logger_service)

    print("--- First Event Triggered ---")
    messaging_engine.notify("User_Logged_In")

    # Dynamic unregistration
    messaging_engine.unregister(sms_service)

    print("\n--- Second Event Triggered (SMS unsubscribed) ---")
    messaging_engine.notify("Payment_Received")
```

### Logic Walkthrough
1. **Initialization**: We create a `Subject` instance which initializes an empty list `_observers`.
2. **Registration**: When `register(obs)` is called, the `Observer` object is added to the list. This allows the Subject to keep track of who needs to be notified.
3. **Triggering**: When a business event occurs (e.g., "Payment_Received"), the `notify(event)` method is invoked.
4. **Broadcasting**: The `notify` method iterates through the list of observers and calls the `update(event)` method on each.
5. **Reaction**: Each `ConcreteObserver` implements its own specific logic inside `update()`. The `EmailNotificationService` sends an email, while the `LoggerService` writes to a disk.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Description |
| :--- | :--- | :--- | :--- |
| **Register** | $O(1)$ or $O(N)$ | $O(1)$ | Adding to a list is $O(1)$, though checking for duplicates makes it $O(N)$. |
| **Unregister** | $O(N)$ | $O(1)$ | Searching for the object in the list to remove it takes linear time. |
| **Notify** | $O(N)$ | $O(1)$ | Must iterate through every registered observer to trigger the update. |
| **Overall Space** | - | $O(N)$ | Space scales linearly with the number of registered observers. |

---

## 6. Real-World Applications

### 1. GUI Frameworks (Event Listeners)
In Java Swing, JavaScript/React, or Android development, "EventListeners" are a direct implementation of the Observer pattern. A button (Subject) notifies all registered click-listeners (Observers) when it is pressed.

### 2. Model-View-Controller (MVC) Architecture
The **Model** acts as the Subject. When the data in the Model changes, it notifies the **View** (Observer) to re-render the UI, ensuring the user sees the most current data without the View having to poll the Model.

### 3. Distributed Systems (Pub/Sub)
While the classic Observer pattern is synchronous and happens within one memory space, systems like **Apache Kafka**, **RabbitMQ**, and **AWS SNS** are essentially distributed versions of this pattern. The "Topic" is the Subject, and the "Consumer Groups" are the Observers.

### 4. State Management Libraries
Libraries like **Redux** (JavaScript) or **Vuex** use this pattern. When the global state (Store) is updated, all connected components (Observers) are notified to re-render.
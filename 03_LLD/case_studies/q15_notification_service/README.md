# Notification Service LLD (Observer Pattern)

## 1. Overview & System Requirements
The **Notification Service** is a classic implementation of the **Observer Design Pattern**. Its primary goal is to create a decoupled system where a central event source (the Subject) can notify multiple disparate delivery channels (the Observers) whenever a specific event occurs, without the source needing to know the internal details of how each channel operates.

### Core Entities
- **Notification Service (Subject):** The central hub that manages subscriptions and triggers the notification process.
- **Notification Channel (Observer):** An abstract interface for any medium that can deliver a message.
- **Concrete Channels:** Specific implementations such as `EmailNotification`, `SMSNotification`, and `PushNotification`.
- **User/Client:** The entity that triggers a notification or manages their subscription preferences.

### Functional Requirements
- **Subscription Management:** Ability to add (subscribe) or remove (unsubscribe) notification channels dynamically at runtime.
- **Broadcasting:** When a notification is triggered, all currently subscribed channels must receive the message.
- **Extensibility:** Adding a new channel (e.g., Slack, WhatsApp) should not require modifying the core `NotificationService` logic.
- **Consistency:** Every observer should be notified of the event in a consistent manner via a standardized interface.

---

## 2. Design Principles & Patterns

### Design Patterns Applied
1. **Observer Pattern (Behavioral):** This is the core of the system. It establishes a one-to-many dependency between the `NotificationService` and various `NotificationChannels`. When the service's state changes (a notification is sent), all dependents are notified automatically.
2. **Strategy Pattern (Behavioral):** While the Observer pattern handles *who* gets notified, each concrete channel implements a different *strategy* for *how* the message is delivered.
3. **Interface Segregation / Dependency Inversion:** The `NotificationService` depends on the `NotificationObserver` abstraction rather than concrete classes like `EmailNotification`, ensuring high flexibility.

### SOLID Principles Implementation
- **Single Responsibility Principle (SRP):** The `NotificationService` is only responsible for managing observers and triggering updates. The concrete channel classes are only responsible for the delivery logic of their specific medium.
- **Open/Closed Principle (OCP):** The system is **open for extension** (we can add new notification channels) but **closed for modification** (we don't need to change the `NotificationService` code to support a new channel).
- **Liskov Substitution Principle (LSP):** Any concrete notification channel can be substituted for the `NotificationObserver` base class without breaking the system.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-------------------------+           +----------------------------+
|    NotificationService  |           |     NotificationObserver   |
|-------------------------|           |----------------------------|
| - observers: List       |           | + update(message: String)   |
|-------------------------|           +-------------^--------------+
| + attach(observer)      |                        |
| + detach(observer)      |         ________________|________________
| + notifyAll(message)    |        |                |                |
+------------+------------+        |                |                |
             |              +------+-------+ +------+-------+ +------+-------+
             |              | EmailChannel | |  SMSChannel  | | PushChannel  |
             |              +--------------+ +--------------+ +--------------+
             |              | + update()   | | + update()   | | + update()   |
             |              +--------------+ +--------------+ +--------------+
             |
             +---- (Maintains a list of NotificationObservers)
```

### Relationships
- **Composition:** `NotificationService` maintains a collection of `NotificationObserver` objects.
- **Inheritance/Realization:** `EmailChannel`, `SMSChannel`, and `PushChannel` inherit from/implement the `NotificationObserver` interface.
- **Association:** The client interacts with the `NotificationService` to trigger events.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List

# --- Observer Interface ---
class NotificationObserver(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """
    @abstractmethod
    def update(self, message: str) -> None:
        pass

# --- Concrete Observers ---
class EmailNotification(NotificationObserver):
    def update(self, message: str) -> None:
        print(f"Sending Email: {message}")

class SMSNotification(NotificationObserver):
    def update(self, message: str) -> None:
        print(f"Sending SMS: {message}")

class PushNotification(NotificationObserver):
    def update(self, message: str) -> None:
        print(f"Sending Push Notification: {message}")

# --- Subject ---
class NotificationService:
    """
    The Subject owns some important state and notifies observers when the state changes.
    """
    def __init__(self):
        # List to maintain all subscribed observers
        self._observers: List[NotificationObserver] = []

    def attach(self, observer: NotificationObserver) -> None:
        """Registers an observer to the notification list."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Attached {observer.__class__.__name__}")

    def detach(self, observer: NotificationObserver) -> None:
        """Removes an observer from the notification list."""
        try:
            self._observers.remove(observer)
            print(f"Detached {observer.__class__.__name__}")
        except ValueError:
            print("Observer not found in the list.")

    def notify_all(self, message: str) -> None:
        """Triggers the update method in all subscribed observers."""
        print(f"\nBroadcasting message: '{message}'")
        for observer in self._observers:
            observer.update(message)

# --- Client Code ---
if __name__ == "__main__":
    # Initialize the Subject
    notifier = NotificationService()

    # Create Concrete Observers
    email_chan = EmailNotification()
    sms_chan = SMSNotification()
    push_chan = PushNotification()

    # User subscribes to Email and SMS
    notifier.attach(email_chan)
    notifier.attach(sms_chan)

    # Trigger a notification
    notifier.notify_all("Welcome to the Platform!")

    # User decides to add Push notifications and remove SMS
    notifier.attach(push_chan)
    notifier.detach(sms_chan)

    # Trigger another notification
    notifier.notify_all("Your order has been shipped!")
```

### Logic Walkthrough
1. **Initialization:** We create a `NotificationService` instance. Internally, it holds an empty list `_observers`.
2. **Subscription (`attach`):** When we call `attach(email_chan)`, the `EmailNotification` object is added to the list. The service doesn't care that it is an "Email" channel; it only knows it is a `NotificationObserver`.
3. **Triggering (`notify_all`):** When `notify_all("message")` is invoked, the service loops through its `_observers` list.
4. **Execution (`update`):** For each observer in the list, the service calls `.update(message)`. The specific implementation of the `update` method in `EmailNotification` or `SMSNotification` determines how the message is delivered.
5. **Unsubscription (`detach`):** Removing an observer ensures that subsequent calls to `notify_all` will skip that specific channel.

---

## 5. Real-World Applications

The Observer Pattern and this specific Notification Service LLD are widely used in industry:

| Application Area | Implementation Example |
| :--- | :--- |
| **Event-Driven Architecture** | **Apache Kafka / RabbitMQ**: Producers send messages to a topic (Subject), and multiple consumers (Observers) subscribe to those topics. |
| **Frontend Frameworks** | **React/Vue State Management**: When a state (store) changes, all components observing that state are automatically re-rendered. |
| **UI Programming** | **GUI Event Listeners**: In Java Swing or JavaScript DOM, adding an `addEventListener` is an implementation of the Observer pattern. |
| **Cloud Services** | **AWS SNS (Simple Notification Service)**: A publisher sends a message to an SNS topic, which then fans out the message to SQS queues, Lambda functions, or Email endpoints. |

### Complexity Analysis
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| `attach()` | $O(1)$ | $O(1)$ | Appending to a list. |
| `detach()` | $O(N)$ | $O(1)$ | Searching for the observer in the list. |
| `notify_all()` | $O(N)$ | $O(1)$ | Iterating through all $N$ subscribed observers. |
| **Total Space** | $O(N)$ | - | Where $N$ is the number of active subscribers. |
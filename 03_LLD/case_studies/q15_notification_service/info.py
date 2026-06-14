INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Notification Service (Observer Pattern).',
    'groups': ['OOP Case Studies', 'Behavioral Patterns'],
    'readme_content': """# Notification Service LLD (Observer Pattern)

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
    \"\"\"
    The Observer interface declares the update method, used by subjects.
    \"\"\"
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
    \"\"\"
    The Subject owns some important state and notifies observers when the state changes.
    \"\"\"
    def __init__(self):
        # List to maintain all subscribed observers
        self._observers: List[NotificationObserver] = []

    def attach(self, observer: NotificationObserver) -> None:
        \"\"\"Registers an observer to the notification list.\"\"\"
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Attached {observer.__class__.__name__}")

    def detach(self, observer: NotificationObserver) -> None:
        \"\"\"Removes an observer from the notification list.\"\"\"
        try:
            self._observers.remove(observer)
            print(f"Detached {observer.__class__.__name__}")
        except ValueError:
            print("Observer not found in the list.")

    def notify_all(self, message: str) -> None:
        \"\"\"Triggers the update method in all subscribed observers.\"\"\"
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
| **Total Space** | $O(N)$ | - | Where $N$ is the number of active subscribers. |""",
    'solutions': """# System Design Document: Notification Service

## 1. Requirements & System Constraints

The Notification Service is a cross-cutting concern in a microservices architecture. Its primary goal is to decouple the business logic (Event Producers) from the delivery mechanism (Notification Channels).

### 1.1 Functional Requirements
*   **Multi-Channel Support:** Ability to send notifications via Email, SMS, and Push Notifications.
*   **Template Management:** Support for dynamic templates with placeholders (e.g., "Hello {{name}}, your order {{orderId}} has shipped").
*   **User Preferences:** Users must be able to opt-in or opt-out of specific notification types per channel.
*   **Priority Handling:** Support for different priorities (e.g., `HIGH` for OTPs, `LOW` for marketing).
*   **Delivery Tracking:** Ability to track the status of a notification (Sent, Delivered, Failed, Read).
*   **Pluggable Providers:** Ability to switch providers (e.g., moving from Twilio to MessageBird) without changing core business logic.

### 1.2 Non-Functional Requirements
*   **High Availability:** The service must be available to receive notification requests even if a specific downstream provider is down.
*   **Scalability:** Must handle bursts of traffic (e.g., a flash sale triggering millions of push notifications).
*   **Reliability (At-least-once Delivery):** Ensuring that critical notifications (like password resets) are eventually delivered.
*   **Low Latency:** Transactional notifications should be delivered within seconds.

### 1.3 Scale Estimations (Example)
*   **Daily Volume:** 100 million notifications/day.
*   **Average Throughput:** ~1,150 requests per second (RPS).
*   **Peak Throughput:** ~10,000+ RPS during marketing campaigns.
*   **Storage:** Notification logs for 30 days $\approx 100M \times 30 \times 500 \text{ bytes} \approx 1.5 \text{ TB}$.

---

## 2. High-Level Architecture

The system implements the **Observer Pattern** at a distributed scale. The "Subject" is the Notification Manager, and the "Observers" are the specific Channel Providers. Instead of in-memory observers, we use a Message Queue to achieve asynchronous decoupling.

### 2.1 Architecture Diagram

```mermaid
graph TD
    subgraph "Event Producers"
        OrderSvc[Order Service]
        AuthSvc[Auth Service]
        MktSvc[Marketing Service]
    end

    subgraph "Notification Core"
        API[Notification Gateway API]
        PrefSvc[Preference Service]
        TempSvc[Template Engine]
        NotifMgr[Notification Manager / Subject]
    end

    subgraph "Message Bus (Pub/Sub)"
        Queue[Message Queue - Kafka/RabbitMQ]
    end

    subgraph "Channel Observers"
        EmailWorker[Email Worker]
        SMSWorker[SMS Worker]
        PushWorker[Push Worker]
    end

    subgraph "Third Party Providers"
        SendGrid[SendGrid / SES]
        Twilio[Twilio / Nexmo]
        FCM[Firebase / APNs]
    end

    OrderSvc --> API
    AuthSvc --> API
    MktSvc --> API

    API --> PrefSvc
    API --> TempSvc
    API --> NotifMgr
    NotifMgr --> Queue

    Queue --> EmailWorker
    Queue --> SMSWorker
    Queue --> PushWorker

    EmailWorker --> SendGrid
    SMSWorker --> Twilio
    PushWorker --> FCM
```

### 2.2 Component Interactions
1.  **Gateway API:** Receives a request containing `userId`, `notificationType`, and `metadata`.
2.  **Preference Service:** Validates if the user has enabled the specific `notificationType` for the requested channels.
3.  **Template Engine:** Fetches the template associated with the `notificationType` and hydrates it with the provided `metadata`.
4.  **Notification Manager:** Acts as the Subject. It wraps the final payload into an event and publishes it to the Message Queue.
5.  **Channel Workers:** Act as Observers. They subscribe to specific topics/queues, pull the messages, and invoke the third-party provider APIs.

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection
*   **Relational DB (PostgreSQL):** Used for `UserPreferences` and `Templates`. These require strong consistency and complex querying.
*   **NoSQL DB (Cassandra or MongoDB):** Used for `NotificationLogs`. This table is write-heavy and grows linearly; a NoSQL store allows for better horizontal scaling and TTL (Time-to-Live) for old logs.

### 3.2 Schema

#### Table: `notification_templates` (SQL)
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `template_id` | UUID | PK | Unique identifier for the template |
| `type` | String | Index, Unique | e.g., `ORDER_CONFIRMATION` |
| `channel` | Enum | Index | `EMAIL`, `SMS`, `PUSH` |
| `content` | Text | - | Template string with placeholders |
| `subject` | String | - | Used primarily for Email |

#### Table: `user_preferences` (SQL)
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK, FK | Link to User Service |
| `type` | String | PK | Notification type |
| `channel` | Enum | PK | `EMAIL`, `SMS`, `PUSH` |
| `is_enabled` | Boolean | - | Opt-in/Opt-out status |

#### Table: `notification_logs` (NoSQL)
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `notification_id`| UUID | Partition Key | Unique delivery ID |
| `user_id` | UUID | Clustering Key | For querying user history |
| `channel` | String | - | Channel used |
| `status` | Enum | - | `QUEUED`, `SENT`, `DELIVERED`, `FAILED` |
| `retry_count` | Int | - | Number of attempts |
| `created_at` | Timestamp | Index | For cleanup/archiving |

---

## 4. Core API Design

### 4.1 Send Notification
`POST /v1/notifications/send`

**Request Payload:**
```json
{
  "userId": "u-12345",
  "notificationType": "ORDER_SHIPPED",
  "priority": "MEDIUM",
  "metadata": {
    "customerName": "John Doe",
    "orderId": "ORD-9988",
    "trackingUrl": "https://ship.it/123"
  },
  "overrideChannels": ["EMAIL", "PUSH"] 
}
```

**Response Payload:**
```json
{
  "notificationId": "notif-abc-123",
  "status": "ACCEPTED",
  "estimatedDelivery": "2023-10-27T10:00:05Z"
}
```

### 4.2 Update Preferences
`PATCH /v1/preferences`

**Request Payload:**
```json
{
  "userId": "u-12345",
  "preferences": [
    { "type": "MARKETING", "channel": "EMAIL", "enabled": false },
    { "type": "TRANSACTIONAL", "channel": "SMS", "enabled": true }
  ]
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Asynchronous Processing & Buffering
To prevent the system from crashing during traffic spikes, we use a **Message Queue (Kafka)**.
*   **Topic Partitioning:** Separate topics for `Email`, `SMS`, and `Push` to ensure a bottleneck in the SMS provider doesn't delay Email delivery.
*   **Consumer Groups:** Scale workers horizontally based on the lag in each queue.

### 5.2 Rate Limiting & Throttling
*   **Provider Limits:** Third-party APIs (like Twilio) have strict rate limits. We implement a **Token Bucket** algorithm at the Worker level to throttle requests.
*   **User-level Throttling:** To prevent spamming users, we track the number of notifications sent to a specific `userId` within a sliding window.

### 5.3 Reliability & Fault Tolerance
*   **Exponential Backoff:** If a provider returns a $5xx$ error, the worker retries with increasing delays ($2^n$).
*   **Dead Letter Queue (DLQ):** If a notification fails after $X$ retries, it is moved to a DLQ for manual inspection or alerting.
*   **Idempotency:** Each request is assigned a `notificationId`. Workers check a distributed cache (Redis) to ensure the same ID isn't processed twice.

### 5.4 Caching Strategy
*   **Template Cache:** Templates are cached in Redis as they change infrequently.
*   **Preference Cache:** User preferences are cached with a short TTL to avoid hitting the SQL DB for every single notification.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem
The Notification Service prioritizes **Availability** and **Partition Tolerance (AP)**. 
*   It is acceptable if a "Notification Read" status is eventually consistent.
*   It is NOT acceptable for the system to stop accepting notifications because the log database is momentarily unavailable.

### 6.2 Latency vs. Durability
By introducing a Message Queue, we trade off **immediate confirmation** (the API returns "Accepted", not "Delivered") for **durability and system stability**. The producer doesn't wait for the actual network call to the third-party provider, significantly reducing API latency.

### 6.3 SQL vs. NoSQL for Logs
We chose NoSQL for logs because the volume of data is massive and the access pattern is primarily write-heavy or range-scans by `userId`. Using a relational database for logs would lead to massive index overhead and expensive vacuuming/maintenance operations.""",
}

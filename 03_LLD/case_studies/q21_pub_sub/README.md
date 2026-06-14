# Pub-Sub System LLD

The **Publish-Subscribe (Pub-Sub)** pattern is a messaging pattern where senders (publishers) do not program the messages to be sent directly to specific receivers (subscribers). Instead, messages are categorized into **topics**, and subscribers express interest in one or more topics. This creates a highly decoupled architecture where the publisher has no knowledge of who the subscribers are or how many exist.

---

## 1. Overview & System Requirements

### Core Entities
- **Publisher**: The entity that generates data or events and sends them to the broker.
- **Subscriber**: The entity that registers interest in a specific topic and consumes messages.
- **Topic**: A logical channel or category used to route messages.
- **Broker (Event Bus)**: The central orchestrator that manages subscriptions and routes messages from publishers to the correct subscribers.
- **Message**: The data packet containing the payload and metadata.

### Functional Requirements
- **Subscribe**: A subscriber should be able to register for a specific topic.
- **Unsubscribe**: A subscriber should be able to remove themselves from a topic.
- **Publish**: A publisher should be able to send a message to a topic, which is then delivered to all active subscribers of that topic.
- **Decoupling**: Publishers should not have any direct reference to subscribers.
- **Concurrency**: The system must handle multiple publishers and subscribers safely in a multi-threaded environment.

### Non-Functional Requirements
- **Scalability**: The system should handle a large number of topics and subscribers.
- **Low Latency**: Message delivery should be as fast as possible.
- **Reliability**: Messages should be delivered to all registered subscribers without loss (in-memory implementation).

---

## 2. Design Principles & Patterns

### Design Patterns Applied
| Pattern | Application | Why? |
| :--- | :--- | :--- |
| **Observer Pattern** | The core of Pub-Sub. Subscribers "observe" topics. | To implement a one-to-many dependency where state changes (new messages) are notified automatically. |
| **Singleton Pattern** | Applied to the `PubSubBroker`. | Ensures there is one single point of truth for all subscriptions and message routing across the application. |
| **Interface Segregation** | The `Subscriber` interface. | Allows the broker to interact with any object that implements the `update` method, regardless of its concrete class (e.g., EmailSubscriber, LoggerSubscriber). |

### SOLID Principles
- **Single Responsibility Principle (SRP)**: The `PubSubBroker` only handles routing; the `Subscriber` only handles processing the message; the `Message` only carries data.
- **Open/Closed Principle**: We can add new types of `Subscribers` (e.g., a DatabaseSubscriber) without modifying the `PubSubBroker` code.
- **Dependency Inversion**: The Broker depends on the `Subscriber` abstraction, not on concrete subscriber implementations.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-------------------+           +-----------------------+
|     Publisher     |           |      PubSubBroker     |
+-------------------+           +-----------------------+
| + publish(topic,  |---------->| - subscriptions: Map  |
|   message)        |           | - lock: Lock          |
+-------------------+           +-----------------------+
                                | + subscribe(topic, sub)|
                                | + unsubscribe(topic, s)|
                                | + publish(topic, msg)  |
                                +-----------+-----------+
                                            |
                                            | (notifies)
                                            v
                                +-----------------------+
                                |      <<Interface>>    |
                                |       Subscriber      |
                                +-----------------------+
                                | + update(message)     |
                                +-----------+-----------+
                                            ^
                                            |
                    +-----------------------+-----------------------+
                    |                       |                       |
          +-------------------+   +-------------------+   +-------------------+
          |  EmailSubscriber  |   |  SmsSubscriber    |   |  LogSubscriber    |
          +-------------------+   +-------------------+   +-------------------+
          | + update(message) |   | + update(message)  |   | + update(message)  |
          +-------------------+   +-------------------+   +-------------------+
```

### Relationships
- **Composition**: The `PubSubBroker` contains a mapping of topics to a list of `Subscriber` objects.
- **Implementation**: `EmailSubscriber`, `SmsSubscriber`, etc., implement the `Subscriber` interface.
- **Association**: `Publisher` uses the `PubSubBroker` to send messages.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from threading import Lock
from collections import defaultdict
from typing import List, Dict

# 1. Message Entity
class Message:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return f"Message content: {self.content}"

# 2. Subscriber Interface (Abstraction)
class Subscriber(ABC):
    @abstractmethod
    def update(self, message: Message):
        pass

# 3. Concrete Subscribers
class EmailSubscriber(Subscriber):
    def __init__(self, email: str):
        self.email = email

    def update(self, message: Message):
        print(f"[Email to {self.email}] Received: {message.content}")

class SmsSubscriber(Subscriber):
    def __init__(self, phone: str):
        self.phone = phone

    def update(self, message: Message):
        print(f"[SMS to {self.phone}] Received: {message.content}")

# 4. PubSub Broker (Singleton)
class PubSubBroker:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        # Thread-safe Singleton implementation
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PubSubBroker, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Map of topic_name -> List of Subscriber objects
        self.subscriptions: Dict[str, List[Subscriber]] = defaultdict(list)
        self.broker_lock = Lock()

    def subscribe(self, topic: str, subscriber: Subscriber):
        with self.broker_lock:
            if subscriber not in self.subscriptions[topic]:
                self.subscriptions[topic].append(subscriber)
                print(f"System: Subscriber added to topic '{topic}'")

    def unsubscribe(self, topic: str, subscriber: Subscriber):
        with self.broker_lock:
            if subscriber in self.subscriptions[topic]:
                self.subscriptions[topic].remove(subscriber)
                print(f"System: Subscriber removed from topic '{topic}'")

    def publish(self, topic: str, message: Message):
        with self.broker_lock:
            subscribers = self.subscriptions.get(topic, [])
            if not subscribers:
                print(f"System: No subscribers for topic '{topic}'. Message dropped.")
                return
            
            # Notify all subscribers of the specific topic
            for subscriber in subscribers:
                subscriber.update(message)

# 5. Publisher Entity
class Publisher:
    def __init__(self, name: str):
        self.name = name
        self.broker = PubSubBroker()

    def send(self, topic: str, content: str):
        print(f"Publisher {self.name} publishing to '{topic}': {content}")
        message = Message(content)
        self.broker.publish(topic, message)

# --- Test Drive ---
if __name__ == "__main__":
    # Setup Broker and Publisher
    pub_news = Publisher("NewsAgency")
    pub_weather = Publisher("WeatherStation")

    # Setup Subscribers
    user1 = EmailSubscriber("alice@example.com")
    user2 = SmsSubscriber("+123456789")
    user3 = EmailSubscriber("bob@example.com")

    broker = PubSubBroker()

    # Alice wants News and Weather
    broker.subscribe("news", user1)
    broker.subscribe("weather", user1)
    
    # Bob wants only News
    broker.subscribe("news", user3)
    
    # User2 wants only Weather
    broker.subscribe("weather", user2)

    # Publish events
    pub_news.send("news", "Breaking: LLD Study Guide released!")
    print("-" * 30)
    pub_weather.send("weather", "Warning: Heavy Rain expected tomorrow.")
    print("-" * 30)

    # Bob unsubscribes from news
    broker.unsubscribe("news", user3)
    
    pub_news.send("news", "Update: Study Guide is now free!")
```

### Logic Walkthrough

1.  **The Broker's Map**: The `PubSubBroker` maintains a dictionary where keys are topic names and values are lists of `Subscriber` objects.
2.  **The Subscription Process**: When `subscribe("news", user1)` is called, `user1` (an object implementing the `Subscriber` interface) is appended to the `news` list in the dictionary.
3.  **The Publishing Process**:
    *   The `Publisher` calls `broker.publish(topic, message)`.
    *   The Broker looks up the list of subscribers for that specific topic.
    *   The Broker iterates through the list and calls the `update()` method on each subscriber.
4.  **Thread Safety**: 
    *   `_lock` in `__new__` ensures the Singleton is created only once even if multiple threads try to instantiate the broker.
    *   `broker_lock` ensures that adding/removing subscribers doesn't conflict with the publishing process (preventing `RuntimeError: dictionary changed size during iteration`).

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Subscribe** | $O(1)$ | $O(1)$ | Adding to a list in a map. |
| **Unsubscribe** | $O(N)$ | $O(1)$ | $N$ = number of subscribers in a specific topic. |
| **Publish** | $O(M)$ | $O(1)$ | $M$ = number of subscribers for the target topic. |
| **Overall Space** | - | $O(T \times S)$ | $T$ = topics, $S$ = avg subscribers per topic. |

---

## 5. Real-World Applications

This LLD pattern is the foundational logic for many industry-standard messaging systems:

1.  **Apache Kafka**: Uses a distributed commit log. Producers publish to "topics," and Consumer Groups subscribe to those topics. Kafka allows multiple consumers to read the same message at their own pace.
2.  **Redis Pub/Sub**: A lightweight implementation often used for real-time chat applications or signaling services where messages are fire-and-forget.
3.  **RabbitMQ (Exchange/Queue)**: Implements a more complex version where "Exchanges" act as the broker, routing messages to specific queues based on routing keys (similar to topics).
4.  **AWS SNS (Simple Notification Service)**: A managed Pub-Sub service that can push messages to HTTP endpoints, SQS queues, SMS, and Email.
5.  **Frontend Frameworks**: Redux or Vuex use a similar "Store" pattern where components subscribe to state changes and are notified when the state (topic) is updated.
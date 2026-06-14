INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Pub-Sub System.',
    'groups': ['OOP Case Studies', 'Messaging'],
    'readme_content': """# Pub-Sub System LLD

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
5.  **Frontend Frameworks**: Redux or Vuex use a similar "Store" pattern where components subscribe to state changes and are notified when the state (topic) is updated.""",
    'solutions': """# System Design Document: Distributed Pub-Sub System

## 1. Requirements & System Constraints

The goal is to design a highly scalable, fault-tolerant Publish-Subscribe (Pub-Sub) system that allows publishers to send messages to topics and subscribers to receive messages from those topics without knowing the publishers.

### 1.1 Functional Requirements
- **Topic Management**: Ability to create, update, and delete topics.
- **Publishing**: Publishers can send messages to a specific topic.
- **Subscription**: Subscribers can register interest in one or more topics.
- **Message Delivery**: 
    - **Push Model**: System pushes messages to subscribers (e.g., via Webhooks or WebSockets).
    - **Pull Model**: Subscribers poll the system for new messages (e.g., using an offset).
- **Persistence**: Messages must be persisted for a configurable retention period.
- **Filtering**: (Optional/Advanced) Ability to subscribe to a subset of messages within a topic based on attributes.

### 1.2 Non-Functional Requirements
- **High Throughput**: Support millions of messages per second.
- **Low Latency**: End-to-end latency (publish to receive) should be in the millisecond range.
- **Scalability**: Horizontal scaling of brokers and metadata stores.
- **Durability**: Messages should not be lost once acknowledged by the system.
- **Availability**: High availability ensuring the system remains operational despite node failures.

### 1.3 Scale Estimations (HLD Context)
- **Throughput**: $10^6$ messages/sec.
- **Fan-out**: Average 100 subscribers per topic; Max 10,000.
- **Storage**: If average message size is 1KB and retention is 7 days $\rightarrow$ $10^6 \times 86400 \times 7 \times 1\text{KB} \approx 600\text{TB}$ of storage.
- **Read/Write Ratio**: Write-heavy at the broker level, Read-heavy at the delivery level.

---

## 2. High-Level Architecture

The system follows a decoupled architecture where the **Broker** acts as the intermediary.

### 2.1 Core Components
1. **API Gateway / Load Balancer**: Routes requests to the appropriate service and handles authentication/rate limiting.
2. **Topic Manager (Control Plane)**: Manages topic metadata, partition assignments, and subscription lists.
3. **Message Broker (Data Plane)**:
    - **Ingestion Engine**: Receives messages from publishers and appends them to a commit log.
    - **Storage Engine**: Manages the physical persistence of messages on disk.
4. **Subscription Manager**: Tracks the "offset" or "cursor" for every subscriber for every topic.
5. **Delivery Service**: Handles the logic of pushing messages to subscribers or serving pull requests.

### 2.2 Architecture Diagram

```mermaid
graph TD
    Pub[Publisher] --> LB[Load Balancer]
    LB --> API[API Gateway]
    API --> TM[Topic Manager]
    API --> Broker[Message Broker Cluster]
    
    subgraph "Broker Node"
        B_Log[Append-only Log]
        B_Cache[Page Cache]
    end
    
    Broker --> B_Log
    B_Log --> B_Cache
    
    Broker --> SM[Subscription Manager]
    SM --> DS[Delivery Service]
    
    DS --> Sub1[Subscriber A]
    DS --> Sub2[Subscriber B]
    
    TM --> MetaDB[(Metadata DB - SQL)]
    SM --> OffsetDB[(Offset Store - NoSQL)]
```

---

## 3. Detailed Database Schema Design

The system utilizes two distinct storage layers: one for metadata (configuration) and one for the message stream (data).

### 3.1 Metadata Store (SQL - e.g., PostgreSQL)
Used for configuration where strong consistency is required.

**Table: `topics`**
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `topic_id` | UUID | PK | Unique identifier for the topic |
| `name` | String | Unique, Indexed | Human-readable name |
| `partition_count`| Int | Not Null | Number of shards for the topic |
| `retention_ms` | BigInt | Not Null | How long to keep messages |
| `created_at` | Timestamp | Not Null | Creation time |

**Table: `subscriptions`**
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `sub_id` | UUID | PK | Unique subscription ID |
| `topic_id` | UUID | FK $\rightarrow$ topics | Topic being subscribed to |
| `subscriber_id` | String | Indexed | Unique ID of the consumer |
| `delivery_mode` | Enum | Push/Pull | Method of delivery |
| `created_at` | Timestamp | Not Null | Subscription start time |

### 3.2 Message Store (Distributed Commit Log)
Messages are not stored in a traditional relational database. They are stored in **append-only segments** on disk to maximize sequential I/O.

**Log Format (Physical)**:
- **Segment File**: Each partition is split into segments (e.g., 1GB each).
- **Message Record**: `[Offset (8 bytes)][Timestamp (8 bytes)][Payload Size (4 bytes)][Payload (N bytes)][Checksum (4 bytes)]`.

### 3.3 Offset Store (NoSQL - e.g., Cassandra or Redis)
Used to track the current position of each subscriber.

**Key-Value Schema**:
- **Key**: `topic_id : subscriber_group_id : partition_id`
- **Value**: `offset_integer`
- **Reasoning**: Extremely high write volume as offsets are updated frequently. NoSQL provides the required linear scalability and low latency.

---

## 4. Core API Design

### 4.1 Topic Management
`POST /v1/topics`
- **Request**: `{"name": "user-signups", "partitions": 3, "retention_ms": 604800000}`
- **Response**: `201 Created { "topic_id": "..." }`

### 4.2 Publishing Messages
`POST /v1/publish`
- **Request**: 
  ```json
  {
    "topic": "user-signups",
    "payload": { "user_id": "123", "email": "test@example.com" },
    "partition_key": "user_123" 
  }
  ```
- **Response**: `202 Accepted { "offset": 1024, "partition": 1 }`

### 4.3 Subscription
`POST /v1/subscriptions`
- **Request**:
  ```json
  {
    "topic": "user-signups",
    "subscriber_id": "email-service-1",
    "mode": "pull",
    "endpoint": "https://email-service/webhook" 
  }
  ```
- **Response**: `201 Created { "sub_id": "..." }`

### 4.4 Consuming Messages (Pull Model)
`GET /v1/messages?topic=user-signups&subscriber_id=email-service-1&offset=1024&limit=100`
- **Response**: 
  ```json
  {
    "messages": [
      { "offset": 1024, "payload": { ... }, "timestamp": "..." },
      ...
    ],
    "next_offset": 1124
  }
  ```

---

## 5. Scalability & Advanced Topics

### 5.1 Partitioning & Sharding
To avoid a single broker becoming a bottleneck, topics are split into **partitions**.
- **Partitioning Strategy**: 
    - **Round Robin**: Even distribution.
    - **Key-based Hashing**: `hash(partition_key) % num_partitions`. Ensures all messages for a specific entity (e.g., `user_id`) go to the same partition, maintaining strict ordering per key.

### 5.2 Replication & Fault Tolerance
- **Leader-Follower Model**: Each partition has one leader and multiple followers.
- **ISR (In-Sync Replicas)**: A message is considered "committed" only after it is written to the leader and a quorum of ISRs.
- **Failover**: If the leader fails, the Topic Manager triggers an election to promote the most up-to-date follower.

### 5.3 Delivery Guarantees
- **At-most-once**: Message is sent; subscriber acknowledges before processing. (Fastest, data loss possible).
- **At-least-once**: Subscriber acknowledges *after* successful processing. (No data loss, duplicates possible).
- **Exactly-once**: Achieved via **Idempotent Producers** (Sequence IDs) and **Atomic Transactions** (updating offset and processing result in one transaction).

### 5.4 Performance Optimizations
- **Zero-Copy (sendfile)**: Instead of copying data from kernel space $\rightarrow$ user space $\rightarrow$ kernel space (socket), the broker uses the `sendfile` system call to move data directly from the disk cache to the NIC.
- **Batching**: Publishers batch messages to reduce the number of network requests.
- **Page Cache**: Leveraging the OS page cache for frequently read "tail" of the log.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem
The system is designed as an **AP (Availability and Partition Tolerance)** system for the data plane.
- **Availability**: In the event of a network partition, we allow reads/writes to available replicas to ensure the system doesn't halt.
- **Consistency**: We accept **Eventual Consistency** for followers. While the leader is strictly consistent, followers might lag slightly.

### 6.2 Latency vs. Durability
- **Sync Write**: Writing to disk and waiting for `fsync` before acknowledging. (High durability, high latency).
- **Async Write**: Writing to the OS page cache and acknowledging. (Low latency, risk of data loss on power failure).
- **Decision**: Provide a configurable `acks` parameter (0: No ack, 1: Leader ack, all: Full ISR ack).

### 6.3 Push vs. Pull
| Feature | Push (Webhooks) | Pull (Polling) |
| :--- | :--- | :--- |
| **Latency** | Extremely Low | Dependent on polling interval |
| **Overhead** | High (Broker must manage state) | Low (Subscriber manages state) |
| **Backpressure** | Hard to manage (Overwhelms sub) | Natural (Sub pulls what it can handle) |
| **Use Case** | Real-time alerts, Notifications | Data pipelines, ETL, Batch processing |""",
}

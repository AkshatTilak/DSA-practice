INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Notification System (Push/Email/SMS).',
    'groups': ['Real-World Systems', 'Messaging'],
    'readme_content': """# Notification System HLD

A Notification System is a distributed platform designed to send alerts, messages, and notifications to users across multiple channels (Push, Email, SMS) based on specific triggers. The primary challenge lies in handling massive scale, ensuring reliability (at-least-once delivery), and managing third-party API latencies.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Multi-Channel Support**: Ability to send notifications via Push Notifications (iOS/Android), Email, and SMS.
- **Preference Management**: Users should be able to opt-in or opt-out of specific notification types or channels.
- **Priority Handling**: Critical notifications (e.g., OTP, Security Alerts) must be prioritized over marketing notifications.
- **Retry Mechanism**: Automatic retries for failed deliveries due to transient third-party errors.
- **Tracking & Analytics**: Track the lifecycle of a notification: `Sent` $\rightarrow$ `Delivered` $\rightarrow$ `Opened/Read`.

### Non-Functional Requirements
- **High Availability**: The system must be available to accept notification requests even if a downstream provider is down.
- **Scalability**: Handle millions of notifications per day with peak bursts (e.g., during a global event or sale).
- **Reliability (Durability)**: Once a notification is accepted, it must not be lost.
- **Low Latency**: Real-time notifications (Push/SMS) should be delivered within seconds.

### Scale Assumptions
- **Daily Active Users (DAU)**: 10 Million.
- **Daily Notifications**: 100 Million.
- **Average QPS**: $\approx 1,150$ requests per second.
- **Peak QPS**: $\approx 10,000 - 15,000$ requests per second.
- **Storage**: Tracking logs for 30 days $\approx 100M \times 30 \times 100\text{ bytes} \approx 300\text{ GB/month}$.

---

## 2. High-Level System Architecture

The architecture follows a **decoupled, event-driven pattern** to ensure that the calling service (e.g., Billing Service, Order Service) is not blocked by the latency of third-party notification providers.

### Architectural Components
1.  **API Gateway**: Handles authentication, rate limiting, and request routing.
2.  **Notification Service**: The orchestrator. It validates requests, fetches user preferences, and routes the message to the appropriate queue.
3.  **User Preference Store**: A fast-lookup database containing user settings (e.g., "User A wants Email but not SMS").
4.  **Message Queues (Kafka/RabbitMQ)**: Acts as a buffer. Separate queues are used for different channels (Push, Email, SMS) and priority levels (High vs. Low).
5.  **Notification Workers**: Consumers that pull messages from queues, format templates, and call the external provider APIs.
6.  **Third-Party Providers**:
    *   **Push**: Firebase Cloud Messaging (FCM), Apple Push Notification service (APNs).
    *   **Email**: SendGrid, Mailgun, Amazon SES.
    *   **SMS**: Twilio, Vonage.
7.  **Analytics/Tracking DB**: Stores the status and delivery metrics of every notification.

---

## 3. Key HLD Concepts & Component Design

### Database Selection
| Component | Technology | Reason |
| :--- | :--- | :--- |
| **User Preferences** | **NoSQL (DynamoDB/Cassandra)** | Key-value lookups by `user_id` are extremely fast. Schema flexibility allows adding new channels easily. |
| **Notification Logs** | **NoSQL / Time-Series (Cassandra/ElasticSearch)** | High write throughput for logs. Ability to query by time range for analytics. |
| **Message Queue** | **Apache Kafka** | High throughput, durability, and allows multiple consumers to process different channels independently. |

### Priority Queueing
To prevent a massive marketing campaign (low priority) from delaying a password reset OTP (high priority), we implement **Priority Lanes**:
- **High Priority Queue**: Reserved for transactional alerts. Small buffer, highly scaled workers.
- **Low Priority Queue**: Reserved for newsletters/marketing. Larger buffer, processed as resources allow.

### Rate Limiting & Throttling
- **External Rate Limiting**: Third-party providers (e.g., Twilio) have strict quotas. The Workers implement a **Token Bucket** algorithm to ensure we don't exceed these limits and get banned.
- **User-Level Throttling**: Prevent "notification fatigue" by limiting the number of pushes a single user receives per hour.

### Template Engine
To avoid sending raw strings, the system uses a **Template Service**.
- **Input**: `TemplateID: "ORDER_CONFIRM", Variables: {name: "John", orderId: "123"}`.
- **Output**: "Hello John, your order #123 has been shipped!"
- Templates are cached in **Redis** to minimize DB lookups.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Flow
1.  **Trigger**: An internal service sends a request to the `Notification API` with `userId`, `messageType`, and `payload`.
2.  **Preference Check**: The `Notification Service` queries the `User Preference Store`. If the user has disabled the requested channel, the request is dropped.
3.  **Queueing**: The service pushes a message into the corresponding Kafka topic (e.g., `sms-high-priority`).
4.  **Consumption**: A `Worker` consumes the message, fetches the localized template from the `Template Service`, and formats the final message.
5.  **Provider Call**: The worker calls the 3rd party API (e.g., FCM for Push).
6.  **Acknowledgement**: The provider returns a `202 Accepted` or `4xx/5xx Error`.
7.  **Logging**: The worker updates the `Analytics DB` with the status.

### Handling Failures
- **Provider Down**: If a provider (e.g., SendGrid) is down, messages remain in Kafka. We can implement a **Circuit Breaker** to stop calling the failing provider and potentially switch to a fallback provider (e.g., switch from SendGrid to Mailgun).
- **Retry Policy**: Use **Exponential Backoff**. If a delivery fails due to a transient error (5xx), the worker requeues the message with a delay.
- **Dead Letter Queue (DLQ)**: If a message fails after $N$ retries (e.g., 3 times), it is moved to a DLQ for manual inspection or alerting.
- **Idempotency**: To avoid sending the same notification twice (at-least-once delivery), each request is assigned a `notification_id`. Workers check this ID against a Redis cache before sending.

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
In a notification system, **Availability (AP)** is prioritized over Consistency. 
- **Scenario**: If the User Preference DB is slightly lagging (eventual consistency) and a user just opted out of notifications, they might receive one last notification. This is acceptable. However, the system failing to send an OTP because the DB is performing a synchronous update (Consistency) is unacceptable.

### At-Least-Once vs. Exactly-Once Delivery
- **At-Least-Once**: Guaranteed. We ensure the message is sent. The risk is occasional duplicates.
- **Exactly-Once**: Extremely expensive to implement across distributed systems and 3rd party APIs. 
- **Trade-off**: We implement **At-Least-Once delivery combined with Idempotency keys** on the consumer side to simulate exactly-once behavior.

### Push vs. Pull (Polling)
- **Push**: We push notifications to the user device via FCM/APNs. This is essential for real-time engagement and battery efficiency on mobile devices.
- **Pull**: Users can also pull notifications from an "In-app Notification Center" (read from the Analytics/Log DB).

---

## Complexity Analysis Summary

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Triggering Notification** | $O(1)$ | $O(1)$ | Async push to Kafka. |
| **Preference Lookup** | $O(1)$ | $O(1)$ | Primary key lookup in NoSQL. |
| **Worker Processing** | $O(1)$ | $O(1)$ | Linear processing per message. |
| **Analytics Query** | $O(\log N)$ | $O(1)$ | Indexed by `userId` and `timestamp`. |""",
    'solutions': """# System Design: Multi-Channel Notification System

## 1. Requirements & System Constraints

### Functional Requirements
*   **Multi-Channel Support:** Support for Push Notifications (iOS/Android), Email, and SMS.
*   **User Preferences:** Users should be able to opt-in or opt-out of specific notification channels for different categories (e.g., Marketing: Email only, Transactional: Push and SMS).
*   **Templating Engine:** Support for dynamic content using templates (e.g., "Hello {name}, your order {order_id} has shipped").
*   **Priority Handling:** Ability to distinguish between high-priority (OTP, Password Reset) and low-priority (Marketing, Newsletters) notifications.
*   **Tracking & Analytics:** Track the lifecycle of a notification: `Sent` $\rightarrow$ `Delivered` $\rightarrow$ `Read/Clicked`.
*   **Reliability:** Guarantee "at-least-once" delivery.

### Non-Functional Requirements
*   **High Availability:** The system must be available to accept notification requests even if downstream providers (e.g., Twilio, SendGrid) are experiencing outages.
*   **Scalability:** Handle bursts of traffic (e.g., flash sales, breaking news) efficiently.
*   **Low Latency:** Transactional notifications (OTPs) must be delivered within seconds.
*   **Idempotency:** Prevent sending the same notification multiple times to the user due to retry logic.

### Scale Estimations (HLD)
*   **Daily Active Users (DAU):** 10 Million.
*   **Notifications per Day:** 100 Million.
*   **Average Throughput:** $\approx 1,150$ notifications per second.
*   **Peak Throughput:** $\approx 10,000+$ notifications per second.
*   **Storage:** 100M logs/day $\times$ 30 days retention $\approx 3$ Billion records.

---

## 2. High-Level Architecture

The system follows a decoupled, event-driven architecture to ensure that slow third-party APIs do not block the internal services.

### Architecture Diagram (Mermaid)

```mermaid
graph TD
    Client[Client Services/Apps] -->|POST /send| API[API Gateway]
    API -->|Validate/Auth| NS[Notification Service]
    NS -->|Fetch Prefs/Template| DB[(User DB / Cache)]
    NS -->|Publish Event| MQ[Message Queue / Kafka]
    
    subgraph "Worker Layer"
        MQ -->|Email Topic| EW[Email Worker]
        MQ -->|SMS Topic| SW[SMS Worker]
        MQ -->|Push Topic| PW[Push Worker]
    end
    
    EW -->|API Call| SendGrid[SendGrid/SES]
    SW -->|API Call| Twilio[Twilio/Vonage]
    PW -->|API Call| FCM_APNs[FCM/APNs]
    
    SendGrid -->|Webhook| Tracker[Delivery Tracker]
    Twilio -->|Webhook| Tracker
    FCM_APNs -->|Webhook| Tracker
    
    Tracker -->|Update Status| LogDB[(Notification Logs - NoSQL)]
```

### Component Descriptions
1.  **Notification Service:** The orchestrator. It validates the request, resolves the user's contact info, checks preferences, and fetches the rendered template.
2.  **Message Queue (Kafka):** Acts as a buffer. It separates the intake of notifications from the actual delivery, allowing the system to handle spikes without crashing. Different topics are used for different channels and priorities.
3.  **Channel Workers:** Specialized consumers that handle the specific API logic, rate limits, and retry policies of the third-party providers.
4.  **Third-Party Providers:** External gateways for the actual delivery to the end-user's device.
5.  **Delivery Tracker:** A service that consumes webhooks from providers to update the delivery status of the notification.

---

## 3. Detailed Database Schema Design

### Database Selection
*   **Relational DB (PostgreSQL):** Used for `UserPreferences` and `Templates` because these are highly structured and require strong consistency for updates.
*   **NoSQL DB (Cassandra or DynamoDB):** Used for `NotificationLogs`. The volume of write operations is massive, and the access pattern is primarily time-series (querying logs for a specific user over a time range).

### Schema

#### Table: `UserPreferences` (SQL)
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier of the user |
| `channel` | Enum | PK | EMAIL, SMS, PUSH |
| `category` | Enum | PK | TRANSACTIONAL, MARKETING, SOCIAL |
| `is_enabled` | Boolean | Not Null | Opt-in/out status |

*   **Index:** Composite index on `(user_id, category)` for fast preference lookups.

#### Table: `NotificationTemplates` (SQL)
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `template_id` | String | PK | Unique ID (e.g., "order_shipped_v1") |
| `channel` | Enum | Not Null | The target channel |
| `subject` | String | - | Email subject line |
| `body_template`| Text | Not Null | Template with placeholders |

#### Table: `NotificationLogs` (NoSQL)
| Field | Type | Role | Description |
| :--- | :--- | :--- | :--- |
| `notification_id`| UUID | Partition Key | Unique ID for the request |
| `user_id` | UUID | Sort Key | For querying user history |
| `channel` | String | Attribute | Channel used |
| `status` | String | Attribute | PENDING, SENT, DELIVERED, FAILED |
| `retry_count` | Int | Attribute | Number of delivery attempts |
| `created_at` | Timestamp | Attribute | Time of request |
| `updated_at` | Timestamp | Attribute | Last status update time |

---

## 4. Core API Design

### Send Notification
`POST /v1/notifications/send`

**Request Payload:**
```json
{
  "user_id": "u-12345",
  "category": "TRANSACTIONAL",
  "template_id": "order_confirmation",
  "placeholders": {
    "name": "John Doe",
    "order_id": "ORD-9988",
    "amount": "$45.00"
  },
  "priority": "HIGH"
}
```

**Response:**
```json
{
  "notification_id": "notif-abc-123",
  "status": "ACCEPTED",
  "estimated_delivery": "2023-10-27T10:00:05Z"
}
```

### Update User Preferences
`PATCH /v1/user/preferences`

**Request Payload:**
```json
{
  "user_id": "u-12345",
  "preferences": [
    { "channel": "EMAIL", "category": "MARKETING", "is_enabled": false },
    { "channel": "PUSH", "category": "SOCIAL", "is_enabled": true }
  ]
}
```

---

## 5. Scalability & Advanced Topics

### Message Queueing & Priority
To prevent marketing blasts from delaying OTPs, we implement **Priority Queues**:
*   **High Priority Topic:** For OTPs and Security alerts. Dedicated workers with higher resource allocation.
*   **Default Priority Topic:** For transactional updates.
*   **Low Priority Topic:** For newsletters and marketing.

### Idempotency
To prevent duplicate notifications (e.g., due to consumer retries), the `Notification Service` generates a unique `notification_id`. Workers check a distributed lock (Redis) or the `NotificationLogs` table using the `notification_id` before calling the external provider.

### Rate Limiting & Throttling
*   **Internal Rate Limiting:** Prevent a single internal service from flooding the system using a Token Bucket algorithm at the API Gateway.
*   **External Rate Limiting:** Third-party providers have strict quotas. Workers implement **leaky bucket** logic to smooth out bursts and avoid `429 Too Many Requests` errors.

### Fault Tolerance & Retries
*   **Exponential Backoff:** If a provider returns a 5xx error, the worker retries with increasing delays ($2^n$ seconds).
*   **Dead Letter Queue (DLQ):** If a notification fails after $X$ attempts, it is moved to a DLQ for manual inspection or automated fallback (e.g., if Push fails, try SMS).
*   **Circuit Breaker:** If a provider (e.g., SendGrid) is completely down, the circuit breaker trips, and the system either fails fast or switches to a backup provider (e.g., Amazon SES).

### Caching Strategy
*   **User Preferences:** Cached in Redis with a TTL. Since preferences don't change often, this eliminates millions of DB reads.
*   **Templates:** Cached in local memory (LRU Cache) within the Notification Service as they are updated infrequently.

---

## 6. Trade-off Analysis

### CAP Theorem: Availability over Consistency
The system prioritizes **Availability** and **Partition Tolerance** (AP). In a notification system, it is acceptable if the "Read" status of a notification is updated a few seconds late (Eventual Consistency), but it is unacceptable for the system to stop accepting notification requests because a log database is lagging.

### Latency vs. Reliability
By introducing a Message Queue, we introduce a small amount of overhead (latency) in terms of the time it takes to move a message from the producer to the consumer. However, this is a necessary trade-off to achieve **Reliability** and **Durability**, ensuring that no notification is lost if a worker crashes.

### SQL vs. NoSQL for Logs
*   **SQL:** Would struggle with the write-heavy nature of 100M events/day and the massive storage growth, leading to expensive indexing and slow vacuuming.
*   **NoSQL (Cassandra/DynamoDB):** Provides linear scalability and optimized writes, making it the superior choice for audit logs and delivery tracking.""",
}

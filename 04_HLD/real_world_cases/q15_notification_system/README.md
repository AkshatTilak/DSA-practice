# Notification System HLD

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
| **Analytics Query** | $O(\log N)$ | $O(1)$ | Indexed by `userId` and `timestamp`. |
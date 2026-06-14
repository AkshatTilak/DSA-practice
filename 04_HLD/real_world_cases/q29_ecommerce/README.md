# Ecommerce Platform HLD (Amazon/Flipkart)

Designing a global e-commerce platform is a classic "Hard" HLD challenge because it requires balancing **extreme read scalability** (browsing millions of products) with **strict write consistency** (preventing overselling inventory) and **distributed transaction management** (handling payments and orders across microservices).

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Catalog Management**: Users can search for products, view product details, and filter by categories.
*   **Shopping Cart**: Users can add/remove items and persist the cart across sessions.
*   **Order Processing**: Users can place orders, which must be handled atomically.
*   **Payment Integration**: Secure integration with third-party payment gateways.
*   **Inventory Management**: Real-time tracking of stock levels to prevent over-selling.
*   **User Profiles & Order History**: Manage user data and track past purchases.

### Non-Functional Requirements
*   **High Availability**: The system must be available $24/7$. Downtime during a sale (e.g., Black Friday) results in massive revenue loss.
*   **Scalability**: Must handle massive spikes in traffic during flash sales (10x-100x normal load).
*   **Consistency**: 
    *   **Strong Consistency** for Inventory and Payments.
    *   **Eventual Consistency** for Product Reviews, Search Index, and Recommendation engines.
*   **Low Latency**: Product page loads must be $< 200\text{ms}$ to maintain conversion rates.

### Scale Assumptions
| Metric | Value | Note |
| :--- | :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million | Global scale |
| **Average Orders/Day** | 10 Million | $\approx 115$ orders per second average |
| **Peak QPS (Reads)** | 500k - 1M | Heavy browsing vs. buying ratio |
| **Peak QPS (Writes)** | 50k - 100k | During flash sales |
| **Storage** | Petabytes | Product images, user data, order logs |

---

## 2. High-Level System Architecture

The system follows a **Microservices Architecture** to allow independent scaling of components (e.g., the Search service scales differently than the Payment service).

### Architecture Components
1.  **API Gateway**: Acts as the entry point. Handles authentication, rate limiting, request routing, and SSL termination.
2.  **Product Catalog Service**: Manages product metadata. Uses a combination of a primary DB and a search index.
3.  **Cart Service**: High-write, low-latency service to manage temporary user selections.
4.  **Order Service**: Orchestrates the checkout process. This is the "Source of Truth" for transactions.
5.  **Inventory Service**: Tracks stock levels. Must be highly consistent.
6.  **Payment Service**: Interfaces with external providers (Stripe, PayPal, Adyen).
7.  **Notification Service**: Asynchronous alerts via Email/SMS/Push.

### High-Level Diagram (Logical Flow)
`Client` $\rightarrow$ `CDN` $\rightarrow$ `Load Balancer` $\rightarrow$ `API Gateway` $\rightarrow$ `Microservices` $\rightarrow$ `Databases/Caches` $\rightarrow$ `Message Queue` $\rightarrow$ `Downstream Workers`

---

## 3. Key HLD Concepts & Component Design

### A. Product Catalog & Search (Read Path)
To handle millions of products and high search volume:
*   **Database**: Use **MongoDB** or **PostgreSQL with JSONB** for the product catalog because product attributes vary wildly (a laptop has RAM; a shirt has size/color).
*   **Search Index**: Sync data from the primary DB to **ElasticSearch** or **Solr**. This enables full-text search, fuzzy matching, and faceted filtering (e.g., "Filter by Brand: Apple").
*   **Caching**: Use **Redis** for "Hot Products" (top 1% of products that get 90% of traffic).

### B. The Inventory Challenge (The "Hard" Part)
Preventing "overselling" is critical. If 1,000 people try to buy 1 remaining iPhone, only 1 must succeed.
*   **Distributed Locking**: Use **Redis (Redlock)** or **Zookeeper** to lock the inventory item during the checkout window.
*   **Atomic Decrements**: Use SQL `UPDATE inventory SET stock = stock - 1 WHERE product_id = X AND stock > 0;`. The database's ACID properties ensure that the `stock > 0` check and decrement happen atomically.
*   **Inventory Sharding**: For extreme flash sales, split the inventory of a single product across multiple shards to avoid a single database row becoming a write bottleneck.

### C. Shopping Cart Design
*   **Storage**: Use **Redis** (Key-Value) for active sessions.
*   **Persistence**: Periodically persist the cart to a NoSQL DB (like **Cassandra**) so users don't lose their cart when switching devices.

### D. Database Selection Matrix

| Service | Database | Why? |
| :--- | :--- | :--- |
| **User Profile** | PostgreSQL | Structured data, strong consistency. |
| **Catalog** | MongoDB $\rightarrow$ ES | Flexible schema for diverse products + fast search. |
| **Cart** | Redis | Extreme low latency for frequent updates. |
| **Orders** | PostgreSQL | ACID compliance is non-negotiable for financial records. |
| **Inventory** | PostgreSQL/Redis | Atomic operations to prevent overselling. |
| **Analytics** | ClickHouse/Hive | OLAP for business intelligence and trends. |

---

## 4. Data Flows & Fault Tolerance

### Order Placement Walkthrough (The "Saga" Pattern)
Since the system is distributed, we cannot use a single global database transaction. We use a **Saga Pattern (Orchestration-based)** to ensure eventual consistency.

1.  **Order Service**: Creates an order in `PENDING` state.
2.  **Inventory Service**: Reserves the item (Decrements stock). If stock is 0 $\rightarrow$ Trigger **Compensating Transaction** (Cancel Order).
3.  **Payment Service**: Processes payment. If payment fails $\rightarrow$ Trigger **Compensating Transaction** (Release Inventory, Cancel Order).
4.  **Order Service**: Updates order status to `CONFIRMED`.
5.  **Notification Service**: Sends confirmation email via **Kafka** event.

### Fault Tolerance Strategies
*   **Database Replication**: Use Multi-AZ (Availability Zone) deployment with a Primary-Replica setup.
*   **Circuit Breaker**: If the Payment Service is slow or down, the Order Service uses a circuit breaker (e.g., Resilience4j) to fail fast and notify the user rather than hanging the entire system.
*   **Idempotency**: The Payment Service must implement **Idempotency Keys**. If a client retries a "Charge" request due to a timeout, the server uses the key to ensure the user is only charged once.
*   **Dead Letter Queues (DLQ)**: If the Notification Service fails to send an email after 3 retries, the message is moved to a DLQ for manual inspection.

---

## 5. Production Trade-offs

### Consistency vs. Availability (CAP Theorem)
*   **Product Catalog**: We choose **Availability (AP)**. It is okay if a user sees a slightly outdated price or description for a few seconds.
*   **Inventory/Payment**: We choose **Consistency (CP)**. We cannot risk selling a product we don't have or charging a user without recording the order.

### Synchronous vs. Asynchronous Communication
*   **Sync (REST/gRPC)**: Used for "Check Inventory" or "Process Payment" where an immediate response is required to proceed.
*   **Async (Kafka/RabbitMQ)**: Used for "Send Email," "Update Search Index," and "Analytics." This decouples the critical checkout path from non-critical side effects, reducing latency.

### SQL vs. NoSQL for Orders
While NoSQL scales better, **SQL (PostgreSQL)** is chosen for Orders because of **ACID transactions**. A lost order or a corrupted transaction in a NoSQL system would lead to massive customer dissatisfaction and financial discrepancies.

---

## Summary Complexity Analysis

| Operation | Time Complexity | Bottleneck | Mitigation |
| :--- | :--- | :--- | :--- |
| **Product Search** | $O(\log N)$ | Search Index latency | ElasticSearch Sharding |
| **Add to Cart** | $O(1)$ | Network I/O | Redis In-Memory Store |
| **Place Order** | $O(S)$ | Distributed Locking | Saga Pattern + Optimistic Locking |
| **Inventory Update**| $O(1)$ | Row-level contention | Inventory Sharding |

*(where $N$ is number of products, $S$ is the number of services in the Saga chain)*
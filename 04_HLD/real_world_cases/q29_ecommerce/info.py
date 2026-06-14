INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design E-commerce Platform (Amazon/Flipkart).',
    'groups': ['Real-World Systems', 'Distributed Systems'],
    'readme_content': """# Ecommerce Platform HLD (Amazon/Flipkart)

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

*(where $N$ is number of products, $S$ is the number of services in the Saga chain)*""",
    'solutions': """# System Design Document: Global E-commerce Platform

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **User Management:** User registration, authentication, profile management, and address books.
*   **Product Catalog:** Browsing products, searching with filters, and viewing detailed product pages.
*   **Shopping Cart:** Ability to add/remove items and persist the cart across sessions.
*   **Order Processing:** Checkout flow, order placement, and order history.
*   **Inventory Management:** Real-time tracking of stock levels and preventing overselling.
*   **Payment Integration:** Integration with third-party gateways (Stripe, PayPal) and payment status tracking.
*   **Reviews & Ratings:** Users can rate and review products they have purchased.

### 1.2 Non-Functional Requirements
*   **High Availability:** The system must be available 24/7, especially during peak sale events (e.g., Black Friday).
*   **Scalability:** Must handle millions of concurrent users and hundreds of millions of SKUs.
*   **Strong Consistency:** Required for Inventory and Payments (ACID compliance).
*   **Eventual Consistency:** Acceptable for Product Search, Reviews, and Recommendations.
*   **Low Latency:** Product discovery and browsing must be extremely fast (< 100ms).

### 1.3 Scale Estimations (High Level)
*   **Daily Active Users (DAU):** 10 Million.
*   **Average Orders per Day:** 1 Million.
*   **Peak Traffic:** 10x normal load during flash sales.
*   **Product Catalog Size:** 100 Million items.
*   **Read/Write Ratio:** Heavily read-intensive (approx. 100:1 for catalog browsing vs. ordering).

---

## 2. High-Level Architecture

The system follows a **Microservices Architecture** to ensure independent scalability and deployment of core business domains.

### 2.1 Architecture Diagram (Mermaid)

```mermaid
graph TD
    User((User)) --> CDN[Content Delivery Network]
    User --> AGW[API Gateway / Load Balancer]
    
    AGW --> UserSvc[User Service]
    AGW --> CatalogSvc[Catalog/Search Service]
    AGW --> CartSvc[Cart Service]
    AGW --> OrderSvc[Order Service]
    AGW --> PaymentSvc[Payment Service]
    
    CatalogSvc --> ES[(Elasticsearch)]
    CatalogSvc --> ProdDB[(Product DB - NoSQL)]
    
    UserSvc --> UserDB[(User DB - SQL)]
    
    CartSvc --> RedisCart[(Redis Cache)]
    
    OrderSvc --> OrderDB[(Order DB - SQL)]
    OrderSvc --> InvSvc[Inventory Service]
    
    InvSvc --> InvDB[(Inventory DB - SQL)]
    
    PaymentSvc --> PayGW[External Payment Gateway]
    
    OrderSvc --> Kafka{Message Queue - Kafka}
    Kafka --> EmailSvc[Notification Service]
    Kafka --> AnalyticsSvc[Analytics Service]
    Kafka --> InventorySvc[Inventory Update Worker]
```

### 2.2 Component Descriptions
*   **API Gateway:** Handles authentication, rate limiting, request routing, and load balancing.
*   **Catalog Service:** Manages product data. Uses Elasticsearch for high-performance full-text search and filtering.
*   **Cart Service:** A lightweight service using an in-memory store (Redis) for low-latency updates.
*   **Order Service:** Orchestrates the checkout process. Ensures the transition from "Pending" to "Paid" to "Shipped".
*   **Inventory Service:** The "Source of Truth" for stock. Uses pessimistic locking or distributed locks to prevent overselling.
*   **Payment Service:** Wraps external API calls and handles webhooks for asynchronous payment confirmation.
*   **Notification Service:** Consumes events from Kafka to send emails/push notifications asynchronously.

---

## 3. Detailed Database Schema Design

The system uses **Polyglot Persistence** based on the specific needs of each service.

### 3.1 User Service (Relational - PostgreSQL)
*Used for ACID compliance on user accounts and security.*
*   **Users Table:** `user_id (PK)`, `email (Unique)`, `password_hash`, `created_at`, `updated_at`.
*   **Addresses Table:** `address_id (PK)`, `user_id (FK)`, `street`, `city`, `state`, `zip_code`, `is_default`.

### 3.2 Catalog Service (NoSQL - MongoDB & Elasticsearch)
*Used for flexible schema (different attributes for electronics vs. clothing) and fast search.*
*   **Products Collection (MongoDB):** 
    *   `product_id (PK)`, `name`, `description`, `category_id`, `brand`, `base_price`, `attributes (Map/JSON)`, `created_at`.
*   **Categories Collection:** `category_id (PK)`, `name`, `parent_category_id`.
*   **Search Index (Elasticsearch):** Denormalized view of `product_id`, `name`, `description`, `category`, `price`, `tags`.

### 3.3 Cart Service (Key-Value - Redis)
*Used for temporary storage with TTL.*
*   **Key:** `cart:{user_id}`
*   **Value:** `List<{product_id, quantity, added_at}>`

### 3.4 Order Service (Relational - PostgreSQL)
*Used for financial integrity and audit trails.*
*   **Orders Table:** `order_id (PK)`, `user_id (FK)`, `total_amount`, `order_status (Enum)`, `shipping_address_id`, `created_at`.
*   **Order_Items Table:** `item_id (PK)`, `order_id (FK)`, `product_id`, `quantity`, `price_at_purchase`.

### 3.5 Inventory Service (Relational - PostgreSQL)
*Strict consistency is paramount.*
*   **Inventory Table:** `product_id (PK)`, `stock_quantity`, `reserved_quantity`, `version (for optimistic locking)`.

---

## 4. Core API Design

### 4.1 Product Search & Discovery
`GET /v1/products?query=laptop&category=electronics&sort=price_asc&page=1&size=20`
*   **Response:**
    ```json
    {
      "products": [
        {"id": "p123", "name": "MacBook Pro", "price": 2499.00, "rating": 4.8, "thumbnail": "url"}
      ],
      "total": 150,
      "pages": 8
    }
    ```

### 4.2 Cart Management
`POST /v1/cart/items`
*   **Payload:** `{"product_id": "p123", "quantity": 1}`
*   **Response:** `201 Created`

### 4.3 Order Placement (Checkout)
`POST /v1/orders`
*   **Payload:** 
    ```json
    {
      "shipping_address_id": "addr_456",
      "payment_method_id": "pm_789",
      "cart_id": "cart_001"
    }
    ```
*   **Response:** `202 Accepted` (Processing asynchronously).

### 4.4 Payment Webhook (Internal/External)
`POST /v1/payments/webhook`
*   **Payload:** `{"order_id": "ord_999", "status": "SUCCESS", "transaction_id": "tx_abc"}`

---

## 5. Scalability & Advanced Topics

### 5.1 Caching Strategy
*   **Edge Caching (CDN):** Static assets (images, CSS, JS) and semi-static product pages are cached at the edge.
*   **Distributed Cache (Redis):** 
    *   **Session Store:** User authentication tokens.
    *   **Hot Products:** Top 1% of products that generate 90% of traffic are cached to reduce DB load.
    *   **Read-through Cache:** Catalog service checks Redis before hitting MongoDB.

### 5.2 Database Scalability
*   **Read Replicas:** Used for User and Order DBs to handle heavy read traffic.
*   **Sharding:**
    *   **Order DB:** Sharded by `user_id` to ensure all orders for a single user reside on one shard.
    *   **Product DB:** Sharded by `category_id` or `product_id` using a consistent hashing algorithm.

### 5.3 Handling Concurrent Inventory (Flash Sales)
To prevent overselling:
1.  **Distributed Locking:** Use Redis Redlock to lock a product ID during the checkout transition.
2.  **Optimistic Locking:** Use a `version` column in the SQL DB: 
    `UPDATE inventory SET stock = stock - 1, version = version + 1 WHERE product_id = ? AND version = ? AND stock > 0;`
3.  **Inventory Reservation:** When a user hits "Checkout", reserve stock for 15 minutes. If payment fails or timer expires, release stock via a TTL-based event.

### 5.4 Message Queues (Kafka)
*   **Order Pipeline:** `OrderPlaced` $\rightarrow$ `PaymentProcessed` $\rightarrow$ `InventoryDeducted` $\rightarrow$ `ShipmentTriggered`.
*   **Decoupling:** The Order service does not wait for the Email service to send a confirmation; it pushes an event to Kafka.

---

## 6. Trade-off Analysis

| Trade-off | Decision | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs Availability** | **Mixed (PACELC)** | For **Catalog/Search**, we prioritize Availability (AP). For **Inventory/Payment**, we prioritize Consistency (CP). |
| **SQL vs NoSQL** | **Polyglot** | SQL is essential for transactions (Orders/Inventory). NoSQL (MongoDB/Elasticsearch) is essential for flexible attributes and high-speed searching. |
| **Sync vs Async** | **Async Checkout** | Making the checkout synchronous would create bottlenecks. Using a "Pending" state and Kafka allows the system to handle bursts and retry failed steps. |
| **Latency vs Storage** | **Denormalization** | We denormalize product data into Elasticsearch. This increases storage cost but reduces latency from seconds (complex SQL joins) to milliseconds. |
| **Strong vs Eventual Consistency** | **Eventual (Reviews)** | Product reviews do not need to appear instantly for all users worldwide. Eventual consistency via Kafka allows the system to scale. |""",
}

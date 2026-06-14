INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Swiggy / DoorDash - Food delivery logistics.',
    'groups': ['Real-World Systems', 'Distributed Systems'],
    'readme_content': r"""# Swiggy / DoorDash HLD: Food Delivery Logistics

This study guide provides a professional, high-level design for a large-scale food delivery platform like Swiggy or DoorDash. This system is fundamentally a **three-sided marketplace** involving **Customers**, **Restaurants**, and **Delivery Partners**, requiring complex real-time orchestration and geospatial indexing.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Customer:** Search for restaurants, browse menus, place orders, track delivery in real-time, and provide ratings.
*   **Restaurant:** Manage menu items, receive orders, update order status (Preparing $\rightarrow$ Ready for Pickup).
*   **Delivery Partner:** Receive delivery requests, accept/reject orders, update delivery status, and share real-time GPS location.
*   **Platform (The Brain):** Efficiently match a pending order to the most optimal delivery partner based on location, availability, and traffic.

### Non-Functional Requirements
*   **High Availability:** The system must be available $24/7$, especially during peak meal hours (lunch/dinner).
*   **Low Latency:** Tracking updates must feel real-time ($< 2$ seconds lag).
*   **Scalability:** Must handle massive spikes in traffic (e.g., during sports events or holidays).
*   **Consistency:** Strong consistency for payments and order status; eventual consistency for driver location tracking.
*   **Reliability:** No orders should be "lost" in the system.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 10 Million |
| **Average Orders per Day** | 1 Million |
| **Active Delivery Partners** | 500,000 |
| **Peak QPS (Search/Track)** | 100k - 200k requests per second |
| **Location Update Frequency** | Every 3-5 seconds per active driver |

---

## 2. High-Level System Architecture

The system follows a **Microservices Architecture** to decouple the three primary user personas and the matching engine.

### Architecture Diagram Components
1.  **API Gateway:** Handles authentication, rate limiting, and request routing.
2.  **Search Service:** Powered by Elasticsearch for full-text search and filtering (cuisine, rating, distance).
3.  **Order Service:** Manages the order lifecycle and state machine (Created $\rightarrow$ Paid $\rightarrow$ Confirmed $\rightarrow$ Preparing $\rightarrow$ Picked Up $\rightarrow$ Delivered).
4.  **Restaurant Service:** Manages restaurant metadata, menus, and availability.
5.  **Payment Service:** Integration with Stripe/PayPal/Razorpay.
6.  **Location/Tracking Service:** Handles high-velocity GPS pings from drivers and serves them to customers.
7.  **Dispatch/Matching Service:** The core engine that matches orders to drivers.
8.  **Notification Service:** Sends push notifications/SMS via Firebase (FCM) or Apple (APNs).

---

## 3. Key HLD Concepts & Component Design

### A. Geospatial Indexing (The Core Challenge)
Finding the "nearest" driver cannot be done with a standard SQL `SELECT` query because distance calculations across millions of rows are too slow.

*   **Choice: Google S2 or Uber H3 (Hexagonal Hierarchical Spatial Index).**
    *   **Why H3?** Unlike square grids, hexagons have a constant distance between the center and all six neighbors, reducing quantization errors in movement and making "radius searches" much more accurate.
*   **Mechanism:** The map is divided into cells. Each driver's coordinates are mapped to a `CellID`.
*   **Storage:** Current driver locations are stored in **Redis** (Key: `CellID`, Value: `Set of DriverIDs`) for sub-millisecond lookups.

### B. The Dispatch Matching Engine
Matching is not just about the "closest" driver; it involves optimizing for "Expected Time of Arrival" (ETA).

1.  **Candidate Generation:** When an order is ready, the Dispatch Service queries the H3 index for all drivers in the current and neighboring cells.
2.  **Filtering:** Filter drivers who are already on a delivery or have rejected the current order.
3.  **Ranking:** Rank candidates based on:
    *   Distance to restaurant.
    *   Driver's current direction (heading).
    *   Predicted traffic patterns.
4.  **Offer Logic:** Send the request to the top candidate. If not accepted within $T$ seconds, move to the next candidate.

### C. Database Selection
| Component | Technology | Reason |
| :--- | :--- | :--- |
| **Order/User Profile** | **PostgreSQL** | Requires ACID compliance for financial transactions and order states. |
| **Menu/Catalog** | **MongoDB** | Menus are semi-structured (nested categories, modifiers) and read-heavy. |
| **Driver Location** | **Redis** | Extremely high write volume; data is transient (only the latest location matters). |
| **Search** | **Elasticsearch** | Optimized for geospatial queries and fuzzy text searching. |
| **Analytics/Logs** | **ClickHouse / S3** | OLAP for analyzing delivery times and driver efficiency. |

### D. Real-time Tracking
To avoid polling the server every second (which would crash the DB), the system uses **WebSockets**.
*   **Driver App** $\xrightarrow{WebSocket}$ **Location Service** $\xrightarrow{Redis}$ **WebSocket Server** $\xrightarrow{WebSocket}$ **Customer App**.
*   The Location Service acts as a Pub/Sub hub. The customer "subscribes" to the `DriverID` assigned to their order.

---

## 4. Data Flows & Fault Tolerance

### Order-to-Delivery Walkthrough
1.  **Placement:** Customer places order $\rightarrow$ Order Service $\rightarrow$ Payment Service $\rightarrow$ Order marked as `PAID`.
2.  **Notification:** Order Service triggers Restaurant Service to notify the kitchen.
3.  **Dispatch Trigger:** Once the restaurant marks the order as `PREPARING` or `READY`, the **Dispatch Service** is triggered.
4.  **Matching:** 
    *   Dispatch Service queries Redis for `DriverIDs` in the restaurant's H3 cell.
    *   A "Dispatch Request" is sent via the Notification Service to the driver.
5.  **Acceptance:** Driver accepts $\rightarrow$ Order state changes to `PICKED_UP` $\rightarrow$ Customer is notified via WebSocket.
6.  **Delivery:** Driver reaches customer $\rightarrow$ Order marked as `DELIVERED` $\rightarrow$ Payment settled to restaurant and driver.

### Fault Tolerance & Resilience
*   **Idempotency:** Payment and Order placement use `Idempotency-Keys` to prevent double-charging if a user clicks "Order" twice during a network glitch.
*   **Dead Letter Queues (DLQ):** If the Notification Service fails to alert a driver, the message is moved to a DLQ, and a retry logic triggers a different driver immediately.
*   **Circuit Breakers:** If the Payment Gateway is down, the Order Service triggers a circuit breaker to prevent the system from hanging, showing a "Payment provider unavailable" message to the user.
*   **Replication:** PostgreSQL uses Primary-Replica setup to ensure that if the primary node fails, a replica is promoted to prevent data loss.

---

## 5. Production Trade-offs

### Consistency vs. Availability (CAP Theorem)
*   **Order/Payment Path $\rightarrow$ Consistency (CP):** We cannot risk "losing" an order or double-charging. We prioritize strong consistency over absolute availability. If the DB is in a partition state, we stop taking orders.
*   **Location Tracking Path $\rightarrow$ Availability (AP):** If a driver's location is lagging by 2 seconds or a single update is lost, it doesn't break the system. We prioritize availability and low latency (eventual consistency).

### Polling vs. WebSockets
*   **Polling:** Simple to implement, but creates massive overhead on the server (HTTP headers for every request).
*   **WebSockets:** Maintains a persistent TCP connection. While it uses more memory on the server (to keep connections open), it drastically reduces latency and bandwidth for real-time tracking.

### Grid Size Trade-off (H3 Resolution)
*   **Small Cells (High Res):** Very precise, but a driver might cross cell boundaries every few seconds, causing frequent Redis writes.
*   **Large Cells (Low Res):** Fewer updates, but the matching engine has to process way more drivers per cell, increasing the computational cost of ranking.
*   **Optimal Approach:** Use a multi-resolution approach where the system starts searching in a small cell and expands to larger rings if no driver is found.

---

## Complexity Analysis Summary

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Search Restaurant** | $O(\log N)$ | $O(N)$ | Elasticsearch inverted index. |
| **Driver Location Update** | $O(1)$ | $O(D)$ | Redis Key-Value write. |
| **Finding Nearby Drivers** | $O(K)$ | $O(K)$ | $K$ = Drivers in current + neighboring H3 cells. |
| **Order State Transition** | $O(1)$ | $O(1)$ | ACID transaction in SQL. |""",
    'solutions': r"""# System Design: Food Delivery Logistics (Swiggy / DoorDash)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Customer Side:**
    *   Search and browse restaurants based on location and cuisine.
    *   Place orders and make payments.
    *   Real-time tracking of the order and the delivery partner.
    *   Order history and ratings/reviews.
*   **Restaurant Side:**
    *   Manage menu items, pricing, and availability.
    *   Receive and accept/reject orders.
    *   Update order status (Preparing $\rightarrow$ Ready for Pickup).
*   **Delivery Partner Side:**
    *   Update availability status (Online/Offline).
    *   Accept/Reject delivery requests.
    *   Navigate to restaurant and customer locations.
    *   Update delivery status (Picked up $\rightarrow$ Delivered).
*   **System/Logistics:**
    *   **Matching Engine:** Efficiently assign the best available delivery partner to an order based on proximity, vehicle type, and load.
    *   **ETA Calculation:** Provide real-time estimated time of arrival.

### 1.2 Non-Functional Requirements
*   **High Availability:** The system must be available 24/7, especially during peak meal times.
*   **Low Latency:** Tracking updates must be near real-time (< 2 seconds lag).
*   **Consistency:** Strong consistency for payments and order status transitions.
*   **Scalability:** Handle massive spikes during lunch/dinner hours and holidays.

### 1.3 Scale Estimations (HLD)
*   **DAU:** 10 Million.
*   **Avg Orders per Day:** 1 Million.
*   **Peak Orders per Second (OPS):** ~500 - 1,000.
*   **Active Delivery Partners:** 500k.
*   **Location Updates:** Every 5 seconds per active driver $\rightarrow$ $500,000 / 5 = 100k$ writes per second. This is the primary write bottleneck.

---

## 2. High-Level Architecture

### 2.1 Core Components
*   **API Gateway:** Handles authentication, rate limiting, and request routing.
*   **User/Profile Service:** Manages user accounts, addresses, and preferences.
*   **Restaurant Service:** Manages restaurant metadata and menus.
*   **Order Service:** Orchestrates the order lifecycle (State Machine).
*   **Payment Service:** Integrates with third-party gateways (Stripe/PayPal).
*   **Location Service (Geo-Service):** Tracks driver coordinates and performs spatial queries (find nearby drivers).
*   **Dispatch/Matching Service:** The "brain" that matches an order to a driver.
*   **Notification Service:** Sends Push/SMS/Email notifications via Firebase (FCM) or Twilio.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    User((Customer)) --> AGW[API Gateway]
    Driver((Driver)) --> AGW
    Restaurant((Restaurant)) --> AGW

    AGW --> UserSvc[User Service]
    AGW --> RestSvc[Restaurant Service]
    AGW --> OrderSvc[Order Service]
    AGW --> LocSvc[Location Service]

    OrderSvc --> PaySvc[Payment Service]
    OrderSvc --> DispatchSvc[Dispatch Service]
    
    LocSvc --> GeoDB[(Redis Geo/S2)]
    
    DispatchSvc --> LocSvc
    DispatchSvc --> OrderSvc

    OrderSvc --> Kafka{Message Queue}
    Kafka --> NotifySvc[Notification Service]
    Kafka --> Analytics[Analytics/ML Engine]
    
    NotifySvc --> User
    NotifySvc --> Driver
    NotifySvc --> Restaurant
```

### 2.3 Order Flow Sequence
1. **Order Placement:** Customer $\rightarrow$ Order Svc $\rightarrow$ Payment Svc $\rightarrow$ Order Svc (Status: Paid).
2. **Restaurant Notification:** Order Svc $\rightarrow$ Kafka $\rightarrow$ Notification Svc $\rightarrow$ Restaurant.
3. **Dispatching:** Order Svc (Status: Ready) $\rightarrow$ Dispatch Svc.
4. **Matching:** Dispatch Svc queries Location Svc for $N$ closest drivers $\rightarrow$ Sends request to Driver $\rightarrow$ Driver Accepts.
5. **Tracking:** Driver $\rightarrow$ Location Svc (Update Lat/Lng) $\rightarrow$ Customer (via WebSocket/Polling).

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection
*   **Relational (PostgreSQL):** Used for User, Order, and Payment data where ACID compliance is non-negotiable.
*   **NoSQL (MongoDB/Cassandra):** Used for Restaurant Menus (highly polymorphic) and Order History (write-heavy, read-rarely).
*   **In-Memory (Redis):** Used for Driver real-time locations and session management.

### 3.2 Schema Definitions

#### User Table (SQL)
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | |
| `name` | VARCHAR | NOT NULL | |
| `email` | VARCHAR | UNIQUE | |
| `phone` | VARCHAR | UNIQUE | |
| `created_at` | TIMESTAMP | | |

#### Restaurant Table (SQL/NoSQL)
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `restaurant_id` | UUID | PK | |
| `name` | VARCHAR | | |
| `address` | TEXT | | |
| `geo_location` | GEOGRAPHY | INDEX | PostGIS Point |
| `rating` | DECIMAL | | |
| `is_active` | BOOLEAN | | |

#### Menu Table (NoSQL - MongoDB)
```json
{
  "restaurant_id": "UUID",
  "categories": [
    {
      "category_name": "Beverages",
      "items": [
        {"item_id": "UUID", "name": "Coke", "price": 2.99, "available": true}
      ]
    }
  ]
}
```

#### Order Table (SQL)
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `order_id` | UUID | PK | |
| `customer_id` | UUID | FK | |
| `restaurant_id`| UUID | FK | |
| `driver_id` | UUID | FK | Null until matched |
| `status` | ENUM | | PLACED, PAID, PREPARING, PICKED_UP, DELIVERED |
| `total_amount` | DECIMAL | | |
| `created_at` | TIMESTAMP | | |

#### Driver Table (SQL)
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `driver_id` | UUID | PK | |
| `vehicle_type` | ENUM | | Bike, Car, Scooter |
| `current_status`| ENUM | | ONLINE, BUSY, OFFLINE |
| `rating` | DECIMAL | | |

---

## 4. Core API Design

### 4.1 Customer APIs
*   `GET /v1/restaurants?lat={lat}&lng={lng}&cuisine={type}`
    *   Returns a list of nearby restaurants.
*   `POST /v1/orders`
    *   Request: `{ "restaurant_id": "UUID", "items": [{ "item_id": "UUID", "qty": 1 }], "address_id": "UUID" }`
    *   Response: `{ "order_id": "UUID", "status": "PLACED" }`
*   `GET /v1/orders/{order_id}/track`
    *   Response: `{ "driver_lat": 12.97, "driver_lng": 77.59, "eta": "12 mins" }`

### 4.2 Driver APIs
*   `PATCH /v1/driver/status`
    *   Request: `{ "status": "ONLINE" }`
*   `POST /v1/driver/location`
    *   Request: `{ "lat": 12.97, "lng": 77.59 }` (Sent every 5s)
*   `POST /v1/orders/{order_id}/accept`
    *   Response: `{ "success": true, "pickup_location": "..." }`

### 4.3 Restaurant APIs
*   `GET /v1/restaurant/orders/pending`
    *   Returns list of orders needing preparation.
*   `PATCH /v1/orders/{order_id}/status`
    *   Request: `{ "status": "READY_FOR_PICKUP" }`

---

## 5. Scalability & Advanced Topics

### 5.1 Handling High-Frequency Location Updates
Updating a SQL database 100k times per second is infeasible. 
*   **Redis Geo-hashes:** Use `GEOADD` to store driver coordinates and `GEORADIUS` to find drivers within a radius. Redis is in-memory and can handle the write throughput.
*   **S2 Geometry / Uber H3:** Divide the map into hexagonal cells. Drivers are indexed by cell ID. This allows the Dispatch Service to query only the cells surrounding the restaurant.

### 5.2 The Matching Algorithm (Dispatch Service)
Matching is not just "closest driver." It involves:
1.  **Filtering:** Only drivers who are `ONLINE` and not `BUSY`.
2.  **Scoring:** Calculate a score based on (Distance to Restaurant + Estimated Time to reach).
3.  **Batching:** Instead of instant matching, batch orders every 5-10 seconds to optimize the global assignment (avoiding the "greedy" approach where one driver takes an order they are barely suited for, leaving a later order unfulfillable).

### 5.3 Real-time Tracking
*   **WebSockets:** Maintain a persistent connection between the Client and the Location Service. When a driver updates their location, the server pushes the update to the specific customer.
*   **Polling Fallback:** If WebSockets are unavailable, use long-polling every 10 seconds.

### 5.4 Distributed Transactions (SAGA Pattern)
Since an order involves multiple services (Order $\rightarrow$ Payment $\rightarrow$ Restaurant $\rightarrow$ Driver), we use a **SAGA Orchestration** pattern:
*   If Payment fails $\rightarrow$ Order is marked as `FAILED`.
*   If Restaurant rejects order $\rightarrow$ Trigger Payment Refund $\rightarrow$ Order marked as `CANCELLED`.

### 5.5 Caching Strategy
*   **Restaurant Menus:** Cached in Redis with a TTL. Updated via a Cache-Aside pattern when the restaurant updates the menu.
*   **User Sessions:** JWTs stored in Redis for fast authentication.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Availability vs. Consistency
*   **Payment & Order Status:** We prioritize **Consistency (CP)**. It is better for a user to see a "Loading" spinner than to be charged twice or have an order disappear.
*   **Driver Tracking:** We prioritize **Availability (AP)**. If a driver's location update is delayed by 2 seconds or missed, it doesn't break the system. Eventual consistency is acceptable.

### 6.2 Push vs. Pull for Tracking
*   **Push (WebSockets):** Lower latency, higher server resource consumption (open connections).
*   **Pull (HTTP Polling):** Higher latency, easier to scale horizontally (stateless).
*   **Decision:** Use WebSockets for the active "Tracking" screen to provide a premium UX, and fallback to polling for background status checks.

### 6.3 Latency vs. Precision in Matching
*   **Exact Distance:** Calculating Haversine distance for 1,000 drivers is CPU intensive.
*   **Grid-based (H3/S2):** Using cell-based lookups is significantly faster but slightly less precise.
*   **Decision:** Use Cell-based lookup to narrow down candidates to $\sim 20$ drivers, then apply the precise Haversine formula only to that small subset.""",
}

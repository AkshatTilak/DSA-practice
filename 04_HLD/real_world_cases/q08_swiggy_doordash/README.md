# Swiggy / DoorDash HLD: Food Delivery Logistics

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
| **Order State Transition** | $O(1)$ | $O(1)$ | ACID transaction in SQL. |
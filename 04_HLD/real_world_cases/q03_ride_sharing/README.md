# Ride Sharing Service (Uber/Lyft) HLD

This study guide provides a comprehensive architectural deep-dive into designing a ride-sharing dispatch system. The core challenge of this system is the **spatial indexing problem**: efficiently matching a passenger with the nearest available driver in real-time across a global map.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Passenger**: Request a ride by providing a pickup and destination location.
*   **Driver**: Update their current location periodically and toggle availability (Online/Offline).
*   **Matching Engine**: Match a passenger with an available driver based on proximity and availability.
*   **Trip Management**: Track the status of a ride (Requested $\rightarrow$ Accepted $\rightarrow$ In-Progress $\rightarrow$ Completed).
*   **Real-time Updates**: Provide real-time location tracking of the driver to the passenger.

### Non-Functional Requirements
*   **Low Latency**: The matching process must happen in near real-time (< 1 second for driver search).
*   **High Availability**: The system must be available 24/7. A downtime means thousands of people cannot commute.
*   **Scalability**: Must handle massive spikes in traffic (e.g., New Year's Eve, rush hour).
*   **Reliability/Durability**: Ride history and payment records must never be lost.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million |
| **Active Drivers** | 1 Million |
| **Location Update Frequency** | Every 3-5 seconds per active driver |
| **QPS (Location Updates)** | $\approx 333,000$ write requests per second |
| **QPS (Ride Requests)** | $\approx 10,000$ requests per second |
| **Storage** | High volume of time-series data for trip history and location logs |

---

## 2. High-Level System Architecture

The system follows a **Microservices Architecture** to decouple location tracking from the matching logic and payment processing.

### Architecture Diagram Components
1.  **API Gateway**: Handles authentication, rate limiting, and routes requests to specific services.
2.  **Driver Location Service**: Maintains the real-time location of all online drivers.
3.  **Ride/Matching Service**: Orchestrates the "request $\rightarrow$ match $\rightarrow$ assign" workflow.
4.  **Geo-Index (Spatial Store)**: A specialized data store (Redis/S2/H3) used to query drivers by location.
5.  **Notification Service**: Uses WebSockets or Push Notifications (FCM/APNs) to alert drivers and passengers.
6.  **Trip Service**: Manages the state machine of a trip and stores historical data.

---

## 3. Key HLD Concepts & Component Design

### A. The Spatial Indexing Problem (The Core)
A standard SQL query like `SELECT * FROM drivers WHERE distance(user_loc, driver_loc) < 5km` is $O(N)$, which is impossible at our scale. We need a spatial index.

#### 1. QuadTrees
*   **Concept**: A tree where each node has exactly four children. The map is recursively divided into four quadrants until a quadrant contains a small enough number of drivers.
*   **Pros**: Dynamic updates, efficient for varying density (cities vs. rural).
*   **Cons**: Hard to distribute across multiple servers (partitioning a tree is complex).

#### 2. Google S2 Geometry / Uber H3 (The Industry Standard)
*   **Concept**: These libraries map a 2D sphere (Earth) onto a 1D space (Hilbert Curve for S2, Hexagonal Grids for H3).
*   **S2**: Uses a 64-bit integer to represent a cell. Nearby cells often have similar integer values.
*   **H3 (Hexagons)**: Uber uses H3 because hexagons have a uniform distance between the center and all six neighbors, reducing quantization error during radius searches.
*   **Implementation**: Store the `CellID` in a distributed cache (Redis).

### B. Technology Stack Selection
| Component | Technology | Reason |
| :--- | :--- | :--- |
| **Location Cache** | **Redis (GeoHash)** | Extreme low latency for writes/reads of volatile coordinate data. |
| **Trip History DB** | **Cassandra / DynamoDB** | High write throughput, scalable, and handles time-series data well. |
| **User/Driver Profiles** | **PostgreSQL / MySQL** | Strong ACID compliance for identity and payment data. |
| **Event Bus** | **Apache Kafka** | Decouples the Matching Service from Analytics and Billing. |
| **Communication** | **WebSockets / gRPC** | Bi-directional, low-latency communication for real-time car movement. |

### C. Database Sharding
To handle millions of drivers, we shard data by **City/Region**. Since ride-sharing is inherently local (a driver in NYC doesn't care about a passenger in LA), partitioning by `CityID` ensures that most queries stay within a single shard.

---

## 4. Data Flows & Fault Tolerance

### Request Walkthrough: Requesting a Ride
1.  **Passenger Request**: Passenger sends `requestRide(pickup, destination)` via API Gateway.
2.  **Matching Engine**: 
    *   Queries the **Geo-Index** using the passenger's `S2/H3 CellID`.
    *   Retrieves a list of the nearest $N$ available drivers.
    *   Filters drivers based on vehicle type (XL, Luxury) and rating.
3.  **Dispatch**: 
    *   The system sends a request to the #1 ranked driver via the **Notification Service**.
    *   If the driver rejects or times out (e.g., 15 seconds), the system moves to the #2 ranked driver.
4.  **Acceptance**: Driver accepts $\rightarrow$ Trip Service creates a `TripID` $\rightarrow$ Status updates to `Accepted` $\rightarrow$ Passenger is notified.
5.  **Real-time Tracking**: Driver's app sends location updates every 3s $\rightarrow$ Location Service $\rightarrow$ Redis $\rightarrow$ Pushed to Passenger via WebSocket.

### Fault Tolerance & Reliability
*   **Node Failure**: If a Geo-Index shard fails, we use **Redis Sentinel/Cluster** for automatic failover.
*   **Matching Deadlocks**: Use a distributed lock (via Redis/Zookeeper) on the `DriverID` to ensure a driver isn't assigned to two passengers simultaneously.
*   **Network Partition**: If the driver's app loses connection, the system marks the driver as "Inactive" after $X$ missed heartbeats to avoid "Ghost Drivers."

---

## 5. Production Trade-offs

### CAP Theorem Analysis
In this system, we prioritize **Availability** and **Partition Tolerance** (AP) for location updates, but **Consistency** and **Partition Tolerance** (CP) for ride assignment and payments.
*   **Location Updates (AP)**: It is okay if a passenger sees a driver 2 seconds behind their actual position. We favor availability over absolute consistency.
*   **Ride Matching (CP)**: It is **not** okay to assign one driver to two people. We use strong consistency/distributed locking here.

### Latency vs. Accuracy
*   ** Trade-off**: We could calculate the exact distance using the Haversine formula for every driver in the city, but it's too slow.
*   **Solution**: Use **Approximate Proximity** via H3/S2 cells to narrow the candidate list to $\approx 50$ drivers, then apply the expensive Haversine formula only to that small subset.

### Pull vs. Push for Location
*   **Pull**: Passenger app polls the server every 3s. (High overhead, wasteful).
*   **Push**: Server pushes updates via WebSockets. (Lower latency, higher server state maintenance).
*   **Decision**: Use **Push** for the active trip duration to ensure a premium user experience.

---

## Summary Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Driver Location Update** | $O(1)$ | $O(D)$ | $D = \text{Total Active Drivers}$ |
| **Finding Nearby Drivers** | $O(K)$ | $O(K)$ | $K = \text{Number of drivers in nearby cells}$ |
| **Trip State Update** | $O(1)$ | $O(T)$ | $T = \text{Total active trips}$ |
| **Geo-Index Query** | $O(\log N)$ | $O(N)$ | Where $N$ is the number of cells in the index |
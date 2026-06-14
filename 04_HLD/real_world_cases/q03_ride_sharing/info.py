INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/design-ride-sharing-service-like-uber-lyft-system-design/',
    'description': 'Design Uber dispatch driver passenger matching service.',
    'type': 'design',
    'groups': ['Real-World Systems', 'Distributed Systems'],
    'readme_content': """# Ride Sharing Service (Uber/Lyft) HLD

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
| **Geo-Index Query** | $O(\log N)$ | $O(N)$ | Where $N$ is the number of cells in the index |""",
    'solutions': """# System Design: Ride-Sharing Dispatch & Matching Service

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Driver Location Updates:** Drivers must be able to send their real-time GPS coordinates to the system frequently (e.g., every 3-5 seconds).
*   **Ride Request:** Passengers can request a ride by providing their current location and destination.
*   **Matching Logic:** The system must find the "best" available driver based on proximity and availability.
*   **Dispatch Process:** The system notifies a driver of a ride request. The driver can accept or reject the request.
*   **Ride Lifecycle:** Track ride states from `REQUESTED` $\rightarrow$ `MATCHED` $\rightarrow$ `ARRIVED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`.

### 1.2 Non-Functional Requirements
*   **Low Latency:** Matching and dispatching must happen in near real-time (< 2 seconds).
*   **High Availability:** The system must be available 24/7; a downtime means lost revenue and stranded users.
*   **Scalability:** Must handle millions of concurrent drivers and passengers across multiple global cities.
*   **Consistency:** Strict consistency for the matching process to ensure a driver is not assigned to two rides simultaneously.

### 1.3 Scale Estimations (HLD)
*   **Active Drivers:** 1 Million.
*   **Location Updates:** 1M drivers updating every 3 seconds $\approx$ 333k writes/sec.
*   **Ride Requests:** ~100k requests per minute $\approx$ 1.6k requests/sec.
*   **Data Volume:** Location data is ephemeral, but ride history is permanent. Ride history grows linearly with usage.

---

## 2. High-Level Architecture

The system adopts a microservices architecture to decouple high-write location ingestion from the complex matching logic.

### 2.1 Core Components
1.  **Driver Location Service:** Handles high-frequency GPS pings. It updates a fast, geo-spatial index.
2.  **Ride Management Service:** Manages the lifecycle of a ride request (creation, state transitions).
3.  **Matching Service:** The "Brain." It queries the Location Service for nearby drivers and applies the matching algorithm.
4.  **Dispatch/Notification Service:** Manages real-time communication with drivers and passengers via WebSockets or Push Notifications.
5.  **Geo-Index (Redis/S2):** A specialized storage for spatial queries to find drivers within a specific radius.

### 2.2 Architecture Diagram

```mermaid
graph TD
    P[Passenger App] -->|Request Ride| RMS[Ride Management Service]
    D[Driver App] -->|Update Location| LS[Driver Location Service]
    D -->|Accept/Reject| RMS
    
    LS -->|Write Lat/Lng| GeoIndex[(Geo-Spatial Index - Redis/S2)]
    
    RMS -->|Trigger Match| MS[Matching Service]
    MS -->|Query Nearby Drivers| GeoIndex
    MS -->|Assign Driver| RMS
    
    RMS -->|Notify Driver| NS[Notification Service]
    NS -->|WebSocket/Push| D
    NS -->|WebSocket/Push| P
    
    RMS -->|Persist Ride| DB[(Ride DB - PostgreSQL/Cassandra)]
```

---

## 3. Detailed Database Schema Design

### 3.1 Storage Strategy
*   **Ephemeral Data (Location):** Redis is used for driver locations because the data changes every few seconds and we only care about the *current* state.
*   **Persistent Data (User/Ride):** A relational database (PostgreSQL) is used for ride records and user profiles to ensure ACID compliance for billing and trip history.

### 3.2 Schema

#### Table: `drivers` (SQL)
| Field | Type | Constraints | Note |
| :--- | :--- | :--- | :--- |
| `driver_id` | UUID | PK | Unique Driver ID |
| `name` | VARCHAR | NOT NULL | |
| `status` | ENUM | NOT NULL | `ONLINE`, `OFFLINE`, `BUSY` |
| `rating` | FLOAT | | |
| `city_id` | INT | FK | For regional partitioning |

#### Table: `rides` (SQL)
| Field | Type | Constraints | Note |
| :--- | :--- | :--- | :--- |
| `ride_id` | UUID | PK | Unique Ride ID |
| `passenger_id`| UUID | FK | |
| `driver_id` | UUID | FK, Nullable | Assigned driver |
| `pickup_loc` | Point | NOT NULL | PostGIS Point (lat, lng) |
| `dropoff_loc`| Point | NOT NULL | PostGIS Point (lat, lng) |
| `status` | ENUM | NOT NULL | `REQUESTED`, `MATCHED`, `COMPLETED`, etc. |
| `created_at` | Timestamp| NOT NULL | |

#### Geo-Spatial Index (Redis)
*   **Structure:** `GEOADD` (Sorted Set)
*   **Key:** `drivers:locations:{city_id}`
*   **Member:** `driver_id`
*   **Score:** `longitude, latitude`
*   **Query:** `GEORADIUS` or `GEOSEARCH` to find drivers within $X$ km.

---

## 4. Core API Design

### 4.1 Driver Location Update
`PATCH /v1/driver/location`
**Payload:**
```json
{
  "driver_id": "d-123",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timestamp": "2023-10-27T10:00:00Z"
}
```
**Response:** `204 No Content`

### 4.2 Request Ride
`POST /v1/ride/request`
**Payload:**
```json
{
  "passenger_id": "p-456",
  "pickup": {"lat": 40.7130, "lng": -74.0070},
  "destination": {"lat": 40.7580, "lng": -73.9855},
  "ride_type": "UberX"
}
```
**Response:** `201 Created`
```json
{
  "ride_id": "r-789",
  "status": "SEARCHING"
}
```

### 4.3 Accept Ride
`POST /v1/ride/accept`
**Payload:**
```json
{
  "ride_id": "r-789",
  "driver_id": "d-123"
}
```
**Response:** `200 OK` or `409 Conflict` (if ride already taken).

---

## 5. Scalability & Advanced Topics

### 5.1 Geo-Sharding (The S2/Geohash approach)
To avoid a single Redis instance becoming a bottleneck, we partition the world into cells.
*   **Google S2 Geometry:** Divides the earth into a hierarchy of cells. We can map each driver to a `CellID`.
*   **Partitioning:** Drivers in different cities or regions are stored in different Redis clusters. The Matching Service calculates the S2 cell of the passenger and queries the corresponding cluster.

### 5.2 Matching Algorithm (Greedy vs. Batching)
*   **Greedy Matching:** The first available driver within $X$ radius is picked. This is fast but can lead to sub-optimal global wait times.
*   **Batch Matching:** The system collects all requests and available drivers over a short window (e.g., 2-5 seconds) and solves a **Bipartite Matching Problem** (using the Hungarian Algorithm or Kuhn-Munkres) to minimize the total aggregate wait time for all passengers.

### 5.3 Handling High Write Volume
*   **Write-back Cache:** Driver locations are written to Redis. A background worker asynchronously persists sampled location data to a Cold Store (Cassandra/HBase) for historical analysis/dispute resolution.
*   **Load Balancing:** Use a Layer 7 Load Balancer (NGINX/Envoy) to distribute GPS pings across multiple instances of the Location Service.

### 5.4 Concurrency & Race Conditions
To prevent two drivers from accepting the same ride:
1.  **Optimistic Locking:** Use a version column in the `rides` table.
    `UPDATE rides SET driver_id = 'd-123', status = 'MATCHED' WHERE ride_id = 'r-789' AND driver_id IS NULL;`
2.  **Distributed Lock:** Use Redlock (Redis) to lock the `ride_id` for the duration of the acceptance processing.

---

## 6. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs Availability** | Availability for Location; Consistency for Matching | If a location update is lost, the next one arrives in 3s (Low impact). If a ride is double-booked, it's a terrible UX (High impact). |
| **SQL vs NoSQL** | Hybrid | SQL (PostgreSQL) for ACID compliance on payments/rides; Redis for low-latency spatial queries; Cassandra for massive location logs. |
| **Latency vs Accuracy** | Latency (Approximate Proximity) | Calculating exact road distance (ETA) for 100 drivers is too slow. We use "as-the-crow-flies" (Euclidean/Haversine) distance to filter the top 10 candidates, then call a Routing Engine (OSRM/Google Maps) for exact ETAs. |
| **Pull vs Push** | Push (WebSockets) | Drivers cannot poll the server every second for rides. WebSockets allow the server to push the match instantly. |""",
}

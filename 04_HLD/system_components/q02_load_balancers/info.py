INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/load-balancers-system-design/',
    'description': 'LB routing logic.',
    'type': 'design',
    'groups': ['Distributed Systems', 'Networking'],
    'readme_content': """# Load Balancer Design HLD

A **Load Balancer (LB)** is a critical component in distributed systems that acts as a reverse proxy to distribute incoming network or application traffic across multiple backend servers. Its primary goal is to ensure no single server becomes a bottleneck, thereby maximizing throughput, minimizing response time, and ensuring high availability.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Traffic Distribution**: Efficiently distribute incoming requests across a pool of healthy backend servers.
*   **Health Monitoring**: Continuously monitor the status of backend servers and remove unhealthy ones from the rotation.
*   **Service Discovery**: Dynamically keep track of available server instances.
*   **Session Persistence**: Optionally ensure that a specific client is routed to the same server for the duration of a session (Sticky Sessions).

### Non-Functional Requirements
*   **High Availability**: The LB itself must not be a single point of failure (SPOF).
*   **Low Latency**: The overhead introduced by the LB should be negligible (typically $\mu s$ to low $ms$).
*   **Scalability**: Ability to handle massive spikes in QPS (Queries Per Second) by scaling horizontally.
*   **Reliability**: Guarantee that requests are not lost during server failovers.

### Scale Assumptions
*   **Traffic**: Millions of concurrent users.
*   **QPS**: $10^5$ to $10^7$ requests per second.
*   **Backend**: Hundreds or thousands of microservices instances.

---

## 2. High-Level System Architecture

The typical placement of a load balancer is between the client and the application servers. In a production-grade enterprise environment, LBs are often deployed in layers.

### Architecture Flow
`Client` $\rightarrow$ `DNS (Global Server LB)` $\rightarrow$ `External LB (L4/L7)` $\rightarrow$ `Internal LB` $\rightarrow$ `Application Servers` $\rightarrow$ `Database/Cache`

### Component Roles
1.  **DNS/Global Server Load Balancing (GSLB)**: Routes the user to the nearest data center based on geographic location (using Anycast or GeoDNS).
2.  **L4 Load Balancer (Transport Layer)**: Operates at the TCP/UDP level. It routes traffic based on IP address and port without looking at the actual content of the packets. Fast and efficient.
3.  **L7 Load Balancer (Application Layer)**: Operates at the HTTP/HTTPS level. It can inspect headers, cookies, and URL paths to make intelligent routing decisions (e.g., `/api/users` $\rightarrow$ User Service).
4.  **Health Checker**: A sidecar process or internal module that pings servers via TCP handshakes or HTTP `/health` endpoints.
5.  **Backend Pool**: A dynamic group of server instances capable of handling the requests.

---

## 3. Key HLD Concepts & Component Design

### LB Routing Logic (The Core)

The choice of algorithm determines how "balanced" the load actually is.

| Algorithm | Logic | Best Use Case | Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **Round Robin** | Sequential distribution. | Identical server specs. | Simple, fair. | Ignores server load/capacity. |
| **Weighted Round Robin** | Based on assigned weights. | Heterogeneous hardware. | Accounts for server power. | Requires manual weight tuning. |
| **Least Connections** | Routes to server with fewest active connections. | Long-lived connections (e.g., WebSocket). | Prevents overloading one node. | More overhead to track state. |
| **Least Response Time** | Routes to server with lowest latency + fewest connections. | Performance-critical apps. | Optimizes user experience. | Complex to calculate in real-time. |
| **IP Hash** | `hash(ClientIP) % N servers`. | Session persistence. | Client stays with one server. | Imbalanced if few clients have huge traffic. |
| **Consistent Hashing** | Maps servers/requests to a logical circle. | Caching layers (Redis/Memcached). | Minimal reshuffle when scaling. | More complex implementation. |

### Layer 4 vs. Layer 7 Comparison

| Feature | L4 (Transport Layer) | L7 (Application Layer) |
| :--- | :--- | :--- |
| **OSI Layer** | Layer 4 (TCP/UDP) | Layer 7 (HTTP/FTP/gRPC) |
| **Inspection** | IP + Port only | Full Packet (Headers, Cookies, Body) |
| **Performance** | Extremely Fast (Low CPU) | Slower (Deep Packet Inspection) |
| **Routing** | Simple routing | Smart routing (Content-based) |
| **SSL Termination**| Usually passed through | Terminates SSL (handles decryption) |

### Health Check Mechanism
The LB prevents "Black Holing" (sending requests to a dead server) using:
*   **Passive Health Checks**: Monitoring live traffic; if a server returns $5xx$ errors repeatedly, it's marked as down.
*   **Active Health Checks**: Sending a "Heartbeat" request every $X$ seconds. If the server fails to respond within $Y$ ms, it is removed from the pool.

---

## 4. Data Flows & Fault Tolerance

### Request Walkthrough (L7 Path)
1.  **Connection**: Client initiates a TLS handshake with the L7 Load Balancer.
2.  **Termination**: The LB terminates the SSL connection (decrypts the traffic).
3.  **Parsing**: The LB inspects the HTTP header (e.g., `Host: api.example.com`, `Path: /payments`).
4.  **Routing**: Based on the **Routing Logic** (e.g., Consistent Hashing), the LB selects a healthy server from the Payment Service pool.
5.  **Forwarding**: The LB forwards the request to the selected server via a new TCP connection (or a connection pool).
6.  **Response**: The server responds to the LB, which then encrypts the response and sends it back to the client.

### Handling Failures
*   **Backend Server Crash**: The Health Checker detects the failure $\rightarrow$ Server is removed from the active pool $\rightarrow$ Traffic is redistributed among remaining nodes.
*   **LB Failure (The SPOF Problem)**: 
    *   **Active-Passive Setup**: A primary LB handles traffic; a standby LB monitors the primary via a heartbeat. If the primary fails, the standby takes over the Virtual IP (VIP).
    *   **Active-Active Setup**: Multiple LBs share the load via DNS Round Robin or Anycast.
*   **Cascading Failure**: If one server dies, others might get overloaded and die too. **Solution**: Implement **Circuit Breakers** and **Rate Limiting** at the LB level.

---

## 5. Production Trade-offs

### Consistency vs. Availability (CAP Theorem)
In the context of session persistence (Sticky Sessions):
*   **Strict Consistency**: Ensuring a user *always* hits the same server to access local cache. This risks availability if that specific server crashes.
*   **Eventual Consistency/Stateless**: Using a distributed cache (Redis) for sessions. This allows the LB to route to *any* server, increasing availability and scalability at the cost of a slight network hop to the cache.

### Latency vs. Intelligence
*   **L4** provides the lowest possible latency because it doesn't "read" the data.
*   **L7** provides the most intelligence (can route based on user ID or device type) but introduces latency due to SSL termination and packet inspection.
*   **Hybrid Approach**: Use L4 for the entry point (high throughput) and L7 for internal microservice routing (high precision).

### Complexity Analysis of Routing Algorithms

| Algorithm | Time Complexity | Space Complexity | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Round Robin** | $O(1)$ | $O(1)$ | Basic load distribution |
| **Least Conn** | $O(1)$ or $O(\log N)$ | $O(N)$ | Heavyweight requests |
| **IP Hash** | $O(1)$ | $O(1)$ | Basic session stickiness |
| **Consistent Hashing**| $O(\log N)$ | $O(N)$ | Distributed Caching |

*(Where $N$ is the number of backend servers)*""",
    'solutions': """# System Design Guide: Load Balancer Routing Logic

## 1. Requirements & System Constraints

The objective is to design the routing logic for a high-performance Load Balancer (LB) capable of distributing incoming network traffic across a pool of backend servers to ensure reliability, availability, and optimal resource utilization.

### 1.1 Functional Requirements
*   **Routing Algorithms**: Support multiple distribution strategies:
    *   **Round Robin**: Sequential distribution.
    *   **Weighted Round Robin**: Distribution based on server capacity.
    *   **Least Connections**: Routing to the server with the fewest active requests.
    *   **Consistent Hashing**: Mapping requests to servers based on a key (e.g., Client IP, User ID) to ensure session persistence.
*   **Health Monitoring**: Continuously monitor backend server health and automatically remove unhealthy nodes from the rotation.
*   **Session Persistence (Sticky Sessions)**: Ensure a client is routed to the same backend server for the duration of a session.
*   **Dynamic Configuration**: Ability to add or remove backend servers without downtime.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency**: The routing decision must be made in microseconds to avoid becoming a bottleneck.
*   **High Availability**: The LB must not be a Single Point of Failure (SPOF).
*   **Scalability**: Capable of handling millions of requests per second (RPS).
*   **Fault Tolerance**: Graceful degradation if a subset of backend servers fails.

### 1.3 Scale Estimations
*   **Traffic**: 1 Million Requests Per Second (RPS).
*   **Backend Pool**: 10 to 1,000 servers per cluster.
*   **Latency Budget**: Routing overhead < 1ms.

---

## 2. High-Level Architecture

The system is split into two primary planes: the **Control Plane** (management and configuration) and the **Data Plane** (the high-speed request path).

### 2.1 Architecture Diagram

```mermaid
graph TD
    Client[Client] --> DNS[DNS / Global Server LB]
    DNS --> LB_DataPlane[LB Data Plane - Proxy/Router]
    
    subgraph "Control Plane"
        Admin[Admin API/Console] --> ConfigDB[(Config DB)]
        ConfigDB --> Orchestrator[Config Orchestrator]
        HealthChecker[Health Checker] --> ConfigDB
        Orchestrator --> LB_DataPlane
    end
    
    LB_DataPlane --> S1[Backend Server 1]
    LB_DataPlane --> S2[Backend Server 2]
    LB_DataPlane --> S3[Backend Server 3]
    
    HealthChecker -.-> S1
    HealthChecker -.-> S2
    HealthChecker -.-> S3
```

### 2.2 Component Descriptions
*   **LB Data Plane**: The "Hot Path." It intercepts packets, applies the routing logic stored in local memory, and forwards the request.
*   **Control Plane**: Manages the "Source of Truth." It handles the registration of servers and the definition of routing policies.
*   **Health Checker**: An active probe service that sends heartbeats (TCP/HTTP) to backends. If a server fails $N$ consecutive checks, it is marked "Unhealthy."
*   **Config Orchestrator**: Pushes configuration updates (e.g., new server lists) to the Data Plane using a pub/sub mechanism or a configuration provider (like etcd or Consul).

---

## 3. Detailed Design: Routing Logic

### 3.1 Routing Algorithm Implementations

#### A. Round Robin & Weighted Round Robin
*   **Logic**: Maintain an index pointer. For Weighted RR, create a virtual list where servers appear proportional to their weight.
*   **Complexity**: $O(1)$.
*   **Use Case**: Homogeneous workloads where all requests have similar resource costs.

#### B. Least Connections
*   **Logic**: Maintain a counter of active connections per server. The LB selects the server with the minimum count.
*   **Complexity**: $O(1)$ with a Min-Heap or $O(N)$ for small $N$.
*   **Use Case**: Long-lived connections (e.g., WebSockets, database streams).

#### C. Consistent Hashing
*   **Logic**: Map servers and request keys (e.g., `hash(client_ip)`) onto a logical ring (0 to $2^{32}-1$). The request is routed to the first server encountered moving clockwise on the ring.
*   **Complexity**: $O(\log N)$ using binary search on the ring.
*   **Use Case**: Statefull services, caching layers (to maximize cache hit rates).

### 3.2 Database Schema (Control Plane)

Since configuration changes are infrequent compared to request volume, a Relational Database (PostgreSQL) is used for strong consistency, while the Data Plane uses an in-memory cache.

**Table: `clusters`**
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `cluster_id` | UUID | PK | Unique ID for the server group |
| `name` | String | Index | Human-readable name |
| `routing_policy` | Enum | - | RR, WRR, LC, CH |
| `health_check_interval`| Int | - | Seconds between probes |

**Table: `backend_nodes`**
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `node_id` | UUID | PK | Unique ID for the server |
| `cluster_id` | UUID | FK | Reference to the cluster |
| `ip_address` | String | - | Server IP |
| `port` | Int | - | Server Port |
| `weight` | Int | - | Weight for WRR |
| `status` | Enum | Index | Healthy, Unhealthy, Draining |

---

## 4. Core API Design

The Control Plane provides REST endpoints for administrative tasks.

### 4.1 Add Backend Node
`POST /api/v1/clusters/{cluster_id}/nodes`
**Request:**
```json
{
  "ip_address": "10.0.0.5",
  "port": 8080,
  "weight": 10
}
```
**Response:** `201 Created`

### 4.2 Update Routing Policy
`PATCH /api/v1/clusters/{cluster_id}`
**Request:**
```json
{
  "routing_policy": "CONSISTENT_HASHING"
}
```
**Response:** `200 OK`

### 4.3 Get Cluster Health
`GET /api/v1/clusters/{cluster_id}/health`
**Response:**
```json
{
  "cluster_id": "uuid-123",
  "healthy_nodes": 45,
  "unhealthy_nodes": 2,
  "nodes": [
    {"node_id": "n1", "status": "HEALTHY", "latency": "12ms"},
    {"node_id": "n2", "status": "UNHEALTHY", "latency": "N/A"}
  ]
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 L4 vs L7 Load Balancing
*   **L4 (Transport Layer)**: Routes based on IP and Port. Faster, less CPU intensive, no visibility into HTTP headers. (e.g., Maglev, LVS).
*   **L7 (Application Layer)**: Routes based on URL, Cookies, or Headers. Allows for "Canary Deployments" and "A/B Testing." (e.g., Nginx, HAProxy, Envoy).

### 5.2 Avoiding the LB Single Point of Failure
*   **Anycast IP**: Use BGP to announce the same IP address from multiple LB nodes globally.
*   **VRRP (Virtual Router Redundancy Protocol)**: A "Master-Backup" setup where the backup takes over the Virtual IP (VIP) if the master fails.

### 5.3 Health Check Optimization
*   **Active Probing**: LB sends periodic pings.
*   **Passive Probing**: LB observes actual traffic. If a server returns five consecutive 5xx errors, it is marked unhealthy.

### 5.4 Handling "Thundering Herd"
When a server recovers from failure, it may be overwhelmed by a sudden surge of traffic.
*   **Slow Start Mode**: Gradually increase the weight of a newly healthy server over a period of time (e.g., 0% $\rightarrow$ 100% over 2 minutes).

---

## 6. Trade-off Analysis

| Trade-off | Selection | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs. Availability** | **Availability (AP)** | In a routing scenario, it is better to route a request to a slightly suboptimal server (Availability) than to fail the request because the LB is waiting for the latest config update (Consistency). |
| **Least Conn vs. Round Robin** | **Round Robin** | RR has $O(1)$ complexity and requires no shared state between LB instances. Least Conn requires tracking global active connections, which adds overhead in distributed LB setups. |
| **L4 vs L7** | **Hybrid** | Use L4 for initial high-volume entry (performance) and L7 for internal microservice routing (flexibility/logic). |
| **Stateful vs Stateless** | **Stateless** | By using Consistent Hashing based on the request key rather than storing session IDs in the LB memory, the LB remains stateless and easier to scale horizontally. |""",
}

# Load Balancer Design HLD

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

*(Where $N$ is the number of backend servers)*
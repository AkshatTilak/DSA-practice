# API Gateway and Load Balancer HLD

This study guide provides a deep dive into the design of an **API Gateway** and a **Load Balancer**, two fundamental components of any modern distributed system. While often used together, they serve distinct purposes: the Load Balancer focuses on **traffic distribution**, while the API Gateway focuses on **request orchestration and policy enforcement**.

---

## 1. Overview & System Requirements

### 1.1 Functional Requirements
The system must act as the single entry point for all client requests and ensure they are routed to the correct backend services efficiently and securely.

*   **Request Routing**: Route requests to the appropriate microservice based on the path or headers.
*   **Authentication & Authorization**: Validate JWTs, API keys, or OAuth tokens before the request reaches the backend.
*   **Rate Limiting & Throttling**: Protect backend services from being overwhelmed (DoS protection and quota management).
*   **Protocol Translation**: Convert between different protocols (e.g., HTTP/REST $\rightarrow$ gRPC, WebSocket $\rightarrow$ HTTP).
*   **Response Aggregation**: Combine data from multiple microservices into a single response to reduce client round-trips (BFF - Backend for Frontend pattern).
*   **Load Balancing**: Evenly distribute incoming traffic across a pool of healthy server instances.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency**: The gateway must introduce minimal overhead (typically $< 10\text{ms}$).
*   **High Availability**: The system must be "Always On" (99.99% SLA); it is a single point of failure (SPOF) if not designed correctly.
*   **Scalability**: Must handle massive spikes in traffic (e.g., flash sales) via horizontal scaling.
*   **Durability & Observability**: Centralized logging, metrics (Prometheus), and tracing (Jaeger/Zipkin) for all entering requests.

### 1.3 Scale Assumptions
*   **Daily Active Users (DAU)**: 100 Million.
*   **Peak QPS**: 1 Million requests per second.
*   **Average Payload**: 2 KB.
*   **Network Latency Budget**: Total overhead added by Gateway/LB should be negligible compared to backend processing.

---

## 2. High-Level System Architecture

The architecture follows a layered approach to separate concerns between network-level routing and application-level orchestration.

### Architecture Diagram (Conceptual Flow)
`Client` $\rightarrow$ `DNS` $\rightarrow$ `External L4 Load Balancer` $\rightarrow$ `API Gateway Cluster` $\rightarrow$ `Internal L7 Load Balancer/Service Mesh` $\rightarrow$ `Microservices`

### Component Breakdown

| Component | Primary Role | Responsibility |
| :--- | :--- | :--- |
| **DNS** | Resolution | Maps domain (api.example.com) to the VIP of the External LB. |
| **L4 Load Balancer** | Traffic Distribution | High-throughput, low-latency routing based on IP and TCP/UDP ports. |
| **API Gateway** | Orchestration | Auth, Rate Limiting, Routing, Transformation, and Monitoring. |
| **Service Registry** | Discovery | Stores the current healthy IP addresses of backend services (e.g., Consul, Eureka). |
| **Distributed Cache** | State Store | Stores rate limit counters and session tokens (e.g., Redis). |
| **Backend Services** | Business Logic | The actual microservices providing the requested data. |

---

## 3. Key HLD Concepts & Component Design

### 3.1 Load Balancer: L4 vs. L7
The design utilizes both layers for maximum efficiency.

*   **Layer 4 (Transport Layer)**:
    *   **Mechanism**: Operates at the TCP/UDP level. It doesn't inspect the HTTP packet contents.
    *   **Pros**: Extremely fast, low CPU usage, handles millions of connections.
    *   **Use Case**: The very first entry point to distribute traffic across multiple API Gateway instances.
*   **Layer 7 (Application Layer)**:
    *   **Mechanism**: Operates at the HTTP/HTTPS level. It can inspect headers, cookies, and URL paths.
    *   **Pros**: Intelligent routing (e.g., `/users` $\rightarrow$ User Service, `/orders` $\rightarrow$ Order Service).
    *   **Use Case**: The API Gateway itself acts as an L7 LB to route to microservices.

### 3.2 Load Balancing Algorithms
To ensure optimal distribution, we choose algorithms based on the use case:
*   **Round Robin**: Simple, works if all backends have equal capacity.
*   **Least Connections**: Routes to the server with the fewest active requests (best for long-lived connections).
*   **Consistent Hashing**: Ensures a specific client (via IP or UserID) always hits the same backend. Crucial for local caching.
*   **Weighted Round Robin**: Accounts for servers with different hardware specs (e.g., a 32-core server gets more traffic than an 8-core server).

### 3.3 API Gateway Core Logic
The Gateway implements a **Filter Chain Pattern**:
1.  **Request Filter**: `SSL Termination` $\rightarrow$ `Auth Check` $\rightarrow$ `Rate Limiter` $\rightarrow$ `Request Transformer`.
2.  **Routing Logic**: Consults the **Service Registry** $\rightarrow$ Selects endpoint via **LB Algorithm**.
3.  **Response Filter**: `Log Response` $\rightarrow$ `Header Manipulation` $\rightarrow$ `Response Compression`.

### 3.4 Distributed Rate Limiting
To prevent abuse, we implement a **Token Bucket** or **Sliding Window Log** algorithm using **Redis**.
*   **Why Redis?** Centralized state is required because a client might hit Gateway Node A for request 1 and Gateway Node B for request 2.
*   **Optimization**: To avoid the "Redis Bottleneck," we use **local batching**. Each gateway node tracks requests locally and syncs with Redis every $N$ milliseconds.

---

## 4. Data Flows & Fault Tolerance

### 4.1 Step-by-Step Request Walkthrough
1.  **Client** sends an HTTPS request to `api.example.com/v1/orders`.
2.  **DNS** resolves the domain to the **L4 Load Balancer's** Virtual IP (VIP).
3.  **L4 LB** forwards the TCP packet to one of the available **API Gateway** instances.
4.  **API Gateway** performs the following:
    *   **Auth**: Extracts JWT $\rightarrow$ Validates signature $\rightarrow$ Checks permissions.
    *   **Rate Limit**: Checks Redis if `user_123` has exceeded 100 requests/min.
    *   **Routing**: Sees path `/v1/orders` $\rightarrow$ Queries **Service Registry** $\rightarrow$ Gets a list of Order Service IPs.
    *   **LB**: Uses **Consistent Hashing** to pick `Order-Service-Node-3`.
5.  **Order Service** processes the request and returns the data.
6.  **API Gateway** transforms the response (e.g., removes internal IDs) and returns it to the client.

### 4.2 Fault Tolerance & Reliability
*   **Health Checks**: The LB and Gateway constantly ping backends (`/health` endpoint). If a node fails, it is removed from the rotation immediately.
*   **Circuit Breaker (e.g., Resilience4j)**: If the Order Service is timing out (50% failure rate), the Gateway "opens the circuit" and returns a cached response or a `503 Service Unavailable` immediately, preventing a **cascading failure**.
*   **Retries with Exponential Backoff**: If a request fails due to a transient network glitch, the Gateway retries the request on a *different* node.
*   **Fail-Open Rate Limiting**: If the Redis cluster goes down, the Gateway is configured to "fail-open" (allow all requests) rather than blocking all traffic, prioritizing availability over strict limiting.

---

## 5. Production Trade-offs

### 5.1 CAP Theorem Application
In the context of a distributed API Gateway/Rate Limiter:
*   **Consistency vs. Availability**: For rate limiting, we prioritize **Availability (AP)**. It is better to allow a few extra requests over the limit (Eventual Consistency) than to block all traffic because the rate-limit counter couldn't be synced across regions.

### 5.2 Latency vs. Feature Richness
*   **The Trade-off**: Every filter added to the Gateway (Auth, Logging, Transformation, Validation) adds milliseconds to the request.
*   **The Solution**: Use a **Sidecar Proxy (Service Mesh)** like Istio or Linkerd. Move "infrastructure" concerns (mTLS, Retries) to the sidecar and keep the API Gateway focused on "edge" concerns (Auth, Public API versioning).

### 5.3 Centralized vs. Decentralized Gateway
| Approach | Pros | Cons |
| :--- | :--- | :--- |
| **Centralized** | Easy to manage, single point of security/audit. | Potential SPOF, can become a performance bottleneck. |
| **Decentralized (BFF)** | Tailored responses for Mobile vs. Web, reduced blast radius. | Higher operational overhead (multiple gateways to manage). |

## Summary Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **L4 Routing** | $O(1)$ | $O(1)$ | Simple packet forwarding. |
| **L7 Routing** | $O(1)$ | $O(N)$ | Map lookup where $N$ is number of routes. |
| **Rate Limiting** | $O(1)$ | $O(U)$ | Redis `INCR` where $U$ is number of users. |
| **Consistent Hashing** | $O(\log V)$ | $O(V)$ | $V$ is number of virtual nodes in the ring. |
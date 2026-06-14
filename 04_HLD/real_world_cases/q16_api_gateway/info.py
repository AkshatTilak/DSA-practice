INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design API Gateway and Load Balancer.',
    'groups': ['Real-World Systems', 'Networking'],
    'readme_content': """# API Gateway and Load Balancer HLD

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
| **Consistent Hashing** | $O(\log V)$ | $O(V)$ | $V$ is number of virtual nodes in the ring. |""",
    'solutions': """# System Design: API Gateway and Load Balancer

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Request Routing:** Route incoming HTTP requests to the appropriate backend microservice based on the path, host, or headers.
*   **Authentication & Authorization:** Centralize security checks (JWT validation, API key verification) before requests reach backend services.
*   **Rate Limiting & Throttling:** Prevent system abuse by limiting the number of requests a client can make within a time window.
*   **Load Balancing:** Distribute traffic across multiple instances of a service to ensure high availability and optimal resource utilization.
*   **Protocol Translation:** Convert between different protocols (e.g., REST/HTTP to gRPC or WebSockets).
*   **Response Aggregation:** Combine results from multiple microservices into a single response to reduce client-side round trips.
*   **Observability:** Centralized logging, metrics collection, and distributed tracing (injection of Trace IDs).

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** The gateway is in the critical path of every request; overhead must be minimal (typically < 10-30ms).
*   **High Availability:** The gateway must be a highly available cluster; if the gateway goes down, the entire ecosystem is unreachable.
*   **Scalability:** Must scale horizontally to handle millions of requests per second (RPS).
*   **Fault Tolerance:** Implement circuit breakers to prevent a failing backend service from cascading failure across the system.

### 1.3 Scale Estimations (HLD)
*   **Traffic:** 100,000 requests per second (RPS) average; 500,000 RPS peak.
*   **Latency Budget:** $\le 20\text{ms}$ overhead added by the gateway.
*   **Backend Services:** 50+ distinct microservices.
*   **Concurrent Connections:** Millions of keep-alive TCP connections.

---

## 2. High-Level Architecture

The system employs a multi-tier approach. A Layer 4 (L4) Load Balancer distributes traffic across a cluster of API Gateway instances (Layer 7). The API Gateway then interacts with a Service Registry to find healthy backend pods.

### 2.1 Architecture Diagram

```mermaid
graph TD
    Client[Client/Mobile/Web] --> L4LB[L4 Load Balancer - Maglev/AWS NLB]
    L4LB --> AGW1[API Gateway Instance 1]
    L4LB --> AGW2[API Gateway Instance 2]
    L4LB --> AGWn[API Gateway Instance N]

    subgraph "API Gateway Internal Logic"
        AGW1 --> FilterChain[Filter Chain: Auth -> Rate Limit -> Transformation]
        FilterChain --> Router[Router/Dispatcher]
    end

    Router --> SR[Service Registry - Consul/Eureka]
    Router --> S1[Service A - Instance 1]
    Router --> S2[Service A - Instance 2]
    Router --> S3[Service B - Instance 1]

    AGW1 -.-> Cache[(Redis - Rate Limit/Auth Cache)]
    AGW1 -.-> ConfigDB[(Config DB - Routes/Policies)]
```

### 2.2 Component Interaction
1.  **L4 Load Balancer:** Handles TCP/UDP traffic. It uses a simple hashing algorithm (like IP hash) to distribute traffic to the API Gateway cluster.
2.  **API Gateway Cluster:** A set of stateless nodes. Each node runs a "Filter Chain."
3.  **Filter Chain:**
    *   **Auth Filter:** Validates JWTs or API keys.
    *   **Rate Limit Filter:** Checks Redis for the current request count against the allowed quota.
    *   **Transformation Filter:** Modifies headers or rewrites paths (e.g., `/api/v1/users` $\rightarrow$ `/users-service/v1`).
4.  **Service Registry:** Provides the current IP addresses of healthy backend service instances.
5.  **Router:** Selects a backend instance using a Load Balancing algorithm (e.g., Round Robin, Least Connections).

---

## 3. Detailed Database Schema Design

The API Gateway is primarily a data-plane component (stateless), but it requires a control-plane to manage configurations and a fast store for stateful constraints (rate limiting).

### 3.1 Configuration Store (SQL - PostgreSQL)
Used to manage routing rules, API keys, and global policies. SQL is chosen for strong consistency and complex querying of administrative rules.

**Table: `routes`**
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `route_id` | UUID | PK | Unique identifier for the route |
| `path_pattern` | VARCHAR | Indexed | Regex or glob pattern (e.g., `/api/users/*`) |
| `target_service` | VARCHAR | Not Null | Name of the backend service (for Registry lookup) |
| `timeout_ms` | INT | Default 5000 | Request timeout |
| `is_active` | BOOLEAN | Default True | Kill-switch for the route |

**Table: `api_keys`**
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `key_hash` | VARCHAR | PK | SHA-256 hash of the API key |
| `client_id` | UUID | FK | Reference to client profile |
| `tier` | VARCHAR | Not Null | 'Free', 'Premium', 'Enterprise' |
| `expires_at` | TIMESTAMP | Indexed | Key expiration date |

### 3.2 Rate Limit Store (NoSQL - Redis)
Redis is used for its atomic increments (`INCR`) and TTL (Time-to-Live) capabilities, essential for sliding-window or fixed-window rate limiting.

**Key Structure:**
*   **Key:** `ratelimit:{client_id}:{endpoint_id}:{window_timestamp}`
*   **Value:** `Integer` (Current request count)
*   **TTL:** 60 seconds (for a 1-minute window).

---

## 4. Core API Design (Control Plane)

The API Gateway is managed by a Control Plane API that allows admins to update routing and policies without restarting the gateway instances.

### 4.1 Update Route
`POST /admin/routes`
**Request:**
```json
{
  "path_pattern": "/api/v1/payments/*",
  "target_service": "payments-service",
  "timeout_ms": 2000,
  "auth_required": true,
  "rate_limit_policy": "payment_tier_policy"
}
```
**Response:** `201 Created`

### 4.2 Update Rate Limit Policy
`PUT /admin/policies/{policy_id}`
**Request:**
```json
{
  "policy_id": "payment_tier_policy",
  "requests_per_second": 100,
  "burst_capacity": 150
}
```
**Response:** `200 OK`

---

## 5. Scalability & Advanced Topics

### 5.1 Load Balancing Algorithms
*   **Round Robin:** Simple, works well if all backend instances have identical specs.
*   **Least Connections:** Routes to the instance with the fewest active requests; better for long-lived connections.
*   **Consistent Hashing:** Routes based on a request attribute (e.g., `user_id`). Ensures a specific user always hits the same backend instance, enabling effective local caching.

### 5.2 Rate Limiting Strategy
*   **Token Bucket:** Allows for bursts of traffic while maintaining a steady average rate.
*   **Distributed Rate Limiting:** To avoid "local" limits on individual gateway nodes, a global Redis cluster is used. To reduce Redis latency, the gateway can use **Local Batching**: increment the counter locally for 100ms, then sync to Redis in one call.

### 5.3 Fault Tolerance & Reliability
*   **Circuit Breaker:** If a backend service returns $5xx$ errors above a certain threshold (e.g., 50% failure over 10 seconds), the gateway "opens" the circuit and fails fast for that service, preventing resource exhaustion.
*   **Retries with Exponential Backoff:** For idempotent requests (GET, PUT), the gateway can retry a failed request on a different backend instance.
*   **Health Checks:** The gateway continuously polls `/health` endpoints of backends or relies on a Heartbeat mechanism from the Service Registry.

### 5.4 Caching Strategy
*   **Edge Caching:** Cache responses for static or semi-static data (e.g., `/api/v1/countries`) using a TTL.
*   **Cache Key:** `hash(HTTP_Method + Path + QueryParams + Auth_Tier)`.

---

## 6. Trade-off Analysis

| Trade-off | Decision | Reasoning |
| :--- | :--- | :--- |
| **Latency vs. Security** | Filter Chain | We accept a small latency hit (ms) to ensure all requests are authenticated and rate-limited before they hit the internal network. |
| **Consistency vs. Availability (Rate Limiting)** | Eventual Consistency | We use Redis. If Redis is temporarily unavailable, the gateway fails "open" (allows traffic) rather than "closed" (blocking all users), prioritizing availability. |
| **L4 LB vs L7 LB (at entry)** | L4 at entry $\rightarrow$ L7 Gateway | L4 (NLB) is significantly faster and handles TCP millions of packets. L7 (Gateway) provides the intelligence (routing, auth) needed for microservices. |
| **SQL vs NoSQL (Config)** | SQL for Config, NoSQL for State | Routing rules change rarely and require relational integrity (SQL). Rate limits change millions of times per second (Redis). |
| **Centralized vs Distributed Gateway** | Centralized Cluster | While a "Sidecar" (Service Mesh) is more granular, a centralized API Gateway is simpler to manage for external-facing traffic and provides a single point of security enforcement. |""",
}

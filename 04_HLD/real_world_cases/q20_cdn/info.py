INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design CDN (Content Delivery Network).',
    'groups': ['Real-World Systems', 'Networking'],
    'readme_content': """# Content Delivery Network (CDN) HLD

A **Content Delivery Network (CDN)** is a geographically distributed network of proxy servers and their data centers. The primary goal is to provide high availability and performance by distributing content closer to end-users, thereby reducing latency, minimizing bandwidth costs for the origin server, and increasing the overall reliability of the application.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Content Delivery:** Serve static assets (images, JS, CSS, videos) and potentially dynamic content to users with minimum latency.
*   **Caching:** Store copies of content at the "edge" of the network (PoPs).
*   **Cache Invalidation:** Ability to purge or update content across all edge nodes when the source content changes.
*   **Origin Integration:** Seamlessly fetch content from the origin server upon a cache miss.
*   **Traffic Routing:** Intelligent routing to direct users to the nearest available edge server.

### Non-Functional Requirements
*   **Ultra-Low Latency:** Minimize the Round Trip Time (RTT) by reducing the physical distance between the user and the data.
*   **High Availability:** The system must be resilient to PoP (Point of Presence) failures.
*   **Massive Scalability:** Handle millions of requests per second (RPS) and petabytes of data.
*   **Durability:** Ensure content is not lost, though edge caches are transient; the origin remains the source of truth.
*   **Eventual Consistency:** Updates to content at the origin may take time to propagate to all edge nodes.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | $10^8+$ users |
| **Request Volume** | $10^6 - 10^7$ Requests Per Second (RPS) |
| **Storage Volume** | Petabytes of cached data across global PoPs |
| **Latency Goal** | $< 50\text{ms}$ for cached content |

---

## 2. High-Level System Architecture

The architecture is divided into the **Data Plane** (handling the actual requests) and the **Control Plane** (handling configuration and purges).

### Architecture Diagram Components

1.  **Client:** The end-user browser or application requesting a resource.
2.  **DNS & GSLB (Global Server Load Balancer):** The "brains" that decide which edge location the user should be routed to based on geography, network health, and server load.
3.  **PoP (Point of Presence):** A physical data center located in a specific city/region containing multiple cache servers.
4.  **Edge Cache Servers:** Servers that store content in RAM (L1) and SSD (L2) for rapid retrieval.
5.  **Origin Server:** The authoritative source of the content (e.g., an S3 bucket or a web server).
6.  **Control Plane:** Manages the distribution of configuration and triggers cache invalidation (Purge API).

### The High-Level Flow
$\text{Client} \rightarrow \text{DNS/GSLB} \rightarrow \text{Edge PoP} \rightarrow (\text{if miss}) \rightarrow \text{Origin Server}$

---

## 3. Key HLD Concepts & Component Design

### A. Request Routing (How to find the nearest Edge)
To minimize latency, the system must map a user's IP to the nearest PoP.
*   **Anycast DNS:** Multiple servers share the same IP address. BGP (Border Gateway Protocol) routes the packet to the "topologically nearest" node. This is the industry standard for CDNs.
*   **Geo-DNS:** The DNS server looks up the user's IP in a database and returns the IP address of the PoP closest to that geography.
*   **HTTP Redirection:** The initial request hits a central load balancer, which sends a `302 Redirect` to a specific edge server. (Slow, used less frequently).

### B. Caching Strategy
Edge servers use a multi-tiered storage approach to balance speed and capacity:
*   **L1 (RAM):** Extremely fast, stores the most "hot" objects.
*   **L2 (SSD/NVMe):** Larger capacity, slightly slower than RAM.
*   **Eviction Policy:** **LRU (Least Recently Used)** is most common. If the cache is full, the least accessed item is removed.

### C. Cache Invalidation & Consistency
How does the CDN know the content at the origin has changed?
*   **TTL (Time to Live):** The origin sets an `Expires` or `Cache-Control: max-age` header. The edge server deletes the item once the TTL expires.
*   **Purging (Push Model):** The origin sends an API call to the CDN Control Plane to explicitly delete a specific URL across all PoPs.
*   **Validation (Conditional GET):** The edge server sends an `If-Modified-Since` request to the origin. If the content hasn't changed, the origin returns `304 Not Modified`, saving bandwidth.

### D. Technology Selection
| Component | Technology | Why? |
| :--- | :--- | :--- |
| **Edge Storage** | Redis / Memcached / Local Disk | Low latency retrieval of key-value pairs (URL $\rightarrow$ Content). |
| **Routing** | BGP / Anycast | Fastest way to route packets at the network layer. |
| **Control Plane** | Kafka + NoSQL | Kafka for broadcasting purge events to thousands of edge nodes; NoSQL for storing global config. |
| **Origin Storage** | AWS S3 / Azure Blob | High durability and availability for the source of truth. |

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Walkthrough (The Read Path)
1.  **DNS Lookup:** The client requests `images.example.com/logo.png`.
2.  **GSLB Routing:** The DNS system (using Anycast) routes the request to the nearest PoP.
3.  **Edge Cache Check:** The request hits an Edge Server.
    *   **Cache Hit:** The server returns the image immediately. **(Latency: $\sim 10\text{--}30\text{ms}$)**.
    *   **Cache Miss:** The server forwards the request to the Origin Server.
4.  **Origin Fetch:** The Origin returns the image to the Edge Server.
5.  **Cache Populate:** The Edge Server stores the image (based on TTL) and returns it to the client. **(Latency: $\sim 100\text{ms} - 2\text{s}$)**.

### Fault Tolerance & Resilience
*   **PoP Failure:** If an entire PoP goes offline, BGP automatically reroutes traffic to the next closest PoP.
*   **Server Failure within PoP:** A local Load Balancer (e.g., Nginx or HAProxy) detects a health check failure and redistributes traffic to other servers in the same PoP.
*   **Origin Failure:**
    *   **Stale-While-Revalidate:** The CDN continues to serve expired content if the origin is down, rather than returning a 5xx error.
    *   **Origin Shield:** An intermediate caching layer between the Edge and the Origin to prevent "thundering herd" problems (where millions of requests hit the origin simultaneously after a cache expiry).

---

## 5. Production Trade-offs

### Consistency vs. Latency (CAP Theorem)
A CDN prioritizes **Availability** and **Partition Tolerance (AP)** over **Consistency**.
*   **Trade-off:** It is acceptable if a user in Tokyo sees a version of a page that is 5 minutes older than a user in New York. Forcing strong consistency would require every edge node to synchronize before serving, which would destroy the latency benefits of a CDN.

### Push vs. Pull Caching
| Feature | Pull (On-Demand) | Push (Pre-fetching) |
| :--- | :--- | :--- |
| **Mechanism** | Edge fetches content on first miss. | Origin pushes content to edge proactively. |
| **Storage Efficiency** | High (only stores what is requested). | Low (stores content that might not be used). |
| **Initial Latency** | High (first user suffers a miss). | Low (content is already there). |
| **Use Case** | Long-tail content, massive libraries. | High-profile releases (e.g., new movie trailer). |

### Complexity Analysis
*   **Time Complexity:**
    *   Cache Hit: $O(1)$ lookup in hash map/local storage.
    *   Cache Miss: $O(1) + \text{RTT to Origin}$.
*   **Space Complexity:** $O(N \times M)$ where $N$ is the number of PoPs and $M$ is the amount of cached data per PoP.""",
    'solutions': """# System Design: Content Delivery Network (CDN)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Content Delivery:** Serve static assets (images, JS, CSS, videos) to users from the nearest geographical location to minimize latency.
*   **Content Acquisition:** 
    *   **Pull Model:** Automatically fetch content from the origin server upon the first request (cache miss).
    *   **Push Model:** Allow origin servers to proactively push content to edge nodes.
*   **Cache Invalidation:** Provide a mechanism to purge or update stale content across the global network.
*   **Request Routing:** Route users to the optimal Edge PoP (Point of Presence) based on latency, geography, or server health.
*   **Analytics:** Track requests, cache hit/miss ratios, and bandwidth usage.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** The primary goal is to reduce Time to First Byte (TTFB).
*   **High Availability:** The system must be resilient to PoP failures; traffic should failover to the next closest node.
*   **Scalability:** Support millions of requests per second (RPS) and petabytes of cached data.
*   **Eventual Consistency:** Content updates do not need to be instantaneous globally, but purge requests should propagate within seconds/minutes.

### 1.3 Scale Estimations
*   **Traffic:** Assume 10 million requests per second globally.
*   **Content Size:** Average asset size 500KB; total library size in petabytes.
*   **PoPs:** 50–100 global locations.
*   **Read/Write Ratio:** Extremely read-heavy (10,000:1).

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **DNS Resolver / Request Router:** Uses Anycast DNS or Geo-DNS to map the user's IP to the closest Edge PoP.
2.  **Edge Server (PoP):** A cluster of caching servers that store content in memory (L1) and SSDs (L2).
3.  **Origin Server:** The customer's primary server containing the authoritative version of the content.
4.  **Control Plane:** The management layer used for configuration, monitoring, and processing purge requests.
5.  **Purge Queue:** A distributed message bus used to propagate invalidation signals to all Edge servers.

### 2.2 Architecture Diagram

```mermaid
graph TD
    User((User)) --> DNS[DNS / Anycast Router]
    DNS --> PoP1[Edge PoP - New York]
    DNS --> PoP2[Edge PoP - London]
    DNS --> PoP3[Edge PoP - Tokyo]

    subgraph "Edge PoP (e.g., New York)"
        LB[Load Balancer] --> CacheSrv1[Cache Server 1]
        LB --> CacheSrv2[Cache Server 2]
        CacheSrv1 --> LocalCache[(Local SSD/RAM)]
    end

    CacheSrv1 -- Cache Miss --> Origin[Origin Server]
    
    subgraph "Control Plane"
        Admin[Admin API] --> ConfigDB[(Config DB)]
        Admin --> PurgeQueue[Purge Queue/Message Bus]
    end

    PurgeQueue --> PoP1
    PurgeQueue --> PoP2
    PurgeQueue --> PoP3
    
    CacheSrv1 --> Analytics[Analytics Engine]
```

### 2.3 Request Flow
1.  **DNS Resolution:** The user requests `static.example.com/image.jpg`. The DNS router identifies the user's location via IP and returns the IP of the nearest PoP.
2.  **Edge Request:** The user connects to the PoP's Load Balancer, which forwards the request to a Cache Server.
3.  **Cache Check:**
    *   **Hit:** Content is returned immediately from RAM or SSD.
    *   **Miss:** The Edge server requests the content from the Origin Server, stores a copy locally (based on TTL), and serves it to the user.
4.  **Purge Flow:** An administrator triggers a purge via the Control Plane $\rightarrow$ Message is sent to the Purge Queue $\rightarrow$ All PoPs receive the signal and evict the specific object from their local cache.

---

## 3. Detailed Database Schema Design

The CDN requires two distinct types of storage: a **Configuration Store** (Consistency) and an **Analytics Store** (Throughput).

### 3.1 Configuration Store (SQL - PostgreSQL)
Used for managing customer accounts, domain mappings, and TTL settings.

**Table: `customers`**
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | UUID | PK | Unique identifier for the client |
| `account_name` | String | | Company name |
| `api_key` | String | Index | For authentication |

**Table: `cdn_configs`**
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `config_id` | UUID | PK | Unique config ID |
| `customer_id` | UUID | FK | Link to customer |
| `domain` | String | Index | The domain being served (e.g., `cdn.example.com`) |
| `origin_url` | String | | Where to fetch content from |
| `default_ttl` | Integer | | Default cache duration in seconds |

### 3.2 Analytics Store (NoSQL - ClickHouse or Cassandra)
Because the volume of logs is massive, a column-oriented database is used for time-series analysis.

**Table: `request_logs`**
| Field | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | DateTime | Event time (Primary Sort Key) |
| `pop_id` | String | Which PoP served the request |
| `url` | String | The requested resource |
| `status` | Integer | HTTP Status (200, 404, etc.) |
| `cache_status` | Enum | HIT, MISS, EXPIRED |
| `latency` | Integer | Time taken to serve in ms |
| `client_ip` | String | User's IP for geo-analysis |

### 3.3 Reasoning
*   **SQL for Config:** Configuration changes are infrequent but must be consistent. ACID properties ensure that when a domain is added, it is correctly mapped.
*   **NoSQL for Analytics:** We are writing millions of rows per second. ClickHouse allows for high-compression and lightning-fast aggregations (e.g., "What was the hit rate in London last hour?").

---

## 4. Core API Design

### 4.1 Content Management API
Used by customers to manage their CDN settings.

**`POST /v1/configs`**
*   **Description:** Set up a new origin mapping.
*   **Payload:**
    ```json
    {
      "domain": "static.example.com",
      "origin_url": "https://origin.example.com/assets",
      "default_ttl": 3600
    }
    ```
*   **Response:** `201 Created`

**`DELETE /v1/purge`**
*   **Description:** Invalidate specific assets or wildcards.
*   **Payload:**
    ```json
    {
      "paths": ["/images/logo.png", "/css/*"],
      "purge_type": "hard" 
    }
    ```
*   **Response:** `202 Accepted` (Processing asynchronously)

### 4.2 Analytics API
**`GET /v1/stats?domain=static.example.com&start=...&end=...`**
*   **Response:**
    ```json
    {
      "cache_hit_ratio": 0.94,
      "total_requests": 15000000,
      "bandwidth_gb": 4500,
      "top_pops": [{"pop": "NYC", "hits": 5000000}, {"pop": "LON", "hits": 4000000}]
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Caching Strategies
*   **Multi-tier Caching:** 
    *   **L1 (RAM):** Hot assets stored in memory (Redis/Memcached) for microsecond access.
    *   **L2 (SSD):** Larger set of assets stored on NVMe drives.
*   **Eviction Policy:** **LRU (Least Recently Used)** is standard. For very high-traffic sites, **LFU (Least Frequently Used)** prevents "one-hit wonders" from polluting the cache.
*   **Cache Warming:** For anticipated traffic spikes (e.g., a movie release), the Control Plane can "push" content to the edges before users request it.

### 5.2 Request Routing (The "Magic")
*   **Anycast DNS:** Multiple PoPs advertise the same IP address via BGP. The internet routing infrastructure naturally sends the packet to the "closest" PoP in terms of network hops.
*   **Geo-DNS:** The DNS server looks up the user's IP in a Geo-IP database and returns the IP of the PoP physically closest to the user.

### 5.3 Handling the "Thundering Herd" Problem
If a highly popular object expires, thousands of concurrent requests might hit the Origin Server simultaneously.
*   **Request Collapsing:** The Edge server ensures only *one* request for a specific object is sent to the Origin; others wait for the response and share the result.

### 5.4 Fault Tolerance
*   **Health Checks:** The Control Plane constantly pings PoPs. If a PoP is unresponsive, the DNS router removes that PoP's IP from the rotation.
*   **Origin Shield:** A mid-tier caching layer between the Edge PoPs and the Origin. This reduces the load on the Origin server by aggregating requests from multiple PoPs.

---

## 6. Trade-off Analysis

| Trade-off | Decision | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs. Latency** | **Latency (AP)** | In a CDN, serving a slightly stale image is better than making a user wait 500ms for a round-trip to the origin. Eventual consistency is accepted. |
| **Push vs. Pull** | **Hybrid** | Pull is effortless for customers; Push is necessary for massive files (Videos/Game Patches) to avoid origin overload during the first wave of requests. |
| **Storage vs. Cost** | **Aggressive Eviction** | Storing every file at every PoP is impossible. We trade off a slightly lower hit rate (via LRU eviction) to keep hardware costs manageable. |
| **Anycast vs. Unicast** | **Anycast** | Anycast provides seamless failover and lower latency without requiring complex client-side logic or frequent DNS TTL refreshes. |""",
}

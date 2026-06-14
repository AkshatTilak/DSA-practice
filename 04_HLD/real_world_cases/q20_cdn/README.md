# Content Delivery Network (CDN) HLD

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
*   **Space Complexity:** $O(N \times M)$ where $N$ is the number of PoPs and $M$ is the amount of cached data per PoP.
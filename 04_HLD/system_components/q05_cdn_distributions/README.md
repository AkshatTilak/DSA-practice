# Content Delivery Network (CDN) Distributions HLD

A **Content Delivery Network (CDN)** is a geographically distributed network of proxy servers and their data centers. The primary objective is to provide high availability and performance by distributing static content (images, videos, JS, CSS) closer to the end-users, thereby reducing latency and offloading traffic from the origin server.

The specific challenge of **Static Content Edge Validation** focuses on how an edge server determines if the cached version of a resource is still current or if it must be re-validated/refetched from the origin.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Low Latency Delivery**: Serve static assets from the nearest Point of Presence (PoP).
- **Edge Validation**: Efficiently verify if cached content is stale using HTTP headers.
- **Cache Population**: Support both "Pull" (on-demand) and "Push" (pre-emptive) mechanisms.
- **Content Invalidation**: Ability to purge or update specific assets globally before their TTL expires.

### Non-Functional Requirements
- **High Availability**: The system must remain available even if the origin server experiences downtime (stale-while-revalidate).
- **Scalability**: Handle massive spikes in traffic (e.g., a viral video or a software update) without overloading the origin.
- **Durability**: Ensure that assets are correctly replicated across PoPs.
- **Consistency**: Eventual consistency is acceptable for most static assets, but strict invalidation is required for security patches or critical updates.

### Scale Assumptions
- **DAU**: 100M+ active users globally.
- **QPS**: Millions of requests per second during peak hours.
- **Storage**: Petabytes of data distributed across thousands of edge nodes.
- **Latency Goal**: Reduce Round Trip Time (RTT) from $\sim 200\text{ms}$ (Origin) to $< 20\text{ms}$ (Edge).

---

## 2. High-Level System Architecture

The CDN architecture transitions the request flow from a centralized model to a distributed edge model.

### Architecture Components
1. **The Origin Server**: The authoritative source of truth (e.g., an S3 bucket or a web server).
2. **DNS / GSLB (Global Server Load Balancer)**: The "brain" that directs the user to the optimal PoP based on Geo-IP, BGP routing, or current server health.
3. **PoP (Point of Presence)**: A data center located at the network edge.
    - **Edge Cache Servers**: Servers that store the actual content.
    - **Local Load Balancer**: Distributes traffic within the PoP to specific cache nodes.
4. **Purge Service**: An administrative API used to invalidate cached content across all PoPs.

### The Request Path
`Client` $\xrightarrow{\text{DNS Query}}$ `GSLB` $\xrightarrow{\text{IP Address}}$ `Edge PoP` $\xrightarrow{\text{Cache Miss}}$ `Origin Server`

---

## 3. Key HLD Concepts & Component Design

### Static Content Edge Validation
Validation is the process of checking if a cached resource is still fresh. This is governed by the **HTTP Caching Headers**.

| Header | Mechanism | Description |
| :--- | :--- | :--- |
| `Cache-Control` | **TTL (Time to Live)** | Defines the duration (e.g., `max-age=3600`) the edge server can serve the content without asking the origin. |
| `ETag` | **Validation Token** | A unique hash of the file content. The edge sends `If-None-Match: <hash>` to the origin. If the hash matches, the origin returns **304 Not Modified**. |
| `Last-Modified` | **Timestamp** | The edge sends `If-Modified-Since: <date>`. The origin returns 304 if the file hasn't changed since that date. |

### Routing Strategy: Consistent Hashing
Within a single PoP, there are multiple cache servers. To avoid duplicating the same file on every server (which wastes space), we use **Consistent Hashing**.
- **Why**: It ensures that a specific URL always maps to the same cache server. If a server is added or removed, only a small fraction of keys are remapped, minimizing "cache churn."

### Push vs. Pull Models
- **Pull Model**: The edge server requests the content from the origin only when a user asks for it and it's not in the cache (Lazy Loading).
- **Push Model**: The origin proactively pushes content to the edges. This is ideal for high-demand assets (e.g., a new iOS update) to prevent a "thundering herd" effect on the origin.

### Storage Hierarchy
To balance cost and speed, edge servers use a tiered storage approach:
- **L1 (RAM)**: Most requested "Hot" assets.
- **L2 (SSD/NVMe)**: "Warm" assets.
- **L3 (Origin/Regional Shield)**: The source of truth.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Walkthrough (Validation Flow)
1. **DNS Resolution**: User requests `cdn.example.com/image.jpg`. The GSLB returns the IP of the nearest PoP.
2. **Edge Cache Lookup**: The PoP load balancer routes the request to a cache server via consistent hashing.
3. **Freshness Check**:
    - **Scenario A (Fresh)**: `Current_Time - Cached_Time < TTL`. Server returns `200 OK` immediately.
    - **Scenario B (Stale)**: `TTL` expired. The edge server sends a **Conditional GET** to the origin: `If-None-Match: "v123"`.
4. **Origin Response**:
    - If content is unchanged $\rightarrow$ Origin returns `304 Not Modified`. Edge updates TTL and serves cached copy.
    - If content changed $\rightarrow$ Origin returns `200 OK` with new bytes and a new `ETag`.
5. **Delivery**: Content is delivered to the client.

### Handling Failures & Edge Cases
- **Origin Down**: The edge server can be configured to serve "stale" content (via `stale-if-error` header) rather than returning a 5xx error.
- **Cache Stampede (Thundering Herd)**: When a very popular object expires, thousands of requests might hit the origin simultaneously. 
    - **Solution**: **Request Collapsing**. The edge server locks the request for that specific URL and only allows *one* request to the origin; all other concurrent requests wait for that single response to populate the cache.
- **PoP Failure**: GSLB detects the PoP is unhealthy via heartbeats and automatically reroutes traffic to the next closest PoP.

---

## 5. Production Trade-offs

### CAP Theorem Perspective
CDNs prioritize **Availability** and **Partition Tolerance** (AP). 
- **Consistency Trade-off**: We accept **Eventual Consistency**. It may take a few minutes for a "Purge" command to propagate to every edge node worldwide. Using a versioned URL (e.g., `style.v2.css` instead of `style.css`) is the industry standard to bypass this consistency issue.

### Latency vs. Storage Cost
- **Aggressive Caching (Long TTL)**: Reduces origin load and latency but increases the risk of serving stale content.
- **Conservative Caching (Short TTL)**: Ensures freshness but increases origin load and increases the probability of a cache miss (increasing latency).

### Summary Complexity Analysis

| Operation | Time Complexity | Network Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Cache Hit** | $O(1)$ | Low (Edge $\to$ User) | Fastest path. |
| **Cache Miss (Pull)** | $O(1)$ | High (Edge $\to$ Origin $\to$ User) | Slower; involves origin roundtrip. |
| **Validation (304)** | $O(1)$ | Medium (Edge $\to$ Origin $\to$ Edge) | Only headers are exchanged, not the whole body. |
| **Purge/Invalidation** | $O(N)$ | Medium (Admin $\to$ All PoPs) | $N$ = Number of PoPs/Edge Nodes. |

```python
# Conceptual implementation of an Edge Cache Validation Logic
class EdgeCache:
    def __init__(self, origin_server):
        self.storage = {} # {url: {"content": bytes, "etag": str, "expiry": int}}
        self.origin = origin_server

    def get_content(self, url):
        entry = self.storage.get(url)
        
        if entry and entry['expiry'] > current_time():
            print("Cache Hit: Serving fresh content")
            return entry['content'], 200

        if entry:
            print("Cache Stale: Validating with origin...")
            is_modified, new_content, new_etag, new_expiry = self.origin.validate(url, entry['etag'])
            if not is_modified:
                print("Origin returned 304: Updating TTL")
                self.storage[url]['expiry'] = new_expiry
                return entry['content'], 200
            else:
                print("Origin returned 200: Content updated")
                self.storage[url] = {"content": new_content, "etag": new_etag, "expiry": new_expiry}
                return new_content, 200
        
        print("Cache Miss: Fetching from origin...")
        content, etag, expiry = self.origin.fetch(url)
        self.storage[url] = {"content": content, "etag": etag, "expiry": expiry}
        return content, 200
```
INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/content-delivery-networks-cdn-system-design/',
    'description': 'Static content edge validation.',
    'type': 'design',
    'groups': ['Networking', 'Distributed Systems'],
    'readme_content': """# Content Delivery Network (CDN) Distributions HLD

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
```""",
    'solutions': """# System Design Document: Static Content Edge Validation

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Integrity Verification:** Ensure that static assets (JS, CSS, Images, WASM) delivered via the CDN have not been tampered with or corrupted during transit or storage.
*   **Version Validation:** Prevent "version skew" where a client receives a mismatched set of assets (e.g., an old CSS file with a new HTML file).
*   **Access Control at Edge:** Validate signed URLs or tokens at the edge to ensure only authorized users can access specific static content.
*   **Atomic Updates:** Ensure that a new version of a static site is promoted globally and validated before being served.
*   **Cache Invalidation:** Provide a mechanism to explicitly invalidate specific assets or entire distributions across all PoPs (Points of Presence).

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** Validation logic must execute in the low millisecond range to avoid impacting the Time to First Byte (TTFB).
*   **High Availability:** The validation mechanism must not become a single point of failure; if the validation service is unreachable, a fallback policy (fail-open or fail-closed) must be defined.
*   **Global Scalability:** The system must handle millions of requests per second (RPS) across diverse geographic regions.
*   **Security:** Protection against Cache Poisoning attacks and unauthorized origin access.

### 1.3 Scale Estimations (HLD)
*   **Traffic:** 10M+ requests per second globally.
*   **Asset Volume:** 100TB+ of static content.
*   **Manifest Size:** Metadata for millions of files, requiring a distributed, low-latency lookup store.
*   **Propagation Delay:** Global invalidation/update propagation should occur within < 60 seconds.

---

## 2. High-Level Architecture

The architecture leverages **Edge Computing** (e.g., Lambda@Edge, Cloudflare Workers, Fastly Compute@Edge) to intercept requests and responses, validating them against a globally distributed **Manifest Store**.

### 2.1 Component Diagram

```mermaid
graph TD
    Client[Client Browser] --> CDN_Edge[CDN Edge PoP]
    
    subgraph "Edge Node"
        CDN_Edge --> Edge_Func[Edge Validation Function]
        Edge_Func --> Edge_Cache[Local Edge Cache]
    end
    
    Edge_Func --> Manifest_Store[(Global Manifest Store - NoSQL)]
    Edge_Func --> Origin[Origin Storage - S3/GCS]
    
    subgraph "Control Plane"
        CI_CD[CI/CD Pipeline] --> Manifest_Writer[Manifest Writer Service]
        Manifest_Writer --> Manifest_Store
        Manifest_Writer --> Purge_API[CDN Purge API]
    end
    
    Purge_API --> CDN_Edge
```

### 2.2 Interaction Workflow
1.  **Deployment:** The CI/CD pipeline uploads assets to the Origin. It calculates the SHA-256 hash of each file and updates the **Global Manifest Store** with the new version mapping.
2.  **Request:** A client requests `style.v2.css`.
3.  **Edge Interception:** The Edge Function intercepts the request.
4.  **Validation:** 
    *   The function checks the `Manifest Store` (or a local cached copy) for the expected hash/version of `style.v2.css`.
    *   If the asset is in `Edge Cache`, it validates the cached asset's hash.
    *   If the asset is missing or invalid, it fetches it from the `Origin`.
5.  **Integrity Check:** The Edge Function verifies the checksum of the fetched content before serving it to the client and caching it.
6.  **Response:** The validated content is delivered to the client.

---

## 3. Detailed Database Schema Design

The **Global Manifest Store** must be a globally replicated NoSQL database (e.g., DynamoDB Global Tables or CosmosDB) to ensure low-latency reads at any PoP.

### 3.1 Schema: `AssetManifest`
This table stores the "Source of Truth" for every static asset version.

| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `asset_path` | String | PK | The URI of the asset (e.g., `/static/js/main.js`). |
| `version_id` | String | SK | Unique version identifier (e.g., Git commit hash or Semantic Version). |
| `checksum` | String | - | SHA-256 hash of the file content. |
| `content_type` | String | - | MIME type (e.g., `text/javascript`). |
| `created_at` | Timestamp | - | Deployment timestamp. |
| `status` | Enum | - | `STAGING`, `ACTIVE`, `DEPRECATED`. |

### 3.2 Indexing Strategy
*   **Primary Key:** Composite key `(asset_path, version_id)` allows for rapid lookup of specific versions.
*   **Global Secondary Index (GSI):** An index on `status` where `status = 'ACTIVE'` allows the edge to quickly find the current production version of an asset if the request does not specify a version.

### 3.3 Storage Reasoning
*   **NoSQL over SQL:** We require predictable, single-digit millisecond read latency and seamless global replication. The schema is simple and doesn't require complex joins.
*   **Edge Caching:** To avoid hitting the Manifest Store on every single request, the Edge Function caches the manifest entry for a short TTL (e.g., 60 seconds) or until an invalidation signal is received.

---

## 4. Core API Design

### 4.1 Manifest Update API (Internal Control Plane)
Used by CI/CD to register new assets.

**Endpoint:** `POST /v1/manifest/update`
**Request Payload:**
```json
{
  "deployment_id": "dep_98765",
  "assets": [
    {
      "path": "/js/bundle.js",
      "version": "v1.0.4",
      "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "mime_type": "application/javascript"
    }
  ],
  "activate": true
}
```
**Response:** `202 Accepted` (Processing asynchronous replication).

### 4.2 Asset Invalidation API
Used to purge corrupted or leaked assets.

**Endpoint:** `POST /v1/purge`
**Request Payload:**
```json
{
  "paths": ["/js/bundle.js", "/css/theme.css"],
  "scope": "global",
  "force_revalidate": true
}
```
**Response:** `200 OK`.

---

## 5. Scalability & Advanced Topics

### 5.1 Caching Strategies
*   **Tiered Caching:** Use a Regional Edge Cache between the PoP and the Origin to reduce origin load during a "cache stampede" when a new version is released.
*   **Stale-While-Revalidate:** Configure the CDN to serve a stale version of the asset while the Edge Function validates the new version in the background.

### 5.2 Edge Validation Logic (Optimization)
To prevent expensive hash calculations on every request:
1.  **Header-based Validation:** The origin attaches a `X-Asset-Hash` header. The Edge Function compares this header against the Manifest Store.
2.  **Sampling:** For very large assets (e.g., 100MB video chunks), perform "sparse validation" by hashing only the first, middle, and last 4KB of the file.

### 5.3 Rate Limiting & Security
*   **Origin Shielding:** Only allow requests to the Origin if they originate from the CDN's IP range and carry a secret "Origin-Access-Key".
*   **Signed URLs:** For private static content, the Edge Function validates an HMAC signature in the URL query string before checking the manifest.

### 5.4 Fault Tolerance
*   **Fail-Open Mechanism:** If the Manifest Store is unreachable, the Edge Function can be configured to "Fail-Open" (serve the cached asset without validation) to ensure availability, while logging a critical alert.
*   **Circuit Breaker:** If the Origin returns 5xx errors, the Edge Function stops attempting re-validation and serves the last known good version from cache.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priorities
In this system, we prioritize **Availability (A)** and **Partition Tolerance (P)**. 
*   **Reasoning:** A CDN that refuses to serve a CSS file because it cannot reach the validation database results in a broken website (high impact). Therefore, we accept **Eventual Consistency (C)**, meaning some PoPs may serve version $N$ while others serve $N+1$ for a few seconds during propagation.

### 6.2 Latency vs. Security
| Approach | Latency | Security/Integrity |
| :--- | :--- | :--- |
| **No Validation** | Lowest | Low (Risk of Cache Poisoning/Corruption) |
| **Header Validation** | Low | Medium (Relies on Origin Header trust) |
| **Full Body Hashing** | High | Highest (Guarantees byte-for-byte integrity) |

**Decision:** Implement **Header Validation** by default, with **Full Body Hashing** triggered only on the first fetch from Origin to Edge.

### 6.3 Storage vs. Compute
We choose to store the manifest in a distributed NoSQL store rather than embedding versioning in the file names (e.g., `main.v123.js`). 
*   **Trade-off:** This increases the compute overhead at the edge (one lookup per asset). 
*   **Benefit:** It allows for "Instant Rollbacks" by simply updating the `ACTIVE` version in the manifest without needing to change the HTML references across the entire site.""",
}

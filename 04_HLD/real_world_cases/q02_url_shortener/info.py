INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/design-url-shortener-tinyurl/',
    'description': 'Design a high-scale TinyURL redirection engine.',
    'type': 'design',
    'groups': ['Real-World Systems', 'Hashing'],
    'readme_content': """# URL Shortener (TinyURL) HLD

A URL shortener is a service that takes a long URL and converts it into a short, unique alias. When a user visits the short URL, the system redirects them to the original long URL. While it seems simple, designing this for **billions of requests** requires careful consideration of hashing, database scaling, and caching.

---

## 1. Overview & System Requirements

### Functional Requirements
- **URL Shortening**: Given a long URL, the system should generate a shorter, unique alias.
- **Redirection**: When a user hits the short URL, the system should redirect them to the original long URL with minimum latency.
- **Custom Aliases**: Users should optionally be able to provide a custom short link (e.g., `tinyurl.com/my-portfolio`).
- **Expiration**: Links should have a default or user-defined expiration date.

### Non-Functional Requirements
- **High Availability**: The redirection service must be available $24/7$. A failure in the redirect engine means broken links across the web.
- **Low Latency**: The redirection process must happen in milliseconds.
- **Scalability**: The system must handle a massive volume of reads (redirections) and a significant volume of writes (shortening).
- **Unpredictability**: Shortened IDs should not be easily guessable to prevent "scraping" of the database.

### Scale Assumptions & Estimations
| Metric | Assumption | Calculation / Value |
| :--- | :--- | :--- |
| **Write Volume** | 100M new URLs / month | $\approx 40$ writes per second (avg) |
| **Read Volume** | 10B redirections / month | $\approx 4,000$ reads per second (avg) |
| **Read/Write Ratio** | High Read Heavy | $100:1$ |
| **Storage (5 years)** | $100\text{M} \times 12 \times 5$ | $6$ Billion records |
| **Avg Record Size** | $\sim 500$ bytes | $6\text{B} \times 500\text{B} \approx 3\text{ TB}$ |
| **Bandwidth** | Read heavy | $4,000 \text{ req/s} \times 500 \text{ bytes} \approx 2\text{ MB/s}$ |

---

## 2. High-Level System Architecture

The system follows a microservices architecture to separate the **Write Path** (creation) from the **Read Path** (redirection).

### Component Breakdown
1.  **Client**: Browser or API client.
2.  **Load Balancer (LB)**: Distributes incoming traffic across multiple application servers to prevent any single point of failure.
3.  **API Gateway**: Handles authentication, rate limiting (to prevent spam), and request routing.
4.  **Application Servers (Write Service)**: Handles the logic for generating short IDs and storing the mapping.
5.  **Application Servers (Read Service)**: Handles the lookup of short IDs and issues HTTP redirects.
6.  **Key Generation Service (KGS)**: A dedicated service that pre-generates unique IDs to avoid runtime collisions.
7.  **Caching Layer (Redis)**: Stores frequently accessed mappings (hot URLs) to reduce database load.
8.  **Database (NoSQL)**: Stores the mapping of `short_url` $\rightarrow$ `long_url`.

---

## 3. Key HLD Concepts & Component Design

### A. The Shortening Algorithm (Base62 Encoding)
To create a short ID, we use **Base62 encoding** ($0-9, a-z, A-Z$).
- If we use a 7-character string: $62^7 \approx 3.5 \text{ Trillion}$ unique combinations.
- This is more than enough to cover our 6 billion record estimate.

**Why not use a Hash (MD5/SHA)?**
Hashing a long URL creates a very long string. If we truncate the hash (e.g., take the first 7 chars), we encounter **collisions**. Resolving collisions (checking the DB, appending salt, re-hashing) adds significant latency to the write path.

### B. Key Generation Service (KGS)
To solve the collision problem, we use a **KGS**.
- The KGS pre-generates a massive range of unique IDs and stores them in a separate table (e.g., `Available_Keys`).
- When the Write Service needs a key, it simply "grabs" one from the KGS.
- **Optimization**: The KGS can load a batch of keys into memory to avoid frequent DB hits.
- **Concurrency**: Use a distributed lock or a range-based allocation (each server gets a range of IDs) to ensure no two servers issue the same key.

### C. Database Selection
We need a database that supports high read throughput and simple Key-Value lookups.
- **Choice**: **NoSQL (e.g., Cassandra or DynamoDB)**.
- **Reasoning**:
    - We don't need complex ACID transactions or joins.
    - NoSQL scales horizontally (sharding) much more easily than SQL.
    - The data model is simple: `short_url (PK) | long_url | created_at | expiration_date`.

### D. Caching Strategy
Since $10\%$ of URLs usually generate $90\%$ of traffic (Pareto Principle), caching is critical.
- **Technology**: Redis.
- **Eviction Policy**: **LRU (Least Recently Used)**.
- **Flow**: Read Service checks Redis $\rightarrow$ If Miss $\rightarrow$ Check DB $\rightarrow$ Update Redis $\rightarrow$ Return.

---

## 4. Data Flows & Fault Tolerance

### Write Path: Creating a Short URL
1. Client sends `POST /shorten` with the `long_url`.
2. LB forwards request to a Write Server.
3. Server requests a unique key from the **KGS**.
4. Server stores the mapping `(short_url, long_url, expiration)` in the NoSQL DB.
5. Server returns the `short_url` to the client.

### Read Path: Redirection
1. Client hits `GET /abc1234`.
2. LB forwards request to a Read Server.
3. Server checks **Redis Cache**.
    - **Hit**: Immediately returns the `long_url`.
    - **Miss**: Server queries **NoSQL DB**.
4. If found in DB, it is cached in Redis and returned.
5. **HTTP Response**: The server returns an **HTTP 301 (Permanent Redirect)**.
    - *Note*: 301 allows the browser to cache the redirect, reducing load on our servers. Use 302 (Temporary) if we need to track analytics for every single click.

### Fault Tolerance & Reliability
- **DB Replication**: Use multi-region replication (Master-Slave) to ensure that if one data center goes down, the redirection service remains active.
- **KGS Redundancy**: Run multiple KGS instances. If one fails, the others can continue providing keys from their pre-allocated ranges.
- **Rate Limiting**: Implement a token-bucket algorithm at the API Gateway to prevent malicious users from exhausting the KGS key pool.

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
For a URL shortener, **Availability** is prioritized over **Consistency** (AP system).
- If a user creates a short link and it takes a few milliseconds to propagate across global replicas, it is an acceptable trade-off.
- If the system is unavailable, the link is "broken," which is a critical failure.

### Storage vs. Computation
By using a **KGS**, we trade a small amount of extra storage (the `Available_Keys` table) for significantly lower computation and latency during the write process (avoiding hash collisions).

### Summary Complexity Analysis
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Shortening (Write)** | $O(1)$ | $O(1)$ | KGS provides keys in constant time. |
| **Redirection (Read)** | $O(1)$ | $O(1)$ | Cache/KV lookup is constant time. |
| **Storage** | N/A | $O(N)$ | Linear growth relative to the number of URLs. |""",
    'solutions': """# System Design Document: High-Scale URL Shortener (TinyURL)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **URL Shortening**: The system should take a long URL and return a unique, shorter alias.
*   **Redirection**: When a user accesses the short URL, the system should redirect them to the original long URL with minimum latency.
*   **Custom Aliases**: Users should be able to provide a custom string for their short URL.
*   **Expiration**: URLs should have an optional expiration date after which the link becomes invalid.
*   **Analytics**: (Optional/Bonus) Track the number of clicks and basic geographic data for the URLs.

### 1.2 Non-Functional Requirements
*   **High Availability**: The redirection service must be available 24/7; downtime directly impacts user experience.
*   **Low Latency**: Redirection should happen in milliseconds.
*   **Scalability**: The system must handle a massive volume of reads (redirections) and a steady stream of writes (shortening).
*   **Uniqueness**: No two different long URLs should map to the same short URL unless intended.
*   **Predictability**: The short URL should be non-guessable to prevent "scraping" of the database.

### 1.3 Scale Estimations
*   **Traffic Volume**:
    *   New URLs created: 100 Million per month.
    *   Read/Write Ratio: 100:1 (Redirection is far more common than creation).
    *   Total Reads: $100\text{M} \times 100 = 10\text{B}$ redirections per month.
*   **QPS (Queries Per Second)**:
    *   Write QPS: $100\text{M} / (30 \times 24 \times 3600) \approx 40 \text{ req/sec}$.
    *   Read QPS: $10\text{B} / (30 \times 24 \times 3600) \approx 3,800 \text{ req/sec}$.
*   **Storage**:
    *   Assume 5 years of data retention.
    *   Total records: $100\text{M} \times 12 \times 5 = 6\text{B}$ records.
    *   Avg record size: $\sim 500$ bytes (Long URL, short URL, metadata).
    *   Total storage: $6\text{B} \times 500\text{B} \approx 3\text{TB}$.

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **Load Balancer**: Distributes incoming traffic across multiple application servers.
2.  **API Gateway/App Servers**: Handles the business logic for shortening and redirection.
3.  **Key Generation Service (KGS)**: A dedicated service to provide unique, pre-generated IDs to avoid collisions and database checks during the write path.
4.  **Caching Layer (Redis)**: Stores frequently accessed URL mappings to reduce database load.
5.  **Database**: Stores the mapping between short keys and long URLs.

### 2.2 Architecture Diagram

```mermaid
graph TD
    User((User)) --> LB[Load Balancer]
    LB --> App[Application Servers]
    App --> Cache[(Redis Cache)]
    App --> DB[(NoSQL Database)]
    App --> KGS[Key Generation Service]
    KGS --> KGS_DB[(KGS Storage)]
```

### 2.3 Sequence Flow
**Write Path (Shortening):**
1. Client sends a `POST` request with the `longUrl`.
2. App server requests a unique key from the **KGS**.
3. App server stores the mapping `{shortKey: longUrl}` in the **Database**.
4. App server returns the short URL to the client.

**Read Path (Redirection):**
1. Client hits `GET /{shortKey}`.
2. App server checks the **Cache**. If hit, it returns the `longUrl`.
3. If cache miss, App server queries the **Database**.
4. App server updates the cache and returns a `302 Found` redirect to the `longUrl`.

---

## 3. Detailed Database Schema Design

### 3.1 Storage Choice: NoSQL vs SQL
For this use case, a **NoSQL Key-Value or Wide-Column store** (e.g., DynamoDB, Cassandra) is preferred over RDBMS for the following reasons:
*   **Scalability**: NoSQL scales horizontally more easily to handle billions of records.
*   **Simple Access Pattern**: The primary operation is a simple key-lookup.
*   **Availability**: NoSQL databases typically offer better availability and partition tolerance (AP in CAP).

### 3.2 Table Design: `url_mapping`

| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `short_key` | String (PK) | Unique, Indexed | The Base62 encoded unique ID |
| `long_url` | String | Not Null | The original destination URL |
| `user_id` | String | Indexed | Reference to the creator |
| `created_at` | Timestamp | Not Null | Creation date for cleanup |
| `expires_at` | Timestamp | Indexed | Expiration date for TTL |

**Indexing Strategy**:
*   Primary Key on `short_key` for $\mathcal{O}(1)$ lookup.
*   Secondary index on `expires_at` to facilitate a background cleanup job for expired links.

---

## 4. Core API Design

### 4.1 Create Short URL
`POST /api/v1/shorten`

**Request Body:**
```json
{
  "longUrl": "https://www.example.com/very/long/path/to/resource",
  "customAlias": "my-promo-link", 
  "expireAt": "2025-12-31T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
  "shortUrl": "https://tiny.url/aB12c3D",
  "createdAt": "2023-10-01T10:00:00Z"
}
```

### 4.2 Redirect to Long URL
`GET /{shortKey}`

**Response:**
*   **Success**: `302 Found` (Temporary Redirect) $\rightarrow$ Header `Location: https://www.example.com/...`
*   **Not Found**: `404 Not Found`
*   **Expired**: `410 Gone`

---

## 5. Scalability & Advanced Topics

### 5.1 Key Generation Service (KGS)
To avoid generating the same key and checking the database (which would add latency), we use a KGS:
*   **Algorithm**: Use a 64-bit counter $\rightarrow$ Convert to **Base62** (`[a-z, A-Z, 0-9]`). A 7-character string provides $62^7 \approx 3.5 \text{ Trillion}$ unique combinations.
*   **Pre-generation**: KGS pre-generates keys and stores them in a table.
*   **Buffering**: To prevent the KGS from becoming a bottleneck, App Servers load a "chunk" of keys (e.g., 1,000 keys) into local memory.

### 5.2 Caching Strategy
*   **Cache Policy**: Use an **LRU (Least Recently Used)** eviction policy.
*   **Data Store**: Redis.
*   **Optimization**: Since the read/write ratio is 100:1, caching the top 20% of "hot" URLs will likely handle 80% of the traffic (Pareto Principle).

### 5.3 Partitioning & Sharding
If the database grows beyond a single node's capacity:
*   **Hash-based Partitioning**: Partition the data based on the hash of the `short_key`. This ensures a uniform distribution of requests across shards.
*   **Range-based Partitioning**: Not recommended here as it can lead to "hotspots" if certain key ranges are more popular.

### 5.4 Rate Limiting
To prevent abuse (e.g., a bot creating millions of URLs):
*   Implement a **Token Bucket** or **Leaky Bucket** algorithm.
*   Limit by `user_id` or `IP address`.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem
In the context of the CAP Theorem, this system prioritizes **Availability** and **Partition Tolerance (AP)**.
*   **Reasoning**: If a database node goes down or a network partition occurs, it is better to serve a slightly stale redirect (or a temporary error for a brand new link) than to bring down the entire redirection engine.

### 6.2 Redirect Status Codes: 301 vs 302
*   **301 (Permanent Redirect)**: Browsers cache the destination. This reduces load on our servers but removes our ability to track analytics (clicks) for subsequent visits.
*   **302 (Temporary Redirect)**: Every request hits our server. This allows for precise analytics and the ability to change the destination URL later.
*   **Decision**: Use **302** to support the "Analytics" functional requirement.

### 6.3 Storage vs Latency
By introducing the KGS and Redis Cache, we increase the system's architectural complexity (more moving parts) and storage overhead (pre-generated keys). However, this significantly reduces the write-path latency (no DB check for collision) and read-path latency (avoiding DB hits for hot URLs).""",
}

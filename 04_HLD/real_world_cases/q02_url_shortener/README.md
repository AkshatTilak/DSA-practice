# URL Shortener (TinyURL) HLD

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
| **Storage** | N/A | $O(N)$ | Linear growth relative to the number of URLs. |
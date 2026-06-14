# Instagram HLD: Stories, Feed, and Reels

This study guide provides a comprehensive high-level design (HLD) for a massive-scale social media platform similar to Instagram. The system must handle billions of users, petabytes of media, and deliver a seamless, low-latency experience for content consumption.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Feed:** Users can follow other users and see a curated feed of photos/videos from people they follow.
*   **Stories:** Users can upload photos/videos that disappear after 24 hours.
*   **Reels:** Short-form vertical videos with a discovery-based recommendation engine.
*   **Media Upload:** Support for high-resolution images and videos.
*   **Social Graph:** Ability to follow/unfollow users.

### Non-Functional Requirements
*   **High Availability:** The system must be available $99.99\%$ of the time (AP system in CAP theorem).
*   **Low Latency:** Feed loading and story transitions must be near-instantaneous (< 200ms).
*   **Scalability:** Must handle $\sim 1$ Billion Daily Active Users (DAU).
*   **Durability:** Once a post is uploaded, it must not be lost.
*   **Eventual Consistency:** It is acceptable if a follower sees a post a few seconds after it is uploaded.

### Scale Assumptions & Estimations
| Metric | Assumption | Calculation/Value |
| :--- | :--- | :--- |
| **DAU** | 1 Billion | $10^9$ users |
| **Read/Write Ratio** | 100:1 | Extremely read-heavy |
| **Avg. Posts/User/Day** | 0.1 posts | $100M$ posts per day |
| **Avg. Media Size** | 200 KB (Img), 5 MB (Vid) | Massive storage needs |
| **Write QPS** | $100M / 86400$ | $\sim 1,200$ writes/sec (Avg) |
| **Read QPS** | $1,200 \times 100$ | $\sim 120,000$ reads/sec (Avg) |
| **Storage (Daily)** | $100M \times 1 \text{MB (avg)}$ | $\sim 100 \text{TB}$ per day |

---

## 2. High-Level System Architecture

The system follows a **microservices architecture** to decouple the heavy write-path of media uploads from the high-concurrency read-path of feed generation.

### Component Breakdown
1.  **API Gateway / Load Balancer:** Entry point for all clients. Handles rate limiting, authentication, and request routing.
2.  **Media Service:** Handles file uploads, metadata extraction, and integration with the object store.
3.  **Feed Service:** Aggregates posts from followed users and serves them to the client.
4.  **Story Service:** Manages ephemeral content with TTL (Time-To-Live) logic.
5.  **Reels/Discovery Service:** Uses a recommendation engine (ML) to serve content from non-followed users.
6.  **Social Graph Service:** Manages the "Follow/Unfollow" relationships using a graph-optimized store.
7.  **Object Store (S3/GCS):** Stores raw images and videos.
8.  **CDN (CloudFront/Akamai):** Caches media at edge locations globally to reduce latency.
9.  **Cache Layer (Redis):** Stores pre-computed feeds and hot user metadata.

---

## 3. Key HLD Concepts & Component Design

### A. Feed Generation: The "Fan-out" Strategy
Generating a feed in real-time for a user following 1,000 people is computationally expensive. We use a hybrid approach:

*   **Push Model (Fan-out on Write):** When a user posts, the system pushes the post ID into the "Timeline Cache" (Redis) of all their followers.
    *   *Pros:* Read is $O(1)$.
    *   *Cons:* Write is $O(N)$ where $N$ is the number of followers.
*   **Pull Model (Fan-out on Load):** The feed is aggregated from all followed users at the time the request is made.
    *   *Pros:* Write is $O(1)$.
    *   *Cons:* Read is $O(N \log N)$ or worse.
*   **The Hybrid Solution (Celebrity Problem):**
    *   **Normal Users:** Use the **Push Model**.
    *   **Celebrities (Millions of followers):** Use the **Pull Model**. Their posts are not pushed to millions of caches; instead, when a follower loads their feed, the system pulls the celebrity's latest posts and merges them into the pre-computed feed.

### B. Story Design (Ephemeral Content)
Stories require a different storage strategy because they expire.
*   **Storage:** Use a NoSQL database like **Cassandra** or **DynamoDB** because they handle high write throughput and support **TTL (Time-To-Live)** features natively.
*   **Indexing:** Stories are indexed by `user_id` and `timestamp`.
*   **Flow:** A story is written with a TTL of 24 hours. After this, the DB automatically deletes the record, and a background worker triggers the deletion of the actual media from S3.

### C. Reels & Recommendation Engine
Unlike the Feed (which is based on the Social Graph), Reels are based on **Content-Based Filtering** and **Collaborative Filtering**.
*   **Feature Store:** Stores user preferences (e.g., "User A likes cooking videos").
*   **Ranking Service:** A machine learning model ranks candidate reels based on user embeddings and video tags.
*   **Streaming:** Use **HLS (HTTP Live Streaming)** or **DASH**. Videos are transcoded into multiple resolutions (360p, 720p, 1080p) to adapt to the user's bandwidth.

### D. Technology Stack Selection
| Component | Technology | Why? |
| :--- | :--- | :--- |
| **User Profile/Auth** | PostgreSQL | Strong consistency, ACID compliance for user accounts. |
| **Social Graph** | Neo4j / DynamoDB | Optimizing for "friends-of-friends" and relationship queries. |
| **Feed Metadata** | Cassandra | High write throughput, linear scalability. |
| **Cache** | Redis | Extremely low latency for pre-computed feeds. |
| **Media Storage** | S3 + CDN | Cost-effective storage and global edge delivery. |
| **Async Tasks** | Kafka | Decoupling media transcoding and notification services. |

---

## 4. Data Flows & Fault Tolerance

### Data Flow: Posting a Photo/Video
1.  **Upload:** Client $\rightarrow$ API Gateway $\rightarrow$ Media Service $\rightarrow$ **S3**.
2.  **Processing:** Media Service pushes an event to **Kafka**.
3.  **Transcoding:** A worker consumes from Kafka, generates thumbnails, and transcodes video into multiple resolutions.
4.  **Metadata:** Post metadata (URL, user_id, timestamp) is written to the **Metadata DB (Cassandra)**.
5.  **Fan-out:** The Feed Service identifies followers and updates their **Redis Timeline Caches**.

### Data Flow: Loading the Feed
1.  **Request:** Client $\rightarrow$ API Gateway $\rightarrow$ Feed Service.
2.  **Fetch:** Feed Service checks **Redis** for the pre-computed list of post IDs.
3.  **Hydration:** The service fetches the actual post content (captions, media URLs) from the Metadata DB/Cache.
4.  **Merge:** If the user follows celebrities, the service pulls their latest posts and merges them.
5.  **Response:** Returns a JSON list of posts to the client.

### Fault Tolerance & Reliability
*   **Replication:** Databases are replicated across multiple Availability Zones (AZs).
*   **Circuit Breakers:** If the Recommendation Service for Reels is down, the system falls back to a "Trending" list (static cache) to avoid a total outage.
*   **Write-Ahead Logging (WAL):** Ensures data durability in the event of a database crash.
*   **Retry Policy:** Exponential backoff for media uploads to handle transient network failures.

---

## 5. Production Trade-offs

### Consistency vs. Availability (CAP Theorem)
Instagram chooses **Availability** and **Partition Tolerance (AP)**.
*   **Trade-off:** If a user posts a photo, their friend in another country might not see it for a few seconds (Eventual Consistency). This is acceptable. Strong consistency (CP) would make the system too slow and prone to timeouts during network partitions.

### Latency vs. Storage (Pre-computation)
*   **Trade-off:** Pre-computing feeds for every user in Redis consumes a massive amount of memory (RAM).
*   **Decision:** We sacrifice storage cost for latency. The "Read" experience is the primary product driver; therefore, spending more on Redis clusters to avoid expensive real-time joins is a strategic choice.

### SQL vs. NoSQL
*   **SQL (Postgres):** Used for User Accounts and Billing where structure is rigid and consistency is paramount.
*   **NoSQL (Cassandra):** Used for the Feed and Stories where the data volume is astronomical, and we need a "write-heavy" optimized store that can scale horizontally.

---

## Complexity Summary

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Post Upload** | $O(F)$ | $O(1)$ | $F$ = number of followers (fan-out) |
| **Feed Load** | $O(K)$ | $O(K)$ | $K$ = number of posts per page |
| **Story Retrieval**| $O(1)$ | $O(1)$ | Direct lookup by `user_id` |
| **Reel Discovery** | $O(M \log M)$ | $O(M)$ | $M$ = candidate pool for ML ranking |
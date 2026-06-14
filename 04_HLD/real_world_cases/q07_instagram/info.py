INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Instagram - Stories, feed, reels.',
    'groups': ['Real-World Systems', 'Distributed Systems'],
    'readme_content': """# Instagram HLD: Stories, Feed, and Reels

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
| **Reel Discovery** | $O(M \log M)$ | $O(M)$ | $M$ = candidate pool for ML ranking |""",
    'solutions': """# System Design Document: Instagram (Stories, Feed, Reels)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Stories:** Users can upload photos/videos that disappear after 24 hours. Users can view stories from people they follow.
*   **Feed:** A personalized stream of posts (images/videos) from followed users, sorted by a combination of recency and relevance.
*   **Reels:** Short-form video content. Users can scroll through a global discovery feed (algorithmic) or see reels from followed users.
*   **Social Graph:** Ability to follow/unfollow other users.
*   **Interactions:** Like and comment on posts, reels, and stories.

### 1.2 Non-Functional Requirements
*   **High Availability:** The system must be available 24/7 (AP over CP in CAP theorem).
*   **Low Latency:** Feed loading and story transitions must be near-instant (< 200ms).
*   **Scalability:** Support for 500M+ Daily Active Users (DAU).
*   **Eventual Consistency:** It is acceptable if a post takes a few seconds to appear in all followers' feeds.
*   **Durability:** Permanent content (Reels, Posts) must never be lost.

### 1.3 Scale Estimations (HLD)
*   **DAU:** 500 Million.
*   **Read/Write Ratio:** Heavily read-biased (approx. 100:1).
*   **Stories:** ~1 Billion uploads/day. Each story lasts 24h.
*   **Feed:** Each user views ~20-50 posts per session.
*   **Storage:** 
    *   Images (~2MB avg), Videos (~10-50MB avg).
    *   Daily storage growth: Hundreds of Terabytes.
*   **Throughput:** 
    *   Peak QPS (Read): Millions of requests per second during global events.
    *   Peak QPS (Write): Hundreds of thousands per second.

---

## 2. High-Level Architecture

The system follows a microservices architecture to decouple the ephemeral nature of Stories from the permanent nature of Reels and the complex aggregation of the Feed.

### 2.1 Architecture Diagram (Mermaid)

```mermaid
graph TD
    Client[Mobile App/Web] --> AGW[API Gateway / Load Balancer]
    
    AGW --> UserSvc[User & Social Graph Service]
    AGW --> MediaSvc[Media Upload Service]
    AGW --> StorySvc[Story Service]
    AGW --> ReelSvc[Reel Service]
    AGW --> FeedSvc[Feed Generation Service]

    UserSvc --> UserDB[(User DB - PostgreSQL)]
    UserSvc --> GraphDB[(Graph DB - Neo4j/CockroachDB)]
    
    MediaSvc --> S3[Object Store - AWS S3/GCS]
    S3 --> CDN[CDN - CloudFront/Akamai]
    MediaSvc --> Transcoder[Video Transcoding Pipeline]
    Transcoder --> S3

    StorySvc --> StoryDB[(Story DB - Cassandra/DynamoDB)]
    StorySvc --> StoryCache[(Redis - Story Index)]

    ReelSvc --> ReelDB[(Reel DB - MongoDB/PostgreSQL)]
    ReelSvc --> ReelCache[(Redis - Global Trending)]

    FeedSvc --> FeedCache[(Redis - User Feed Cache)]
    FeedSvc --> FeedSvc_Logic[Feed Ranking Engine]
    FeedSvc_Logic --> UserSvc
    
    MediaSvc --> Kafka[Message Queue - Kafka]
    Kafka --> FeedSvc
    Kafka --> NotificationSvc[Notification Service]
```

### 2.2 Component Interaction
1.  **Media Upload:** User uploads a Reel/Story $\rightarrow$ `Media Service` $\rightarrow$ S3. A message is sent to Kafka to trigger transcoding (for different resolutions) and to notify the `Feed Service` to update followers' caches.
2.  **Story Consumption:** `Story Service` fetches active stories (current time < expiry) for the followed users from `StoryDB` and returns the CDN URLs.
3.  **Feed Generation:** The `Feed Service` uses a hybrid approach. For regular users, it pulls from a pre-computed `Feed Cache`. For celebrities, it fetches in real-time (Pull model).
4.  **Reels Discovery:** `Reel Service` uses a machine learning ranking engine to suggest content based on user interests, fetching metadata from `ReelDB`.

---

## 3. Detailed Database Schema Design

### 3.1 User & Social Graph (SQL/Graph)
Since social relationships are highly interconnected, a combination of SQL for profiles and a Graph-optimized approach for follows is used.

**Table: `users` (Relational - PostgreSQL)**
| Field | Type | Index | Notes |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique User ID |
| `username` | VARCHAR(50) | Unique | Unique handle |
| `email` | VARCHAR(100) | Unique | User email |
| `created_at` | Timestamp | - | Account creation date |

**Table: `follows` (Relational/Graph - CockroachDB/Neo4j)**
| Field | Type | Index | Notes |
| :--- | :--- | :--- | :--- |
| `follower_id` | UUID | FK, Composite PK | User who follows |
| `followee_id` | UUID | FK, Composite PK | User being followed |
| `created_at` | Timestamp | - | When the follow occurred |

### 3.2 Stories (NoSQL - Cassandra/DynamoDB)
Stories require high write throughput and automatic expiration. Cassandra is ideal due to its wide-column nature and TTL (Time-to-Live) support.

**Table: `stories`**
| Field | Type | Index | Notes |
| :--- | :--- | :--- | :--- |
| `story_id` | UUID | PK | Unique Story ID |
| `user_id` | UUID | Partition Key | Shard by user |
| `media_url` | TEXT | - | Link to S3/CDN |
| `type` | ENUM | - | Image or Video |
| `created_at` | Timestamp | Clustering Key | Sorted descending |
| `expires_at` | Timestamp | - | Used for TTL |

### 3.3 Reels & Posts (NoSQL/Document - MongoDB or PostgreSQL)
Reels are permanent and require complex metadata for search and discovery.

**Table: `reels`**
| Field | Type | Index | Notes |
| :--- | :--- | :--- | :--- |
| `reel_id` | UUID | PK | Unique Reel ID |
| `user_id` | UUID | Index | Creator |
| `video_url` | TEXT | - | S3 Link |
| `caption` | TEXT | - | User description |
| `tags` | ARRAY | GIN Index | For discovery/search |
| `created_at` | Timestamp | Index | Recency |

---

## 4. Core API Design

### 4.1 Media Upload (Stories/Reels)
`POST /v1/media/upload`
*   **Payload:**
    ```json
    {
      "user_id": "uuid",
      "media_type": "REEL", 
      "file": "binary_data",
      "caption": "Check out my trip!",
      "tags": ["travel", "beach"]
    }
    ```
*   **Response:** `202 Accepted` (Processing asynchronously).

### 4.2 Get Feed
`GET /v1/feed?limit=20&offset=0`
*   **Response:**
    ```json
    {
      "items": [
        {
          "post_id": "uuid",
          "user": { "username": "john_doe", "avatar": "url" },
          "media_url": "cdn_url",
          "likes_count": 1200,
          "timestamp": "2023-10-01T10:00:00Z"
        }
      ],
      "next_cursor": "cursor_string"
    }
    ```

### 4.3 Get Stories
`GET /v1/stories`
*   **Response:**
    ```json
    {
      "stories": [
        {
          "user_id": "uuid",
          "content": [
            { "story_id": "uuid", "url": "url", "expires_at": "timestamp" }
          ]
        }
      ]
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Feed Generation: The Fan-out Challenge
Generating a feed for millions of users in real-time is computationally expensive.
*   **Push Model (Fan-out on Write):** When a user posts, the system pushes the post ID into the `Feed Cache` (Redis List) of all their followers. 
    *   *Pros:* Fast reads.
    *   *Cons:* Slow writes for "celebrities" (e.g., a user with 100M followers would trigger 100M writes).
*   **Pull Model (Fan-out on Read):** The system fetches posts from all followed users at the moment the feed is requested and merges them.
    *   *Pros:* Fast writes.
    *   *Cons:* Slow reads.
*   **Hybrid Approach:** 
    *   **Regular Users:** Use the Push model.
    *   **Celebrities:** Use the Pull model. When a user opens their feed, the system fetches the pre-computed feed (from regular follows) and merges it with the latest posts from the celebrities they follow.

### 5.2 Caching Strategy
*   **Edge Caching (CDN):** All images and videos are cached at the edge to reduce latency and origin load.
*   **Feed Cache:** Redis stores the `post_id` list for each user's feed.
*   **User Profile Cache:** LRU cache for frequently accessed user metadata.

### 5.3 Video Transcoding Pipeline
To support various network conditions (3G, 4G, WiFi), videos are processed asynchronously:
1.  Upload to S3 $\rightarrow$ Kafka Event $\rightarrow$ Transcoding Workers.
2.  Workers generate multiple resolutions (360p, 720p, 1080p) and formats (HLS/DASH for adaptive streaming).
3.  Update metadata in `ReelDB` once transcoding is complete.

### 5.4 Database Sharding
*   **UserDB:** Sharded by `user_id`.
*   **StoryDB:** Partitioned by `user_id` and clustered by `created_at` to ensure stories for a single user are stored together and sorted.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Availability vs. Consistency
Instagram prioritizes **Availability and Partition Tolerance (AP)**. If a user likes a post, it is acceptable if the like count is slightly out of sync across different regions for a few seconds. Using a distributed NoSQL store like Cassandra supports this eventual consistency.

### 6.2 Latency vs. Storage
To achieve sub-200ms feed latency, we trade off storage by using **Feed Pre-computation**. We store the same `post_id` in millions of different user feed caches. This increases storage costs significantly but is necessary for the user experience.

### 6.3 SQL vs. NoSQL
*   **PostgreSQL** is used for User profiles and Follows because these require ACID properties and complex relational queries (joins).
*   **Cassandra/DynamoDB** is used for Stories due to the massive write volume and the requirement for automatic data expiration via TTL.
*   **Redis** is used for the Feed because it provides the lowest latency for list-based data structures.""",
}

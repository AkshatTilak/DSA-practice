# News Feed System Design HLD

This guide provides a comprehensive architectural deep-dive into designing a News Feed system similar to Twitter or Facebook. The primary challenge of this system is the **Fan-out** problem: how to efficiently deliver updates from a few users to millions of followers in real-time.

---

## 1. Overview & System Requirements

The goal is to build a system where users can post updates (tweets) and see a curated timeline of updates from people they follow, sorted by reverse chronological order (or an algorithm).

### Functional Requirements
- **Post Tweets**: Users should be able to publish short text updates.
- **Follow/Unfollow**: Users can follow other users to subscribe to their updates.
- **News Feed Retrieval**: Users should see a feed of tweets from all the people they follow.
- **Timeline Pagination**: Feed should be loadable in chunks (infinite scroll).

### Non-Functional Requirements (SLAs)
- **High Availability**: The system must be available $99.99\%$ of the time. Availability is prioritized over strict consistency (CAP Theorem).
- **Low Latency**: Feed generation/loading should happen in under $200\text{ms}$.
- **Scalability**: Must handle hundreds of millions of Daily Active Users (DAU).
- **Eventual Consistency**: It is acceptable if a tweet takes a few seconds to appear in a follower's feed.

### Scale Assumptions
| Metric | Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | $300 \text{ Million}$ |
| **Avg. Follows per User** | $200$ |
| **Tweets per Day** | $500 \text{ Million}$ |
| **Read/Write Ratio** | $100:1$ (Read-heavy) |
| **QPS (Read)** | $\approx 100\text{k} - 500\text{k}$ requests per second |

---

## 2. High-Level System Architecture

The system follows a **decoupled microservices architecture** to allow independent scaling of the write path (posting) and the read path (viewing).

### Architecture Components
1. **API Gateway / Load Balancer**: Routes requests, handles authentication, and rate-limiting.
2. **Tweet Service**: Handles the creation and storage of tweets.
3. **Social Graph Service**: Manages follow/unfollow relationships (typically using a Graph Database or heavily indexed SQL).
4. **Fan-out Service**: The "brain" of the system. It pushes new tweets to the feeds of followers.
5. **Feed Service**: Aggregates and serves the pre-computed feed to the user.
6. **Cache Layer (Redis)**: Stores the pre-computed "News Feed" for active users for $O(1)$ retrieval.
7. **Database Layer**: 
    - **User/Follow DB**: Relational (PostgreSQL/MySQL) for strong consistency on identity.
    - **Tweet DB**: NoSQL (Cassandra or MongoDB) for high write throughput and horizontal scaling.

---

## 3. Key HLD Concepts & Component Design

### The Core Challenge: Fan-out Strategies
Fan-out is the process of delivering a single tweet to all the followers' feeds.

#### A. Push Model (Fan-out on Write)
When a user posts a tweet, the system immediately pushes that tweet into the pre-computed feed caches of all their followers.
- **Pros**: Read latency is extremely low ($O(1)$ to fetch the cache).
- **Cons**: Write latency is high. If a user has $10\text{M}$ followers, $10\text{M}$ cache writes must occur. This is the **"Celebrity Problem."**

#### B. Pull Model (Fan-out on Load)
The feed is not pre-computed. When a user requests their feed, the system fetches the list of people they follow and pulls the most recent tweets from those users.
- **Pros**: Writes are extremely fast ($O(1)$). No write amplification.
- **Cons**: Reads are slow. The system must perform a multi-get/join across many users' tweet lists and sort them.

#### C. Hybrid Model (The Optimal Approach)
We categorize users based on their follower count:
- **Regular Users**: Use the **Push Model**. Since they have few followers, the write amplification is manageable.
- **Celebrities (High Follower Count)**: Use the **Pull Model**. We do not push their tweets to millions of caches. Instead, when a follower loads their feed, the system pulls the celebrity's latest tweets and merges them into the pre-computed feed.

### Storage Selection
- **Redis (Feed Cache)**: We use Redis `ZSET` (Sorted Sets) to store the feed. The `score` is the `timestamp`, allowing for efficient range queries (pagination) and $O(\log N)$ insertion.
- **Cassandra (Tweet Store)**: A wide-column store is ideal here. Partition key = `user_id`, Clustering key = `tweet_id` (sorted by time). This allows very fast retrieval of a specific user's latest tweets.

---

## 4. Data Flows & Fault Tolerance

### Write Path (Posting a Tweet)
1. **User $\to$ Tweet Service**: User submits a tweet.
2. **Tweet Service $\to$ Tweet DB**: Tweet is persisted in Cassandra.
3. **Tweet Service $\to$ Fan-out Service**: An event is pushed to a Message Queue (Kafka).
4. **Fan-out Service**:
    - Checks the author's status (Regular vs. Celebrity).
    - If **Regular**: Fetches follower list from Social Graph $\to$ Updates the Redis Feed Caches of all active followers.
    - If **Celebrity**: Only marks the tweet as "Celebrity Content" in the DB; no push occurs.

### Read Path (Viewing the Feed)
1. **User $\to$ Feed Service**: Request for "Home Timeline."
2. **Feed Service $\to$ Redis**: Fetch the pre-computed list of tweet IDs for the user.
3. **Feed Service $\to$ Social Graph**: Identify which "Celebrities" the user follows.
4. **Feed Service $\to$ Tweet DB**: Pull recent tweets from those celebrities.
5. **Merge & Sort**: Merge the Redis list and the Celebrity list by timestamp $\to$ Return to user.

### Fault Tolerance & Reliability
- **Message Queue (Kafka)**: If the Fan-out service crashes, Kafka ensures that the "push" events are not lost and can be re-processed.
- **Cache Eviction**: We only store feeds for **Active Users** (e.g., users who logged in within the last 30 days) to save memory. Inactive users' feeds are computed on-demand (Pull model).
- **Replication**: Cassandra uses a replication factor of 3 across different availability zones to prevent data loss during node failure.

---

## 5. Production Trade-offs

### CAP Theorem Analysis
This system chooses **AP (Availability and Partition Tolerance)**. 
- In a global system, we cannot afford to block a user's "Post" request just because a follower's cache in another region is unreachable.
- **Trade-off**: We accept **Eventual Consistency**. A follower might see a tweet 2 seconds after it was posted.

### Complexity Analysis
| Operation | Push Model (Regular) | Pull Model (Celebrity) | Hybrid (Optimal) |
| :--- | :--- | :--- | :--- |
| **Write (Post)** | $O(\text{Followers})$ | $O(1)$ | $O(\text{Followers if Regular})$ |
| **Read (Feed)** | $O(1)$ | $O(\text{Followings} \times \text{AvgTweets})$ | $O(1) + O(\text{Celebs followed})$ |
| **Storage** | High (Duplicate feeds) | Low | Balanced |

### Summary of Trade-offs
- **Memory vs. Latency**: Pre-computing feeds in Redis uses massive amounts of RAM but provides sub-millisecond read response times.
- **Write Amplification vs. Read Latency**: The hybrid approach mitigates the "Thundering Herd" problem where a celebrity tweet would otherwise crash the database if everyone tried to "pull" it simultaneously.
INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Recommendation Engine (Netflix-style).',
    'groups': ['Real-World Systems', 'Deep Learning'],
    'readme_content': """# Recommendation Engine HLD (Netflix-style)

## 1. Overview & System Requirements

A recommendation engine is a sophisticated information filtering system that predicts the "rating" or "preference" a user would give to an item. In a Netflix-style system, the goal is to maximize user engagement (watch time) and retention by surfacing the most relevant content among thousands of available titles.

### Functional Requirements
*   **Personalized Home Page:** Provide a curated list of movies/shows for each user.
*   **Similar Content:** Suggest items similar to the one currently being viewed ("More Like This").
*   **Real-time Adaptation:** Update recommendations based on the user's immediate activity (e.g., just finished a horror movie).
*   **Cold Start Handling:** Provide reasonable recommendations for new users or new content with no history.
*   **Diversity and Serendipity:** Avoid "filter bubbles" by introducing diverse genres and new discoveries.

### Non-Functional Requirements
*   **Low Latency:** The home page must load in $< 200\text{ms}$. Complex ML models cannot run in real-time on the entire library.
*   **High Availability:** The system must be highly available. If the recommendation engine fails, the system should fallback to "Trending Now" (global popularity).
*   **Scalability:** Support $200\text{M}+$ Daily Active Users (DAU) and millions of interaction events per second.
*   **Eventual Consistency:** It is acceptable if a movie watched one second ago doesn't disappear from recommendations immediately.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **DAU** | 200 Million |
| **Content Library** | 10,000 - 50,000 Titles |
| **Daily Events** | $\approx 10\text{ Billion}$ (plays, pauses, likes, searches) |
| **Read QPS** | $100\text{k} - 500\text{k}$ (Home page requests) |
| **Write QPS** | $1\text{M} - 5\text{M}$ (User activity streams) |

---

## 2. High-Level System Architecture

The architecture follows a **Multi-Stage Pipeline** pattern. Because calculating a deep learning score for every single movie for every single user is computationally impossible in real-time, we use a funnel approach.

### Architecture Diagram Concept
`User` $\rightarrow$ `API Gateway` $\rightarrow$ `Recommendation Service` $\rightarrow$ `[Candidate Generation] $\rightarrow$ [Ranking] $\rightarrow$ [Re-Ranking]` $\rightarrow$ `Response`

### Component Breakdown
1.  **API Gateway:** Handles authentication, rate limiting, and routes requests to the Recommendation Service.
2.  **Recommendation Service:** The orchestrator that coordinates the retrieval, ranking, and filtering stages.
3.  **Candidate Generation (Retrieval):** A fast stage that narrows down the library from $50,000$ titles to $\approx 200-500$ candidates using simple heuristics or embeddings.
4.  **Ranking (Scoring):** A heavy ML model (e.g., Deep Neural Network) that predicts the exact probability of a user clicking/watching each of the $\approx 500$ candidates.
5.  **Re-Ranking (Filtering):** Applies business logic (e.g., remove already watched content, ensure genre diversity, promote sponsored content).
6.  **Feature Store:** A low-latency key-value store (Redis) containing pre-computed user and item embeddings/features.
7.  **Vector Database:** Stores item embeddings to allow for Approximate Nearest Neighbor (ANN) searches.

---

## 3. Key HLD Concepts & Component Design

### A. The Recommendation Pipeline (The Funnel)

#### Stage 1: Candidate Generation (Retrieval)
The goal is high **recall**. We use multiple "retrievers" to get different perspectives:
*   **Collaborative Filtering (CF):** "Users who liked X also liked Y."
*   **Content-Based Filtering:** "You liked Sci-Fi, here are more Sci-Fi movies."
*   **Popularity-Based:** Top trending movies in the user's region.
*   **Embeddings (Two-Tower Model):** A User Tower and an Item Tower project both users and items into the same $N$-dimensional vector space. We find items where the cosine similarity $\cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$ is highest.

#### Stage 2: Ranking (Scoring)
The goal is high **precision**. We use a complex model (e.g., Wide & Deep Learning or Transformers).
*   **Features used:** User demographics, time of day, device type, recent watch history, item popularity, and the interaction between user and item.
*   **Output:** A probability score $P(\text{watch} | \text{user, item})$.

#### Stage 3: Re-Ranking
*   **Deduping:** Remove movies the user has already seen.
*   **Diversity:** If the top 10 are all "Action," swap some for "Comedy" to prevent fatigue.
*   **Business Constraints:** Boost new releases or "Netflix Originals."

### B. Data Storage & Technology Choices

| Component | Technology | Why? |
| :--- | :--- | :--- |
| **User/Item Metadata** | Cassandra / DynamoDB | High write throughput for user activity and linear scalability. |
| **Feature Store** | Redis / Feast | Sub-millisecond latency required to feed features into the Ranking model. |
| **Vector Store** | Milvus / Pinecone / FAISS | Optimized for ANN (Approximate Nearest Neighbor) search via HNSW indexing. |
| **Message Queue** | Apache Kafka | Decouples user activity (writes) from model updates (async processing). |
| **Batch Processing** | Apache Spark | Handles massive matrix factorization and model training offline. |

### C. Handling the Cold Start Problem
*   **New User:** Use a "Welcome Survey" (choose 3 genres you like) $\rightarrow$ map to initial embeddings $\rightarrow$ provide popularity-based results for their region.
*   **New Item:** Use **Content-Based Filtering**. Analyze the movie's metadata (genre, cast, plot keywords) to place it near similar existing movies in the vector space.

---

## 4. Data Flows & Fault Tolerance

### Read Path: Generating Recommendations
1.  **Request:** User opens the app $\rightarrow$ Request hits `Recommendation Service`.
2.  **Retrieval:** 
    *   Fetch User Embedding from `Feature Store`.
    *   Query `Vector DB` for the top 100 nearest items.
    *   Fetch top 50 "Trending" items from `Redis`.
3.  **Ranking:** 
    *   Combine all candidates ($\approx 150$ items).
    *   Fetch detailed features for these 150 items from `Feature Store`.
    *   Pass features into the `Ranking Model` (deployed as a microservice via TensorFlow Serving or PyTorch).
4.  **Re-Ranking:** Apply filters (remove watched) and diversity logic.
5.  **Response:** Return the sorted list of Movie IDs to the UI.

### Write Path: Processing User Activity
1.  **Event:** User watches "Stranger Things" $\rightarrow$ Event sent to `Kafka`.
2.  **Streaming:** `Flink` or `Spark Streaming` consumes the event.
3.  **Update:** 
    *   Update User Profile in `Cassandra`.
    *   Update real-time features in `Feature Store` (e.g., `last_genre_watched = 'Sci-Fi'`).
4.  **Offline Training:** Periodically, a `Spark` job runs on the entire dataset to re-calculate embeddings and re-train the Ranking model.

### Fault Tolerance & Resilience
*   **Fallback Mechanism:** If the Ranking model times out or crashes, the service skips to the "Retrieval" results. If the Retrieval stage fails, it returns a statically cached "Global Top 10" list.
*   **Circuit Breaker:** Use a pattern (e.g., Resilience4j) to stop calling the Ranking model if its error rate exceeds $5\%$, preventing cascading failure.
*   **Replication:** Vector DBs and Feature Stores are replicated across multiple Availability Zones (AZs).

---

## 5. Production Trade-offs

### Accuracy vs. Latency
*   **Trade-off:** A massive Transformer model would be more accurate but take $500\text{ms}$ to score one item.
*   **Solution:** The **Funnel Architecture**. We use a cheap, fast model for retrieval and a heavy, expensive model only for the final few hundred candidates.

### Exploration vs. Exploitation
*   **Exploitation:** Showing the user exactly what they like (increases short-term clicks).
*   **Exploration:** Showing the user something completely new (prevents long-term boredom/churn).
*   **Strategy:** Use **$\epsilon$-greedy algorithm** or **Thompson Sampling**. For example, $90\%$ of the list is "Exploitation" and $10\%$ is "Exploration" (randomly sampled high-quality content from other genres).

### CAP Theorem Application
*   The Recommendation system prioritizes **Availability** and **Partition Tolerance** (AP).
*   **Consistency:** Eventual consistency is acceptable. If a user likes a movie, it doesn't need to reflect in their recommendations across all devices within milliseconds.

### Complexity Analysis
| Stage | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Retrieval (ANN)** | $O(\log N)$ | $O(N \times D)$ | $N$ = items, $D$ = embedding dim |
| **Ranking** | $O(C \times M)$ | $O(M)$ | $C$ = candidates, $M$ = model size |
| **Re-ranking** | $O(C \log C)$ | $O(C)$ | Sorting the candidates |""",
    'solutions': """# System Design Document: High-Scale Recommendation Engine (Netflix-style)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Personalized Recommendations:** Provide a list of movies/shows tailored to the user's preferences on the home screen.
*   **Similar Content:** "Because you watched X" — recommend items similar to a specific piece of content.
*   **Trending/Popular:** Provide global or regional trending content for new users (solving the cold-start problem).
*   **Real-time Feedback Loop:** Incorporate recent user actions (likes, views, skips) into recommendations quickly.
*   **Diversity & Serendipity:** Ensure the engine doesn't create a "filter bubble" by introducing diverse genres.

### 1.2 Non-Functional Requirements
*   **Low Latency:** The recommendation API must respond within < 200ms to ensure a seamless UI experience.
*   **High Availability:** The system must be available 24/7; failing to provide recommendations should fallback to a "Popular" list rather than a 500 error.
*   **Scalability:** Support 200M+ users and 50k+ content titles with billions of interaction events daily.
*   **Eventual Consistency:** It is acceptable if a recommendation update takes a few minutes to reflect a user's latest action.

### 1.3 Scale Estimations
*   **Users:** 200 Million.
*   **Content Catalog:** 50,000 titles.
*   **Daily Events:** ~1 Billion events (play, pause, search, rate).
*   **Read QPS:** 100k+ requests per second during peak hours.
*   **Storage:** 1B events/day $\times$ 100 bytes $\approx$ 100 GB/day of raw interaction logs.

---

## 2. High-Level Architecture

A modern recommendation engine uses a **Two-Stage Pipeline**: **Candidate Generation (Retrieval)** followed by **Ranking (Scoring)**. This prevents the need to run a complex ML model against the entire catalog for every request.

### 2.1 Architecture Diagram

```mermaid
graph TD
    User((User)) --> Gateway[API Gateway]
    Gateway --> RecService[Recommendation Service]
    
    subgraph "Online Serving Path"
        RecService --> CandidateGen[Candidate Generation Stage]
        CandidateGen --> VectorDB[(Vector DB / Milvus)]
        CandidateGen --> RedisCache[(Redis Cache)]
        
        RecService --> RankingService[Ranking Service]
        RankingService --> FeatureStore[(Feature Store / Feast)]
        RankingService --> MLModel[Ranking ML Model]
        
        RecService --> PostProc[Post-Processing/Filtering]
    end

    subgraph "Offline Training Path"
        User --> Events[Event Collector]
        Events --> Kafka[Kafka Stream]
        Kafka --> DataLake[(S3/HDFS Data Lake)]
        DataLake --> Spark[Spark/Flink Processing]
        Spark --> ModelTraining[ML Training Pipeline]
        ModelTraining --> MLModel
        ModelTraining --> VectorDB
        ModelTraining --> FeatureStore
    end
```

### 2.2 Component Descriptions
1.  **Event Collector:** Captures implicit (watch time, clicks) and explicit (thumbs up/down) signals.
2.  **Candidate Generation (Retrieval):** Reduces the catalog from 50k to $\sim$200-500 candidates. Uses techniques like Matrix Factorization or Two-Tower Neural Networks to find embeddings.
3.  **Ranking (Scoring):** A deep learning model (e.g., Wide & Deep, DeepFM) that takes the 500 candidates and predicts the probability of a user clicking/watching.
4.  **Feature Store:** A low-latency KV store providing user features (e.g., "preferred genre") and item features (e.g., "average rating") to the Ranker.
5.  **Vector DB:** Stores content embeddings. Uses Approximate Nearest Neighbor (ANN) search to find similar items in $O(\log N)$.
6.  **Post-Processing:** Applies business logic (e.g., remove already watched movies, filter age-restricted content, ensure genre diversity).

---

## 3. Detailed Database Schema Design

### 3.1 Interaction Store (Cold Storage/Data Lake)
Used for offline model training.
*   **Table:** `user_interactions` (Stored in Parquet/S3)
    *   `user_id` (UUID)
    *   `content_id` (UUID)
    *   `interaction_type` (Enum: VIEW, LIKE, DISLIKE, SEARCH)
    *   `duration_watched` (Integer - seconds)
    *   `timestamp` (Timestamp)

### 3.2 Content Metadata (SQL - PostgreSQL)
Stores authoritative metadata for the catalog.
*   **Table:** `content`
    *   `content_id` (PK, UUID)
    *   `title` (Varchar)
    *   `genre_ids` (Array/Relation)
    *   `release_date` (Date)
    *   `rating` (Float)
    *   **Index:** B-Tree on `genre_ids` and `release_date`.

### 3.3 Feature Store (NoSQL - Cassandra or DynamoDB)
Stores pre-computed features for the Ranking model.
*   **Table:** `user_features`
    *   `user_id` (PK) $\rightarrow$ `{ "pref_genres": ["Sci-Fi", "Horror"], "avg_watch_time": 45, "last_login": "..." }`
*   **Table:** `item_features`
    *   `content_id` (PK) $\rightarrow$ `{ "popularity_score": 0.98, "avg_completion_rate": 0.75 }`

### 3.4 Vector Store (Milvus / Pinecone)
Stores the embeddings generated by the Two-Tower model.
*   **Collection:** `content_embeddings`
    *   `content_id` (ID)
    *   `embedding` (Vector[128 dimensions])
    *   **Index:** HNSW (Hierarchical Navigable Small World) for fast ANN search.

---

## 4. Core API Design

### 4.1 Get Recommendations
`GET /v1/recommendations`
*   **Query Params:** `user_id`, `limit=20`, `offset=0`
*   **Response:**
```json
{
  "user_id": "u123",
  "recommendations": [
    {
      "content_id": "m456",
      "score": 0.982,
      "reason": "Because you watched Inception",
      "rank": 1
    },
    {
      "content_id": "m789",
      "score": 0.851,
      "reason": "Trending in your region",
      "rank": 2
    }
  ],
  "request_id": "req-abc-123"
}
```

### 4.2 Record User Interaction
`POST /v1/events`
*   **Payload:**
```json
{
  "user_id": "u123",
  "content_id": "m456",
  "event_type": "WATCH",
  "metadata": {
    "timestamp": 1625097600,
    "duration_seconds": 1200,
    "device": "SmartTV"
  }
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 The "Cold Start" Strategy
*   **New User:** Since no history exists, the system defaults to "Popularity-based" recommendations or asks the user to select 3 favorite genres during onboarding.
*   **New Item:** Use **Content-Based Filtering**. Extract features from the movie description/genre and map the item into the vector space near similar existing items.

### 5.2 Caching Strategy
*   **Pre-computed Recommendations:** For the most active users, pre-calculate the Top 100 recs every 4 hours and store them in **Redis**.
*   **Feature Cache:** Use a local LRU cache in the Ranking Service to store frequently accessed `item_features`.

### 5.3 Model Deployment & A/B Testing
*   **Shadow Mode:** Deploy a new model that generates predictions in parallel with the production model, but doesn't serve them to the user. Compare results offline.
*   **Canary Deployment:** Route 5% of traffic to the new ranking model to measure the CTR (Click-Through Rate) increase.

### 5.4 Handling Data Drift
*   Implement a monitoring pipeline that tracks the distribution of predicted scores. If the average predicted probability drops significantly, trigger an automated model retrain.

---

## 6. Trade-off Analysis

### 6.1 Latency vs. Accuracy
*   **Trade-off:** A complex Deep Learning model is more accurate but slower.
*   **Decision:** We use the **Two-Stage approach**. The Retrieval stage is optimized for latency (ANN search), while the Ranking stage is optimized for accuracy (Complex Model). This provides the best of both worlds.

### 6.2 CAP Theorem
*   **Priority:** **Availability and Partition Tolerance (AP)**.
*   **Reasoning:** If the recommendation system is temporarily inconsistent (e.g., a movie the user just disliked still appears for a few minutes), it is far better than the home page failing to load. We accept eventual consistency in the feature store and embeddings.

### 6.3 Storage vs. Computation
*   **Trade-off:** Pre-computing recommendations for all 200M users would require massive storage ($200M \times 100 \text{ IDs}$).
*   **Decision:** Hybrid approach. Pre-compute for "power users" (top 10%) and compute on-the-fly for the remaining 90% using the retrieval-ranking pipeline.

### 6.4 Vector Search: Exact vs. Approximate
*   **Trade-off:** Exact KNN search is $O(N)$, which is too slow for $N=50,000$ at 100k QPS.
*   **Decision:** Use **ANN (Approximate Nearest Neighbor)**. It reduces search time to $O(\log N)$ by sacrificing a small amount of recall (precision), which is negligible in a recommendation context.""",
}

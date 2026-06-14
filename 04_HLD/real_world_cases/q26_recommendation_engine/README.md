# Recommendation Engine HLD (Netflix-style)

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
| **Re-ranking** | $O(C \log C)$ | $O(C)$ | Sorting the candidates |
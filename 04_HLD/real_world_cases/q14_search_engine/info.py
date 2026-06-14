INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Search Engine (Google-scale).',
    'groups': ['Real-World Systems', 'Distributed Systems'],
    'readme_content': """# Search Engine (Google-Scale) HLD

Designing a search engine at Google-scale is one of the most complex challenges in distributed systems. It requires managing an astronomical amount of data (the entire public web), processing it asynchronously, and serving queries with millisecond latency.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Web Crawling**: Automatically discover and download web pages from the internet.
- **Indexing**: Process downloaded content into a searchable format (Inverted Index).
- **Querying**: Allow users to input keywords and retrieve the most relevant documents.
- **Ranking**: Order results based on relevance, authority, and quality (e.g., PageRank).
- **Freshness**: Ensure new or updated content is indexed in a timely manner.

### Non-Functional Requirements
- **Low Latency**: Search results must be returned in $< 200\text{ms}$.
- **High Availability**: The system must be available $99.99\%$ of the time.
- **Scalability**: Must handle trillions of pages and hundreds of thousands of queries per second (QPS).
- **Durability**: Indexed data must be stored reliably across distributed clusters.

### Scale Assumptions
| Metric | Estimated Value |
| :--- | :--- |
| **Total Web Pages** | $\approx 10^{12}$ (Trillions) |
| **Average Page Size** | $100\text{ KB}$ |
| **Daily New/Updated Pages** | $\approx 10^9$ |
| **Queries Per Second (QPS)** | $10^5 \text{ to } 10^6$ |
| **Total Storage** | Exabytes (raw HTML + Index) |

---

## 2. High-Level System Architecture

The system is split into two primary planes: the **Offline Data Pipeline** (Crawling & Indexing) and the **Online Query Pipeline** (Searching & Ranking).

### Architecture Diagram Components

#### A. The Crawling Pipeline (Offline)
1. **Seed URLs**: A set of high-quality starting points.
2. **URL Frontier**: A distributed priority queue that manages which URLs to visit next, handling politeness (not DOSing servers) and priority.
3. **HTML Downloader**: Distributed workers that fetch pages using HTTP.
4. **Content Extractor**: Parses HTML, extracts text, and finds new outbound links.
5. **Document Store**: A massive NoSQL store (e.g., BigTable/HBase) storing the raw HTML and metadata.

#### B. The Indexing Pipeline (Offline)
1. **Tokenizer/Parser**: Cleans text (lowercase, stop-word removal, stemming).
2. **Inverted Index Builder**: Maps each word to a list of documents containing it.
3. **PageRank Calculator**: A distributed MapReduce job that calculates the "authority" of pages based on the link graph.
4. **Distributed Index Store**: Sharded storage of the inverted index.

#### C. The Query Pipeline (Online)
1. **API Gateway/Load Balancer**: Routes user requests.
2. **Query Processor**: Parses the query, handles synonyms, and expands terms.
3. **Index Searcher (Aggregator)**: Queries multiple index shards in parallel.
4. **Ranker (Re-ranking)**: Applies a complex ML model to the top $K$ results to refine the order.
5. **Cache Layer**: Redis/Memcached for popular queries.

---

## 3. Key HLD Concepts & Component Design

### The Inverted Index
The core data structure of any search engine. Instead of mapping `Document $\rightarrow$ Words`, it maps `Word $\rightarrow$ List of Document IDs`.

**Example:**
- Doc 1: "I love distributed systems"
- Doc 2: "Distributed systems are hard"
- **Index:**
  - `love` $\rightarrow$ $\{1\}$
  - `distributed` $\rightarrow$ $\{1, 2\}$
  - `systems` $\rightarrow$ $\{1, 2\}$
  - `hard` $\rightarrow$ $\{2\}$

### Index Sharding Strategies
To handle trillions of documents, the index must be partitioned across thousands of machines.

| Strategy | Description | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Term-based** | Each shard holds all docs for a specific set of words. | Fast lookup for a single term. | Hot-spotting (e.g., the word "the" crashes a shard). |
| **Doc-based** | Each shard holds the full index for a subset of documents. | Even load distribution. | Must query every shard for every search. |

**Decision**: **Document-based sharding** is generally preferred at scale. Every query is broadcast to all shards, and the results are merged. This avoids the "hot word" problem.

### Ranking Algorithms
1. **TF-IDF (Term Frequency-Inverse Document Frequency)**: Measures how important a word is to a document in a collection.
2. **BM25**: An evolution of TF-IDF that handles term saturation better.
3. **PageRank**: An algorithm that treats links as votes. A page is important if important pages link to it.
   $$\text{PR}(A) = \frac{1-d}{N} + d \sum \frac{\text{PR}(T_i)}{C(T_i)}$$
   *(Where $d$ is damping factor, $T_i$ are pages linking to $A$, and $C(T_i)$ is the count of outbound links from $T_i$).*

### Technology Stack Choices
- **Storage (Raw Docs)**: **BigTable** or **HBase** (Wide-column stores) for massive scale and fast lookups by URL.
- **Index Processing**: **Apache Spark** or **MapReduce** for batch calculating PageRank and building the index.
- **Coordination**: **ZooKeeper** for managing cluster state and shard locations.
- **Cache**: **Redis** for caching the most frequent search results.

---

## 4. Data Flows & Fault Tolerance

### Request Flow: User Search
1. **Client $\rightarrow$ Load Balancer**: User enters "Distributed Systems".
2. **Query Processor**: 
   - Checks **Redis Cache**. If hit, return immediately.
   - If miss: Tokenizes query $\rightarrow$ "distributed", "systems".
3. **Fan-out Search**: The processor sends the query to **all Index Shards**.
4. **Local Search**: Each shard looks up "distributed" and "systems" in its local inverted index and returns the top $N$ candidate Doc IDs.
5. **Aggregation & Ranking**:
   - The processor merges candidates.
   - It fetches metadata (PageRank, Title, Snippet) for the top $K$ results.
   - A **Machine Learning Ranker** (e.g., using BERT or LambdaMART) re-orders results based on user location, history, and quality.
6. **Response**: Returns a paginated list of results to the user.

### The Crawl Cycle
1. **Frontier $\rightarrow$ Downloader**: The frontier picks a URL based on priority.
2. **Downloader $\rightarrow$ Extractor**: Fetches HTML; extractor pulls text and new links.
3. **Extractor $\rightarrow$ Frontier**: New links are added back to the frontier for future crawling.
4. **Extractor $\rightarrow$ Doc Store**: The cleaned page content is saved.

### Fault Tolerance & Reliability
- **Replication**: Each index shard is replicated across multiple nodes (Leader-Follower). If a shard leader fails, a follower is promoted.
- **Checkpointing**: The Index Builder saves state periodically. If a MapReduce job fails, it resumes from the last checkpoint.
- **Circuit Breakers**: If a specific index shard is slow/timed out, the aggregator ignores it to maintain low latency, accepting a slight drop in recall (completeness).

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
In a search engine, **Availability and Partition Tolerance (AP)** are prioritized over Strong Consistency. 
- **Trade-off**: If a web page is updated, it is acceptable if the search result reflects the old version for a few hours. We prioritize returning *some* results quickly over returning the *absolute latest* version of every page.

### Latency vs. Precision (The Two-Stage Pipeline)
Computing a complex ML ranking model for 1 billion candidate documents is impossible in $200\text{ms}$.
- **Stage 1 (Retrieval)**: Use a fast, "cheap" algorithm (Inverted Index + BM25) to narrow down billions of docs to $\approx 1,000$ candidates.
- **Stage 2 (Re-ranking)**: Use a "heavy" ML model to precisely rank only those $1,000$ candidates.

### Storage vs. Performance
- **Compression**: Inverted lists are stored using **Delta Encoding** (storing the difference between Doc IDs rather than the IDs themselves) and **Variable-byte encoding** to reduce Disk I/O and memory footprint.

---

## Summary Table: Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Crawling** | $O(\text{Pages} \times \text{Avg Links})$ | $O(\text{Total HTML})$ | Bound by network I/O. |
| **Indexing** | $O(\text{Total Words})$ | $O(\text{Unique Words} \times \text{Avg Docs})$ | Batch process (MapReduce). |
| **Querying** | $O(\frac{\text{Terms} \times \text{Avg List Length}}{\text{Shards}})$ | $O(\text{Results})$ | Parallelized across shards. |
| **Ranking** | $O(K \log K)$ | $O(K)$ | $K$ is the candidate set size. |""",
    'solutions': """# System Design: Google-Scale Search Engine

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Web Crawling:** Automatically discover and download web pages from the internet.
*   **Indexing:** Process crawled content and build a searchable data structure (Inverted Index).
*   **Searching:** Allow users to input queries and retrieve the most relevant documents.
*   **Ranking:** Order results based on relevance and authority (e.g., PageRank, ML-based scoring).
*   **Freshness:** Regularly update indices to reflect changes in the web.

### 1.2 Non-Functional Requirements
*   **Low Latency:** Query results must return in $< 200\text{ms}$.
*   **High Scalability:** Handle billions of pages and millions of queries per second (QPS).
*   **High Availability:** The system must be available $99.99\%$ of the time.
*   **Fault Tolerance:** No single point of failure; ability to recover from node crashes.
*   **Accuracy/Relevance:** High precision and recall for search results.

### 1.3 Scale Estimations
*   **Pages to Index:** $\sim 10^{12}$ (1 Trillion pages).
*   **Average Page Size:** $100\text{ KB}$.
*   **Total Storage (Raw):** $10^{12} \times 100\text{ KB} \approx 100\text{ Petabytes}$.
*   **Search QPS:** $\sim 100,000$ to $1,000,000$ queries per second.
*   **Index Size:** Assuming average 500 words per page, total entries $\approx 5 \times 10^{14}$.

---

## 2. High-Level Architecture

The system is divided into two primary planes: the **Write Path (Indexing Pipeline)** and the **Read Path (Query Pipeline)**.

### 2.1 Architecture Diagram

```mermaid
graph TD
    subgraph "Indexing Pipeline (Write Path)"
        Seed[Seed URLs] --> Frontier[URL Frontier]
        Frontier --> Fetcher[Web Fetcher]
        Fetcher --> DNS[DNS Resolver]
        Fetcher --> ContentExtractor[Content Extractor]
        ContentExtractor --> DupDetector[Duplicate Detector]
        DupDetector --> Indexer[Indexer/Mapper]
        Indexer --> InvIndex[(Inverted Index)]
        Indexer --> DocStore[(Document Store)]
        Indexer --> PageRank[PageRank Calculator]
        PageRank --> PageRankStore[(PageRank Store)]
    end

    subgraph "Search Pipeline (Read Path)"
        User((User)) --> LB[Load Balancer]
        LB --> QuerySvc[Query Service]
        QuerySvc --> Cache[Result Cache]
        QuerySvc --> Parser[Query Parser/Expander]
        Parser --> IndexSearch[Index Searcher]
        IndexSearch --> InvIndex
        IndexSearch --> PageRankStore
        IndexSearch --> Ranker[Ranking Engine/ML Model]
        Ranker --> ResultSvc[Result Aggregator]
        ResultSvc --> User
    end

    InvIndex -.-> IndexSearch
    DocStore -.-> ResultSvc
```

### 2.2 Component Breakdown

#### A. Indexing Pipeline
1.  **URL Frontier:** A distributed queue that manages which URLs to visit next, handling politeness (avoiding DDOSing a site) and priority.
2.  **Web Fetcher:** Downloads HTML content. Uses a distributed DNS cache to minimize lookup latency.
3.  **Content Extractor & Duplicate Detector:** Extracts text and cleans HTML. Uses **SimHash** or **MinHash** to detect near-duplicate pages to avoid indexing the same content multiple times.
4.  **Indexer:** Tokenizes text, removes stop words, performs stemming/lemmatization, and updates the Inverted Index.
5.  **PageRank Calculator:** An offline MapReduce/Spark job that computes the importance of pages based on the link graph.

#### B. Search Pipeline
1.  **Query Service:** The entry point. Handles authentication, rate limiting, and request routing.
2.  **Query Parser:** Converts the raw string into a structured query (e.g., handling quotes, minus signs, and synonyms).
3.  **Index Searcher:** Queries the Inverted Index to find the list of documents containing the search terms (Posting Lists).
4.  **Ranking Engine:** Applies a scoring function combining **TF-IDF/BM25** (term frequency) and **PageRank** (global authority) to sort results.
5.  **Result Aggregator:** Fetches snippets and titles from the Document Store to present to the user.

---

## 3. Detailed Database Schema Design

### 3.1 The Inverted Index (The Core)
Because of the scale, a traditional SQL database cannot store the index. We use a **Distributed Key-Value Store** (e.g., BigTable or HBase).

**Schema:**
*   **Key:** `term` (e.g., "distributed_systems")
*   **Value:** `PostingList` $\to$ `List<{doc_id, frequency, positions[]}>`

*Optimization:* Since posting lists can be massive, they are compressed using **Delta Encoding** or **Variable Byte Encoding** and split into shards.

### 3.2 Document Store
Stores the actual page content or a compressed version for snippet generation.
*   **Store:** NoSQL Column-Family Store (Cassandra/HBase).
*   **Key:** `doc_id`
*   **Value:** `{url, title, body_text, language, last_crawled_timestamp}`

### 3.3 PageRank Store
*   **Store:** Distributed KV store.
*   **Key:** `doc_id`
*   **Value:** `rank_score` (float)

### 3.4 URL Frontier Store
*   **Store:** Distributed Queue / Database (Redis + MySQL for persistence).
*   **Fields:** `url`, `priority`, `last_visited`, `status` (Pending, Visited, Failed).

---

## 4. Core API Design

### 4.1 Search API
**Endpoint:** `GET /v1/search`

**Request Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `q` | String | The search query |
| `page` | Integer | Page number for pagination |
| `start` | Integer | Offset for results |
| `filter` | String | Filter by date, region, etc. |

**Response Payload:**
```json
{
  "query": "system design",
  "total_results": 1500000,
  "latency_ms": 45,
  "results": [
    {
      "doc_id": "abc123xyz",
      "url": "https://example.com/system-design",
      "title": "Mastering System Design",
      "snippet": "...the core principles of <b>system design</b> involve scalability...",
      "rank": 1
    },
    {
      "doc_id": "def456uvw",
      "url": "https://blog.tech/design-guide",
      "title": "Guide to Distributed Systems",
      "snippet": "...when designing a <b>system</b>, consider the CAP theorem...",
      "rank": 2
    }
  ]
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Index Sharding (Partitioning)
To handle trillions of documents, the index must be partitioned across thousands of nodes:
*   **Document-based Partitioning (Local Index):** Each node stores a full index for a subset of documents. A query is broadcast to all nodes, and results are merged. (Better for write-heavy workloads).
*   **Term-based Partitioning (Global Index):** Each node stores all documents for a specific set of terms (e.g., Node A handles 'A-C', Node B 'D-F'). (Better for read-heavy workloads, but creates hotspots for common terms like "the" or "news").
*   **Hybrid Approach:** Use term-based for rare words and document-based for common words.

### 5.2 Caching Strategy
*   **Query Cache:** Store `Query String $\to$ Result List` in Redis. Very high hit rate for trending topics.
*   **Index Cache:** Keep frequently accessed "Posting Lists" in memory (RAM) using an LRU cache.
*   **DNS Cache:** To avoid repeated lookups during crawling.

### 5.3 Ranking Algorithm
1.  **Phase 1 (Retrieval):** Use the Inverted Index to get a candidate set of $\sim 10,000$ documents using BM25.
2.  **Phase 2 (Ranking):** Pass the candidate set through a heavy Machine Learning model (e.g., Learning to Rank - LTR) using features like:
    *   PageRank.
    *   User location and search history.
    *   Click-through rate (CTR) of the link for that query.
    *   Document freshness.

### 5.4 Crawling Politeness & Scheduling
*   **Robots.txt:** The fetcher must respect `robots.txt` to avoid banned areas.
*   **Politeness:** Maintain a queue per domain to ensure the fetcher doesn't hit one server too many times per second.
*   **Priority:** Pages with higher PageRank are recrawled more frequently.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Availability vs. Consistency
A search engine prioritizes **Availability and Partition Tolerance (AP)**. It is acceptable if a user sees a slightly outdated search result (Eventual Consistency) rather than the system being unavailable. The crawling and indexing process is asynchronous by nature.

### 6.2 Latency vs. Storage
*   **Storage Trade-off:** We store the index multiple times (replication) and use massive Document Stores to avoid expensive on-the-fly computations. We sacrifice disk space for millisecond retrieval.
*   **Latency Trade-off:** We use a multi-stage ranking process. We don't run a complex ML model on 1 billion documents; we prune the set to 10k using a fast index lookup first, then rank the small set.

### 6.3 Precision vs. Recall
*   **Recall:** Ensuring all relevant documents are found. (Improved by query expansion/synonyms).
*   **Precision:** Ensuring the top results are actually relevant. (Improved by the ML Ranking Engine).
*   In a Google-scale engine, **Precision** is more important for the first page of results, as users rarely click past page one.""",
}

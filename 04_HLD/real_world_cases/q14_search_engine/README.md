# Search Engine (Google-Scale) HLD

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
| **Ranking** | $O(K \log K)$ | $O(K)$ | $K$ is the candidate set size. |
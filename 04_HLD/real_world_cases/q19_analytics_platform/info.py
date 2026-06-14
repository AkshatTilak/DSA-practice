INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Analytics Platform (Batch + Real-time).',
    'groups': ['Real-World Systems', 'Data Pipelines'],
    'readme_content': """# Analytics Platform (Batch + Real-time) HLD

An Analytics Platform is a mission-critical system designed to ingest massive volumes of event data (clicks, views, transactions) and transform them into actionable insights. The primary challenge is the **tension between latency and accuracy**: real-time streams provide immediate insights but may be approximate, while batch processing provides absolute accuracy but with significant lag.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Event Ingestion**: Collect events from various sources (Web, Mobile, Backend) with high throughput.
- **Real-time Analytics**: Provide low-latency dashboards for monitoring (e.g., "How many users are active right now?").
- **Batch Analytics**: Provide deep-dive historical reports (e.g., "What was the Monthly Active User (MAU) growth over the last 2 years?").
- **Query Interface**: Support aggregations (`SUM`, `COUNT`, `AVG`) and filtering across various dimensions (Geography, Device, User Segment).

### Non-Functional Requirements
- **Scalability**: Must handle millions of events per second (EPS) and petabytes of historical data.
- **Availability**: High availability for ingestion (we cannot afford to lose events).
- **Durability**: Once an event is received, it must be stored permanently in a data lake.
- **Latency**: 
    - **Ingestion to Real-time Dashboard**: $< 1$ second.
    - **Query Latency**: $< 500\text{ms}$ for common dashboard queries.
- **Accuracy**: Batch layer must be the "Source of Truth" (100% accuracy).

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million |
| **Events per User/Day** | 10 events $\rightarrow$ 1 Billion events/day |
| **Average Event Size** | 1 KB $\rightarrow$ 1 TB of raw data/day |
| **Write QPS** | $\approx 11,500$ events/sec average (Peaks $5\times$ to $10\times$) |
| **Read QPS** | Low to Medium (mostly internal analysts/dashboards) |

---

## 2. High-Level System Architecture

The system follows the **Lambda Architecture**, which separates the data flow into a "Speed Layer" and a "Batch Layer" to balance latency and accuracy.

### Architecture Diagram (Conceptual Flow)
`Client` $\rightarrow$ `API Gateway` $\rightarrow$ `Message Queue (Kafka)` $\rightarrow$ **Split Path**:
1. **Speed Layer**: `Kafka` $\rightarrow$ `Stream Processor (Flink/Spark Streaming)` $\rightarrow$ `Real-time OLAP (Druid/Pinot)` $\rightarrow$ `Dashboard`.
2. **Batch Layer**: `Kafka` $\rightarrow$ `Data Lake (S3/HDFS)` $\rightarrow$ `Batch Processor (Spark/Hive)` $\rightarrow$ `Data Warehouse (Snowflake/BigQuery)` $\rightarrow$ `Dashboard`.

### Component Roles
- **API Gateway / Collector**: Validates incoming events and pushes them to the message queue.
- **Apache Kafka**: Acts as the distributed commit log (buffer) to decouple ingestion from processing.
- **Speed Layer (Stream Processing)**: Processes data in windows (e.g., 1-minute sliding windows) for immediate visibility.
- **Batch Layer (ETL)**: Runs periodic jobs (e.g., every 6 hours) to clean, deduplicate, and aggregate raw data.
- **OLAP Storage**: Specialized columnar databases designed for fast aggregations over large datasets.
- **Serving Layer**: A unified API that merges results from both the Speed and Batch layers to provide a seamless view.

---

## 3. Key HLD Concepts & Component Design

### A. Data Ingestion & Buffering
We use **Apache Kafka** because it provides:
- **Durability**: Events are persisted on disk.
- **Scalability**: Partitioning allows parallel consumption.
- **Multi-consumer**: Both the Speed and Batch layers can read from the same topic independently.

### B. The Speed Layer (Real-time)
**Technology**: Apache Flink or Spark Streaming.
- **Windowing**: Uses *Tumbling* or *Sliding* windows to calculate metrics (e.g., count clicks every 10 seconds).
- **State Management**: Flink maintains state for aggregates, allowing it to handle late-arriving data using **Watermarks**.
- **Approximate Algorithms**: To keep latency low, we use **HyperLogLog (HLL)** for counting unique users (Cardinality estimation) instead of storing every unique ID in memory.

### C. The Batch Layer (Historical)
**Technology**: Apache Spark + S3 (Parquet).
- **Storage Format**: Data is stored in **Apache Parquet** (Columnar format). This is critical because analytics queries usually only need 2-3 columns out of 100.
- **Compaction**: Batch jobs merge small files into larger ones to optimize HDFS/S3 read performance.
- **Deduplication**: The batch layer removes duplicate events that may have been sent due to network retries.

### D. The Serving Layer (OLAP Database)
Standard SQL databases (Postgres/MySQL) fail at this scale. We use **OLAP (Online Analytical Processing)** databases like **Apache Druid**, **ClickHouse**, or **Apache Pinot**.
- **Columnar Storage**: Stores data by column, drastically reducing I/O for `SUM` and `AVG` operations.
- **Indexing**: Uses bitmap indexes to quickly filter through millions of rows.
- **Pre-aggregation**: Stores "roll-ups" (pre-computed sums) to speed up common queries.

---

## 4. Data Flows & Fault Tolerance

### Write Path Walkthrough
1. **Event Trigger**: A user clicks a button; the frontend sends a JSON payload to the `/collect` endpoint.
2. **Ingestion**: The API Gateway performs basic schema validation and produces a message to the `raw_events` Kafka topic.
3. **Real-time Path**: 
    - Flink consumes the event $\rightarrow$ updates a running count in state $\rightarrow$ writes the aggregate to ClickHouse.
    - **Latency**: $\sim 200\text{ms}$.
4. **Batch Path**: 
    - A Kafka Connector (like S3 Sink) writes raw events to S3 in 15-minute chunks.
    - Every 6 hours, a Spark job reads the S3 data $\rightarrow$ cleans it $\rightarrow$ writes a final aggregate to the Data Warehouse.
    - **Latency**: $\sim 6$ hours.

### Fault Tolerance & Reliability
- **Kafka Replication**: Each partition is replicated across 3 brokers to prevent data loss if one node fails.
- **Flink Checkpointing**: Flink periodically saves its state to S3. If a worker crashes, it resumes from the last checkpoint (Exactly-once processing).
- **Idempotency**: Every event is assigned a unique `event_id`. The batch layer uses this ID to perform deduplication, ensuring that retries don't inflate the metrics.
- **Backpressure**: If the OLAP database slows down, Kafka buffers the data, preventing the API Gateway from crashing.

---

## 5. Production Trade-offs

### Lambda vs. Kappa Architecture
| Feature | Lambda Architecture | Kappa Architecture |
| :--- | :--- | :--- |
| **Structure** | Batch + Speed Layers | Stream Layer Only |
| **Complexity** | High (Maintain two codebases) | Low (One codebase) |
| **Accuracy** | High (Batch corrects Speed) | Dependent on stream replay |
| **Use Case** | When historical reprocessing is complex | When data can be re-processed via Kafka |

*Decision*: We chose **Lambda** here because historical data cleaning (deduplication, late-arrival handling) is often more robust in a dedicated Batch Spark job than in a continuous stream.

### Consistency vs. Latency (CAP Theorem)
In an analytics platform, we prioritize **Availability and Partition Tolerance (AP)** over strong consistency.
- **Eventual Consistency**: It is acceptable if a dashboard is "off" by 0.1% for a few seconds, as long as the Batch layer eventually corrects it.
- **Trade-off**: We use **Approximate Counting (HyperLogLog)** to trade a small amount of precision for a massive gain in query speed and memory efficiency.

### Storage Trade-off: Row vs. Columnar
- **Row-based (Postgres)**: Great for `SELECT * FROM users WHERE id = 1`. Bad for `SELECT SUM(revenue) FROM sales`.
- **Columnar (ClickHouse/Parquet)**: Great for `SELECT SUM(revenue)`. Bad for updating a single row.
- **Choice**: Since analytics is read-heavy and aggregate-heavy, **Columnar is the only viable option**.

---

## Complexity Analysis Summary

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Event Ingestion** | $O(1)$ | $O(1)$ | Simple append to Kafka log. |
| **Real-time Aggregation** | $O(1)$ | $O(K)$ | $K$ is the number of unique keys in the window. |
| **Batch Processing** | $O(N \log N)$ | $O(N)$ | $N$ is the total volume of events; $\log N$ for sorting/shuffling. |
| **OLAP Query** | $O(\text{columns} \times \text{rows})$ | $O(1)$ | Highly optimized via columnar scans and indexing. |""",
    'solutions': """# System Design Document: Enterprise Analytics Platform (Batch + Real-time)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Event Ingestion:** Ability to ingest massive volumes of events (clickstreams, logs, transactions) from various sources (web, mobile, backend services).
*   **Real-time Analytics:** Provide low-latency insights (seconds) for operational monitoring and live dashboards.
*   **Batch Analytics:** Provide high-accuracy, complex historical reports and trend analysis over months or years.
*   **Custom Query Interface:** Allow users to define custom dimensions and metrics for aggregation.
*   **Alerting System:** Trigger notifications when specific metrics cross predefined thresholds in real-time.
*   **Data Retention:** Support tiered storage (hot, warm, cold) to manage costs over time.

### 1.2 Non-Functional Requirements
*   **Scalability:** Must handle peaks of $10^5$ to $10^6$ events per second.
*   **Availability:** 99.99% availability for ingestion; 99.9% for query services.
*   **Fault Tolerance:** No data loss during ingestion or processing (at-least-once or exactly-once semantics).
*   **Latency:** 
    *   Ingestion to Real-time Dashboard: $< 2$ seconds.
    *   Query Response Time: $< 500\text{ms}$ for pre-aggregated data, $< 10\text{s}$ for ad-hoc historical queries.
*   **Consistency:** Eventual consistency for analytics; strong consistency for configuration/metadata.

### 1.3 Scale Estimations (HLD)
*   **Daily Volume:** $10^6 \text{ events/sec} \times 86,400 \text{ sec} \approx 86.4 \text{ Billion events/day}$.
*   **Data Size:** Avg event size $500\text{ bytes} \implies \approx 43 \text{ TB/day}$ raw data.
*   **Storage (Annual):** $\sim 15 \text{ PB/year}$ (before compression/aggregation).
*   **Query Volume:** $\sim 1,000$ concurrent users running various dashboard queries.

---

## 2. High-Level Architecture

The system adopts a **Lambda Architecture** to balance the trade-off between latency (Speed Layer) and accuracy/completeness (Batch Layer).

### 2.1 Architecture Diagram

```mermaid
graph TD
    subgraph Sources
        Web[Web App]
        Mob[Mobile App]
        Svc[Backend Services]
    end

    subgraph Ingestion_Layer
        GW[API Gateway / Load Balancer]
        Kaf[Apache Kafka / Redpanda]
    end

    subgraph Speed_Layer_RealTime
        Flink[Apache Flink / Spark Streaming]
        Redis[(Redis - Hot Metrics)]
        Druid[(Apache Druid / ClickHouse)]
    end

    subgraph Batch_Layer_Historical
        S3[(S3 / Data Lake - Parquet)]
        Spark[Apache Spark / Hive]
        Snowflake[(Snowflake / BigQuery)]
    end

    subgraph Serving_Layer
        QuerySvc[Query Service API]
        MetaDB[(PostgreSQL - Metadata)]
        Dash[Frontend Dashboards]
    end

    %% Flow
    Web & Mob & Svc --> GW
    GW --> Kaf
    Kaf --> Flink
    Kaf --> S3
    Flink --> Redis
    Flink --> Druid
    S3 --> Spark
    Spark --> Snowflake
    
    QuerySvc --> Redis
    QuerySvc --> Druid
    QuerySvc --> Snowflake
    QuerySvc --> MetaDB
    Dash --> QuerySvc
```

### 2.2 Component Interactions
1.  **Ingestion:** Events are pushed to the API Gateway, which validates the schema and produces them into **Kafka** topics partitioned by `tenant_id` or `event_type`.
2.  **Speed Layer:** **Apache Flink** consumes from Kafka, performs windowed aggregations (e.g., 1-minute sliding windows), and writes results to **Druid** (for OLAP) and **Redis** (for instant counters).
3.  **Batch Layer:** Raw events are archived from Kafka to **S3** in Parquet format. **Spark** jobs run periodically (e.g., every 4 hours) to perform heavy cleanup, deduplication, and deep aggregations, loading results into a data warehouse like **Snowflake**.
4.  **Serving Layer:** The **Query Service** acts as an orchestrator. It decides whether to fetch data from Redis (real-time), Druid (recent history), or Snowflake (long-term trends) based on the time range requested.

---

## 3. Detailed Database Schema Design

### 3.1 Metadata Store (PostgreSQL)
Used for managing users, dashboards, and alert configurations.
*   **`users`**: `user_id (PK), email, organization_id, created_at`
*   **`metrics_config`**: `metric_id (PK), name, definition_sql, aggregation_type (SUM, AVG, COUNT), alert_threshold`
*   **`dashboards`**: `dashboard_id (PK), user_id (FK), layout_json, created_at`

### 3.2 Real-time OLAP Store (Apache Druid / ClickHouse)
Designed for high-dimensional slicing and dicing.
*   **Table: `events_realtime`**
    *   `timestamp` (Primary Dimension/Partition Key)
    *   `event_type` (String, Indexed)
    *   `user_id` (String, Indexed)
    *   `dimension_json` (JSONB/Map - for flexible attributes)
    *   `metric_value` (Double)
    *   **Indexing:** Partitioned by `Day`, Clustered by `event_type` and `user_id`.

### 3.3 Historical Data Lake (S3 + Parquet)
*   **Structure:** `s3://analytics-bucket/year=2023/month=10/day=27/event_type=click/part-001.parquet`
*   **Format:** Columnar (Parquet) to minimize I/O for aggregate queries.

### 3.4 Hot Cache (Redis)
*   **Key Pattern:** `metric:{metric_id}:{window_timestamp}` $\rightarrow$ `value`
*   **TTL:** 24 hours.

---

## 4. Core API Design

### 4.1 Event Ingestion API
`POST /v1/events`
*   **Payload:**
    ```json
    {
      "event_id": "uuid-123",
      "event_type": "page_view",
      "user_id": "user_888",
      "timestamp": "2023-10-27T10:00:00Z",
      "properties": {
        "page_url": "/home",
        "device": "mobile",
        "region": "US-East"
      }
    }
    ```
*   **Response:** `202 Accepted` (Async processing).

### 4.2 Analytics Query API
`POST /v1/query`
*   **Payload:**
    ```json
    {
      "metric_id": "daily_active_users",
      "start_time": "2023-10-01T00:00:00Z",
      "end_time": "2023-10-27T23:59:59Z",
      "granularity": "hour",
      "dimensions": ["region", "device"],
      "filters": [{ "field": "event_type", "op": "eq", "value": "login" }]
    }
    ```
*   **Response:**
    ```json
    {
      "data": [
        { "timestamp": "2023-10-27T10:00:00Z", "region": "US-East", "device": "mobile", "value": 1500 },
        { "timestamp": "2023-10-27T10:00:00Z", "region": "US-East", "device": "desktop", "value": 800 }
      ]
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Handling Data Skew
*   **Problem:** A few "celebrity" users or viral events can overload specific Kafka partitions or Flink operators.
*   **Solution:** Use **Salting**. Append a random integer to the partition key for hot keys, aggregate locally, and then perform a global aggregation in a second stage.

### 5.2 Storage Tiering
*   **Hot (0-7 days):** Druid/ClickHouse on SSDs for sub-second queries.
*   **Warm (7-90 days):** Druid deep storage (S3) with cached segments.
*   **Cold (90+ days):** Snowflake/Iceberg on S3; accessed via asynchronous batch queries.

### 5.3 Fault Tolerance & Exactly-Once
*   **Kafka:** Use `acks=all` and idempotent producers.
*   **Flink:** Enable **Checkpointing** and use the Two-Phase Commit (2PC) sink to ensure that data written to Druid/Redis is not duplicated during a task failure.
*   **Batch:** Spark jobs are idempotent; they overwrite specific partitions in the Data Warehouse upon retry.

### 5.4 Query Optimization
*   **Materialized Views:** Pre-calculate common aggregations (e.g., hourly sums) in Druid.
*   **Projection:** Only read the specific columns required from Parquet files to reduce S3 egress costs.

---

## 6. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **Lambda vs Kappa** | **Lambda** | While Kappa is simpler (single stream), Lambda is chosen here to allow the Batch layer to handle "Late Arriving Data" and massive historical reprocessing without stressing the real-time stream. |
| **Consistency vs Availability** | **Availability** | In analytics, missing a few events in a dashboard for 2 seconds (Eventual Consistency) is preferable to rejecting ingestion requests (Strong Consistency) during a network partition. |
| **Row vs Columnar Store** | **Columnar** | Since analytics involves aggregating over millions of rows for a few columns (e.g., `SUM(revenue)`), columnar storage (Parquet/ClickHouse) provides orders of magnitude better performance than row-based (Postgres). |
| **Latency vs Storage Cost** | **Tiered Storage** | Keeping all data in Druid/RAM is too expensive. Moving old data to S3/Parquet increases query latency for old data but reduces costs by $\approx 90\%$. |""",
}

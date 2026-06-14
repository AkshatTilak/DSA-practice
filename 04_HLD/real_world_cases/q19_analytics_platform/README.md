# Analytics Platform (Batch + Real-time) HLD

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
| **OLAP Query** | $O(\text{columns} \times \text{rows})$ | $O(1)$ | Highly optimized via columnar scans and indexing. |
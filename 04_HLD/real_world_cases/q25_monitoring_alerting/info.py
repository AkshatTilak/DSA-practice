INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Monitoring & Alerting (Prometheus/Grafana).',
    'groups': ['Real-World Systems', 'Data Pipelines'],
    'readme_content': """# Monitoring & Alerting System HLD (Prometheus/Grafana)

## 1. Overview & System Requirements

A **Monitoring and Alerting System** is a critical piece of infrastructure designed to provide observability into the health, performance, and reliability of distributed systems. Unlike logging (which records discrete events), monitoring focuses on **metrics**—numerical representations of data measured over intervals of time (Time-Series Data).

The industry standard for this is the **Prometheus** ecosystem for data collection and alerting, combined with **Grafana** for visualization.

### Functional Requirements
- **Metric Collection**: Ability to collect numerical metrics (counters, gauges, histograms) from various services.
- **Querying**: A powerful query language (PromQL) to aggregate and filter time-series data.
- **Visualization**: Real-time dashboards to visualize system health and trends.
- **Alerting**: Define threshold-based rules to trigger notifications when a system enters an unhealthy state.
- **Service Discovery**: Automatically detect new targets/instances to monitor in dynamic environments (e.g., Kubernetes).

### Non-Functional Requirements
- **High Availability**: The monitoring system must not go down when the production system goes down (it must be more reliable than the system it monitors).
- **Scalability**: Must handle millions of unique time series (cardinality) and high write throughput.
- **Low Latency**: Dashboards should load quickly, and alerts should trigger within seconds of a threshold breach.
- **Durability**: Metrics should be persisted to disk, though short-term loss of some samples is often acceptable compared to transactional data.

### Scale Assumptions
- **Infrastructure**: 10,000 server nodes.
- **Metrics per Node**: $\sim 100$ metrics.
- **Scrape Interval**: 15 seconds.
- **Throughput**: $\frac{10,000 \text{ nodes} \times 100 \text{ metrics}}{15 \text{ seconds}} \approx 66,667$ samples per second (Write QPS).
- **Storage**: Retaining 15 days of data with 2-byte floats and 8-byte timestamps.

---

## 2. High-Level System Architecture

The architecture follows a **pull-based model** where the monitoring server actively fetches metrics from targets.

### Architecture Diagram Components
1.  **Targets (Exporters)**: Applications or "Exporters" (e.g., Node Exporter) that expose a `/metrics` HTTP endpoint.
2.  **Prometheus Server**: The core engine that scrapes data, stores it in a TSDB, and evaluates alert rules.
3.  **TSDB (Time Series Database)**: A specialized database optimized for time-stamped numerical data.
4.  **Alertmanager**: A standalone component that handles alerts sent by Prometheus (deduplication, grouping, routing).
5.  **Grafana**: The visualization layer that queries Prometheus via API to render graphs.
6.  **Service Discovery (SD)**: Integration with Kubernetes or Consul to find target IPs automatically.

```mermaid
graph TD
    subgraph "Target Layer"
        App1[App A /metrics]
        App2[App B /metrics]
        NodeExp[Node Exporter]
    end

    subgraph "Monitoring Core"
        Prom[Prometheus Server]
        TSDB[(TSDB Storage)]
        SD[Service Discovery]
    end

    subgraph "Alerting & Viz"
        AM[Alertmanager]
        Grafana[Grafana Dashboards]
    end

    subgraph "Notifications"
        Slack[Slack/PagerDuty/Email]
    end

    SD --> Prom
    Prom -- "HTTP Pull" --> App1
    Prom -- "HTTP Pull" --> App2
    Prom -- "HTTP Pull" --> NodeExp
    Prom <--> TSDB
    Prom -- "Trigger Alert" --> AM
    AM --> Slack
    Grafana -- "PromQL Query" --> Prom
```

---

## 3. Key HLD Concepts & Component Design

### A. Pull vs. Push Model
Prometheus uses a **Pull Model**.
- **Why Pull?** 
    - **Self-Protection**: The server decides when to scrape; it cannot be DDoS-ed by a malfunctioning client pushing millions of metrics.
    - **Health Monitoring**: If the server cannot pull from a target, it immediately knows the target is down (implicit "up" metric).
    - **Easier Configuration**: Targets don't need to know where the monitoring server is; the server discovers them.
- **When to Push?** For short-lived jobs (e.g., CronJobs), a **Pushgateway** is used. The job pushes to the gateway, and Prometheus pulls from the gateway.

### B. The Time Series Database (TSDB)
Standard SQL databases are inefficient for time-series data due to massive index overhead.
- **Data Model**: A time series is identified by a **metric name** and a set of **labels** (key-value pairs).
  - Example: `http_requests_total{method="POST", endpoint="/api/login", env="prod"}`
- **Storage Strategy**:
    - **In-memory Head Block**: Recent samples are stored in memory for fast access.
    - **WAL (Write Ahead Log)**: Every single sample is written to a WAL to prevent data loss during crashes.
    - **Chunking**: Periodically, memory blocks are compressed and flushed to disk as "chunks" to reduce storage footprint.
    - **Inverted Index**: To find all series matching `{env="prod"}`, Prometheus uses an inverted index mapping label values to series IDs.

### C. Prometheus Query Language (PromQL)
PromQL allows for powerful on-the-fly aggregations:
- **Rate**: `rate(http_requests_total[5m])` — Calculates the per-second rate of increase over the last 5 minutes.
- **Aggregation**: `sum(rate(http_requests_total[5m])) by (method)` — Sums the rates grouped by the HTTP method.

### D. Alerting Pipeline
1.  **Rule Evaluation**: Prometheus evaluates expressions (e.g., `cpu_usage > 80%`) every $X$ seconds.
2.  **Pending State**: If a rule is true, the alert enters a `Pending` state. It must remain true for a defined `for` duration (e.g., 5 minutes) to avoid "flapping" (brief spikes).
3.  **Firing State**: Once the duration is met, the alert is sent to **Alertmanager**.
4.  **Alertmanager Logic**:
    - **Grouping**: If 100 servers go down, send *one* alert saying "100 servers are down" instead of 100 separate emails.
    - **Inhibition**: If the Data Center is down, suppress alerts for the individual servers inside it.
    - **Routing**: Send "Critical" alerts to PagerDuty and "Warning" alerts to Slack.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Data Flow: Metric to Dashboard
1.  **Instrument**: The application uses a Prometheus client library to increment a counter in memory.
2.  **Expose**: The application exposes these counters on `/metrics` in a plain-text format.
3.  **Scrape**: Prometheus queries the `/metrics` endpoint via HTTP.
4.  **Persist**: The sample is written to the WAL and then stored in the TSDB.
5.  **Visualize**: A user opens Grafana $\rightarrow$ Grafana sends a PromQL query to Prometheus $\rightarrow$ Prometheus scans the TSDB $\rightarrow$ Returns data $\rightarrow$ Grafana renders the graph.

### Fault Tolerance & Reliability
| Failure Scenario | Mitigation Strategy |
| :--- | :--- |
| **Prometheus Node Crash** | **WAL (Write Ahead Log)** ensures that data not yet flushed to disk is recovered upon restart. |
| **Target Node Crash** | Prometheus marks the target as `UP=0`, triggering an "Instance Down" alert. |
| **TSDB Disk Full** | **Retention Policies**: Automatically delete data older than $X$ days (e.g., 15 days). |
| **High Cardinality Explosion** | (e.g., putting UserID in a label). Use **recording rules** to pre-calculate aggregates and drop high-cardinality raw data. |

---

## 5. Production Trade-offs & Scaling

### The "Single Node" Limitation
Prometheus is designed as a single-node system. It does not natively support horizontal scaling (sharding).

**Trade-off: Simplicity vs. Scalability**
- **Pros**: No complex cluster management, extremely fast local reads/writes.
- **Cons**: Limited by the disk and RAM of one machine.

### Scaling Strategies for Large-Scale Systems
To handle global-scale monitoring, the following architectures are used:

1.  **Functional Sharding**:
    - Run one Prometheus server for "Database Metrics," one for "Frontend Metrics," and one for "Network Metrics."
2.  **Hierarchical Federation**:
    - **Edge Prometheus**: Local servers in each region/cluster scrape targets.
    - **Global Prometheus**: A central server scrapes only the *aggregated* metrics from the Edge servers.
3.  **Long-Term Storage (The "Thanos/Cortex" approach)**:
    - **Sidecar Pattern**: A sidecar process uploads TSDB blocks to S3/GCS (Object Storage).
    - **Querier**: A separate component that queries both the local Prometheus (for recent data) and S3 (for historical data), providing a **Global View**.
    - **Downsampling**: Converting 15s resolution data to 1h resolution for data older than 30 days to save space.

### Summary Complexity Analysis

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Write (Scrape)** | $O(1)$ | $O(N)$ | Appending to WAL and Memory. |
| **Query (Simple)** | $O(\log S)$ | $O(R)$ | Binary search on index for series $S$, result set $R$. |
| **Query (Aggregated)**| $O(S \times T)$ | $O(R)$ | Must scan $T$ time samples for $S$ series. |
| **Alert Evaluation** | $O(Rules \times S)$ | $O(1)$ | Periodic scan of active series. |""",
    'solutions': """# System Design: Monitoring & Alerting System (Prometheus/Grafana Style)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Metric Collection:** The system must collect numerical metrics (counters, gauges, histograms) from various targets (servers, containers, applications).
*   **Time-Series Storage:** Store metrics with a timestamp and a set of labels (tags) for multi-dimensional querying.
*   **Query Engine:** Provide a powerful query language to aggregate, filter, and perform mathematical operations on time-series data over specific time ranges.
*   **Alerting:** Allow users to define rules (e.g., `CPU > 80% for 5 mins`) and trigger notifications via third-party integrations (Slack, PagerDuty, Email).
*   **Visualization:** Provide a dashboarding interface to visualize trends, spikes, and system health.
*   **Service Discovery:** Automatically detect new targets to monitor without manual configuration.

### 1.2 Non-Functional Requirements
*   **High Write Throughput:** Capable of handling millions of samples per second.
*   **Low Query Latency:** Dashboards must load quickly, and alerts must trigger in near real-time.
*   **Availability:** The monitoring system must be more available than the systems it monitors (avoiding the "monitoring the monitor" paradox).
*   **Scalability:** Ability to scale horizontally as the number of monitored targets increases.
*   **Eventual Consistency:** Strong consistency is not required for historical data; eventual consistency is acceptable for dashboards.

### 1.3 Scale Estimations (HLD)
*   **Targets:** 100,000 targets.
*   **Metrics per Target:** Average 100 metrics.
*   **Scrape Interval:** Every 15 seconds.
*   **Ingestion Rate:** $\frac{100,000 \text{ targets} \times 100 \text{ metrics}}{15 \text{ seconds}} \approx 666,666 \text{ samples/sec}$.
*   **Data Volume:** Each sample (Timestamp: 8 bytes, Value: 8 bytes, Series ID: 8 bytes) $\approx$ 24 bytes. 
    *   Daily volume: $666k \times 86,400 \times 24 \approx 1.38 \text{ TB/day}$ (uncompressed).

---

## 2. High-Level Architecture

The system follows a **Pull-based** architecture for collection and a **Distributed TSDB** for storage.

### 2.1 Architecture Components
1.  **Exporters:** Small binaries that run alongside the application, translating internal app metrics into a format the collector understands (e.g., `/metrics` endpoint).
2.  **Prometheus Server (Collector):** 
    *   **Scraper:** Periodically polls exporters based on a configuration/service discovery.
    *   **TSDB (Time Series Database):** Optimized storage for time-stamped data.
    *   **Rule Evaluator:** Periodically runs alerting rules against the TSDB.
3.  **Alert Manager:** Handles alerts sent by the server. It manages deduplication, grouping, and routing to notification channels.
4.  **Grafana (Visualization):** Connects to the Prometheus Query API to render dashboards.
5.  **Service Discovery (SD):** Integrates with Kubernetes, AWS, or Consul to find targets dynamically.

### 2.2 Architecture Diagram

```mermaid
graph TD
    subgraph "Target Environment"
        App1[App A + Exporter]
        App2[App B + Exporter]
        App3[App C + Exporter]
    end

    subgraph "Monitoring Core"
        SD[Service Discovery] --> Scraper
        Scraper[Prometheus Scraper] --> TSDB[(TSDB - Time Series DB)]
        TSDB --> QueryEngine[Query Engine/PromQL]
        TSDB --> RuleEval[Rule Evaluator]
    end

    subgraph "Alerting Pipeline"
        RuleEval --> AM[Alert Manager]
        AM --> Slack[Slack/PagerDuty/Email]
    end

    subgraph "Visualization"
        Grafana[Grafana Dashboards] --> QueryEngine
    end

    Scraper -.-> App1
    Scraper -.-> App2
    Scraper -.-> App3
```

---

## 3. Detailed Database Schema Design

A standard Relational Database (SQL) is inefficient for time-series data due to the massive number of rows and the need for range scans. We use a specialized **TSDB approach**.

### 3.1 Data Model
A time series is uniquely identified by its **Metric Name** and its **Labels**.
*   **Series:** `http_requests_total{method="POST", endpoint="/api/login", env="prod"}`
*   **Sample:** `(timestamp, value)`

### 3.2 Storage Components
To optimize storage, we separate the **Index** from the **Samples**.

#### A. Inverted Index (Label $\rightarrow$ Series ID)
To find all series matching `env="prod"`, we use an inverted index.
*   **Table/Store:** `LabelIndex`
*   **Structure:** `Key: "env=prod" -> Value: [SeriesID_1, SeriesID_45, SeriesID_102...]`
*   **Reasoning:** Allows $O(1)$ or $O(\log N)$ lookup of series IDs regardless of the number of samples.

#### B. Sample Store (Series ID $\rightarrow$ Samples)
Samples are stored in chunks (e.g., 2-hour blocks) to optimize disk I/O.
*   **Structure:** `SeriesID | Timestamp | Value`
*   **Storage Format:** 
    *   **Write-Ahead Log (WAL):** All incoming samples are written to a WAL for crash recovery.
    *   **Memory Chunk:** Recently received samples are kept in a memory-mapped buffer.
    *   **Compressed Block:** Once a chunk is full, it is compressed using **Delta-Delta Encoding** (for timestamps) and **XOR Encoding** (for floating-point values, e.g., Facebook's Gorilla paper) and flushed to disk.

### 3.3 Summary of Storage Selection
| Feature | Selection | Reasoning |
| :--- | :--- | :--- |
| **Primary Storage** | LSM-Tree based TSDB | High write throughput, optimized for sequential time-range reads. |
| **Indexing** | Inverted Index | Fast retrieval of series based on arbitrary label combinations. |
| **Compression** | Gorilla/Delta-Delta | Reduces storage footprint by up to 90% for predictable time-series. |

---

## 4. Core API Design

### 4.1 Query API (PromQL Interface)
Used by Grafana and the Rule Evaluator.

**Endpoint:** `GET /api/v1/query`
*   **Request:**
    *   `query`: The PromQL expression (e.g., `sum(rate(http_requests_total[5m])) by (endpoint)`)
    *   `time`: Epoch timestamp for instant queries.
*   **Response:**
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": { "endpoint": "/api/login", "env": "prod" },
        "value": [1625097600, "45.2"]
      }
    ]
  }
}
```

**Endpoint:** `GET /api/v1/query_range`
*   **Request:** `query`, `start`, `end`, `step` (resolution).
*   **Response:** Returns a matrix of values over the time range.

### 4.2 Target Management API
Used to update the scraper's list of targets.

**Endpoint:** `POST /api/v1/targets`
*   **Payload:**
```json
{
  "targets": [
    { "labels": { "job": "api-server" }, "static_configs": [{ "targets": ["10.0.0.1:9090", "10.0.0.2:9090"] }] }
  ]
}
```

### 4.3 Alert Configuration API
**Endpoint:** `POST /api/v1/rules`
*   **Payload:**
```json
{
  "alert": "HighCpuUsage",
  "expr": "cpu_usage > 80",
  "for": "5m",
  "labels": { "severity": "critical" },
  "annotations": { "summary": "CPU usage is too high on {{ $labels.instance }}" }
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Scaling Ingestion (Horizontal Scaling)
Since a single Prometheus server has a limit on the number of series it can handle, we employ **Functional Sharding**:
*   **Shard by Target:** Server A scrapes `Service-Group-1`, Server B scrapes `Service-Group-2`.
*   **Shard by Metric:** Server A handles `CPU/Memory` metrics, Server B handles `HTTP/Request` metrics.

### 5.2 Long-Term Storage (Remote Write)
Local TSDBs are usually limited to short retention (e.g., 15 days). For long-term historical analysis:
*   **Remote Write:** The server pushes samples to a centralized long-term store (e.g., **Thanos**, **Cortex**, or **Mimir**).
*   **Object Storage:** These systems move old blocks to S3/GCS, providing virtually infinite retention.
*   **Downsampling:** To keep queries fast, the system aggregates 15s data into 1h blocks for data older than 30 days.

### 5.3 Fault Tolerance & HA
*   **Replication:** Run two identical Prometheus servers scraping the same targets.
*   **Deduplication:** The Alert Manager receives alerts from both servers but uses the alert fingerprint to ensure only one notification is sent.
*   **WAL (Write Ahead Log):** Ensures that in-memory samples are not lost during a crash.

### 5.4 Handling "Cardinality Explosion"
If a user adds a label like `user_id` (which has millions of unique values), the index size explodes, crashing the system.
*   **Mitigation:** 
    *   Implement **Cardinality Limits** per metric.
    *   Alert on the growth of the `prometheus_tsdb_head_series` metric.
    *   Use a "Relabeling" config to drop high-cardinality labels at the ingestion point.

---

## 6. Trade-off Analysis

### 6.1 Pull vs. Push Model
| Feature | Pull (Prometheus) | Push (Graphite/InfluxDB) |
| :--- | :--- | :--- |
| **Control** | Server controls the load; prevents flooding. | Client controls load; can overwhelm server. |
| **Health Check** | Implicitly knows if target is down (up=0). | Doesn't know if target is down (silence). |
| **Config** | Requires Service Discovery for dynamic envs. | Simpler setup for client (just send data). |
| **Network** | Requires network path from server to target. | Only requires path from target to server. |
*   *Decision:* Pull is preferred for infrastructure monitoring; Push is used via a **Pushgateway** for short-lived batch jobs.

### 6.2 Latency vs. Storage (Compression)
*   **Trade-off:** Real-time samples are kept in raw memory for $O(1)$ access (Low Latency), but historical data is heavily compressed (Low Storage).
*   **Impact:** This introduces a "compaction" phase where CPU spikes occur as the system transforms memory chunks into compressed disk blocks.

### 6.3 CAP Theorem Priority
*   **Priority:** **Availability (A)** and **Partition Tolerance (P)**.
*   **Reasoning:** In monitoring, it is better to have slightly stale data or a missing sample than for the entire ingestion pipeline to stop because one node is unavailable. Eventual consistency is acceptable for a dashboard showing a 5-minute average.""",
}

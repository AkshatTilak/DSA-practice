INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/kafka-system-design/',
    'description': 'Topic partition consumer lags.',
    'type': 'design',
    'groups': ['Messaging', 'Distributed Systems'],
    'readme_content': r"""# Kafka Messaging System Design: Managing Consumer Lag

## 1. Overview & System Requirements

In a distributed event-streaming platform like **Apache Kafka**, the system acts as a decoupled buffer between producers (data sources) and consumers (data sinks). A critical performance metric in this architecture is **Consumer Lag**.

### Problem Statement: Consumer Lag
**Consumer Lag** occurs when the rate at which messages are produced to a Kafka topic exceeds the rate at which the consumer group can process those messages. This results in a growing gap between the **Log End Offset (LEO)**—the last message written—and the **Current Offset**—the last message processed by the consumer.

### System Requirements

#### Functional Requirements
- **Publish/Subscribe:** Producers must be able to send messages to topics; consumers must be able to subscribe to them.
- **Persistence:** Messages must be stored on disk for a configurable retention period.
- **Scalability:** Ability to handle millions of events per second via partitioning.
- **Offset Management:** Tracking the progress of each consumer group per partition.

#### Non-Functional Requirements (SLAs)
- **High Throughput:** Optimize for sequential I/O and zero-copy data transfer.
- **Durability:** Ensure messages are replicated across multiple brokers to prevent data loss.
- **Availability:** The system must remain operational even if a broker or consumer node fails.
- **Low Latency:** Minimize the time from production to consumption (end-to-end latency).

#### Scale Assumptions
- **Traffic:** $10^6$ to $10^8$ messages per second.
- **Storage:** Petabytes of log data distributed across a cluster.
- **Consumers:** Thousands of consumer instances across various microservices.

---

## 2. High-Level System Architecture

The Kafka architecture is designed as a distributed commit log.

### Component Breakdown
1. **Producers:** Clients that push data to Kafka. They decide which partition to send data to based on a key (via hashing) or round-robin.
2. **Brokers:** The servers that store the data. Each broker manages a set of **Partitions**.
3. **Topics & Partitions:** A topic is a logical category. It is split into partitions for parallelism. Each partition is an ordered, immutable sequence of records.
4. **Consumer Groups:** A group of consumers collaborating to consume a topic. **Crucially: Each partition is assigned to exactly one consumer within a group.**
5. **Zookeeper / KRaft:** Manages cluster metadata, leader election for partitions, and consumer group coordination.

### The Read/Write Path
- **Write Path:** Producer $\rightarrow$ Broker (Leader Partition) $\rightarrow$ Disk (Sequential Append) $\rightarrow$ Replication to Followers.
- **Read Path:** Consumer $\rightarrow$ Broker (Leader Partition) $\rightarrow$ Zero-copy transfer to Consumer $\rightarrow$ Offset Commit.

---

## 3. Key HLD Concepts: Deep Dive into Consumer Lag

### The Mechanics of Lag
Mathematically, lag for a specific partition $p$ in consumer group $g$ is:
$$\text{Lag}_{g,p} = \text{LogEndOffset}_p - \text{CurrentOffset}_{g,p}$$

### Root Causes of Lag
| Cause | Description | Impact |
| :--- | :--- | :--- |
| **Processing Bottleneck** | Consumer business logic (e.g., DB writes, API calls) is slower than the producer. | Linear growth of lag over time. |
| **Data Skew** | A poorly chosen partition key sends 90% of data to one partition. | One consumer is overwhelmed while others are idle. |
| **Rebalance Storms** | Frequent consumer joins/leaves trigger "stop-the-world" rebalances. | Processing halts entirely during the rebalance phase. |
| **Poison Pill** | A malformed message causes the consumer to crash or retry indefinitely. | Lag stops moving forward for that specific partition. |
| **Resource Exhaustion** | Consumer CPU/RAM saturation or network congestion. | Increased processing time per record. |

---

## 4. Strategies to Solve Consumer Lag

When lag is detected (via monitoring tools like Prometheus or Burrow), we apply the following architectural patterns:

### Strategy A: Horizontal Scaling (The Standard Approach)
Since Kafka allows parallelism via partitions, the most direct way to increase throughput is to increase the number of consumers.
- **Requirement:** $\text{Number of Consumers} \le \text{Number of Partitions}$.
- **Action:** Increase the partition count of the topic $\rightarrow$ Spin up more consumer instances in the group.
- **Trade-off:** Increasing partitions can increase overhead on the broker and may affect message ordering if keys are changed.

### Strategy B: Decoupled Processing (The Worker Pattern)
If the bottleneck is a slow synchronous operation (e.g., calling a 3rd party API), we decouple **Consumption** from **Processing**.
1. **Consumer Thread:** Polls Kafka and hands the message to an internal **BlockingQueue**.
2. **Worker Pool:** A set of worker threads pulls from the queue and processes messages in parallel.
- **Risk:** This breaks Kafka's ordering guarantee within a partition. To maintain order, use a "Key-based Dispatcher" to ensure messages with the same key go to the same worker thread.

### Strategy C: Tuning Consumer Parameters
Optimizing the `KafkaConsumer` config to maximize batch efficiency:
- `max.poll.records`: Increase this to process more records per poll cycle.
- `fetch.min.bytes`: Increase this to force the broker to wait until enough data is accumulated, reducing the number of requests.
- `max.partition.fetch.bytes`: Increase if messages are large.

### Strategy D: Handling Poison Pills (DLQ)
To prevent a single bad message from stalling the entire pipeline:
- **Dead Letter Queue (DLQ):** If a message fails after $N$ retries, move it to a separate "DLQ Topic" for manual inspection and commit the offset to move forward.

---

## 5. Data Flow & Fault Tolerance

### Request Walkthrough: Handling a Lagging Partition
1. **Detection:** A monitoring system alerts that `Partition 4` has a lag of $1,000,000$ records.
2. **Analysis:** The engineer observes that `Consumer-C` is utilizing 100% CPU while `Consumer-A` and `Consumer-B` are at 10%. This indicates **Data Skew**.
3. **Mitigation:**
   - **Short term:** Increase `max.poll.records` to reduce polling overhead.
   - **Long term:** Redesign the partitioning key to be more uniformly distributed (e.g., using a hash of `userId` instead of `regionId`).
4. **Recovery:** The system scales out the consumer group. The Group Coordinator triggers a rebalance, redistributing partitions among the new consumers.

### Fault Tolerance
- **Broker Failure:** If a leader broker fails, a follower is promoted. The consumer automatically reconnects to the new leader.
- **Consumer Failure:** If a consumer stops sending heartbeats, the group coordinator triggers a rebalance, assigning its partitions to remaining healthy consumers.

---

## 6. Production Trade-offs & Complexity Analysis

### Trade-offs: Consistency vs. Latency (The CAP Dilemma)
| Choice | Pros | Cons |
| :--- | :--- | :--- |
| **At-least-once (Default)** | No data loss; simple implementation. | Potential for duplicate processing (requires Idempotent consumers). |
| **At-most-once** | Lowest latency; no duplicates. | Risk of data loss if consumer crashes after committing but before processing. |
| **Exactly-once (EOS)** | Perfect accuracy. | Significant performance hit due to transactional overhead and coordination. |

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Producing a Message** | $O(1)$ | $O(1)$ | Sequential append to log. |
| **Consuming a Message** | $O(1)$ | $O(1)$ | Sequential read via offset. |
| **Rebalance** | $O(C \cdot P)$ | $O(1)$ | Where $C$ is consumers and $P$ is partitions. |
| **Calculating Lag** | $O(1)$ | $O(1)$ | Simple subtraction of two metadata values. |

### Summary Checklist for Interviews
- [ ] Define **Lag** (LEO - Current Offset).
- [ ] Explain the **Partition-Consumer relationship** (1:1 mapping).
- [ ] Discuss **Scaling** (More partitions $\rightarrow$ More consumers).
- [ ] Mention **Parallel Processing** (Internal worker threads vs. Kafka partitions).
- [ ] Address **Data Skew** and **Poison Pills** (DLQs).
- [ ] Compare **Delivery Semantics** (At-least-once vs. Exactly-once).""",
    'solutions': """# Solution Guide: Handling and Mitigating Kafka Topic Partition Consumer Lag

## 1. Requirements & System Constraints

### 1.1 Problem Statement
In a high-throughput Kafka ecosystem, **Consumer Lag** occurs when the rate of production to a topic exceeds the rate of consumption by the consumer group. This leads to increased end-to-end latency, stale data for downstream systems, and potential disk pressure on Kafka brokers if retention policies are tight.

The objective is to design a robust system to monitor, alert, and automatically remediate consumer lag across thousands of partitions and multiple consumer groups.

### 1.2 Functional Requirements
*   **Real-time Monitoring:** Track the delta between the Log End Offset (LEO) and the Current Committed Offset for every partition in every consumer group.
*   **Alerting:** Trigger notifications (Slack, PagerDuty) when lag exceeds defined thresholds (either absolute record count or time-based).
*   **Auto-Scaling:** Dynamically increase consumer instances based on lag metrics (up to the number of partitions).
*   **Bottleneck Analysis:** Identify "hot partitions" caused by skewed keys.
*   **Remediation Control:** Provide mechanisms to temporarily increase processing power or reroute traffic.

### 1.3 Non-Functional Requirements
*   **Low Overhead:** The monitoring system must not introduce significant load on the Kafka brokers.
*   **High Availability:** The lag detection system must be decoupled from the data processing pipeline to ensure it remains operational during consumer crashes.
*   **Scalability:** Support millions of messages per second and thousands of partitions.
*   **Observability:** Provide a dashboard for visualizing lag trends over time.

### 1.4 Scale Estimations
*   **Topics:** 1,000+
*   **Partitions per Topic:** 10–100
*   **Consumer Groups:** 50+
*   **Message Throughput:** 1M+ events/sec
*   **Metric Resolution:** 10–30 second polling intervals.

---

## 2. High-Level Architecture

The architecture consists of a **Control Plane** (Monitoring & Scaling) and a **Data Plane** (Kafka & Consumers).

### 2.1 Core Components
1.  **Kafka Broker Cluster:** The source of offsets.
2.  **Lag Monitor Service:** A specialized service using the Kafka `AdminClient` to fetch the latest offsets and committed offsets.
3.  **Time-Series Database (TSDB):** Stores lag metrics for historical analysis and trend detection (e.g., Prometheus).
4.  **Alert Manager:** Evaluates metrics against thresholds and triggers alerts.
5.  **Auto-Scaler (K8s Operator):** Adjusts the replica count of consumer deployments based on lag data.
6.  **Analysis Engine:** Samples messages from lagging partitions to detect "poison pills" (malformed messages causing processing loops).

### 2.2 Architecture Diagram

```mermaid
graph TD
    subgraph DataPlane [Data Plane]
        P[Producers] --> K[Kafka Broker Cluster]
        K --> C1[Consumer Instance 1]
        K --> C2[Consumer Instance 2]
        K --> CN[Consumer Instance N]
    end

    subgraph ControlPlane [Control Plane]
        LM[Lag Monitor Service] -- Polls Offsets --> K
        LM -- Push Metrics --> TSDB[(Prometheus/TSDB)]
        TSDB --> AM[Alert Manager]
        AM -- Trigger --> Notif[Notifications/PagerDuty]
        TSDB --> AS[Auto-Scaler / K8s Operator]
        AS -- Scale Up/Down --> C1
    end

    subgraph Debugging [Diagnostics]
        AE[Analysis Engine] -- Inspects --> K
        AE -- Reports --> Dash[Grafana Dashboard]
    end
```

---

## 3. Detailed Design

### 3.1 Metric Collection Strategy
To avoid overloading brokers, the **Lag Monitor Service** should not poll every single partition every second.
*   **Strategy:** Use the `AdminClient.listConsumerGroupOffsets` API to fetch offsets for an entire group in one call rather than per-partition.
*   **Calculation:** $\text{Lag} = \text{Log End Offset (LEO)} - \text{Current Committed Offset}$.

### 3.2 Database Schema Design
Since lag is a time-series metric, a traditional SQL database is suboptimal. We use a combination of a TSDB for metrics and a Relational DB for configuration.

#### A. TSDB (Prometheus/InfluxDB)
**Metric Name:** `kafka_consumer_lag`
*   **Labels:** `topic`, `partition`, `consumer_group`, `cluster_id`
*   **Value:** `integer` (number of messages)
*   **Timestamp:** `epoch`

#### B. Configuration DB (PostgreSQL) - For Thresholds
Used to store customized alerting rules per consumer group.

| Field | Type | Description | Index |
| :--- | :--- | :--- | :--- |
| `group_id` | VARCHAR(255) | Primary Key - The Kafka consumer group ID | PK |
| `topic_name` | VARCHAR(255) | Topic associated with the group | Index |
| `lag_threshold` | BIGINT | Max allowable lag before alerting | - |
| `time_threshold` | INT | Max allowable lag in seconds (latency) | - |
| `scaling_enabled` | BOOLEAN | Whether auto-scaling is active for this group | - |
| `max_replicas` | INT | Upper limit for consumer scaling | - |

---

## 4. Core API Design

The Control Plane exposes APIs for managing thresholds and inspecting lag.

### 4.1 Get Current Lag
**Endpoint:** `GET /api/v1/lag/{consumer_group}`
**Response:**
```json
{
  "consumer_group": "order-processor-group",
  "total_lag": 150000,
  "partitions": [
    { "partition": 0, "lag": 2000, "offset": 10500, "leo": 12000 },
    { "partition": 1, "lag": 148000, "offset": 5000, "leo": 153000 }
  ],
  "status": "CRITICAL"
}
```

### 4.2 Update Thresholds
**Endpoint:** `POST /api/v1/thresholds`
**Payload:**
```json
{
  "consumer_group": "order-processor-group",
  "lag_threshold": 100000,
  "time_threshold": 300,
  "scaling_enabled": true,
  "max_replicas": 32
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Remediation Strategies for High Lag
When lag is detected, the system can trigger the following actions:

1.  **Horizontal Scaling:** Increase the number of consumer pods. *Constraint: The number of consumers cannot exceed the number of partitions.*
2.  **Parallel Processing (Internal):** If the partition count is fixed, the consumer should implement an internal worker pool (e.g., using a `CompletableFuture` or `Worker Queue`) to process messages concurrently.
    *   *Caution:* This breaks strict ordering per partition unless messages are sharded by key internally.
3.  **Batch Size Tuning:** Dynamically adjust `max.poll.records` and `fetch.min.bytes` to increase throughput at the cost of slight latency.
4.  **Increasing Partitions:** If the consumer group is at `max_replicas` (replicas == partitions) and lag persists, the system must trigger a partition expansion.
    *   *Risk:* Changing partition counts changes the mapping of keys to partitions, breaking ordering for existing keys.

### 5.2 Handling "Poison Pills"
Often, lag is caused by a single message that causes the consumer to crash or retry infinitely.
*   **DLQ (Dead Letter Queue):** Implement a try-catch block around the processing logic. After $N$ retries, move the message to a `topic_name_dlq` and commit the offset to move forward.

### 5.3 Tackling Data Skew (Hot Partitions)
If one partition has significantly more lag than others:
*   **Key Redistribution:** Analyze the key distribution. If one key is too frequent, implement a "salted key" strategy to spread that key across multiple partitions.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Perspective
The monitoring system prioritizes **Availability (A)** and **Partition Tolerance (P)** over **Consistency (C)**. It is acceptable if the lag metric is slightly delayed by a few seconds; it is not acceptable for the monitoring system to go down and leave the engineers blind to a production outage.

### 6.2 Latency vs. Throughput
*   **Increasing Batch Size:** Higher `max.poll.records` increases throughput (efficiency) but increases the "stale" time for the first message in the batch.
*   **Parallel Processing:** Using internal threads increases throughput but sacrifices the guaranteed order of processing within a partition.

### 6.3 Polling vs. Pushing
*   **Polling (Current Design):** Using `AdminClient` to poll offsets is simpler and puts less load on the broker.
*   **Pushing (Alternative):** Consumers could push their offsets to the TSDB every $X$ messages.
    *   *Trade-off:* Pushing increases the load on the consumer application and the TSDB, and if the consumer crashes, the last "push" may be missing, leading to inaccurate lag metrics. Polling the broker is the "Source of Truth."""
}

INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Event Streaming Platform (Kafka style).',
    'groups': ['Real-World Systems', 'Messaging'],
    'readme_content': """# Event Streaming Platform (Kafka-style) HLD

## 1. Overview & System Requirements

An Event Streaming Platform is a distributed commit log that allows producers to publish streams of records and consumers to subscribe to them. Unlike traditional message queues (like RabbitMQ) that delete messages after consumption, an event streaming platform treats the log as a durable, append-only sequence of events that can be replayed.

### Functional Requirements
- **Produce**: Ability for producers to send messages to a specific **Topic**.
- **Consume**: Ability for consumers to read messages from a topic.
- **Durability**: Messages must be persisted to disk and not lost upon broker failure.
- **Scalability**: The system must support horizontal scaling of both throughput and storage.
- **Consumer Groups**: Support for multiple consumers to share the load of a single topic (load balancing).
- **Retention**: Messages should be kept for a configurable period (time-based) or size (limit-based).

### Non-Functional Requirements
- **High Throughput**: Must handle millions of events per second.
- **Low Latency**: Minimal overhead between production and consumption.
- **High Availability**: The system must remain operational even if several brokers crash.
- **Order Guarantees**: Maintain strict ordering of messages **within a partition**.
- **Fault Tolerance**: Automatic leader election and data replication.

### Scale Assumptions
- **Throughput**: $10^6$ to $10^7$ events/sec.
- **Data Volume**: Petabytes of stored logs.
- **Consumers**: Thousands of concurrent consumer groups.
- **Latency**: End-to-end latency in the tens of milliseconds.

---

## 2. High-Level System Architecture

The system follows a decoupled architecture where producers and consumers interact with a cluster of brokers.

### Architecture Diagram Components
1.  **Producers**: Client applications that push data to brokers. They decide which partition a message goes to (via round-robin or key-based hashing).
2.  **Brokers**: The server nodes that store the data. Each broker manages one or more partitions of various topics.
3.  **Topics & Partitions**: A Topic is a logical category. It is split into **Partitions** to allow parallel processing across brokers.
4.  **Controller**: A designated broker that manages the state of partitions and handles leader elections.
5.  **Metadata Store (ZooKeeper/KRaft)**: Stores the cluster topology, partition leadership, and consumer offsets.
6.  **Consumers & Consumer Groups**: Clients that pull data. A **Consumer Group** ensures that each partition is read by only one member of the group at a time.

### Write vs. Read Path
- **Write Path**: Producer $\rightarrow$ Topic Partition Leader $\rightarrow$ Replication to Followers $\rightarrow$ ACK to Producer.
- **Read Path**: Consumer $\rightarrow$ Request Offset $\rightarrow$ Partition Leader $\rightarrow$ Page Cache $\rightarrow$ Network.

---

## 3. Key HLD Concepts & Component Design

### A. The Log-Structured Storage (The "Secret Sauce")
To achieve extreme throughput, the system avoids random disk I/O.
- **Append-Only Log**: Every message is appended to the end of a file. Sequential I/O is orders of magnitude faster than random I/O on both HDD and SSD.
- **Segments**: A partition is split into segments (e.g., 1GB files). Old segments are deleted based on retention policies, avoiding the need to rewrite the entire log.
- **Index Files**: To find a specific offset quickly, the system maintains an index mapping offsets to physical byte positions in the segment file.

### B. Partitioning & Scalability
- **Horizontal Scaling**: By splitting a topic into $N$ partitions, we can distribute those partitions across $M$ brokers.
- **Key-based Routing**: `partition = hash(key) % num_partitions`. This ensures all messages with the same key (e.g., `user_id`) land in the same partition, preserving **temporal ordering** for that entity.

### C. Replication & Reliability
- **ISR (In-Sync Replicas)**: Each partition has one **Leader** and multiple **Followers**. Only followers that are "caught up" with the leader are in the ISR list.
- **Quorum-based Writes**: The producer can choose the consistency level:
    - `acks=0`: Fire and forget.
    - `acks=1`: Leader writes to local log $\rightarrow$ ACK.
    - `acks=all`: Leader and all ISRs write $\rightarrow$ ACK.

### D. Performance Optimizations
- **Zero-Copy (sendfile)**: Instead of reading data into application memory and then writing it to the socket, the OS uses the `sendfile()` system call to move data directly from the **Page Cache** to the **NIC buffer**. This eliminates CPU context switches and unnecessary memory copies.
- **Batching**: Producers batch messages together to reduce the number of network requests.
- **Page Cache**: The system relies heavily on the OS page cache. Most reads occur from RAM, not disk.

---

## 4. Data Flows & Fault Tolerance

### Walkthrough: Producing a Message
1. **Metadata Lookup**: Producer asks the broker for the leader of `Topic A, Partition 1`.
2. **Batching**: Producer buffers messages locally until a size or time threshold is met.
3. **Dispatch**: Producer sends the batch to the Leader Broker.
4. **Persistence**: Leader appends the batch to its local segment file.
5. **Replication**: Follower brokers pull the data from the leader.
6. **Acknowledgement**: Once the requested `acks` condition is met, the leader sends an ACK to the producer.

### Walkthrough: Consuming a Message
1. **Join Group**: Consumer joins a `Consumer Group` and is assigned specific partitions.
2. **Fetch Request**: Consumer requests messages starting from `Offset X`.
3. **Zero-Copy Transfer**: Broker locates the offset in the index, finds the byte position in the segment, and streams it via `sendfile()`.
4. **Commit Offset**: After processing, the consumer commits the new offset (e.g., `Offset X + 100`) back to the metadata store.

### Fault Tolerance & Recovery
| Failure Scenario | Handling Mechanism |
| :--- | :--- |
| **Broker Crash** | The **Controller** detects the heartbeat failure and elects a new leader from the **ISR** list. |
| **Follower Lag** | If a follower falls too far behind, it is removed from the ISR. When it recovers, it syncs from the leader's last checkpoint. |
| **Controller Crash** | The remaining brokers use the metadata store (ZooKeeper/KRaft) to elect a new Controller. |
| **Disk Corruption** | Data is recovered from other replicas in the ISR. |

---

## 5. Production Trade-offs

### CAP Theorem Analysis
An event streaming platform is typically a **CP (Consistent and Partition Tolerant)** system by default, but it is configurable:
- **For High Consistency**: Set `acks=all` and `min.insync.replicas=2`. This ensures no data loss but increases latency and reduces availability (if too many brokers are down, writes fail).
- **For High Availability**: Set `acks=1`. This ensures faster writes and higher availability, but a leader crash before replication could lead to data loss.

### Latency vs. Throughput
- **Trade-off**: Batching.
- **Larger Batches**: Increase throughput (fewer network calls, better compression) but increase end-to-end latency (messages sit in the producer buffer longer).
- **Smaller Batches**: Decrease latency but increase CPU overhead and network congestion.

### Summary Complexity Analysis
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Produce (Write)** | $O(1)$ | $O(1)$ | Sequential append is constant time. |
| **Consume (Read)** | $O(1)$ | $O(1)$ | Offset lookup via index is constant time. |
| **Leader Election** | $O(N)$ | $O(1)$ | Where $N$ is the number of replicas. |
| **Storage** | $O(M)$ | $O(M \times R)$ | $M = \text{total messages}, R = \text{replication factor}$. |""",
    'solutions': """# System Design: Distributed Event Streaming Platform (Kafka-style)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Produce Events:** Producers must be able to send streams of events (messages) to specific "Topics."
*   **Consume Events:** Consumers must be able to read events from topics.
*   **Topics & Partitioning:** Topics must be divisible into partitions to allow for horizontal scaling and parallelism.
*   **Consumer Groups:** Multiple consumers should be able to join a group to share the load of a topic (one partition per consumer in a group).
*   **Persistence:** Events must be persisted to disk to allow for "replayability" (reading old data).
*   **Offset Management:** The system must track the position (offset) of each consumer group within a partition.
*   **Retention:** Support for time-based (e.g., 7 days) or size-based (e.g., 100GB) data retention.

### 1.2 Non-Functional Requirements
*   **High Throughput:** Ability to handle millions of events per second.
*   **Low Latency:** End-to-end latency (producer $\rightarrow$ broker $\rightarrow$ consumer) should be in the millisecond range.
*   **Durability:** Once an event is acknowledged as written, it must not be lost (replication).
*   **Scalability:** Ability to add brokers to the cluster without downtime.
*   **Fault Tolerance:** Automatic failover if a broker or partition leader crashes.

### 1.3 Scale Estimations (HLD)
*   **Throughput:** 10M events/sec.
*   **Average Event Size:** 1 KB.
*   **Ingress Bandwidth:** $10 \text{M} \times 1\text{KB} \approx 10\text{GB/s}$.
*   **Storage (7-day retention):** $10\text{GB/s} \times 86,400\text{s} \times 7\text{days} \approx 6\text{PB}$.
*   **Fan-out:** Average of 3 consumers per event $\approx 30\text{GB/s}$ egress.

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **Producer:** Client application that publishes data. It handles partitioning logic (e.g., hashing a key) and batching.
2.  **Broker:** The server responsible for receiving, storing, and serving events. It manages a set of partition replicas.
3.  **Consumer:** Client application that polls the broker for new data.
4.  **Cluster Coordinator (Metadata Store):** A distributed consensus service (e.g., KRaft or Zookeeper) that manages cluster metadata, broker registration, and leader election for partitions.
5.  **Log Segment:** The physical storage unit on the broker's disk where events are appended.

### 2.2 Architecture Diagram

```mermaid
graph TD
    subgraph Producers
        P1[Producer A]
        P2[Producer B]
    end

    subgraph ControlPlane [Control Plane / Metadata Store]
        CS[Cluster Coordinator/KRaft]
    end

    subgraph BrokerCluster [Broker Cluster]
        B1[Broker 1]
        B2[Broker 2]
        B3[Broker 3]
    end

    subgraph Consumers
        CG1[Consumer Group 1]
        CG2[Consumer Group 2]
    end

    P1 -->|Write Event| B1
    P2 -->|Write Event| B2
    B1 <-->|Heartbeat/Metadata| CS
    B2 <-->|Heartbeat/Metadata| CS
    B3 <-->|Heartbeat/Metadata| CS
    B1 ---|Replicate| B2
    B2 ---|Replicate| B3
    B1 -->|Pull Data| CG1
    B2 -->|Pull Data| CG1
    B3 -->|Pull Data| CG2
```

### 2.3 Component Interactions
1.  **Metadata Discovery:** Producers and Consumers query the Cluster Coordinator to find which broker is the **Leader** for a specific partition.
2.  **Writing (Produce):** The Producer sends a batch of messages to the Leader Broker. The Leader writes to its local log and waits for a subset of followers (ISR - In-Sync Replicas) to acknowledge before confirming success to the Producer.
3.  **Reading (Consume):** Consumers request data from the Leader Broker starting from a specific **Offset**.
4.  **Rebalancing:** When a consumer joins or leaves a group, the Coordinator re-assigns partitions among the remaining members.

---

## 3. Detailed Database & Storage Design

The platform does not use a traditional relational database for event storage; instead, it uses a **Distributed Commit Log**.

### 3.1 Storage Layer (The Log)
Events are stored in an append-only file format.
*   **Topic-Partition Directory:** Each partition is a directory on the broker's disk.
*   **Segments:** The log is split into segments (e.g., 1GB each). Once a segment is full, it is closed and a new one is opened. This simplifies deletion/retention.
*   **Index Files:** To avoid scanning the whole log, a sparse index is maintained mapping `Offset $\rightarrow$ Physical Position` in the segment file.

### 3.2 Metadata Schema (Stored in Coordinator/KV Store)
While events are in logs, the cluster state is kept in a highly available KV store.

| Entity | Fields | Description |
| :--- | :--- | :--- |
| **Topic** | `topic_id (PK), name, partitions_count, replication_factor` | General topic configuration. |
| **Partition** | `partition_id (PK), topic_id (FK), leader_broker_id, replicas[]` | Mapping of partition to brokers. |
| **Broker** | `broker_id (PK), host, port, status` | Registry of active nodes. |
| **ConsumerOffset**| `group_id, topic_id, partition_id, offset (Value)` | Tracks the last committed read position. |

**Reasoning:** A Distributed KV store (like Raft-based logs) is chosen over SQL because it provides the necessary linearizability for leader election and cluster membership changes with extremely low latency.

---

## 4. Core API Design

The system primarily uses a binary protocol over TCP for performance, but logically, the APIs are as follows:

### 4.1 Producer API
`POST /produce`
*   **Request:**
    ```json
    {
      "topic": "user_signups",
      "partition": 2, 
      "messages": [
        {"key": "user_123", "value": "...", "timestamp": 1625000000},
        {"key": "user_456", "value": "...", "timestamp": 1625000001}
      ],
      "acks": "all" 
    }
    ```
*   **Response:** `{"status": "success", "offsets": [101, 102]}`

### 4.2 Consumer API
`GET /fetch`
*   **Request:**
    ```json
    {
      "topic": "user_signups",
      "partition": 2,
      "offset": 101,
      "max_bytes": 1048576
    }
    ```
*   **Response:**
    ```json
    {
      "messages": [...],
      "next_offset": 110
    }
    ```

### 4.3 Offset Commit API
`POST /commit`
*   **Request:**
    ```json
    {
      "group_id": "analytics_group",
      "topic": "user_signups",
      "partition": 2,
      "offset": 110
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 High Throughput Optimizations
*   **Sequential I/O:** By using an append-only log, the system avoids random disk seeks, leveraging the maximum speed of HDDs/SSDs.
*   **Zero-Copy (sendfile):** The broker uses the `sendfile` system call to transfer data directly from the OS page cache to the network socket, bypassing the application's user-space buffer.
*   **Batching:** Producers aggregate messages into batches to reduce the number of network requests and disk IOPS.

### 5.2 Partitioning & Sharding
*   **Scaling:** If a topic's throughput exceeds a single broker's capacity, it is split into $N$ partitions distributed across $N$ brokers.
*   **Routing:**
    *   `Key-based`: `partition = hash(key) % num_partitions` (ensures ordering for the same key).
    *   `Round-robin`: Distributed evenly (better load balance).

### 5.3 Fault Tolerance & Replication
*   **ISR (In-Sync Replicas):** The leader maintains a list of followers that are up-to-date.
*   **Ack Levels:**
    *   `acks=0`: No confirmation (highest speed, lowest reliability).
    *   `acks=1`: Leader acknowledges (medium reliability).
    *   `acks=all`: All ISRs acknowledge (highest reliability, highest latency).
*   **Leader Election:** If the leader fails, the Cluster Coordinator promotes the next member of the ISR to be the leader.

### 5.4 Consumer Group Rebalancing
*   When a new consumer joins a group, the "Group Coordinator" (one of the brokers) triggers a rebalance.
*   Partitions are revoked from existing members and redistributed to ensure every partition is read by exactly one consumer in the group.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priority
The system is generally **CP (Consistent and Partition Tolerant)** when `acks=all` is used, as it prioritizes data integrity over availability. However, it can be tuned toward **AP (Available and Partition Tolerant)** by setting `acks=1` or `acks=0`, allowing the system to accept writes even if some replicas are down.

### 6.2 Latency vs. Throughput
*   **Batching:** Increasing batch size increases throughput (fewer syscalls, better compression) but increases latency (messages wait for the batch to fill).
*   **Compression:** Using Gzip/Snappy/LZ4 reduces network and storage usage but increases CPU overhead on both producer and consumer.

### 6.3 Storage vs. Memory
*   The system relies heavily on the **OS Page Cache**. Recent reads/writes happen in memory; older data is read from disk. This allows the system to perform nearly at memory speed for real-time consumers while still providing the durability of disk for historical replay.

### 6.4 Pull vs. Push Model
*   **Pull (Chosen):** Consumers pull data at their own pace.
    *   *Pros:* Prevents consumers from being overwhelmed; allows batching; simplifies offset management.
    *   *Cons:* Slight increase in latency due to polling intervals.""",
}

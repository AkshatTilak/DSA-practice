# Event Streaming Platform (Kafka-style) HLD

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
| **Storage** | $O(M)$ | $O(M \times R)$ | $M = \text{total messages}, R = \text{replication factor}$. |
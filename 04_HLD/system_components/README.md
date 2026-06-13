# High-Level Design: System Components

High-Level Design (HLD) centers on system scaling patterns, distributed infrastructure components, availability, partition tolerance, and caching strategies. This module deep-dives into core building blocks used to scale web applications: CDNs, Load Balancers, API Gateways, Database Replicas, Message Queues (Kafka), and Distributed Hash Tables.

---

## 🗺️ Visual Architecture: Consistent Hashing Ring

Here is a mapping of a **Consistent Hashing Ring** with virtual nodes, balancing key distribution across active database servers:

```text
               [Node A (Virtual v0)] (Angle 0)
                      ●
                  .       .
             .                 .
    [Node C] ●                 ● [Node B]
           .                     .
          .                       .
           .                     .
    [Key K2] ●                 ● [Key K1]
             .                 .
                  .       .
                      ●
               [Node A (Virtual v1)]
```

### Hash Ring Mechanics:
1. Both database servers and request partition keys are hashed into the same numeric range (e.g. $[0, 2^{32}-1]$) visualized as a circular ring.
2. A client request with Key `K1` is hashed, and we traverse clockwise to locate the first active server node (e.g. `Node B`).
3. Virtual nodes (assigning multiple points on the ring to the same physical node) are used to balance distribution and prevent hotspots.
4. When a server node joins or leaves, only a fraction of keys ($K / N$) need to be re-mapped, preserving cache consistency.

---

## 📊 Component Performance Metrics

| Component | Average Latency | Primary Failure Mode | Scaling Strategy |
| :--- | :--- | :--- | :--- |
| In-Memory Cache (Redis) | $1 - 5 \text{ ms}$ | Cache Stampede / Eviction | Replication, Redis Cluster sharding |
| Message Queue (Kafka) | $5 - 10 \text{ ms}$ | Partition Lag / Consumer Down | Partition partition count adjustment |
| Distributed DB (NoSQL) | $10 - 50 \text{ ms}$ | Split-brain / Network Partition | Consistent hashing nodes replication |

---

## 🏢 Real-World Production Use-Case

### Databases: Cassandra Distributed Data Partitioning
Cassandra databases scale horizontally across thousands of nodes without a single point of failure (masterless architecture).
1. Every write request is hashed into a token range using a Murmur3 Partitioner.
2. The hash value dictates where the write is routed on the **Consistent Hashing Ring**.
3. Replicas are placed by moving clockwise around the ring to peer nodes.
4. If a database node crashes, write requests are temporarily stored by neighboring nodes (hinted handoff), ensuring high availability and seamless partition handling.
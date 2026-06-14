# Distributed Job Scheduler HLD

A **Distributed Job Scheduler** is a system designed to execute tasks (jobs) at a specific time or on a recurring basis across a cluster of machines. Unlike a simple `cron` job on a single server, a distributed scheduler must handle millions of jobs, ensure high availability, guarantee execution reliability, and scale horizontally.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Job Submission**: Users can schedule a job to run once at a specific time or periodically (e.g., every 5 minutes, daily).
- **Job Execution**: The system must trigger the job as close to the scheduled time as possible.
- **Job Management**: Ability to cancel a scheduled job or update its execution time.
- **Status Tracking**: Users can query whether a job is `Pending`, `Running`, `Completed`, or `Failed`.
- **Retry Logic**: If a job fails, the system should retry it based on a defined policy (e.g., exponential backoff).

### Non-Functional Requirements
- **Durability**: Once a job is accepted, it must not be lost even if a node crashes.
- **High Availability**: No single point of failure (SPOF). The scheduler must remain operational during regional or zonal outages.
- **Scalability**: Handle millions of scheduled jobs per day and thousands of concurrent executions.
- **Precision**: Low scheduling latency (execution should happen within seconds of the target time).
- **Reliability (At-Least-Once)**: Guarantee that every job is executed at least once.

### Scale Assumptions
| Metric | Value |
| :--- | :--- |
| **Daily Active Jobs** | 100 Million |
| **Peak QPS (Submission)** | 10,000 requests/sec |
| **Storage Requirement** | $\sim 100M \text{ jobs} \times 1\text{KB/job} \approx 100\text{ GB/day}$ |
| **Execution Latency** | $\leq 1\text{ second deviation from target}$ |

---

## 2. High-Level System Architecture

The system is decoupled into three main phases: **Submission**, **Scheduling (Triggering)**, and **Execution**.

### Architecture Diagram Components

1.  **API Gateway & Job Service**: Handles incoming requests for scheduling, updating, and canceling jobs. It validates the request and persists the job metadata.
2.  **Job Store (Database)**: A persistent store that keeps the "Source of Truth" for all jobs, their schedules, and their current states.
3.  **Scheduling Tier (The Trigger)**: A set of distributed nodes that monitor the Job Store/Cache and push "due" jobs into the execution queue.
4.  **Distributed Message Queue (Task Queue)**: Acts as a buffer between the scheduler and the workers (e.g., Kafka or RabbitMQ).
5.  **Worker Pool**: A fleet of stateless consumers that pull tasks from the queue and execute the actual business logic.
6.  **State Tracker**: Updates the Job Store when a worker completes or fails a task.

---

## 3. Key HLD Concepts & Component Design

### A. The Scheduling Strategy (The "How")
The biggest challenge is efficiently finding jobs that are due *now* without scanning the entire database every second.

**Option 1: Database Polling (Inefficient)**
`SELECT * FROM jobs WHERE execution_time <= NOW() AND status = 'PENDING'`
- **Pros**: Simple.
- **Cons**: Heavy DB load, doesn't scale, high latency.

**Option 2: Distributed Timing Wheel (High Precision)**
A circular buffer where each slot represents a time unit.
- **Pros**: $O(1)$ complexity to add and trigger jobs.
- **Cons**: Complex to implement in a distributed manner; memory-intensive if the time horizon is large.

**Option 3: Redis Sorted Sets (Optimal for Most Cases)**
Store jobs in a Redis ZSet where the `score` is the `epoch_timestamp` of execution.
- **Operation**: The scheduler calls `ZRANGEBYSCORE jobs_set 0 <current_timestamp>`.
- **Pros**: Extremely fast, supports distributed access, naturally ordered.

### B. Database Choice
- **Metadata Store**: **PostgreSQL** or **MySQL**. We need ACID properties to ensure that updating a job's status from `Pending` to `Running` is atomic to prevent double-execution.
- **Scheduling Cache**: **Redis**. Used as a priority queue (ZSet) to trigger the jobs.

### C. Execution Queue
- **Kafka**: Chosen for its high throughput and ability to replay events. It decouples the *trigger* (scheduling) from the *action* (execution), ensuring that a spike in jobs doesn't crash the workers.

### D. Ensuring "At-Least-Once" Delivery
To prevent jobs from being lost:
1.  **Transactional Outbox**: When a job is submitted, it is written to the DB and the Redis ZSet within a coordinated flow.
2.  **Acknowledgment**: Workers only acknowledge the message in Kafka *after* the job is successfully executed. If a worker crashes, Kafka re-delivers the message to another worker.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Workflow: Scheduling a Job
1.  **Submission**: Client $\rightarrow$ `submitJob(jobId, time, payload)` $\rightarrow$ **Job Service**.
2.  **Persistence**: Job Service saves the job to **PostgreSQL** (Status: `PENDING`).
3.  **Indexing**: Job Service adds `(jobId, timestamp)` to the **Redis ZSet**.
4.  **Triggering**: The **Scheduler Node** polls Redis: `ZRANGEBYSCORE`.
5.  **Dispatch**: Scheduler pushes `jobId` to **Kafka**.
6.  **Execution**: **Worker** consumes from Kafka $\rightarrow$ fetches payload from DB $\rightarrow$ executes logic.
7.  **Completion**: Worker updates PostgreSQL (Status: `COMPLETED`).

### Handling Failures
| Failure Scenario | Mitigation Strategy |
| :--- | :--- |
| **Scheduler Node Crashes** | Use **Zookeeper/Etcd** for Leader Election. Only the leader polls Redis. If the leader dies, a follower takes over. |
| **Worker Crashes** | Kafka's consumer group mechanism ensures the partition is reassigned. The new worker picks up the unacknowledged job. |
| **Redis Cache Loss** | A **Reconciliation Job** runs every few minutes, scanning the DB for `PENDING` jobs that missed their window and re-populating the Redis ZSet. |
| **Job Logic Fails** | Implement a **Retry Queue** with exponential backoff. If max retries are reached, move the job to a **Dead Letter Queue (DLQ)** for manual intervention. |

---

## 5. Production Trade-offs

### Consistency vs. Latency (CAP Theorem)
We prioritize **Availability** and **Partition Tolerance** (AP) for the trigger mechanism (Redis) to ensure jobs are triggered promptly. However, we prioritize **Consistency** (CP) for the Job Store (PostgreSQL) to ensure we don't lose track of job states or double-bill a customer.

### At-Least-Once vs. Exactly-Once
Achieving "Exactly-Once" is computationally expensive and often impossible in distributed systems (the Two Generals' Problem).
- **Trade-off**: We implement **At-Least-Once** delivery combined with **Idempotency**.
- **Implementation**: Every job is assigned a unique `UUID`. The Worker checks a `ProcessedJobs` table/cache before execution. If the `UUID` exists, the worker skips execution.

### Pull vs. Push Model
- **Push (Scheduler $\rightarrow$ Kafka $\rightarrow$ Worker)**: Better for high throughput and handling bursts. This is the chosen design.
- **Pull (Worker $\rightarrow$ DB)**: Simple, but creates massive DB contention (locking) when thousands of workers poll the same table.

---

## Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Job Submission** | $O(1)$ | $O(1)$ | DB write + Redis ZADD |
| **Finding Due Jobs** | $O(\log N + M)$ | $O(M)$ | $N = \text{Total jobs}, M = \text{Due jobs}$ |
| **Job Execution** | $O(1)$ | $O(1)$ | Constant time to dequeue and trigger |
| **Job Cancellation** | $O(\log N)$ | $O(1)$ | Redis ZREM |
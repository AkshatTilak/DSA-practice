# Workflow Orchestrator HLD

A **Workflow Orchestrator** (similar to Apache Airflow, Temporal, or Prefect) is a distributed system designed to author, schedule, and monitor complex sequences of tasks. These tasks are typically represented as a **Directed Acyclic Graph (DAG)**, where nodes represent units of work and edges represent dependencies.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **DAG Definition**: Ability to define workflows as DAGs (tasks and their dependencies).
*   **Scheduling**: Trigger workflows based on time (cron), events, or manual triggers.
*   **Dependency Management**: Ensure a task only executes after its upstream dependencies have successfully completed.
*   **Execution & Scaling**: Distribute task execution across a pool of workers.
*   **Fault Tolerance**: Automatic retries for failed tasks with configurable backoff policies.
*   **Observability**: A UI/API to track task states (`Scheduled`, `Running`, `Success`, `Failed`, `Upstream_Failed`).
*   **State Persistence**: Maintain a history of all workflow runs and task attempts.

### Non-Functional Requirements
*   **Durability**: Task states must be persisted; if the scheduler crashes, it must resume from the last known state.
*   **Scalability**: Support thousands of concurrent DAGs and millions of task instances per day.
*   **Reliability (At-least-once)**: Guarantee that every scheduled task is executed at least once.
*   **Availability**: The scheduler and API must be highly available to prevent gaps in workflow triggers.

### Scale Assumptions
*   **DAU**: 1,000+ Data Engineers/DevOps users.
*   **Throughput**: 10k+ DAGs; $10^6$ task instances per day.
*   **Latency**: Scheduling latency (time from "ready" to "queued") should be $< 1$ second.
*   **Storage**: High volume of historical logs and state transitions (TB scale over time).

---

## 2. High-Level System Architecture

The architecture follows a decoupled **Producer-Consumer** pattern to separate the "planning" (Scheduling) from the "execution" (Working).

### Architecture Components

1.  **API Server / UI**:
    *   Provides the interface to upload DAG definitions, trigger runs, and monitor progress.
    *   Acts as a gateway to the Metadata Database.
2.  **Metadata Database (SQL)**:
    *   The "Source of Truth." Stores DAG structures, task definitions, run history, and current state.
    *   **Why SQL?** DAGs are inherently relational (Nodes $\to$ Edges). ACID properties are critical to ensure a task isn't marked as "Success" and "Failed" simultaneously.
3.  **Scheduler**:
    *   The brain of the system. It continuously polls the Metadata DB for DAGs that need to run.
    *   Checks if dependencies are met $\to$ Updates task state to `Queued` $\to$ Pushes task ID to the Message Queue.
4.  **Message Queue (Broker)**:
    *   Decouples the Scheduler from the Workers.
    *   **Choices**: Redis (fast), RabbitMQ (reliable), or Kafka (high throughput/replayable).
5.  **Workers**:
    *   Pull tasks from the queue, execute the underlying logic (Python script, Bash command, Docker container), and report the result back to the Metadata DB.
6.  **Executor**:
    *   A logical layer that determines *how* tasks are distributed (e.g., `CeleryExecutor` for a queue-based approach or `KubernetesExecutor` for spawning a pod per task).

---

## 3. Key HLD Concepts & Component Design

### The DAG Representation
A DAG is represented as a set of vertices $V$ and edges $E$. To prevent infinite loops, the system must perform a **Cycle Detection** check (using DFS) upon DAG upload.

### State Machine Logic
Each task instance transitions through a strict state machine:
$\text{None} \xrightarrow{\text{Scheduled}} \text{Queued} \xrightarrow{\text{Worker Pick-up}} \text{Running} \xrightarrow{\text{Completion}} \text{Success/Failed}$

### The Scheduling Loop
The scheduler runs a continuous loop:
1.  **Scan**: Find DAGs whose schedule interval has passed.
2.  **Dependency Check**: For each task in the DAG, check if all `upstream_task_ids` are in the `Success` state.
3.  **Queue**: If dependencies are met and the task is not yet running, move state to `Queued` and push to the Message Broker.

### Worker Execution & Heartbeats
To handle **Worker Crashes**, the system implements a heartbeat mechanism:
*   While a worker is executing a task, it updates a `last_heartbeat` timestamp in the Metadata DB every $N$ seconds.
*   A **Zombie Hunter** process (part of the scheduler) scans for tasks in `Running` state with a stale heartbeat.
*   Stale tasks are marked as `Failed` or `Up-for-Retry`.

### Technology Stack Selection

| Component | Choice | Justification |
| :--- | :--- | :--- |
| **Metadata DB** | PostgreSQL | Strong ACID compliance for state transitions; excellent support for relational queries. |
| **Message Queue** | Redis / RabbitMQ | Low latency for task distribution; supports priority queues. |
| **Storage** | S3 / GCS | Used for storing large task logs and artifacts (XComs/Data exchange). |
| **Coordination** | ZooKeeper / Etcd | Used for Leader Election among multiple Scheduler instances. |

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Flow (Task Execution)
1.  **Definition**: User uploads a Python file defining a DAG $\to$ API $\to$ Metadata DB.
2.  **Trigger**: Scheduler detects a cron trigger $\to$ creates a `DagRun` entry in DB.
3.  **Orchestration**: Scheduler identifies Task A (no dependencies) $\to$ Sets state to `Queued` $\to$ Pushes `{dag_id, task_id, run_id}` to Redis.
4.  **Execution**: Worker pulls message $\to$ Sets state to `Running` $\to$ Executes the code.
5.  **Completion**: Worker finishes $\to$ Sets state to `Success` $\to$ Updates DB.
6.  **Downstream Trigger**: In the next scheduler loop, Task B (dependent on A) is now eligible $\to$ Repeat from Step 3.

### Handling Failures

| Failure Scenario | Mitigation Strategy |
| :--- | :--- |
| **Worker Crashes** | Heartbeat timeout $\to$ Scheduler detects stale task $\to$ Mark as `Failed` $\to$ Trigger Retry. |
| **Scheduler Crashes** | **Active-Passive High Availability**: Use ZooKeeper for leader election. If leader dies, standby takes over. |
| **DB Downtime** | Use synchronous replication (Multi-AZ) to ensure no state loss. |
| **Task Failure** | Configurable `retries` parameter. Use **Exponential Backoff** to avoid hammering a failing downstream API. |
| **Network Partition** | Idempotency Keys: Workers use the `run_id` as a key to ensure they don't execute the same task instance twice. |

---

## 5. Production Trade-offs

### Consistency vs. Latency (CAP Theorem)
In a workflow orchestrator, **Consistency (C)** is prioritized over **Availability (A)**. If the Metadata DB is unavailable, it is better to stop scheduling new tasks than to risk starting the same task multiple times (which could cause data duplication or corruption in data pipelines).

### Pull vs. Push Model
*   **Push (Scheduler $\to$ Worker)**: Low latency, but the scheduler must track worker health and capacity.
*   **Pull (Worker $\to$ Queue)**: Higher scalability. Workers pull only when they have capacity, providing natural **backpressure** and preventing worker overload.

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Cycle Detection** | $O(V + E)$ | $O(V)$ | Performed once during DAG upload via DFS. |
| **Scheduling Loop** | $O(N_{active\_tasks})$ | $O(1)$ | Proportional to the number of tasks being evaluated. |
| **Task State Update** | $O(1)$ | $O(1)$ | Simple indexed primary key update in SQL. |
| **Dependency Lookup** | $O(1)$ | $O(1)$ | Optimized via indexed foreign keys in the DB. |
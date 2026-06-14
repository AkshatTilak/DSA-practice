INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Workflow Orchestrator (Airflow style).',
    'groups': ['Real-World Systems', 'Data Pipelines'],
    'readme_content': r"""# Workflow Orchestrator HLD

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
| **Dependency Lookup** | $O(1)$ | $O(1)$ | Optimized via indexed foreign keys in the DB. |""",
    'solutions': r"""# System Design Document: Distributed Workflow Orchestrator

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **DAG Definition:** Users must be able to define workflows as Directed Acyclic Graphs (DAGs), specifying tasks and their dependencies.
*   **Scheduling:** Support for various scheduling triggers:
    *   Time-based (Cron expressions, fixed intervals).
    *   Event-based (External API triggers, Webhooks).
    *   Dependency-based (Triggered upon completion of another DAG).
*   **Task Execution:** Ability to execute diverse task types (Python scripts, Bash commands, SQL queries, API calls).
*   **Dependency Management:** A task should only execute once all its upstream dependencies have succeeded.
*   **Fault Tolerance & Retries:** Automatic retries with configurable backoff policies upon task failure.
*   **Monitoring & Observability:** A UI to visualize DAG progress, view logs for specific task instances, and manually trigger/clear tasks.
*   **State Management:** Track the state of every DAG run and every individual task instance (e.g., `queued`, `running`, `success`, `failed`, `up_for_retry`).

### 1.2 Non-Functional Requirements
*   **Scalability:** Handle thousands of active DAGs and millions of task instances per day.
*   **High Availability:** No single point of failure for the scheduler or worker nodes.
*   **Reliability (Exactly-Once/At-Least-Once):** Ensure tasks are not lost. While strict exactly-once is hard in distributed systems, the system should aim for at-least-once execution with idempotency requirements on the task level.
*   **Extensibility:** Ability to add new "Operators" (task types) without modifying the core engine.
*   **Durability:** DAG definitions and execution history must persist across system restarts.

### 1.3 Scale Estimations (HLD)
*   **DAGs:** 10,000 active DAGs.
*   **Daily Task Instances:** $\sim 1,000,000$ tasks/day.
*   **Throughput:** Average $\sim 12$ tasks per second, but peak bursts could reach $500$ tasks/sec.
*   **Storage:** Task logs are the primary storage driver. If each task generates 10KB of logs, $10^6 \text{ tasks} \times 10\text{KB} = 10\text{GB/day}$.

---

## 2. High-Level Architecture

The system follows a decoupled architecture separating the **Control Plane** (Scheduler, API, DB) from the **Data Plane** (Workers).

### 2.1 Core Components
1.  **API Server:** The entry point for the UI and external triggers. Handles DAG CRUD operations and manual triggers.
2.  **Scheduler:** The "Brain." It continuously polls the Metadata DB to identify DAGs that need to be run and tasks that are ready for execution based on dependency resolution.
3.  **Metadata Database:** The source of truth for DAG definitions, run states, and task instance history.
4.  **Task Queue (Message Broker):** Decouples the Scheduler from Workers. The Scheduler pushes "ready-to-run" task metadata into the queue.
5.  **Worker Nodes:** Pull tasks from the queue, execute the actual logic, and update the task state in the Metadata DB.
6.  **Log Store:** A distributed storage system (e.g., S3, GCS, or Elasticsearch) to store task execution logs.

### 2.2 Architecture Diagram

```mermaid
graph TD
    User((User/UI)) --> API[API Server]
    API --> DB[(Metadata DB)]
    
    subgraph ControlPlane [Control Plane]
        Scheduler[Scheduler]
        DB
    end
    
    Scheduler --> DB
    Scheduler --> Queue[Task Queue / Broker]
    
    subgraph DataPlane [Execution Plane]
        Queue --> Worker1[Worker 1]
        Queue --> Worker2[Worker 2]
        Queue --> WorkerN[Worker N]
    end
    
    Worker1 --> DB
    Worker2 --> DB
    WorkerN --> DB
    
    Worker1 --> Logs[(Remote Log Store)]
    Worker2 --> Logs
    WorkerN --> Logs
```

### 2.3 Sequence Flow: Task Execution
1.  **Trigger:** The Scheduler detects a Cron trigger or the API receives a manual trigger.
2.  **DagRun Creation:** Scheduler creates a `DagRun` entry in the DB with status `running`.
3.  **Dependency Check:** Scheduler scans the DAG for tasks with no dependencies (or whose dependencies are `success`).
4.  **Queuing:** Scheduler creates `TaskInstance` entries and pushes a message `{dag_run_id, task_id}` to the Task Queue.
5.  **Execution:** A Worker picks up the message, fetches the task definition, and executes the code.
6.  **State Update:** Upon completion, the Worker updates the `TaskInstance` state to `success` or `failed` in the DB.
7.  **Cycle:** The Scheduler sees the state change and triggers the next set of downstream tasks.

---

## 3. Detailed Database Schema Design

A Relational Database (PostgreSQL/MySQL) is chosen for the Metadata DB because workflow orchestration requires strict ACID properties to prevent race conditions (e.g., two schedulers starting the same task).

### 3.1 Schema Tables

#### Table: `dag`
Stores the definition and configuration of the workflow.
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `dag_id` | VARCHAR | PK | Unique identifier for the DAG |
| `schedule_interval`| VARCHAR | | Cron expression or interval |
| `is_paused` | BOOLEAN | | Whether the DAG is currently active |
| `owner` | VARCHAR | | User who created the DAG |
| `created_at` | TIMESTAMP | | Creation timestamp |

#### Table: `task`
Defines the individual units of work within a DAG.
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `task_id` | VARCHAR | PK | Unique identifier for the task |
| `dag_id` | VARCHAR | FK $\rightarrow$ `dag` | Parent DAG |
| `operator_type` | VARCHAR | | e.g., `PythonOperator`, `BashOperator` |
| `command` | TEXT | | The code or command to execute |
| `retries` | INT | | Max number of retries |

#### Table: `task_dependency`
Defines the edges of the DAG.
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `upstream_task_id`| VARCHAR | FK $\rightarrow$ `task` | The prerequisite task |
| `downstream_task_id`| VARCHAR | FK $\rightarrow$ `task` | The task to trigger |

#### Table: `dag_run`
A specific execution instance of a DAG.
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `run_id` | UUID | PK | Unique instance ID |
| `dag_id` | VARCHAR | FK $\rightarrow$ `dag` | Parent DAG |
| `execution_date` | TIMESTAMP | INDEX | The logical date the DAG is running for |
| `state` | ENUM | | `running`, `success`, `failed` |

#### Table: `task_instance`
The state of a specific task within a specific DAG run.
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `ti_id` | UUID | PK | Unique instance ID |
| `run_id` | UUID | FK $\rightarrow$ `dag_run` | Parent Run |
| `task_id` | VARCHAR | FK $\rightarrow$ `task` | Parent Task |
| `state` | ENUM | INDEX | `queued`, `running`, `success`, `failed`, `up_for_retry` |
| `try_number` | INT | | Current attempt count |
| `start_date` | TIMESTAMP | | When execution started |
| `end_date` | TIMESTAMP | | When execution finished |

### 3.2 Indexing Strategy
*   **`task_instance(run_id, state)`**: Crucial for the Scheduler to quickly find tasks that are `success` to unlock downstream tasks.
*   **`dag_run(dag_id, execution_date)`**: To prevent duplicate runs for the same period.
*   **`dag(is_paused)`**: To filter only active DAGs during scheduling cycles.

---

## 4. Core API Design

The API serves as the management layer.

### 4.1 Endpoints

#### `POST /api/v1/dags`
Creates a new DAG definition.
*   **Payload:**
    ```json
    {
      "dag_id": "daily_sales_report",
      "schedule": "0 0 * * *",
      "tasks": [
        {"task_id": "extract", "operator": "PythonOperator", "cmd": "extract_data()"},
        {"task_id": "transform", "operator": "PythonOperator", "cmd": "transform_data()"},
        {"task_id": "load", "operator": "SQLOperator", "cmd": "INSERT INTO ..."}
      ],
      "dependencies": [
        {"upstream": "extract", "downstream": "transform"},
        {"upstream": "transform", "downstream": "load"}
      ]
    }
    ```
*   **Response:** `201 Created`

#### `POST /api/v1/dags/{dag_id}/trigger`
Manually triggers a DAG run.
*   **Payload:** `{"conf": {"date": "2023-10-01"}}` (Optional configuration)
*   **Response:** `202 Accepted` `{ "run_id": "uuid-123" }`

#### `GET /api/v1/runs/{run_id}/status`
Fetches the status of a specific run and all its task instances.
*   **Response:**
    ```json
    {
      "run_id": "uuid-123",
      "state": "running",
      "tasks": [
        {"task_id": "extract", "state": "success", "start": "..."},
        {"task_id": "transform", "state": "running", "start": "..."}
      ]
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Scaling the Scheduler
The Scheduler is often the bottleneck. To scale:
*   **DAG Partitioning:** Instead of one scheduler polling all DAGs, we use a "Scheduler Cluster." DAGs are sharded across scheduler instances using consistent hashing on `dag_id`.
*   **Distributed Locking:** Use a tool like ZooKeeper or Etcd (or `SELECT FOR UPDATE` in SQL) to ensure that only one scheduler instance is processing a specific `dag_id` at a time to avoid double-queuing.

### 5.2 Worker Scaling & Resource Isolation
*   **Dynamic Scaling:** Workers can be deployed as Kubernetes Pods. Use a K8s Horizontal Pod Autoscaler (HPA) based on the depth of the Task Queue.
*   **Worker Queues:** Implement "named queues." For example, `gpu-queue` for ML tasks and `cpu-queue` for data parsing. Workers only subscribe to the queues they are equipped to handle.
*   **Task Timeouts:** Implement a "Zombie Detection" mechanism. The worker sends heartbeats to the DB. If a worker crashes, the scheduler sees the missing heartbeat and marks the task as `up_for_retry`.

### 5.3 Log Management
Writing logs directly to the DB is an anti-pattern.
*   **Remote Log Store:** Workers stream logs to an object store (S3) or a log aggregator (Elasticsearch).
*   **Log Retrieval:** The UI requests logs via the API, which generates a pre-signed URL to the S3 object, offloading the data transfer from the API server.

### 5.4 Fault Tolerance
*   **Idempotency:** Since the system provides "at-least-once" delivery, tasks must be idempotent. The system can support this by passing the `run_id` and `execution_date` to the task, allowing the user to implement "upsert" logic.
*   **Database High Availability:** Use a Multi-AZ RDS deployment with synchronous replication.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Consistency vs. Availability
In a workflow orchestrator, **Consistency (CP)** is prioritized over Availability. If the Metadata DB is unavailable, it is better to stop scheduling new tasks than to risk triggering the same data pipeline twice, which could lead to corrupted data or duplicate financial transactions.

### 6.2 Polling vs. Event-Driven Scheduling
*   **Polling (Current Choice):** The Scheduler polls the DB. 
    *   *Pro:* Simple, robust, handles "missed" intervals easily.
    *   *Con:* Introduces latency between a dependency finishing and the next task starting.
*   **Event-Driven:** Workers notify the Scheduler via a message when a task finishes.
    *   *Pro:* Near-instant trigger.
    *   *Con:* High complexity in handling missed events (lost messages) and race conditions.

### 6.3 SQL vs. NoSQL for Metadata
*   **SQL (Chosen):** Needed for complex joins (Tasks $\rightarrow$ Dependencies $\rightarrow$ Runs) and ACID transactions to ensure state transitions are atomic.
*   **NoSQL:** While better for scaling, it lacks the relational integrity required to maintain a DAG's structural constraints and run-state consistency.

### 6.4 Summary Table

| Trade-off | Selection | Reason |
| :--- | :--- | :--- |
| **State Storage** | PostgreSQL | ACID compliance and relational queries. |
| **Task Dispatch** | Message Queue | Decouples scheduling from execution; enables scaling. |
| **Log Storage** | Object Store (S3) | Cost-effective, scalable, and prevents DB bloat. |
| **Scheduler** | Partitioned Polling | Balances simplicity with horizontal scalability. |""",
}

# System Design Document: Real-time Collaborative Online IDE (Replit Clone)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Project Management:** Users can create, delete, and rename projects (Repls).
*   **Real-time Collaborative Editing:** Multiple users can edit the same file simultaneously with near-zero latency, seeing each other's cursors and changes.
*   **Code Execution:** Users can run their code in a supported language and see the output in a console/terminal.
*   **Interactive Terminal:** Users have access to a shell within the project environment to manage files or install packages.
*   **File System:** Full CRUD operations on a virtual file system within the project.
*   **Persistence:** All code and environment configurations must be persisted across sessions.

### 1.2 Non-Functional Requirements
*   **Low Latency:** Keystroke synchronization must feel instantaneous (< 100ms).
*   **Security & Isolation:** Code execution must be strictly sandboxed to prevent "container escape" or attacks on the host infrastructure.
*   **High Availability:** The system should be available 24/7; a failure in one execution node should not affect other users.
*   **Scalability:** Support millions of users and thousands of concurrent collaborative sessions.
*   **Consistency:** The final state of the code must be consistent across all collaborators.

### 1.3 Scale Estimations (HLD)
*   **Daily Active Users (DAU):** 1 Million.
*   **Concurrent Users:** 100k.
*   **Average Session Duration:** 1 hour.
*   **Write Volume:** High. Every keystroke is a potential update. If 100k users type 2 chars/sec, that's 200k ops/sec.
*   **Storage:** Average project size 5MB. $1M \text{ projects} \times 5\text{MB} = 5\text{TB}$ (manageable, but grows with history).

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **API Gateway:** Handles authentication, rate limiting, and routes requests to internal services.
2.  **Collaboration Service (The "Sync" Engine):** Manages real-time WebSocket connections and resolves conflicts using CRDTs (Conflict-free Replicated Data Types).
3.  **Orchestration Service:** Provisions and manages the lifecycle of execution environments (containers).
4.  **Execution Engine (Sandboxed Worker):** Isolated environments (using Firecracker VMs or gVisor) where user code is actually executed.
5.  **File Service:** Manages the virtual file system, mapping project files to persistent storage.
6.  **Metadata DB:** Stores user profiles, project metadata, and permission settings.

### 2.2 Architecture Diagram (ASCII)

```text
[Client Browser] 
       |
       | (HTTPS/WSS)
       v
[ API Gateway / Load Balancer ]
       |
       +-----------------------+-----------------------+
       |                       |                       |
[Collaboration Service] [Orchestration Service] [File/Metadata Service]
       |                       |                       |
       | (WebSockets)          | (gRPC/Control Plane)   | (SQL/NoSQL)
       v                       v                       v
[ Redis (Session/State) ] [ Execution Nodes ] <---> [ Persistent Storage ]
                                |                     (S3/EFS/Distributed FS)
                                v
                        [ Firecracker VM ]
                        [ (User Code)   ]
```

### 2.3 Interaction Flow
1.  **Opening a Project:** Client $\rightarrow$ Gateway $\rightarrow$ Metadata Service (Fetch project info) $\rightarrow$ Orchestration Service (Wake up/Start Container) $\rightarrow$ Client (Connect to VM).
2.  **Editing Code:** Client $\rightarrow$ Collaboration Service (WebSocket) $\rightarrow$ Broadcast to other users via CRDT $\rightarrow$ Periodically flush to File Service.
3.  **Running Code:** Client $\rightarrow$ Gateway $\rightarrow$ Orchestration Service $\rightarrow$ Command sent to Execution Node $\rightarrow$ Output streamed back via WebSocket.

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection
*   **Relational DB (PostgreSQL):** Used for structured metadata (Users, Project ownership, Permissions). Requires ACID compliance for billing and ownership.
*   **NoSQL / Document Store (MongoDB or DynamoDB):** Used for storing project configurations, environment variables, and session snapshots.
*   **Distributed File System (AWS EFS or Ceph):** Used to store the actual source code files. Storing code as blobs in a DB is inefficient for large projects.
*   **In-Memory Store (Redis):** Used for presence (who is online), cursor positions, and caching active CRDT states.

### 3.2 Schema

#### Table: `Users` (PostgreSQL)
| Field | Type | Key | Note |
| :--- | :--- | :--- | :--- |
| user_id | UUID | PK | Unique identifier |
| username | VARCHAR(50) | Unique | |
| email | VARCHAR(100) | Unique | |
| created_at | Timestamp | | |

#### Table: `Projects` (PostgreSQL)
| Field | Type | Key | Note |
| :--- | :--- | :--- | :--- |
| project_id | UUID | PK | |
| owner_id | UUID | FK | Reference to Users |
| language | VARCHAR(20) | | e.g., 'python', 'nodejs' |
| project_name | VARCHAR(100) | | |
| created_at | Timestamp | | |

#### Table: `Project_Members` (PostgreSQL)
| Field | Type | Key | Note |
| :--- | :--- | :--- | :--- |
| project_id | UUID | FK | |
| user_id | UUID | FK | |
| role | ENUM | | 'owner', 'editor', 'viewer' |

#### Table: `File_Metadata` (NoSQL/Postgres)
| Field | Type | Key | Note |
| :--- | :--- | :--- | :--- |
| file_id | UUID | PK | |
| project_id | UUID | FK/Index | |
| path | TEXT | | e.g., `/src/main.py` |
| size | BIGINT | | |
| last_modified | Timestamp | | |

---

## 4. Core API Design

### 4.1 Project Management (REST)
*   `POST /api/v1/projects`: Create a new project.
    *   Request: `{ "name": "my-app", "language": "python" }`
    *   Response: `{ "project_id": "uuid-123", "status": "provisioning" }`
*   `GET /api/v1/projects/{id}`: Fetch project metadata.
*   `DELETE /api/v1/projects/{id}`: Delete project.

### 4.2 Execution & Terminal (WebSocket)
*   **Connection:** `wss://api.replit.com/terminal/{project_id}`
*   **Payload (Client $\rightarrow$ Server):**
    ```json
    {
      "type": "SHELL_COMMAND",
      "payload": "npm install express"
    }
    ```
*   **Payload (Server $\rightarrow$ Client):**
    ```json
    {
      "type": "SHELL_OUTPUT",
      "payload": "Installing express... Done."
    }
    ```

### 4.3 Real-time Collaboration (WebSocket)
*   **Connection:** `wss://api.replit.com/collab/{project_id}/{file_id}`
*   **Payload (CRDT Update):**
    ```json
    {
      "type": "EDIT_OP",
      "userId": "user-456",
      "op": { "insert": "a", "pos": 12, "clock": 105 }
    }
    ```
*   **Payload (Cursor Update):**
    ```json
    {
      "type": "CURSOR_MOVE",
      "userId": "user-456",
      "pos": { "line": 10, "ch": 5 }
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Real-time Sync: CRDT vs OT
To handle concurrent edits, we use **CRDTs (Conflict-free Replicated Data Types)** (e.g., Yjs or Automerge). 
*   **Why?** Unlike Operational Transformation (OT), CRDTs are mathematically designed to merge concurrently without requiring a central authority to sequence every operation. This allows for better offline support and easier scaling across multiple collaboration servers.

### 5.2 Code Execution Sandbox
Running arbitrary user code is high-risk.
*   **Firecracker MicroVMs:** Instead of standard Docker containers (which share the host kernel), we use Firecracker. It provides VM-level isolation with container-like startup speeds.
*   **Resource Quotas:** Use `cgroups` to limit CPU (e.g., 0.5 vCPU) and RAM (e.g., 512MB) per Repl to prevent "noisy neighbor" or DoS attacks.
*   **Network Isolation:** Use VPCs and Security Groups to ensure a Repl cannot scan the internal network or access other users' VMs.

### 5.3 Scaling the Collaboration Service
*   **Sticky Sessions / Consistent Hashing:** Use a load balancer with consistent hashing based on `project_id`. All users working on the same project should be routed to the same Collaboration Server instance to minimize cross-server communication for CRDT state synchronization.
*   **Pub/Sub Backbone:** Use Redis Pub/Sub or NATS to broadcast updates if a project becomes so large that it needs to be sharded across multiple servers.

### 5.4 Storage Strategy
*   **Hot Path:** Active files are loaded into the Execution VM's local disk (ephemeral SSD).
*   **Warm Path:** Files are mirrored to a Distributed File System (e.g., Amazon EFS) for persistence.
*   **Cold Path:** Periodic snapshots of the project are archived to S3.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priority
*   **Collaboration:** Prioritizes **Availability** and **Partition Tolerance** (AP). Users should be able to type even if the connection is flaky. CRDTs ensure that once the connection is restored, the state eventually converges (**Eventual Consistency**).
*   **Project Metadata:** Prioritizes **Consistency** and **Partition Tolerance** (CP). We cannot have two users owning the same unique project name.

### 6.2 Latency vs. Storage
*   **Trade-off:** Storing every single keystroke as a versioned event allows for "Infinite Undo" and "Time Travel" debugging, but consumes massive storage.
*   **Solution:** Use a hybrid approach. Log operations in real-time to a write-ahead log (WAL) in Redis, then collapse/snapshot the state into the file system every 30 seconds or upon project closure.

### 6.3 Virtualization: Container vs. VM
*   **Container (Docker):** Faster startup, lower overhead, but weaker isolation (shared kernel).
*   **MicroVM (Firecracker):** Slower than containers (though still sub-second), higher overhead, but provides hardware-level isolation.
*   **Decision:** For a public IDE, **MicroVMs** are non-negotiable for security reasons.
# Replit (Online IDE) HLD

Designing a platform like Replit is a complex engineering challenge that merges **real-time collaborative editing** (similar to Google Docs) with **remote code execution** (similar to a cloud-based terminal/OS). This system must handle high concurrency, maintain strict security boundaries to prevent malicious code from escaping the sandbox, and provide ultra-low latency for a seamless typing experience.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Real-time Collaboration**: Multiple users should be able to edit the same file simultaneously with visible cursors and instant updates.
*   **Code Execution**: Users can run their code in various languages (Python, JS, C++, etc.) and see the output in a terminal.
*   **File System Management**: Create, delete, and organize files and folders within a project ("Repl").
*   **Interactive Terminal**: A full-featured shell providing access to the environment where the code is running.
*   **Persistence**: All code changes and environment configurations must be saved.

### Non-Functional Requirements
*   **Low Latency**: Keystroke latency must be minimal (< 50ms) to ensure a "local" feel.
*   **Strong Isolation**: Untrusted user code must be executed in a secure sandbox to prevent attacks on the host system.
*   **Availability**: High availability for the IDE and the execution environments.
*   **Scalability**: Support millions of concurrent users and thousands of active execution containers.
*   **Durability**: Code must not be lost; changes must be persisted reliably.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 1 Million |
| **Concurrent Users** | 100k - 500k |
| **Avg. Users per Repl** | 1 - 5 users |
| **Storage per Repl** | 10MB - 500MB |
| **Execution Duration** | Short-lived (seconds) to Long-lived (hours for servers) |

---

## 2. High-Level System Architecture

The system is split into two primary planes: the **Collaboration Plane** (handling the editor state) and the **Execution Plane** (handling the runtime environment).

### Architecture Diagram Component Roles
1.  **API Gateway**: Entry point for authentication, rate limiting, and routing.
2.  **Collaboration Service**: A WebSocket-based service that manages real-time synchronization of text using **Operational Transformation (OT)** or **CRDTs**.
3.  **Orchestration Service**: Manages the lifecycle of the execution containers (starting, stopping, and scaling).
4.  **Execution Sandbox (The "Pod")**: A highly isolated environment (e.g., gVisor or Firecracker) where the user's code actually runs.
5.  **Virtual File System (VFS)**: A layer that maps the project files to the container and persists them to a distributed database or object store.
6.  **Terminal Service**: A proxy that bridges the browser's Xterm.js terminal to the container's PTY (Pseudo-Terminal).

---

## 3. Key HLD Concepts & Component Design

### A. Real-time Collaboration: OT vs. CRDT
To handle concurrent edits, we cannot simply send the whole file on every change. We must send **diffs**.

| Feature | Operational Transformation (OT) | Conflict-free Replicated Data Types (CRDT) |
| :--- | :--- | :--- |
| **Approach** | Server transforms operations based on state. | Data structures merge mathematically. |
| **Server Role** | Centralized "Source of Truth" required. | Can be Decentralized/P2P. |
| **Complexity** | High server-side logic complexity. | Higher memory overhead (metadata). |
| **Latency** | Requires round-trip to server for confirmation. | Local updates are immediate and convergent. |

**Choice for Replit**: **OT (Operational Transformation)** is generally preferred for centralized IDEs because the server can act as the final arbiter of the file state, making it easier to implement features like access control and snapshots.

### B. The Execution Sandbox (Security)
Standard Docker containers share the host OS kernel. A malicious user could use a kernel exploit to "escape" the container and access the host.
*   **gVisor**: A user-space kernel that intercepts syscalls. It provides a stronger boundary than Docker.
*   **Firecracker (MicroVMs)**: Used by AWS Lambda. It provides the isolation of a VM with the startup speed of a container.
*   **Resource Quotas**: Cgroups are used to limit CPU (e.g., 0.5 vCPU) and RAM (e.g., 512MB) to prevent "noisy neighbor" or Denial of Service (DoS) attacks.

### C. File System & Persistence
User code cannot reside only in the container (as containers are ephemeral).
*   **Active Session**: Files are mounted into the container via a network file system (e.g., NFS or a custom FUSE mount).
*   **Cold Storage**: When a Repl is inactive, the file system is snapshotted and stored in an Object Store (S3) or a NoSQL Document Store.
*   **Metadata**: Project names, permissions, and user ownership are stored in a relational database (PostgreSQL).

### D. Terminal Streaming
The terminal is not a standard HTTP request. It requires a **full-duplex stream**.
*   **Frontend**: Xterm.js renders the terminal.
*   **Backend**: A WebSocket proxy connects to the container's `/dev/pts` (pseudo-terminal).
*   **Protocol**: The proxy forwards bytes from the terminal to the browser and vice versa.

---

## 4. Data Flows & Fault Tolerance

### Path 1: Editing a Line of Code
1.  **Client A** types a character. The editor generates an operation: `Insert('x', position 10)`.
2.  **Client A** applies the change locally immediately (Optimistic UI).
3.  The operation is sent via **WebSocket** to the **Collaboration Service**.
4.  The server checks the version. If **Client B** edited the same line, the server **transforms** the operation to maintain consistency.
5.  The server broadcasts the transformed operation to **Client B**.
6.  The server asynchronously persists the change to the **VFS**.

### Path 2: Executing Code
1.  User clicks "Run".
2.  **Orchestration Service** checks if a container is already running for this Repl.
3.  If not, it provisions a **Firecracker MicroVM**, mounts the project files, and starts the runtime.
4.  The service sends a command to the container to execute `main.py`.
5.  The output (stdout/stderr) is streamed back via the **Terminal Service** to the user's screen.

### Fault Tolerance & Reliability
*   **Node Crash**: If a Collaboration Server crashes, the WebSocket disconnects. The client reconnects to another server, which loads the current state from the VFS.
*   **Container Hang**: A "Watchdog" process monitors container resource usage. If a user writes an infinite loop that consumes 100% CPU, the system kills the process after a timeout.
*   **Network Partition**: If the client loses internet, changes are queued locally. Upon reconnection, the OT engine performs a "catch-up" synchronization.

---

## 5. Production Trade-offs

### Consistency vs. Latency (CAP Theorem)
In the editor, we prioritize **Availability and Partition Tolerance (AP)** on the client side (Optimistic UI) to ensure zero lag. However, the server enforces **Strong Consistency** via the OT sequence number to ensure all users eventually see the exact same code.

### Isolation vs. Cold Start
| Strategy | Isolation | Startup Time | Resource Overhead |
| :--- | :--- | :--- | :--- |
| **Docker** | Low | Very Fast | Very Low |
| **gVisor** | Medium | Fast | Low |
| **Firecracker** | High | Medium | Medium |

**Trade-off**: Replit chooses high isolation (Firecracker/gVisor) because allowing users to run arbitrary code on shared hardware is a massive security risk. To mitigate the "Cold Start" (latency when first clicking Run), the system may keep "warm" generic containers ready to be assigned to a user.

### Storage: SQL vs. NoSQL
*   **SQL (Postgres)**: Used for User accounts, Repl metadata, and Permissions. These require ACID transactions.
*   **Object Store (S3/Blob)**: Used for the actual source code files. Storing large amounts of text/binary files in SQL would lead to massive bloating and poor performance.
# Google Docs HLD: Real-Time Collaborative Editing

This study guide provides a comprehensive high-level design for a real-time collaborative document editing system like Google Docs. The primary challenge in this system is **concurrency control**—ensuring that multiple users can edit the same document simultaneously without losing data or ending up with divergent states.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Real-time Collaboration**: Multiple users can edit a document simultaneously and see changes in near real-time.
- **Consistency**: All users must eventually see the same document state (Convergence).
- **Persistence**: Documents must be saved and retrievable.
- **Presence**: Users should see who else is active in the document and where their cursors are.
- **Version History**: Ability to view and revert to previous versions of the document.

### Non-Functional Requirements
- **Low Latency**: Local edits must be instantaneous (optimistic updates), and remote edits must appear within milliseconds.
- **High Availability**: The system must be available even if individual nodes fail.
- **Scalability**: Must support millions of documents and thousands of concurrent users per document.
- **Durability**: Once an edit is acknowledged, it must never be lost.

### Scale Assumptions
- **Daily Active Users (DAU)**: 100 Million.
- **Concurrent Users per Document**: Typically 1–10, peak up to 100.
- **Average Document Size**: 100 KB to 10 MB.
- **Write Throughput**: High (every keystroke is potentially an operation).

---

## 2. High-Level System Architecture

The system follows a **Client-Server architecture** utilizing **WebSockets** for bi-directional, low-latency communication.

### Architecture Diagram Components
1.  **Client (Browser/App)**: Maintains a local copy of the document and a local operation log. Performs optimistic UI updates.
2.  **Load Balancer**: Distributes WebSocket connections across multiple Collaboration Servers.
3.  **Collaboration Server (The Sequencer)**: The "brain" of the operation. It handles conflict resolution, assigns sequence numbers to operations, and broadcasts updates to other clients.
4.  **Presence Service**: A low-latency key-value store (Redis) to track active users and cursor positions.
5.  **Document Store**: A NoSQL database (e.g., MongoDB or DynamoDB) to store the current snapshot of the document.
6.  **Operation Log Store**: An append-only immutable store (e.g., Cassandra) that stores every single operation performed on a document for versioning and recovery.

---

## 3. Key HLD Concepts & Component Design

### A. Conflict Resolution: OT vs. CRDT
This is the core technical challenge. There are two primary industry standards for resolving concurrent edits:

#### 1. Operational Transformation (OT) - *Used by Google Docs*
OT relies on a central server to sequence operations. When a client sends an operation, the server transforms it against any operations that happened concurrently before broadcasting it.

- **Mechanism**: If User A inserts 'X' at index 5 and User B inserts 'Y' at index 5 simultaneously, the server transforms User B's operation to insert 'Y' at index 6.
- **Pros**: Compact data representation (only stores the change).
- **Cons**: Requires a central server; complex to implement for all possible operation types.

#### 2. Conflict-free Replicated Data Types (CRDTs) - *Used by Figma/Apple Notes*
CRDTs use mathematically unique identifiers for every character/element. Operations are commutative, meaning they can be applied in any order and result in the same state.

- **Mechanism**: Instead of saying "Insert at index 5," it says "Insert character 'X' with ID `user1_seq10` between `ID_A` and `ID_B`."
- **Pros**: Decentralized (Peer-to-Peer capable), no need for a central sequencer.
- **Cons**: High memory overhead (metadata for every single character).

**Decision for Google Docs**: Use **OT** because it offers better memory efficiency for text-heavy documents and allows for a central source of truth for versioning.

### B. Component Selection
| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Communication** | WebSockets | Bi-directional, full-duplex communication is required for real-time "push" updates. |
| **Presence** | Redis | Extremely low latency; cursor data is ephemeral and doesn't need permanent storage. |
| **Doc Store** | MongoDB/DynamoDB | Documents are naturally hierarchical (JSON-like). Flexible schema allows for metadata growth. |
| **Op Log** | Cassandra | High write throughput; optimized for append-only time-series data (ideal for version history). |

---

## 4. Data Flows & Fault Tolerance

### Write Path (The OT Workflow)
1. **Local Edit**: User A types 'H' at position 0. The client updates the UI immediately (**Optimistic Update**) and sends the operation `Insert(char='H', pos=0, version=1)` to the server via WebSocket.
2. **Server Processing**:
   - Server receives the op.
   - Server checks the version. If the server is already at version 5, it means User A is lagging.
   - Server **Transforms** `Insert(pos=0)` against the operations in the log between version 1 and 5.
   - Server updates the document state and appends the transformed operation to the **Operation Log**.
3. **Broadcast**: Server sends the transformed operation `Insert(char='H', pos=X, version=6)` to all other connected clients.
4. **Remote Apply**: User B's client receives the operation and applies it to their local copy.

### Presence Update Path
1. Client sends `CursorMove(x, y)` every 100-200ms.
2. Server updates Redis: `SET doc_123_user_A "x:10,y:20" EX 30`.
3. Server broadcasts the coordinates to other users in the same document "room."

### Fault Tolerance & Reliability
- **Server Crash**: Since the state is backed by the Operation Log (Cassandra) and Snapshots (MongoDB), a new server can reconstruct the document state by loading the last snapshot and replaying subsequent operations.
- **Network Partition (Client)**: If a client goes offline, it buffers local operations. Upon reconnection, it sends the buffer and performs a "catch-up" sync using the OT transformation logic.
- **Load Balancing**: Use **Sticky Sessions** (consistent hashing based on `DocumentID`) to ensure all users editing the same document are connected to the same Collaboration Server. This simplifies OT sequencing.

---

## 5. Production Trade-offs

### CAP Theorem: Consistency vs. Availability
Google Docs chooses **Eventual Consistency** (specifically *Strong Eventual Consistency*). 
- It prioritizes **Availability** and **Partition Tolerance** (AP). Users must be able to type even if the network is spotty. 
- The OT algorithm ensures that once all operations are propagated, all clients converge to the exact same state.

### Latency vs. Accuracy
- **Optimistic Updates**: The system updates the UI before the server acknowledges the write. This reduces perceived latency to $0\text{ms}$, but risks a "jump" in the cursor if the server transforms the operation significantly.

### Complexity Analysis
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Local Edit** | $O(1)$ | $O(1)$ | Immediate UI update. |
| **OT Transformation** | $O(N)$ | $O(1)$ | $N$ is the number of concurrent operations to transform against. |
| **Doc Load** | $O(S)$ | $O(S)$ | $S$ is the size of the document snapshot. |
| **Presence Update** | $O(1)$ | $O(U)$ | $U$ is the number of active users per document. |

### Summary Table: OT vs. CRDT
| Feature | Operational Transformation (OT) | CRDT |
| :--- | :--- | :--- |
| **Central Server** | Required | Optional (P2P possible) |
| **Complexity** | High (Transformation logic) | High (Data structure design) |
| **Memory** | Low (Stores only changes) | High (Stores metadata per char) |
| **Convergence** | Guaranteed by Sequencer | Guaranteed by Math/Commutativity |
| **Best Use Case** | Text Editors (Google Docs) | Collaborative Whiteboards (Figma) |
INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Collaborative Document Editor (like Google Docs).',
    'groups': ['OOP Case Studies', 'Concurrency'],
    'readme_content': """# Collaborative Editor LLD

A **Collaborative Editor** is a complex distributed system where multiple users can edit a shared document simultaneously. The primary challenge is maintaining **Consistency** (all users see the same content) and **Convergence** (all users eventually arrive at the same state) despite network latency and concurrent edits.

---

## 1. Overview & System Requirements

### Core Goal
Design a system that allows multiple clients to perform insertions and deletions on a shared string, ensuring that the final state is identical across all clients regardless of the order in which operations were received.

### Functional Requirements
- **Real-time Editing**: Users can insert or delete characters at specific indices.
- **Concurrency Control**: Handle simultaneous edits from multiple users without data loss or corruption.
- **Synchronization**: The server must synchronize state across all connected clients.
- **Version Tracking**: Maintain a version history to determine which operations need transformation.

### Non-Functional Requirements
- **Low Latency**: Local edits must be reflected immediately (Optimistic UI).
- **Consistency**: Eventual consistency is mandatory.
- **Scalability**: Ability to handle multiple documents and multiple users per document.

---

## 2. Design Principles & Patterns

### Design Patterns Applied
- **Command Pattern**: Every edit (Insert/Delete) is encapsulated as an `Operation` object. This allows operations to be queued, sent over the network, and transformed.
- **Observer Pattern**: The `CollaborativeServer` acts as the subject, and `Clients` act as observers. When the server processes a transformed operation, it notifies all other clients.
- **Strategy Pattern**: Used to implement the **Transformation Engine**. Different conflict resolution strategies (e.g., Operational Transformation vs. CRDT) can be swapped.
- **Singleton Pattern**: The `DocumentManager` is typically a singleton to ensure a single point of truth for all active documents on a server.

### OOP Principles (SOLID)
- **Single Responsibility (SRP)**: The `Document` class manages state, the `OTEngine` handles the math of index shifting, and the `Server` handles communication.
- **Open/Closed Principle**: The system is open for new operation types (e.g., `FormatOperation` for bold/italic) without modifying the core `TransformationEngine` logic.
- **Interface Segregation**: Clients interact with a simplified `EditorInterface` rather than the complex internal server logic.

---

## 3. Class Structure & Relationships

### Class Diagram (Textual)

```mermaid
classDiagram
    class Operation {
        +String type
        +int position
        +char character
        +int version
        +String userId
    }
    class InsertOp { }
    class DeleteOp { }
    Operation <|-- InsertOp
    Operation <|-- DeleteOp

    class OTEngine {
        +transform(opA, opB) Operation
    }

    class Document {
        -StringBuilder content
        -int version
        +apply(Operation op)
    }

    class CollaborativeServer {
        -Map<DocId, Document> documents
        -Map<DocId, List<Operation>> history
        -OTEngine otEngine
        +receiveOperation(Operation op)
        +broadcast(Operation op)
    }

    class Client {
        -Document localDoc
        -List<Operation> pendingOps
        +onRemoteOpReceived(Operation op)
        +sendLocalOp(Operation op)
    }

    CollaborativeServer "1" --> "many" Document
    CollaborativeServer "1" --> "1" OTEngine
    Client "many" --> "1" CollaborativeServer
    Document "1" --> "many" Operation : applies
```

### Key Entities
| Entity | Responsibility |
| :--- | :--- |
| **Operation** | Represents a change (Insert/Delete) with metadata (position, char, version). |
| **OTEngine** | The "Brain." Adjusts the index of an operation based on a concurrent operation. |
| **Document** | Maintains the current text state and the current version number. |
| **Server** | The central authority that sequences operations and manages the global history. |
| **Client** | Maintains a local copy of the document and handles optimistic updates. |

---

## 4. Step-by-Step Logic & Code Walkthrough

### The Operational Transformation (OT) Logic
The heart of this design is the `transform` function. If User A and User B both edit at the same time:
1. User A inserts 'X' at index 5.
2. User B inserts 'Y' at index 2.
3. If the server processes A first, when it sends A's operation to User B, User B must shift their own pending operation (at index 2) if A's edit happened *before* their index.

**Transformation Rule:**
- If `Op A` is an insertion at `posA` and `Op B` is an insertion at `posB`:
    - If `posA < posB`, `Op B`'s position becomes `posB + 1`.
    - If `posA > posB`, `Op B`'s position remains `posB`.

### Implementation

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Operation:
    type: str  # "INSERT" or "DELETE"
    position: int
    char: Optional[str] = None
    version: int = 0
    user_id: str = ""

class OTEngine:
    \"\"\"Operational Transformation Engine to resolve conflicts.\"\"\"
    @staticmethod
    def transform(op_to_transform: Operation, concurrent_op: Operation) -> Operation:
        new_pos = op_to_transform.position
        
        if concurrent_op.type == "INSERT":
            # If someone inserted a character before us, shift our index right
            if concurrent_op.position <= op_to_transform.position:
                new_pos += 1
        elif concurrent_op.type == "DELETE":
            # If someone deleted a character before us, shift our index left
            if concurrent_op.position < op_to_transform.position:
                new_pos -= 1
                
        return Operation(
            type=op_to_transform.type,
            position=new_pos,
            char=op_to_transform.char,
            version=op_to_transform.version + 1,
            user_id=op_to_transform.user_id
        )

class Document:
    def __init__(self):
        self.content = []
        self.version = 0

    def apply(self, op: Operation):
        if op.type == "INSERT":
            self.content.insert(op.position, op.char)
        elif op.type == "DELETE":
            if 0 <= op.position < len(self.content):
                self.content.pop(op.position)
        self.version += 1

    def get_text(self):
        return "".join(self.content)

class CollaborativeServer:
    def __init__(self):
        self.doc = Document()
        self.history: List[Operation] = []
        self.ot_engine = OTEngine()

    def handle_operation(self, incoming_op: Operation) -> Operation:
        # 1. Find all operations that happened since the version the client had
        concurrent_ops = self.history[incoming_op.version:]
        
        # 2. Transform the incoming operation against all concurrent operations
        transformed_op = incoming_op
        for op in concurrent_ops:
            transformed_op = self.ot_engine.transform(transformed_op, op)
        
        # 3. Apply to the server's master document
        self.doc.apply(transformed_op)
        
        # 4. Add to history and return for broadcasting
        self.history.append(transformed_op)
        return transformed_op

# --- Execution Example ---
if __name__ == "__main__":
    server = CollaborativeServer()
    
    # Initial state: "Hello"
    for i, char in enumerate("Hello"):
        server.handle_operation(Operation("INSERT", i, char))
    
    print(f"Initial: {server.doc.get_text()}") # Hello

    # User A wants to insert '!' at the end (pos 5), version is 5
    op_a = Operation("INSERT", 5, "!", version=5, user_id="UserA")
    
    # User B wants to insert ' ' at pos 5 (before the '!'), version is 5
    op_b = Operation("INSERT", 5, " ", version=5, user_id="UserB")

    # Server processes A then B
    res_a = server.handle_operation(op_a)
    res_b = server.handle_operation(op_b)

    print(f"Final State: '{server.doc.get_text()}'") 
    # Expected: "Hello !" (User B's space was transformed to pos 5, '!' shifted to 6)
```

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Local Edit** | $O(1)$ | $O(1)$ | Immediate update to local buffer. |
| **Transformation** | $O(H)$ | $O(1)$ | $H$ is the number of concurrent operations in history since the client's version. |
| **Applying Op** | $O(N)$ | $O(1)$ | Array insertion/deletion in a string of length $N$. |
| **Server Memory** | $O(Ops)$ | $O(Ops)$ | Server must store history of all operations to transform lagging clients. |

---

## 6. Real-World Applications & Extensions

### Production Implementation
In a production-grade system like **Google Docs**, raw OT is often replaced or augmented by:
1. **CRDTs (Conflict-free Replicated Data Types)**: Instead of transforming indices, every character is assigned a unique, fractional, immutable ID (e.g., `LSEQ` or `Yjs`). This eliminates the need for a central server to sequence operations.
2. **WebSockets**: For full-duplex, low-latency communication between clients and servers.
3. **Snapshotting**: To prevent the `history` list from growing infinitely, the server takes periodic snapshots of the document and prunes old history.

### Comparison: OT vs CRDT

| Feature | Operational Transformation (OT) | CRDT |
| :--- | :--- | :--- |
| **Control** | Centralized (Requires Server) | Decentralized (Peer-to-Peer possible) |
| **Complexity** | High (Edge cases in transformation) | Medium (Metadata overhead) |
| **Performance** | Low metadata per op | High metadata (Unique IDs for every char) |
| **Convergence** | Guaranteed by server sequencing | Mathematically guaranteed by data structure |""",
    'solutions': """# System Design: Collaborative Document Editor

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Real-time Collaborative Editing:** Multiple users must be able to edit the same document simultaneously with near-instant synchronization.
*   **Concurrency Control:** The system must resolve conflicts when two users edit the same character or block of text.
*   **Presence Indicators:** Users should see who else is currently editing the document and the real-time position of their cursors.
*   **Persistence & Versioning:** Documents must be saved automatically. Users should be able to view and revert to previous versions of the document.
*   **Permissions & Access Control:** Support for private documents, shared documents, and role-based access (Viewer, Editor, Owner).
*   **Offline Mode:** Users should be able to edit offline and sync changes upon reconnection.

### 1.2 Non-Functional Requirements
*   **Low Latency:** The "keystroke-to-screen" latency should be minimal (< 100ms) to ensure a fluid user experience.
*   **High Availability:** The system must be available 24/7; a failure in one region should not bring down the entire service.
*   **Strong Eventual Consistency:** All clients must converge to the same state after all operations are processed.
*   **Scalability:** Support millions of concurrent documents and thousands of concurrent users per document.

### 1.3 Scale Estimations
*   **Daily Active Users (DAU):** 10 Million.
*   **Average Document Size:** 50 KB.
*   **Concurrent Users per Document:** Average 2, Peak 100.
*   **Write Throughput:** Assuming a user types 2 characters per second, 1M concurrent users $\approx$ 2M operations per second.
*   **Storage:** 10M users $\times$ 10 docs/user $\times$ 50 KB $\approx$ 5 TB for current state. Version history will increase this significantly.

---

## 2. High-Level Architecture

The system utilizes a **Centralized Operational Transformation (OT)** approach. While CRDTs (Conflict-free Replicated Data Types) are an alternative, OT is preferred for a centralized server model to ensure a canonical history and easier snapshotting.

### 2.1 Core Components
1.  **Client Application:** Maintains a local copy of the document, a local buffer of pending operations, and handles the transformation of incoming server operations.
2.  **Load Balancer:** Distributes WebSocket and HTTP traffic.
3.  **WebSocket Gateway (Connection Manager):** Maintains persistent bidirectional connections with clients for real-time updates and cursor movements.
4.  **OT Engine (Operation Service):** The heart of the system. It sequences operations, transforms them against concurrent operations, and updates the document version.
5.  **Document Service:** Manages document metadata, ownership, and sharing permissions.
6.  **Snapshot Service:** Periodically collapses the operation log into a full document state to speed up initial loading.
7.  **Pub/Sub (Redis):** Coordinates updates between multiple WebSocket server instances.

### 2.2 Architecture Diagram (Text-based)

```mermaid
graph TD
    UserA[Client A] <--> LB[Load Balancer]
    UserB[Client B] <--> LB
    LB <--> WS[WebSocket Gateway]
    WS <--> Redis[(Redis Pub/Sub)]
    WS <--> OT[OT Engine / Sync Service]
    OT <--> OpStore[(Operations Log - NoSQL)]
    OT <--> SnapStore[(Snapshot Store - S3/NoSQL)]
    OT <--> DocSvc[Document Metadata Service]
    DocSvc <--> MetaDB[(Metadata DB - SQL)]
```

### 2.3 Sequence Flow for an Edit
1.  **Client A** performs an edit (Insert 'X' at index 5).
2.  **Client A** applies the edit locally (optimistic update) and sends the operation `Op(type: insert, char: 'X', pos: 5, version: 10)` to the server.
3.  **OT Engine** receives the operation. If the server is already at version 12, it transforms Client A's operation against the operations that happened between version 10 and 12.
4.  **OT Engine** commits the transformed operation to the **Operations Log** and increments the version to 13.
5.  **OT Engine** publishes the transformed operation to **Redis**.
6.  **WebSocket Gateway** picks up the event and broadcasts `Op(type: insert, char: 'X', pos: 6, version: 13)` to **Client B**.
7.  **Client B** transforms the incoming operation against its own pending local edits and updates the UI.

---

## 3. Detailed Database Schema Design

### 3.1 Metadata Store (Relational - PostgreSQL)
Used for structured data requiring ACID compliance (Permissions, User profiles).

**Table: `users`**
*   `user_id` (UUID, PK)
*   `email` (String, Unique)
*   `display_name` (String)

**Table: `documents`**
*   `doc_id` (UUID, PK)
*   `owner_id` (UUID, FK -> users.user_id)
*   `title` (String)
*   `created_at` (Timestamp)
*   `last_modified` (Timestamp)

**Table: `permissions`**
*   `permission_id` (UUID, PK)
*   `doc_id` (UUID, FK -> documents.doc_id)
*   `user_id` (UUID, FK -> users.user_id)
*   `role` (Enum: VIEWER, EDITOR, OWNER)
*   *Index: (doc_id, user_id)*

### 3.2 Operations Log (NoSQL - Cassandra/DynamoDB)
We need high write throughput and the ability to fetch operations in a range for a specific document.

**Table: `operations`**
*   `doc_id` (Partition Key)
*   `version` (Sort Key / Clustering Key)
*   `user_id` (UUID)
*   `operation_data` (JSON: `{type: 'insert'|'delete', pos: Int, char: String}`)
*   `timestamp` (Timestamp)

*Reasoning:* NoSQL is used because the operation log grows linearly and is append-only. Cassandra provides the necessary write scale and efficient range queries by `version`.

### 3.3 Snapshot Store (Blob Store / Document DB)
Storing every single operation since the dawn of the document is inefficient for loading.

**Table: `snapshots`**
*   `snapshot_id` (UUID, PK)
*   `doc_id` (UUID, Index)
*   `version` (Int)
*   `content` (Text/Blob)
*   `timestamp` (Timestamp)

---

## 4. Core API Design

### 4.1 REST APIs (Document Management)
| Endpoint | Method | Payload | Description |
| :--- | :--- | :--- | :--- |
| `/v1/docs` | POST | `{title: string}` | Create a new document. |
| `/v1/docs/{id}` | GET | N/A | Fetch metadata and latest snapshot. |
| `/v1/docs/{id}/share` | POST | `{user_id: uuid, role: string}` | Share document with user. |

**Request Payload (`POST /v1/docs`):**
```json
{
  "title": "System Design Specs"
}
```

**Response Payload (`GET /v1/docs/{id}`):**
```json
{
  "doc_id": "uuid-123",
  "title": "System Design Specs",
  "content": "Hello World...",
  "version": 154,
  "permissions": "EDITOR"
}
```

### 4.2 WebSocket Events (Real-time Editing)
**Client $\rightarrow$ Server: `send_operation`**
```json
{
  "type": "EDIT",
  "doc_id": "uuid-123",
  "op": { "type": "insert", "pos": 12, "char": "a" },
  "version": 154
}
```

**Server $\rightarrow$ Client: `broadcast_operation`**
```json
{
  "type": "UPDATE",
  "op": { "type": "insert", "pos": 13, "char": "a" },
  "version": 155,
  "user_id": "uuid-456"
}
```

**Client $\rightarrow$ Server: `cursor_move`**
```json
{
  "type": "CURSOR",
  "doc_id": "uuid-123",
  "pos": 42
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Scaling the OT Engine
*   **Document Sharding:** Since operations for `Doc A` are independent of `Doc B`, we shard by `doc_id`.
*   **Sticky Sessions/Routing:** Use a consistent hashing mechanism at the Load Balancer or a Routing Layer to ensure all users editing the same document are connected to the same OT Engine instance. This avoids complex distributed locking.
*   **Redis Pub/Sub:** If a document's users are spread across multiple WebSocket servers, Redis acts as the message bus to synchronize the servers.

### 5.2 Caching Strategy
*   **L1 Cache (Client):** Local buffer for optimistic UI updates.
*   **L2 Cache (Server):** Redis stores the current "Active State" of the document (the last 100 operations and the latest snapshot) to avoid hitting the database for every keystroke.

### 5.3 Handling Offline Edits
*   The client maintains a **Pending Queue** of operations.
*   When the connection is restored, the client sends all pending operations.
*   The server transforms these operations against all versions that occurred during the offline period. If the gap is too large, the server may force a full document reload (snapshot) to the client.

### 5.4 Presence & Cursor Tracking
*   Cursor positions are transient and don't need to be persisted in the DB.
*   Use an in-memory store (Redis) with a short TTL (e.g., 30 seconds) to track `user_id -> {doc_id, cursor_pos}`.
*   Heartbeats are sent every few seconds to keep the presence alive.

---

## 6. Trade-off Analysis

### 6.1 OT vs. CRDT
| Feature | Operational Transformation (OT) | Conflict-free Replicated Data Types (CRDT) |
| :--- | :--- | :--- |
| **Complexity** | Complex server-side logic. | Complex data structure logic. |
| **State** | Requires a central server to sequence. | Decentralized; works peer-to-peer. |
| **Overhead** | Low storage overhead (just the op). | High overhead (each char has a unique ID). |
| **Consistency** | Strong Eventual Consistency. | Strong Eventual Consistency. |
*   **Decision:** OT is chosen for this design to maintain a canonical version history and lower memory overhead on the client.

### 6.2 CAP Theorem Priorities
*   **Availability vs. Consistency:** In a collaborative editor, **Availability** and **Partition Tolerance** are prioritized (AP). We cannot block a user's typing just because the server is lagging.
*   **Consistency Model:** We use **Eventual Consistency**. Every client might see slightly different states for a few milliseconds, but the OT algorithm ensures they all converge to the same final state.

### 6.3 Latency vs. Storage
*   We trade storage for latency by implementing **Snapshots**. Instead of replaying 10,000 operations to load a document, we load the latest snapshot and replay only the operations that occurred after that snapshot. This increases storage costs but drastically reduces initial load time.""",
}

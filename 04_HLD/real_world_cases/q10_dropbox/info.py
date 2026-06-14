INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Dropbox / Google Drive - File storage/sync.',
    'groups': ['Real-World Systems', 'Caching & Storage'],
    'readme_content': """# Dropbox / Google Drive HLD

This study guide provides a deep dive into the architecture of a cloud-based file synchronization and storage service. Designing a system like Dropbox requires a sophisticated balance between **data durability**, **efficient bandwidth usage**, and **strong consistency** for metadata.

---

## 1. Overview & System Requirements

The goal is to build a system that allows users to upload files from one device and have them automatically synchronized across all other linked devices.

### Functional Requirements
- **File Upload/Download**: Users can upload files and download them to any device.
- **File Synchronization**: Changes made to a file on one device must be reflected across all other devices.
- **Versioning**: Ability to track changes and revert to previous versions of a file.
- **Sharing/Permissions**: Users can share folders/files with other users with specific access levels (Read/Write).
- **Offline Support**: Users can modify files offline; the system syncs changes once the connection is restored.

### Non-Functional Requirements
- **High Durability**: Files must not be lost. Target: 99.999999999% (11 nines) durability.
- **High Availability**: The service should be available globally with minimal downtime.
- **Scalability**: Support hundreds of millions of users and exabytes of data.
- **Efficiency (Bandwidth)**: Avoid re-uploading the entire file if only a small part changes (**Delta Sync**).
- **Consistency**: Metadata (file names, folder structure) must be consistent across devices.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million |
| **Avg. File Size** | 500 KB to 10 MB |
| **Read/Write Ratio** | 1:1 (Frequent syncs and reads) |
| **Total Storage** | $\text{100M users} \times \text{10GB avg} \approx 1 \text{ Exabyte}$ |
| **QPS (Metadata)** | Very high (Heartbeats, polling, metadata updates) |

---

## 2. High-Level System Architecture

The architecture is split into the **Client-side** (the agent installed on the OS) and the **Server-side** (the cloud infrastructure).

### System Component Diagram (Logical Flow)
`Client Agent` $\rightarrow$ `Load Balancer` $\rightarrow$ `API Gateway` $\rightarrow$ `Metadata Service` $\rightarrow$ `DB`
`Client Agent` $\rightarrow$ `Block Service` $\rightarrow$ `Object Storage (S3)`
`Metadata Service` $\rightarrow$ `Notification Service` $\rightarrow$ `Client Agent (WebSockets)`

### Component Roles
1.  **Client Agent**: 
    *   **Watcher**: Monitors local folder changes using OS events (e.g., `inotify` on Linux, `FSEvents` on macOS).
    *   **Chunker**: Splits files into smaller blocks to optimize uploads.
    *   **Indexer**: Maintains a local DB of file hashes to determine what needs syncing.
2.  **Load Balancer**: Distributes traffic across multiple API servers.
3.  **Metadata Service**: Manages file names, versions, user permissions, and the mapping of files to blocks.
4.  **Block Service**: Handles the actual uploading and downloading of data chunks.
5.  **Object Store (S3/GCS)**: The source of truth for the actual file content.
6.  **Notification Service**: Uses WebSockets or Long Polling to notify clients of remote changes instantly.
7.  **Message Queue (Kafka)**: Asynchronously handles tasks like updating search indices or generating thumbnails.

---

## 3. Key HLD Concepts & Component Design

### A. Efficient Data Transfer: Chunking & Delta Sync
Uploading a 1GB file every time a single sentence is changed is inefficient.
- **Fixed-size Chunking**: Simple, but if a byte is inserted at the beginning, all subsequent chunk boundaries shift, forcing a full re-upload.
- **Content-Defined Chunking (CDC)**: Uses a sliding window (e.g., **Rabin Fingerprinting**) to find boundaries based on content. If a byte is inserted, only the affected chunk and its neighbor change; the rest of the hashes remain identical.
- **Deduplication**: Before uploading a chunk, the client sends the hash (SHA-256). If the server already has that hash (globally or per user), the client skips the upload.

### B. Metadata Management
Metadata is small but frequently accessed and updated.
- **Database Choice**: **Relational Database (Postgres/MySQL)**.
    *   **Why?** We need **ACID** transactions to ensure that moving a file from `Folder A` to `Folder B` is atomic.
- **Schema**:
    *   `User`: `user_id, email, password_hash`
    *   `File`: `file_id, name, parent_folder_id, is_directory, latest_version`
    *   `FileVersion`: `version_id, file_id, size, checksum`
    *   `Block`: `block_id, block_hash, storage_path`
    *   `FileVersion_Block`: Mapping table linking a specific version to its ordered list of blocks.

### C. Storage Layer
- **Object Store**: Actual data chunks are stored in an Object Store (like Amazon S3). Object stores are designed for massive scale and high durability.
- **Cold Storage**: Older versions of files can be moved to cheaper "Glacier" storage to reduce costs.

### D. Notification Mechanism
To avoid clients polling the server every second:
- **WebSockets**: Maintains a persistent connection between the client and the Notification Service. When the Metadata Service updates a file, it pushes an event to the Notification Service, which alerts the relevant clients to "pull" the updates.

---

## 4. Data Flows & Fault Tolerance

### Write Path (Uploading a modified file)
1.  **Local Change**: The `Watcher` detects a file change.
2.  **Chunking**: The `Chunker` splits the file into blocks using CDC.
3.  **Hashing**: Client calculates SHA-256 hashes for each block.
4.  **Existence Check**: Client sends hashes to the `Block Service`. The server responds: *"I already have blocks 1, 2, and 4; please send block 3."*
5.  **Upload**: Client uploads only the missing block(s) to the `Block Service` $\rightarrow$ `Object Store`.
6.  **Metadata Update**: Client updates the `Metadata Service` with the new file version and the ordered list of block IDs.
7.  **Broadcast**: `Metadata Service` triggers the `Notification Service` to notify other devices belonging to that user.

### Read Path (Syncing to a new device)
1.  **Sync Request**: Client requests the latest file tree for the user.
2.  **Metadata Fetch**: Server returns the file structure and the block hashes for the latest versions.
3.  **Local Comparison**: Client compares server hashes with local hashes.
4.  **Block Download**: Client downloads only the missing blocks from the `Block Service`.
5.  **Reconstruction**: Client assembles blocks into the final file.

### Fault Tolerance & Reliability
- **Data Durability**: S3 replicates data across multiple availability zones (AZs).
- **Metadata Availability**: Use a Primary-Replica setup for the SQL DB with automated failover.
- **Retry Logic**: Clients implement **exponential backoff** when uploading blocks to handle transient network failures.
- **Integrity Checks**: The client verifies the SHA-256 hash of the downloaded file against the metadata to ensure no corruption occurred.

---

## 5. Production Trade-offs

### CAP Theorem: Consistency vs. Availability
In Dropbox, **Consistency is prioritized for Metadata**, and **Availability is prioritized for Data Access**.
- If the metadata DB is down, we cannot update files (CP), because allowing conflicting updates to the same file across devices leads to complex "conflict files" (e.g., `document_conflict_copy.txt`).
- However, once a file is uploaded, it should be available for download from any edge location (AP).

### Global vs. Per-User Deduplication
| Type | Pros | Cons |
| :--- | :--- | :--- |
| **Per-User** | Simple, high privacy, easier to delete data. | Uses more storage (same file uploaded by 10 users $\rightarrow$ 10 copies). |
| **Global** | Massive storage savings (1 million users sharing one viral PDF $\rightarrow$ 1 copy). | Complex permission logic, potential security risks (side-channel attacks to see if a file exists). |

### Complexity Analysis
| Operation | Time Complexity (Client) | Time Complexity (Server) | Network Complexity |
| :--- | :--- | :--- | :--- |
| **Upload (Full)** | $O(\text{File Size})$ | $O(1)$ per block | $O(\text{File Size})$ |
| **Upload (Delta)** | $O(\text{Changed Size})$ | $O(1)$ per block | $O(\text{Changed Size})$ |
| **Metadata Query**| $O(1)$ | $O(\log N)$ where $N = \text{Files}$ | $O(\text{Metadata Size})$ |
| **Sync Check** | $O(\text{Num Blocks})$ | $O(1)$ | $O(\text{Num Hashes})$ |""",
    'solutions': """# System Design: Dropbox/Google Drive (File Storage & Synchronization)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **File Upload/Download:** Users should be able to upload and download files from any device.
*   **File Synchronization:** Changes made to a file on one device must be reflected across all other devices linked to the same account.
*   **Versioning:** Users should be able to view and restore previous versions of a file.
*   **Offline Support:** Users can modify files offline; changes sync once the connection is restored.
*   **Sharing:** Ability to share files/folders with other users with specific permissions (Read-only, Read/Write).
*   **Folder Hierarchy:** Support for nested folders and directory structures.

### 1.2 Non-Functional Requirements
*   **High Durability:** Data must not be lost. 99.999999999% (11 nines) durability is the gold standard.
*   **High Availability:** The system should be available for access and synchronization at all times.
*   **Strong Consistency (Metadata):** A user should not see an old version of a file after a successful update.
*   **Efficiency (Bandwidth):** Use "Delta Sync" to upload only the modified parts of a file rather than the entire file.
*   **Scalability:** Support millions of concurrent users and petabytes of stored data.

### 1.3 Scale Estimations
*   **Users:** 100 Million total users; 10 Million Daily Active Users (DAU).
*   **Storage:** Average user stores 10GB $\rightarrow$ 1 Exabyte total storage.
*   **Traffic:** High read/write ratio for metadata, bursty write traffic for large file uploads.
*   **File Size:** Range from a few bytes to several gigabytes.

---

## 2. High-Level Architecture

### 2.1 Core Design Concept: Chunking
To optimize synchronization and handle large files, files are split into smaller **chunks** (e.g., 4MB). 
*   **Delta Sync:** If only one part of a 1GB file changes, only the affected chunks are uploaded.
*   **Deduplication:** If two users upload the same file (same hash), the system stores only one copy of the blocks.

### 2.2 Architecture Diagram

```mermaid
graph TD
    Client[Client App/Daemon] --> LB[Load Balancer]
    LB --> Gateway[API Gateway / Auth]
    
    Gateway --> MetaSvc[Metadata Service]
    Gateway --> BlockSvc[Block Service]
    
    MetaSvc --> MetaDB[(Metadata DB - SQL)]
    MetaSvc --> Cache[(Redis Cache)]
    
    BlockSvc --> ObjectStore[Object Storage - S3/Azure Blob]
    BlockSvc --> BlockDB[(Block Index DB - NoSQL)]
    
    Client --> NotifSvc[Notification Service - WebSockets]
    MetaSvc --> NotifSvc
    
    NotifSvc --> Client
```

### 2.3 Component Interactions
1.  **Client App:** Monitors local folder changes (using `inotify` on Linux or `FSEvents` on macOS). It breaks files into chunks, hashes them, and communicates with the server.
2.  **Metadata Service:** Manages file names, folder structures, permissions, and version history.
3.  **Block Service:** Handles the uploading and downloading of raw binary chunks. It interacts with the Object Store.
4.  **Object Store:** A highly durable distributed storage system (like AWS S3) that stores the actual binary chunks.
5.  **Notification Service:** Uses WebSockets or Long Polling to push updates to other connected devices when a file changes.

---

## 3. Detailed Database Schema Design

### 3.1 Metadata Database (Relational - PostgreSQL)
We use a SQL database for metadata because we require ACID properties for file moves, renames, and permission updates to ensure consistency.

**Table: `Users`**
*   `user_id` (UUID, PK)
*   `username` (VARCHAR, Unique)
*   `email` (VARCHAR, Unique)
*   `created_at` (Timestamp)

**Table: `Files`**
*   `file_id` (UUID, PK)
*   `parent_folder_id` (UUID, FK) - References `Folders.folder_id`
*   `name` (VARCHAR)
*   `is_directory` (Boolean)
*   `current_version` (Integer)
*   `owner_id` (UUID, FK)
*   `created_at` (Timestamp)
*   `updated_at` (Timestamp)
*   *Index:* `(owner_id, parent_folder_id)` for fast directory listing.

**Table: `FileVersions`**
*   `version_id` (UUID, PK)
*   `file_id` (UUID, FK)
*   `version_number` (Integer)
*   `created_at` (Timestamp)
*   `checksum` (VARCHAR) - Root hash of the file version.

**Table: `FileVersionBlocks`**
*   `version_id` (UUID, FK)
*   `block_id` (VARCHAR, FK) - Hash of the block.
*   `block_order` (Integer) - Position of block in the file.
*   *PK:* `(version_id, block_order)`

### 3.2 Block Index (NoSQL - Cassandra/DynamoDB)
The Block Index maps a block's hash to its physical location in the Object Store. Since this is a simple Key-Value lookup with massive scale, NoSQL is preferred.

**Table: `Blocks`**
*   `block_hash` (VARCHAR, PK) - SHA-256 hash of content.
*   `storage_path` (VARCHAR) - Path in S3 (e.g., `s3://bucket/hash_prefix/block_hash`).
*   `size` (Integer)
*   `ref_count` (Integer) - Number of files using this block (for garbage collection).

---

## 4. Core API Design

### 4.1 File Upload Flow
The upload is a multi-step process to ensure reliability.

**Step 1: Initiate Upload**
`POST /api/v1/files/upload/init`
*   **Request:** `{ "file_name": "doc.pdf", "parent_id": "folder_123", "total_size": 10485760, "total_chunks": 3 }`
*   **Response:** `{ "upload_session_id": "sess_abc123", "file_id": "file_xyz" }`

**Step 2: Upload Chunks**
`POST /api/v1/files/upload/block`
*   **Request:** `Multipart form: { "session_id": "sess_abc123", "block_index": 0, "block_hash": "sha256_abc", "data": <binary> }`
*   **Response:** `{ "status": "success", "block_id": "sha256_abc" }` (Server checks if block already exists in `Blocks` table to avoid redundant storage).

**Step 3: Commit Upload**
`POST /api/v1/files/upload/commit`
*   **Request:** `{ "session_id": "sess_abc123", "block_hashes": ["sha256_abc", "sha256_def", "sha256_ghi"] }`
*   **Response:** `{ "status": "committed", "version": 1 }`

### 4.2 Other Endpoints
*   `GET /api/v1/files?parent_id={id}`: Lists files in a directory.
*   `GET /api/v1/files/download/{file_id}?version={v}`: Returns a signed URL to download the file or a stream of blocks.
*   `PATCH /api/v1/files/{file_id}`: Update metadata (rename, move).

---

## 5. Scalability & Advanced Topics

### 5.1 Deduplication Strategy
*   **Content-Addressable Storage:** By using the SHA-256 hash of the block as its ID, the system automatically implements "cross-user deduplication." If two different users upload the same 4MB chunk, only one instance is stored in the Object Store.

### 5.2 Sync Mechanism & Notification
To achieve real-time sync across devices:
1.  **Client Side:** The client maintains a local SQLite DB of file hashes.
2.  **Update Flow:** Client $\rightarrow$ Server $\rightarrow$ Metadata DB $\rightarrow$ Notification Service.
3.  **Notification:** The Notification Service pushes a "Change Event" (containing `file_id` and `version`) to all other active sessions of the user via WebSockets.
4.  **Pull:** The other clients receive the event and request only the modified blocks from the Block Service.

### 5.3 Database Sharding & Caching
*   **Metadata Sharding:** Shard the `Files` and `FileVersions` tables by `user_id`. Since most queries are user-centric, this prevents cross-shard joins.
*   **Caching:** Use Redis to cache the file tree for active users to reduce the load on the SQL DB during frequent directory browsing.

### 5.4 Fault Tolerance & Durability
*   **Object Store:** S3 inherently provides high durability through replication across multiple availability zones.
*   **Write-Ahead Log (WAL):** Use WAL in the metadata DB to ensure that file commits are atomic.
*   **Retry Logic:** Clients implement exponential backoff for failed chunk uploads.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Consistency vs. Availability
For a file storage system, **Consistency** is prioritized over **Availability** for metadata (CP). If a user moves a folder, they should not see the folder in both the old and new locations (split-brain). However, the binary data delivery (Block Service) can be **Eventually Consistent** (AP), as the metadata versioning ensures the client requests the correct block hash.

### 6.2 Latency vs. Storage Efficiency
*   **Chunking:** Increases metadata overhead (more rows in `FileVersionBlocks`) and adds slight latency due to hashing on the client. However, it drastically reduces bandwidth and storage costs through delta sync and deduplication.

### 6.3 SQL vs. NoSQL
*   **SQL (Metadata):** Chosen for complex relational queries (e.g., "Find all files shared with User X") and ACID guarantees.
*   **NoSQL (Block Index):** Chosen for the Block Index because the access pattern is a simple key-value lookup ($\text{Hash} \rightarrow \text{Path}$) with a massive volume of entries, requiring linear scalability.""",
}

# Dropbox / Google Drive HLD

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
| **Sync Check** | $O(\text{Num Blocks})$ | $O(1)$ | $O(\text{Num Hashes})$ |
# Video Streaming System HLD (Netflix/YouTube Clone)

Designing a video streaming system is a classic "Hard" HLD problem because it combines massive data ingress (uploads), compute-intensive processing (transcoding), and extreme egress requirements (low-latency global delivery).

---

## 1. Overview & System Requirements

The goal is to design a system capable of handling video uploads, processing them into multiple formats/resolutions, and delivering them to millions of users globally with minimal buffering.

### Functional Requirements
- **Video Upload**: Users should be able to upload videos of various formats and sizes.
- **Transcoding**: The system must convert the raw video into multiple resolutions (e.g., 360p, 720p, 1080p, 4K) and formats (e.g., HLS, DASH) to support different devices and bandwidths.
- **Video Streaming**: Users should be able to stream videos with **Adaptive Bitrate Streaming (ABS)**.
- **Search & Discovery**: Users can search for videos and see recommendations.
- **User Management**: Profiles, watch history, and billing.

### Non-Functional Requirements
- **High Availability**: The system must be available 24/7; a failure in one region should not crash the global service.
- **Low Latency**: Video playback must start instantly (low startup latency) and have minimal buffering.
- **Scalability**: Must handle millions of concurrent viewers and petabytes of data.
- **Reliability/Durability**: Uploaded videos must never be lost.
- **Fault Tolerance**: If a transcoding worker fails, the job should be retried by another worker.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million |
| **Concurrent Viewers** | 10 Million |
| **Average Uploads/Day** | 10,000 videos |
| **Average Video Size** | 500 MB (Raw) $\rightarrow$ several GBs after transcoding |
| **Storage Needs** | Exabytes (considering multiple resolutions and replicas) |
| **Read/Write Ratio** | Extremely Read-Heavy (1:10,000+) |

---

## 2. High-Level System Architecture

The architecture is split into two primary pipelines: the **Write Path (Ingestion & Processing)** and the **Read Path (Delivery)**.

### System Architecture Diagram (Conceptual Flow)
`Client` $\rightarrow$ `Load Balancer` $\rightarrow$ `API Gateway` $\rightarrow$ `Upload Service` $\rightarrow$ `Blob Storage (S3)` $\rightarrow$ `Transcoding Pipeline` $\rightarrow$ `CDN` $\rightarrow$ `End User`

### Component Breakdown

#### A. The Write Path (Ingestion)
1. **Upload Service**: Handles the incoming multipart upload. To optimize, it uses **Presigned URLs** to allow the client to upload directly to Blob Storage, bypassing the application server to reduce bottleneck.
2. **Blob Storage (Raw)**: An object store (like AWS S3) that stores the original high-quality source file.
3. **Transcoding Pipeline**: An asynchronous workflow triggered by an upload event. It breaks the video into chunks, processes them in parallel, and re-assembles them.
4. **Metadata DB**: Stores video titles, tags, uploader ID, and URLs to the transcoded files (e.g., Cassandra or MongoDB for scalability).

#### B. The Read Path (Delivery)
1. **CDN (Content Delivery Network)**: The most critical component. Cached copies of video chunks are stored at "Edge Locations" close to the user to reduce latency and backbone traffic.
2. **Streaming Service**: Handles the logic of which video manifest (HLS/DASH) to provide the user based on their device and location.
3. **API Gateway**: Handles authentication, rate limiting, and routing for metadata requests.

---

## 3. Key HLD Concepts & Component Design

### A. The Transcoding Pipeline (The Core Engine)
Transcoding a 2-hour 4K video is computationally expensive. Doing it sequentially would take hours. We use a **Distributed Chunking Strategy**:

1. **Splitter**: The raw video is split into small chunks (e.g., 2-5 seconds each).
2. **Task Queue**: Each chunk is pushed into a message queue (Kafka/RabbitMQ) as a separate task.
3. **Transcoding Workers**: A fleet of workers pulls chunks from the queue. Each worker transcodes the chunk into multiple resolutions (360p, 720p, 1080p).
4. **Merger/Packager**: Once all chunks for a specific resolution are done, they are packaged into a streaming format (HLS or DASH) and a **Manifest File** (`.m3u8` or `.mpd`) is created.

### B. Adaptive Bitrate Streaming (ABS)
To prevent buffering, the system doesn't send one giant file. It uses ABS:
- The video is divided into chunks of different quality levels.
- The **Manifest File** lists the URLs for these chunks.
- The **Client Player** monitors the user's real-time network speed.
- If speed drops, the player automatically requests the 360p chunk instead of the 1080p chunk for the next 5 seconds.

### C. CDN Strategy (Netflix Open Connect Approach)
Generic CDNs (like Cloudflare/Akamai) are expensive for video. Companies like Netflix build their own:
- **Open Connect Appliances (OCAs)**: Custom hardware servers placed directly inside Internet Service Providers (ISPs).
- **Pre-positioning**: Popular videos are pushed to the OCA during off-peak hours (nightly) so they are already there when the user hits "Play."

### D. Technology Stack Choices
| Component | Technology | Why? |
| :--- | :--- | :--- |
| **Blob Storage** | AWS S3 / Google Cloud Storage | High durability, virtually infinite scalability for large files. |
| **Message Queue** | Apache Kafka | High throughput, allows multiple consumers (transcoding, notifications, analytics). |
| **Metadata DB** | Cassandra / DynamoDB | NoSQL provides the scale needed for billions of rows of video metadata. |
| **Caching** | Redis | For user sessions, trending video lists, and frequently accessed metadata. |
| **Streaming Protocol**| HLS (Apple) / DASH (Industry Standard) | Supports ABS and is compatible with almost all modern browsers/devices. |

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Walkthrough: Upload to Playback
1. **Upload**: User $\rightarrow$ Upload Service $\rightarrow$ Gets Presigned URL $\rightarrow$ Uploads to S3 $\rightarrow$ S3 triggers "Object Created" event.
2. **Processing**: Event $\rightarrow$ Kafka $\rightarrow$ Splitter $\rightarrow$ Kafka (Chunks) $\rightarrow$ Workers (Transcode) $\rightarrow$ S3 (Processed Chunks).
3. **Finalization**: Workers $\rightarrow$ Packager $\rightarrow$ Manifest File created $\rightarrow$ Metadata DB updated to `status: READY`.
4. **Discovery**: User $\rightarrow$ API Gateway $\rightarrow$ Metadata DB $\rightarrow$ Receives Manifest URL.
5. **Streaming**: Client $\rightarrow$ CDN Edge $\rightarrow$ Requests chunks based on bandwidth $\rightarrow$ Video plays.

### Fault Tolerance & Reliability
- **Worker Failure**: If a transcoding worker crashes, the message remains in Kafka (unacknowledged) and is picked up by another worker.
- **CDN Failure**: If a local OCA server is down, the client falls back to a regional CDN or the origin server.
- **Storage Failure**: S3 replicates data across multiple Availability Zones (AZs) to ensure 99.999999999% durability.
- **Database Availability**: Cassandra's peer-to-peer architecture ensures no single point of failure.

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
For a video platform, **Availability** is prioritized over **Strong Consistency**.
- If a user updates their profile picture or a video title, it is acceptable if other users see the old title for a few seconds (**Eventual Consistency**).
- However, the system *must* be available to serve the video stream; otherwise, users leave.

### Latency vs. Cost (Storage)
- **Trade-off**: Storing every video in 10 different resolutions and 3 different formats takes massive storage.
- **Optimization**: Use **Just-in-Time (JIT) Transcoding** for rare/unpopular videos. Store only the high-quality source and transcode on-the-fly if requested, while keeping popular videos pre-transcoded.

### Latency vs. Quality (Chunk Size)
- **Small Chunks (2s)**: Faster startup time, more agile ABS switching, but higher overhead (more HTTP requests).
- **Large Chunks (10s)**: Better compression efficiency and fewer requests, but slower startup and sluggish quality switching.
- **Decision**: Most systems settle for **2-6 seconds**.

---

## Complexity Analysis Summary

| Process | Time Complexity | Space/Storage Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Upload** | $O(N)$ | $O(N)$ | $N$ = File size. |
| **Transcoding** | $O(N \cdot R)$ | $O(N \cdot R \cdot F)$ | $R$ = resolutions, $F$ = formats. |
| **Metadata Lookup**| $O(1)$ | $O(M)$ | $M$ = Total videos. |
| **Streaming** | $O(1)$ | $O(C)$ | $C$ = Chunk size cached at edge. |
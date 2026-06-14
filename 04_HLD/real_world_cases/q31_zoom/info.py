INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Zoom-like Video Conferencing System.',
    'groups': ['Real-World Systems', 'Networking'],
    'readme_content': """# Zoom-like Video Conferencing System HLD

## 1. Overview & System Requirements

Designing a video conferencing system like Zoom is one of the most challenging HLD problems because it involves **real-time bidirectional communication**, massive bandwidth consumption, and extreme sensitivity to latency.

### Functional Requirements
*   **Meeting Management**: Users can create, schedule, and join meetings via a unique Meeting ID.
*   **Real-time Audio/Video**: High-quality, low-latency streaming for one-to-one and one-to-many calls.
*   **Screen Sharing**: Ability to share the desktop/application window in real-time.
*   **Chat**: In-meeting text messaging.
*   **Meeting Controls**: Mute/unmute, camera on/off, and participant management (host privileges).
*   **Recording**: Ability to record meetings and store them for later playback.

### Non-Functional Requirements
*   **Ultra-Low Latency**: End-to-end latency must be $< 200\text{ms}$ for a natural conversational experience.
*   **High Availability**: The system must be available $99.99\%$ of the time; a call should not drop if a single server fails.
*   **Scalability**: Support millions of concurrent users and meetings with thousands of participants per room.
*   **Reliability/Quality**: Graceful degradation (e.g., drop video resolution before dropping audio).
*   **Global Reach**: Low latency regardless of the geographic distance between participants.

### Scale Assumptions
| Metric | Estimated Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | 100 Million |
| **Concurrent Users** | 10 Million |
| **Avg. Meeting Size** | 5-10 participants |
| **Max Meeting Size** | 1,000+ participants |
| **Video Quality** | 720p (HD) $\approx 1.5\text{--}2.5\text{ Mbps}$ per stream |

---

## 2. High-Level System Architecture

The architecture is split into two main planes: the **Control Plane (Signaling)** and the **Data Plane (Media)**.

### Architecture Diagram Components
1.  **Client Application**: Captures audio/video, encodes it, and renders incoming streams.
2.  **API Gateway / Load Balancer**: Entry point for authentication, scheduling, and routing.
3.  **Signaling Server**: Orchestrates the connection. It handles "who is in the room" and exchanges session metadata (SDP) to establish the media path.
4.  **Media Server (SFU - Selective Forwarding Unit)**: The core engine that receives media streams and forwards them to other participants.
5.  **Meeting Service**: Manages meeting metadata (IDs, passwords, schedules) using a distributed database.
6.  **Chat Service**: A WebSocket-based service for real-time text messaging.
7.  **Recording Service**: Captures streams from the SFU and persists them to Object Storage (S3).

### Architecture Flow
*   **Control Path**: Client $\rightarrow$ API Gateway $\rightarrow$ Meeting Service $\rightarrow$ Signaling Server $\rightarrow$ Client.
*   **Data Path**: Client $\rightarrow$ SFU $\rightarrow$ Other Clients.

---

## 3. Key HLD Concepts & Component Design

### A. Networking Protocols (The "How")
Standard HTTP/TCP is unsuitable for video because TCP's retransmission mechanism causes "head-of-line blocking," leading to lag.
*   **UDP (User Datagram Protocol)**: Used for media. It is "fire and forget," which is better for real-time streams where losing one frame is better than delaying the whole stream.
*   **WebRTC (Web Real-Time Communication)**: The industry standard framework. It provides:
    *   **ICE (Interactive Connectivity Establishment)**: To find the best path between peers (STUN/TURN servers).
    *   **DTLS/SRTP**: For secure, encrypted media transport.
*   **WebSocket**: Used for signaling and chat because it provides a persistent, bidirectional connection.

### B. Media Routing Architectures
There are three main ways to route video:
1.  **Mesh (P2P)**: Every user sends their stream to every other user.
    *   *Pros*: No server cost.
    *   *Cons*: Bandwidth kills the client. $N$ users $\rightarrow$ $(N-1)$ upload streams. (Only viable for 2-3 people).
2.  **MCU (Multipoint Control Unit)**: Server mixes all streams into one single video frame and sends it back.
    *   *Pros*: Very low client bandwidth.
    *   *Cons*: Massive CPU load on the server (transcoding is expensive). High latency.
3.  **SFU (Selective Forwarding Unit)**: **(Zoom's Choice)**. The server does not decode or mix. It simply receives a stream and forwards it to others.
    *   *Pros*: Low server CPU, scalable, allows clients to decide which stream to prioritize.
    *   *Cons*: Client must decode multiple streams.

### C. Handling Network Variability
*   **Simulcast**: The client uploads multiple versions of the same stream (Low, Medium, High resolution). The SFU forwards the version that matches the receiver's current bandwidth.
*   **SVC (Scalable Video Coding)**: A more advanced version of Simulcast where a single stream is layered. The server can drop "layers" to reduce quality without needing multiple separate uploads.
*   **Jitter Buffer**: A small buffer on the receiver's side to smooth out packets that arrive at irregular intervals.

### D. Database Selection
| Data Type | Technology | Reason |
| :--- | :--- | :--- |
| **User Profiles/Settings** | PostgreSQL / MySQL | Strong consistency, relational data. |
| **Meeting Metadata** | MongoDB / DynamoDB | High write throughput, flexible schema for meeting attributes. |
| **Presence/Session State** | Redis | Ultra-low latency for "Who is online" and "Room mapping." |
| **Chat History** | Cassandra | Optimized for heavy writes and time-series retrieval. |

---

## 4. Data Flows & Fault Tolerance

### Sequence: Joining a Meeting
1.  **Authentication**: User logs in $\rightarrow$ API Gateway $\rightarrow$ Auth Service.
2.  **Meeting Discovery**: User enters Meeting ID $\rightarrow$ Meeting Service $\rightarrow$ Returns the **SFU IP Address** assigned to that room.
3.  **Signaling (The Handshake)**:
    *   Client A sends an **SDP (Session Description Protocol)** offer via Signaling Server to Client B.
    *   SDP contains: Codecs supported, network capabilities, and security keys.
    *   Client B returns an SDP answer.
4.  **Media Connection**: Clients establish a UDP connection to the SFU.
5.  **Streaming**: Client A $\rightarrow$ Encoded Video $\rightarrow$ SFU $\rightarrow$ Forwards to Client B, C, D.

### Fault Tolerance & Reliability
*   **SFU Failover**: If an SFU node crashes, the Signaling Server detects the heartbeat failure and instructs all clients in that room to reconnect to a standby SFU.
*   **Regional Routing**: Use **Geo-DNS** to route users to the nearest Edge Media Server to minimize the "first mile" latency.
*   **Cascading SFUs**: For massive meetings (1,000+ people), one SFU cannot handle the bandwidth. SFUs are chained:
    *   *User $\rightarrow$ Edge SFU $\rightarrow$ Core SFU $\rightarrow$ Edge SFU $\rightarrow$ Other User.*
*   **Graceful Degradation**: If the CPU spikes or bandwidth drops, the system automatically:
    1.  Drops Video Resolution (1080p $\rightarrow$ 720p $\rightarrow$ 360p).
    2.  Drops Frame Rate (30fps $\rightarrow$ 15fps).
    3.  Disables Video entirely, prioritizing Audio.

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
In a video call, **Availability and Partition Tolerance (AP)** are prioritized over Consistency.
*   **Example**: If the "Participant List" is slightly out of date (someone joined 2 seconds ago but isn't showing yet), it is acceptable. However, if the video freezes because the system is trying to ensure every single node knows the exact state of the room, the product is unusable.

### Latency vs. Quality
*   **The Trade-off**: To get perfect quality, you need larger buffers and TCP-like retransmissions. But this increases latency.
*   **The Decision**: Zoom chooses **Low Latency**. It uses UDP and accepts "packet loss" (which manifests as a momentary pixelation or audio glitch) to ensure the conversation remains in real-time.

### Server CPU vs. Client Bandwidth (SFU vs MCU)
*   **SFU**: Saves server costs (no transcoding) but requires the client to have more bandwidth and CPU to decode multiple incoming streams.
*   **MCU**: Saves client resources but makes the server a massive bottleneck and extremely expensive to scale.
*   **Conclusion**: With modern hardware (GPUs/Multi-core CPUs in laptops/phones), the SFU is the mathematically superior choice for scalability.

### Complexity Analysis Summary
| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Joining Meeting** | $O(1)$ | $O(1)$ | Simple DB lookup and signaling. |
| **Routing Stream** | $O(N)$ | $O(1)$ | Per user, SFU forwards to $N-1$ participants. |
| **Chat Message** | $O(1)$ | $O(M)$ | $M$ = message size, persisted in NoSQL. |
| **Recording** | $O(S)$ | $O(S)$ | $S$ = stream size, written sequentially to S3. |""",
    'solutions': """# System Design: Real-time Video Conferencing System (Zoom Clone)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Meeting Management:** Users can create a meeting, schedule a meeting, and join a meeting via a unique Meeting ID or URL.
*   **Real-time Media Streaming:** High-quality, low-latency audio and video streaming for multiple participants.
*   **Screen Sharing:** Ability for one or more participants to share their screen.
*   **Real-time Messaging:** In-meeting text chat.
*   **Meeting Controls:** Mute/unmute, camera on/off, and the ability for the host to kick participants.
*   **Recording:** Ability to record the session and store it for later playback.
*   **User Management:** Authentication, profiles, and contact lists.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** End-to-end latency should be $< 200\text{ms}$ to ensure natural conversation.
*   **High Availability:** The system must be available $99.99\%$ of the time.
*   **Scalability:** Support millions of concurrent users and meetings of varying sizes (from 1-on-1 to 1,000+ participants).
*   **Reliability:** Graceful degradation (e.g., drop video quality before dropping audio).
*   **Global Reach:** Users should connect to the nearest data center to minimize jitter and lag.

### 1.3 Scale Estimations
*   **Daily Active Users (DAU):** 10 Million.
*   **Peak Concurrent Users (PCU):** 1 Million.
*   **Average Meeting Size:** 5–10 participants.
*   **Bandwidth (Approx):** 
    *   Audio: $\sim 50\text{--}100\text{ kbps}$.
    *   Video (720p): $\sim 1.5\text{--}2.5\text{ Mbps}$ per stream.
*   **Total Peak Bandwidth:** $1\text{M users} \times 2\text{ Mbps} \approx 2\text{ Tbps}$ (distributed across global SFUs).

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **Client Application:** Web/Mobile app implementing WebRTC for media capture and transmission.
2.  **Signaling Server:** A WebSocket-based service that coordinates the connection between participants (exchange of SDP - Session Description Protocol and ICE candidates).
3.  **SFU (Selective Forwarding Unit):** The heart of the media plane. Unlike an MCU (Multipoint Control Unit) which mixes streams, the SFU forwards encrypted media packets from one sender to multiple receivers without transcoding, reducing server CPU load.
4.  **Meeting Service:** Manages the lifecycle of a meeting (creation, joining, participant lists).
5.  **User/Auth Service:** Handles identity and access management.
6.  **Chat Service:** Manages real-time text messaging using Pub/Sub.
7.  **Recording Service:** Captures the media streams from the SFU, transcodes them, and uploads them to object storage.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    UserA[User A - Client] --> LB[Global Load Balancer]
    UserB[User B - Client] --> LB
    UserC[User C - Client] --> LB

    LB --> SignalSvr[Signaling Server - WebSocket]
    LB --> API_Gateway[API Gateway]

    API_Gateway --> MeetSvr[Meeting Service]
    API_Gateway --> UserSvr[User/Auth Service]
    
    SignalSvr --> RedisState[(Redis - Meeting State)]
    
    UserA -- WebRTC/SRTP --> SFU1[SFU Node 1]
    UserB -- WebRTC/SRTP --> SFU1
    UserC -- WebRTC/SRTP --> SFU1
    
    SFU1 -- Forward Stream --> UserA
    SFU1 -- Forward Stream --> UserB
    SFU1 -- Forward Stream --> UserC

    SFU1 --> RecordSvr[Recording Service]
    RecordSvr --> S3[(S3 Object Storage)]
    
    API_Gateway --> ChatSvr[Chat Service]
    ChatSvr --> Cassandra[(Cassandra - Chat History)]
    ChatSvr --> PubSub[Redis Pub/Sub]
```

### 2.3 Media Flow
1.  **Signaling:** User A creates a meeting. The Meeting Service assigns a Meeting ID and an available SFU. User B joins; the Signaling Server exchanges SDP (capabilities) and ICE candidates (network paths) between User A, User B, and the SFU.
2.  **Streaming:** User A sends one stream to the SFU. The SFU forwards that stream to User B and User C.
3.  **Optimization:** The SFU uses **Simulcast** (sender sends 3 quality levels: low, med, high). The SFU forwards the level appropriate for each receiver's bandwidth.

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection
*   **PostgreSQL (Relational):** Used for User profiles and Meeting metadata where ACID compliance and complex querying (e.g., scheduling) are required.
*   **Redis (In-Memory):** Used for real-time meeting state (who is in which room, which SFU is being used) and Signaling session management.
*   **Cassandra (NoSQL):** Used for chat history due to high write throughput and time-series nature.
*   **S3 (Object Store):** Used for storing recorded video files.

### 3.2 Schema Definitions

#### User Table (PostgreSQL)
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier for user |
| `email` | VARCHAR(255)| Unique | User email |
| `password_hash`| TEXT | | Hashed password |
| `created_at` | TIMESTAMP | | Account creation date |

#### Meeting Table (PostgreSQL)
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `meeting_id` | UUID | PK | Unique meeting ID |
| `host_id` | UUID | FK | User who created the meeting |
| `start_time` | TIMESTAMP | | Scheduled start time |
| `status` | ENUM | | Scheduled, Active, Ended |
| `settings` | JSONB | | Recording enabled, Mute on entry, etc. |

#### Participant Table (PostgreSQL)
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `meeting_id` | UUID | FK/PK | Meeting identifier |
| `user_id` | UUID | FK/PK | User identifier |
| `joined_at` | TIMESTAMP | | Join timestamp |
| `role` | ENUM | | Host, Co-host, Participant |

#### Chat Messages (Cassandra)
*   **Partition Key:** `meeting_id`
*   **Clustering Key:** `timestamp` (descending)
*   **Fields:** `message_id (UUID)`, `user_id (UUID)`, `content (Text)`, `timestamp (Long)`.

---

## 4. Core API Design

### 4.1 Meeting Management
**Create Meeting**
`POST /v1/meetings`
*   **Request:** `{ "userId": "uuid", "startTime": "iso-timestamp", "settings": { "isPrivate": true } }`
*   **Response:** `201 Created { "meetingId": "uuid", "joinUrl": "https://zoom.clone/j/uuid" }`

**Join Meeting**
`POST /v1/meetings/{meetingId}/join`
*   **Request:** `{ "userId": "uuid", "token": "auth-token" }`
*   **Response:** `200 OK { "sfuAddress": "sfu-region-1.zoom.clone", "signalingToken": "jwt-token" }`

### 4.2 Meeting Controls
**Update Participant Status**
`PATCH /v1/meetings/{meetingId}/participants/{userId}`
*   **Request:** `{ "mute": true, "videoOff": false }`
*   **Response:** `200 OK`

### 4.3 Real-time Signaling (WebSocket)
The Signaling Server doesn't use REST but WebSocket frames:
*   **Client $\rightarrow$ Server:** `{"type": "offer", "sdp": "...", "meetingId": "uuid"}`
*   **Server $\rightarrow$ Client:** `{"type": "answer", "sdp": "...", "from": "userId"}`
*   **Client $\rightarrow$ Server:** `{"type": "ice-candidate", "candidate": "...", "meetingId": "uuid"}`

---

## 5. Scalability & Advanced Topics

### 5.1 Media Optimization (SFU Strategies)
*   **Simulcast:** The client uploads three versions of the video (180p, 360p, 720p). The SFU decides which one to forward based on the receiver's downlink.
*   **SVC (Scalable Video Coding):** An advanced version of simulcast where a single stream contains multiple layers of quality.
*   **Dynamic Forwarding:** The SFU prioritizes the "Active Speaker" stream (high quality) and down-samples the other participants (low quality) to save bandwidth.

### 5.2 Load Balancing & Geo-Routing
*   **Geo-DNS:** Users are routed to the closest data center via Anycast IP or Geo-DNS.
*   **SFU Orchestrator:** A global service that tracks the CPU/Bandwidth load of all SFU nodes. When a meeting is created, the orchestrator assigns the SFU node with the lowest load in the closest region.

### 5.3 Fault Tolerance & Reliability
*   **SFU Failover:** If an SFU node crashes, the signaling server detects the disconnect and triggers a "Re-join" event. Clients automatically reconnect to a backup SFU node.
*   **Jitter Buffer:** Implemented on the client side to handle packets arriving out of order or with varying delay.
*   **Packet Loss Concealment (PLC):** Use of FEC (Forward Error Correction) to reconstruct lost audio packets.

### 5.4 Recording Pipeline
1.  **SFU Sidecar:** The SFU forks the media streams to a Recording Worker.
2.  **Composition:** The Recording Worker (using FFmpeg) composites multiple streams into a single MP4 file or saves them as raw streams.
3.  **Asynchronous Upload:** The resulting file is uploaded to S3, and a webhook notifies the User Service to mark the recording as "Ready".

---

## 6. Trade-off Analysis

### 6.1 SFU vs. MCU vs. Mesh
*   **Mesh (P2P):** Low server cost, but $O(N^2)$ bandwidth on client. Unusable for $> 3$ participants.
*   **MCU:** Server mixes all video into one stream. Lowest client bandwidth, but extremely high server CPU cost (transcoding).
*   **SFU (Chosen):** Server forwards packets. Balanced CPU cost and bandwidth. Requires clients to decode multiple streams, but this is acceptable for modern devices.

### 6.2 CAP Theorem Priorities
*   **Signaling/Meeting State:** Prioritizes **Availability and Partition Tolerance (AP)**. If a user's "Mute" status takes 1 second to propagate to others, it is acceptable. Eventual consistency via Redis is sufficient.
*   **User Auth/Billing:** Prioritizes **Consistency and Partition Tolerance (CP)**. We cannot allow duplicate account creation or incorrect billing.

### 6.3 Latency vs. Quality
*   **UDP vs TCP:** We use **UDP** (via SRTP) for media. TCP's retransmission mechanism (Head-of-Line blocking) causes unacceptable lag in real-time video. We prefer losing a few frames (packet loss) over delaying the entire stream to wait for a retransmission.""",
}

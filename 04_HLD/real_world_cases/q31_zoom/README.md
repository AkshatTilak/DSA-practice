# Zoom-like Video Conferencing System HLD

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
| **Recording** | $O(S)$ | $O(S)$ | $S$ = stream size, written sequentially to S3. |
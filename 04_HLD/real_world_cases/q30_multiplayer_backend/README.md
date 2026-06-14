# Multiplayer Game Backend HLD

Designing a multiplayer game backend is one of the most challenging HLD problems because it requires a delicate balance between **extreme low latency**, **high concurrency**, and **state synchronization**. Unlike standard REST APIs, game backends often rely on persistent, bidirectional communication and a "tick-based" execution model.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Matchmaking**: Group players based on skill level (MMR), region, and game mode.
- **Real-time State Sync**: Synchronize player positions, actions, and game world state across all clients.
- **Session Management**: Handle game room creation, joining, and termination.
- **Persistence**: Store player profiles, inventories, statistics, and leaderboards.
- **Anti-Cheat/Validation**: Ensure all moves are legal and processed by a "source of truth" (the server).

### Non-Functional Requirements
- **Ultra-Low Latency**: For fast-paced games (FPS, MOBA), latency must be $< 100\text{ms}$.
- **Scalability**: Support millions of Daily Active Users (DAU) and hundreds of thousands of Concurrent Users (CCU).
- **High Availability**: The matchmaking and profile services must be highly available; game sessions must be resilient.
- **Consistency**: Strong consistency for inventory/purchases; eventual consistency for non-critical world state.

### Scale Assumptions
| Metric | Value | Note |
| :--- | :--- | :--- |
| **DAU** | $10^6$ | 1 Million Daily Active Users |
| **CCU** | $10^5$ | 100k Concurrent Users |
| **Tick Rate** | $20\text{--}60\text{Hz}$ | Server updates state 20 to 60 times per second |
| **Avg. Session** | $15\text{--}30\text{ min}$ | Typical match duration |
| **QPS (State Updates)** | $10^5 \times 30\text{Hz}$ | $\approx 3 \text{ Million updates per second}$ |

---

## 2. High-Level System Architecture

The architecture is split into two distinct planes: the **Control Plane** (Slow Path) and the **Game Plane** (Fast Path).

### Architecture Diagram Components

1.  **API Gateway / Load Balancer**: Handles HTTP requests for authentication, profile management, and matchmaking requests.
2.  **Matchmaking Service**: A specialized service that pools players and assigns them to a Game Server.
3.  **Game Session Manager (Orchestrator)**: Manages the lifecycle of **Dedicated Game Servers (DGS)**. It spins up new instances (via Kubernetes/Agones) when demand spikes.
4.  **Dedicated Game Server (DGS)**: The authoritative "source of truth." It runs the game loop, processes physics, and broadcasts state.
5.  **State Store (Redis)**: Stores transient session data, player presence, and matchmaking queues.
6.  **Persistent DB (PostgreSQL/MongoDB)**: Stores long-term user data, items, and historical match results.

---

## 3. Key HLD Concepts & Component Design

### A. Networking Protocols: UDP vs. TCP vs. WebSockets
Standard HTTP is too slow. We choose based on the data type:
- **UDP (User Datagram Protocol)**: Used for **real-time movement and combat**. It is "fire and forget," avoiding the overhead of TCP's handshake and retransmission (which causes "head-of-line blocking").
- **Reliable UDP (RUDP)**: A custom layer over UDP that ensures *critical* packets (e.g., "Player Died") are acknowledged, while non-critical ones (e.g., "Player moved 0.1 units") are dropped if lost.
- **WebSockets/TCP**: Used for **Lobbies, Chat, and Matchmaking** where reliability is more important than raw speed.

### B. The Game Loop & Tick Rate
The DGS does not react to every packet instantly; it operates on a **Tick**.
1. **Input Collection**: Collect all packets from clients since the last tick.
2. **Simulation**: Update physics, check collisions, and process logic.
3. **State Broadcast**: Send the new world state to all connected clients.

**Tick Rate Calculation**: 
If the tick rate is $30\text{Hz}$, the server processes a frame every $33.3\text{ms}$. Higher tick rates increase CPU load but decrease "input lag."

### C. State Synchronization Techniques
To hide latency, we use these industry-standard patterns:
- **Client-Side Prediction**: The client renders the result of an action immediately without waiting for the server. (e.g., you press 'W', and your character moves forward instantly).
- **Server Reconciliation**: The server sends the *authoritative* position. If the client's predicted position differs, the client "snaps" or smoothly interpolates to the server's position.
- **Entity Interpolation**: To prevent other players from "teleporting," the client renders them slightly in the past, smoothly interpolating between the last two received positions.
- **Lag Compensation (Backtracking)**: For shooting games, the server keeps a history of positions. When a player shoots, the server "rewinds" the world to where the target was at the time the shooter saw them (based on the shooter's latency).

### D. Matchmaking Logic
To avoid $O(N^2)$ comparisons, matchmaking uses **Bucketing**:
- Players are grouped into buckets based on **Region $\rightarrow$ Game Mode $\rightarrow$ Skill Range**.
- A **Redis Sorted Set** is often used to store players by MMR, allowing the system to query a range of players near the target skill level efficiently.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step: Joining a Match
1. **Request**: Client sends `joinMatch()` via API Gateway $\rightarrow$ Matchmaking Service.
2. **Queue**: Matchmaking Service adds the player to a Redis-based queue for their skill bracket.
3. **Allocation**: Once a group is formed, the Matchmaker requests a server from the **Session Manager**.
4. **Provisioning**: Session Manager assigns an IP and Port of an available DGS.
5. **Handshake**: Client establishes a UDP connection to the DGS; DGS notifies the Session Manager that the match has started.

### Fault Tolerance & Reliability
- **DGS Crash**: Since the game state is held in memory for speed, a DGS crash usually ends the match. To mitigate this, the Session Manager performs health checks. Match results are periodically checkpointed to Redis.
- **Packet Loss**: Handled by RUDP. If a "critical" packet is missing, the client requests a re-send.
- **Database Failover**: Use a managed SQL cluster (e.g., Aurora) with multi-AZ replication for player profiles.

---

## 5. Production Trade-offs

### CAP Theorem: Consistency vs. Availability
In a multiplayer game, **Availability (Low Latency)** is prioritized over **Strong Consistency**.
- If we waited for every client to acknowledge a position update (Strong Consistency), the game would freeze.
- Instead, we use **Eventual Consistency** (via Server Reconciliation), where the server is the final authority, but clients "guess" the state to maintain fluidity.

### Centralized (DGS) vs. Peer-to-Peer (P2P)
| Feature | Dedicated Server (DGS) | Peer-to-Peer (P2P) |
| :--- | :--- | :--- |
| **Authority** | Server is the source of truth | One player is the "Host" |
| **Security** | High (Anti-cheat is easier) | Low (Host can cheat/modify state) |
| **Latency** | Depends on distance to DC | Depends on distance to Host |
| **Cost** | Expensive (Server costs) | Cheap (No server costs) |
| **Verdict** | **Required for Competitive/Hard** | **Suitable for Co-op/Small scale** |

### Complexity Analysis
| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| **Matchmaking Query** | $O(\log N)$ | $O(N)$ | Redis Sorted Set range queries |
| **State Broadcast** | $O(P)$ | $O(S)$ | $P$ = players in match, $S$ = state size |
| **Input Processing** | $O(I \times L)$ | $O(I)$ | $I$ = inputs per tick, $L$ = logic complexity |
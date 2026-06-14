INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Multiplayer Game Backend.',
    'groups': ['Real-World Systems', 'Concurrency', 'Game Design'],
    'readme_content': """# Multiplayer Game Backend HLD

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
| **Input Processing** | $O(I \times L)$ | $O(I)$ | $I$ = inputs per tick, $L$ = logic complexity |""",
    'solutions': """# System Design: High-Performance Multiplayer Game Backend

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **User Management:** Authentication, profile management, and friend lists.
*   **Matchmaking:** Grouping players based on skill level (Elo/MMR), latency (region), and game mode.
*   **Real-time Gameplay:** Low-latency state synchronization for player movement, actions, and combat.
*   **Game Session Management:** Orchestration of dedicated game servers to host matches.
*   **Leaderboards:** Real-time global and regional rankings.
*   **Persistence:** Saving player progress, inventory, and match history.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** Critical for "twitch" gameplay. Target round-trip time (RTT) $< 50\text{--}100\text{ms}$.
*   **High Scalability:** Support for millions of Daily Active Users (DAU) and hundreds of thousands of Concurrent Users (CCU).
*   **Availability:** High availability for the meta-game (store, profiles), while individual game sessions are isolated (if one server crashes, only that match is affected).
*   **Consistency:** Strong consistency for inventory/purchases; eventual consistency for leaderboards; strict authoritative state for active game sessions.

### 1.3 Scale Estimations
*   **CCU:** 100,000 concurrent players.
*   **Game Server Capacity:** Assume 100 players per match (Battle Royale style).
*   **Active Game Servers:** $\sim 1,000$ concurrent instances.
*   **Tick Rate:** 30Hz to 60Hz (updates per second).
*   **Traffic:** 100k users $\times$ 30 updates/sec $\approx$ 3 million packets per second across the fleet.

---

## 2. High-Level Architecture

The system is split into two primary planes: the **Meta-Game Plane** (Request-Response, REST/gRPC) and the **Game-World Plane** (Real-time, UDP/WebSockets).

### 2.1 Architecture Diagram

```mermaid
graph TD
    Client[Game Client] --> LB[Load Balancer]
    
    subgraph MetaGamePlane [Meta-Game Plane - HTTPS/gRPC]
        LB --> Gateway[API Gateway]
        Gateway --> AuthSvc[Auth Service]
        Gateway --> ProfileSvc[Profile/Inventory Service]
        Gateway --> MatchSvc[Matchmaking Service]
        Gateway --> LeaderboardSvc[Leaderboard Service]
        
        AuthSvc --> UserDB[(User DB - PostgreSQL)]
        ProfileSvc --> ItemDB[(Inventory DB - MongoDB)]
        LeaderboardSvc --> RedisLB[(Redis ZSet)]
        MatchSvc --> MatchQueue[(Redis Queue)]
    end

    subgraph GameWorldPlane [Game-World Plane - UDP/WebSockets]
        MatchSvc --> Orchestrator[Game Server Orchestrator - Agones/K8s]
        Orchestrator --> DGS1[Dedicated Game Server 1]
        Orchestrator --> DGS2[Dedicated Game Server 2]
        Orchestrator --> DGSN[Dedicated Game Server N]
        
        Client -- "Low Latency UDP" --> DGS1
        DGS1 --> GameStateCache[(In-Memory State)]
        DGS1 --> EventBus[Kafka / Message Queue]
    end

    EventBus --> AnalyticsSvc[Analytics/Match History Service]
    AnalyticsSvc --> HistoryDB[(Match History - Cassandra)]
```

### 2.2 Component Breakdown
1.  **API Gateway:** Handles authentication, rate limiting, and routing to microservices.
2.  **Matchmaking Service:** Uses a ticket-based system. Players enter a queue; the service groups them by MMR and region, then requests a game server from the Orchestrator.
3.  **Game Server Orchestrator (Agones):** Built on Kubernetes, it manages the lifecycle of Dedicated Game Servers (DGS). It handles scaling, health checks, and assigning "Allocated" status to servers when a match is found.
4.  **Dedicated Game Server (DGS):** The authoritative source of truth for the game simulation. It runs the physics engine and validates all client inputs to prevent cheating.
5.  **Event Bus (Kafka):** DGS sends match results and telemetry to Kafka to decouple the high-speed game loop from slow database writes.

---

## 3. Detailed Database Schema Design

### 3.1 User & Profile (PostgreSQL)
Used for critical data requiring ACID compliance.
*   **Users Table:** `user_id (PK)`, `username`, `email`, `password_hash`, `created_at`.
*   **Profiles Table:** `user_id (FK)`, `mmr_score`, `level`, `experience`, `region_id`.
*   **Index:** B-Tree index on `username` and `email`.

### 3.2 Inventory (MongoDB)
Used for flexible schema (different item types/attributes).
*   **Collection `inventories`:**
    ```json
    {
      "user_id": "UUID",
      "items": [
        { "item_id": "skin_01", "acquired_at": "timestamp", "attributes": { "color": "gold" } },
        { "item_id": "weapon_05", "level": 10 }
      ]
    }
    ```
*   **Index:** Sharded by `user_id`.

### 3.3 Leaderboards (Redis)
Uses **Sorted Sets (ZSET)** for $O(\log N)$ insertions and range queries.
*   **Key:** `leaderboard:global` or `leaderboard:region:us_east`.
*   **Score:** `mmr_score`.
*   **Value:** `user_id`.

### 3.4 Match History (Cassandra)
Optimized for high-volume writes and time-series retrieval.
*   **Table `match_history`:**
    *   Partition Key: `user_id`
    *   Clustering Key: `match_id` (Descending)
    *   Fields: `game_mode`, `result` (Win/Loss), `kills`, `duration`, `timestamp`.

---

## 4. Core API Design

### 4.1 Meta-Game APIs (REST)

| Endpoint | Method | Payload | Description |
| :--- | :--- | :--- | :--- |
| `/auth/login` | `POST` | `{user, pass}` | Returns JWT and Session ID. |
| `/profile` | `GET` | `Header: JWT` | Returns player stats and inventory. |
| `/match/join` | `POST` | `{game_mode, region}` | Adds player to matchmaking queue. |
| `/match/status` | `GET` | `{ticket_id}` | Polls for match status $\rightarrow$ returns DGS IP/Port. |
| `/leaderboard` | `GET` | `{region, limit}` | Returns top $N$ players. |

**Example `/match/status` Response:**
```json
{
  "status": "MATCH_FOUND",
  "server_address": "1.2.3.4",
  "port": 7777,
  "access_token": "secure_session_token_abc123"
}
```

### 4.2 Game-World Protocol (UDP/Custom Binary)
To minimize overhead, the DGS does not use JSON. It uses a binary format (e.g., **Protocol Buffers** or **FlatBuffers**).

**Packet Structure (Simplified):**
`[PacketHeader (4b)] [SequenceID (4b)] [Payload (Nb)] [Checksum (2b)]`

**Payload Examples:**
*   `PlayerInput`: `{ input_id, movement_vector, action_bits, timestamp }`
*   `GameStateUpdate`: `{ tick_id, [ { player_id, pos_x, pos_y, rot, state }, ... ] }`

---

## 5. Scalability & Advanced Topics

### 5.1 Latency Mitigation (The "Netcode")
Because the speed of light is a constant, we use several techniques to hide lag:
*   **Client-Side Prediction:** The client applies inputs immediately to the local avatar without waiting for server confirmation.
*   **Server Reconciliation:** The server sends the authoritative state. If the client's predicted state differs, the client "snaps" or smoothly interpolates to the server's state.
*   **Entity Interpolation:** Clients render other players slightly in the past (e.g., 100ms) to smoothly interpolate between received state packets.
*   **Lag Compensation (Backtracking):** For combat (e.g., shooting), the server rewinds the world state to the time the player fired the shot (based on their timestamp) to determine if it was a hit.

### 5.2 Matchmaking Scalability
To avoid a single bottleneck:
*   **Regional Queues:** Partition matchmaking by region (e.g., `queue:us_east`, `queue:eu_west`).
*   **Bucket-based Matching:** Group players into MMR buckets (e.g., 1000-1100). This reduces the search space from $O(N^2)$ to $O(N)$ within buckets.

### 5.3 Dedicated Game Server (DGS) Lifecycle
Using **Agones** on Kubernetes:
1.  **Fleet:** K8s maintains a pool of `Ready` game server pods.
2.  **Allocation:** Matchmaker calls Agones API $\rightarrow$ Agones marks a pod as `Allocated` $\rightarrow$ IP/Port returned.
3.  **Termination:** Once the match ends, the DGS signals Agones $\rightarrow$ Pod is shut down or recycled.

### 5.4 Fault Tolerance
*   **Stateless Meta-services:** All API services are stateless; load balancers distribute traffic.
*   **Zonal Redundancy:** Deploy DGS fleets across multiple availability zones to prevent total region blackout.
*   **Circuit Breakers:** Prevent the Matchmaking service from crashing the User DB during login spikes.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priorities
*   **Meta-Game (Profile/Store):** Prioritizes **Consistency and Partition Tolerance (CP)**. It is better to fail a purchase than to duplicate an item (Double Spend).
*   **Game Simulation:** Prioritizes **Availability and Partition Tolerance (AP)**. The game loop cannot pause to wait for a database update. We use an authoritative server with local state and asynchronous persistence.

### 6.2 UDP vs. TCP
*   **TCP:** Too slow due to head-of-line blocking (a single lost packet stalls all subsequent packets).
*   **UDP:** Fast, but unreliable.
*   **Hybrid Approach:** Use **Reliable UDP**. Critical events (e.g., "Player Died", "Game Over") are acknowledged and retransmitted. Ephemeral events (e.g., "Player Position") are sent without acknowledgement; if one is lost, the next update will correct it.

### 6.3 Latency vs. Storage
We sacrifice storage (by keeping redundant match logs and telemetry in Cassandra) to ensure that the "hot path" (DGS $\rightarrow$ Client) is completely devoid of disk I/O. All active game state is kept in RAM.""",
}

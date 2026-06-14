# System Design Document: Online Multiplayer Game Lobby

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Lobby Management**: 
    *   Users can create a lobby (Public or Private).
    *   Users can join a lobby via a unique Lobby ID or through a matchmaking process.
    *   Lobby owners can modify game settings (e.g., map selection, game mode, max players).
    *   Lobby owners can kick players or transfer ownership.
*   **Player Synchronization**:
    *   Real-time tracking of players currently in the lobby.
    *   "Ready" status management: Players must mark themselves as ready.
    *   Automatic updates to all members when a player joins, leaves, or changes status.
*   **Communication**:
    *   Real-time text chat within the lobby.
*   **Game Transition**:
    *   Once the "Start" condition is met (e.g., all players ready), the system must allocate a dedicated game server and transition all players from the lobby to the game instance.

### 1.2 Non-Functional Requirements
*   **Low Latency**: State updates (Ready/Join/Leave) must be reflected in near real-time (< 200ms).
*   **Strong Consistency**: To prevent "ghost" players or overfilling a lobby beyond its maximum capacity.
*   **High Availability**: The lobby service must be available; however, the loss of a single lobby instance should only affect the players in that specific lobby.
*   **Scalability**: Support millions of concurrent users and hundreds of thousands of active lobbies.

### 1.3 Scale Estimations (High-Level)
*   **Concurrent Users (CCU)**: 1 Million.
*   **Average Lobby Size**: 4–10 players.
*   **Lobby Lifetime**: 2–10 minutes.
*   **Throughput**: High volume of small updates (Ready/Not Ready toggles).

---

## 2. High-Level Architecture

The system follows a **Microservices Architecture** utilizing a combination of REST for orchestration and WebSockets for real-time bidirectional communication.

### 2.1 Component Overview
*   **API Gateway**: Entry point for authentication and routing.
*   **Lobby Service**: Handles the business logic of creating, joining, and managing lobby states.
*   **Matchmaking Service**: Pairs players based on skill/region and injects them into lobbies.
*   **State Store (Redis)**: An in-memory data store used for ephemeral lobby data to ensure low-latency access and atomic operations.
*   **Persistence DB (PostgreSQL)**: Stores user profiles and game history.
*   **Game Server Manager (GSM)**: Orchestrates the spinning up of dedicated game server instances (e.g., using Agones/Kubernetes).
*   **Pub/Sub (Redis/Kafka)**: Broadcasts state changes to all clients connected to a specific lobby.

### 2.2 Architecture Diagram (ASCII)

```text
[Client A] <---WS---> [ Load Balancer ] <---> [ Lobby Service Cluster ] <---> [ Redis State Store ]
[Client B] <---WS---> [               ]               |                           ^
[Client C] <---WS---> [               ]               v                           |
                                             [ Game Server Manager ] <-----------+
                                                       |
                                              [ Dedicated Game Server ]
                                              (Game Instance #123)
```

### 2.3 Sequence Flow: Joining and Starting a Game
1. **Join**: Client $\rightarrow$ `POST /lobby/join {lobbyId, userId}` $\rightarrow$ Lobby Service.
2. **Validate**: Lobby Service checks Redis if the lobby exists and has space.
3. **Update State**: Lobby Service adds User to Redis Set and publishes a `PLAYER_JOINED` event via Pub/Sub.
4. **Notify**: All clients in that lobby receive the `PLAYER_JOINED` update via WebSocket.
5. **Ready Up**: Client $\rightarrow$ `WS Send {action: "SET_READY", status: true}` $\rightarrow$ Lobby Service $\rightarrow$ Redis.
6. **Trigger Start**: Once all players are "Ready", Lobby Service calls **Game Server Manager**.
7. **Handoff**: GSM returns an IP/Port. Lobby Service sends `GAME_START {ip, port, token}` to all clients.

---

## 3. Detailed Database Schema Design

### 3.1 Ephemeral State (Redis)
Since lobbies are short-lived, storing them in a relational database would cause massive write overhead and fragmentation. Redis is used as the primary store.

**Key-Value Structures:**
*   **Lobby Metadata**: `lobby:{lobbyId}` $\rightarrow$ Hash
    *   `ownerId`: String
    *   `maxPlayers`: Integer
    *   `gameMode`: String
    *   `map`: String
    *   `status`: Enum (WAITING, STARTING, ACTIVE)
*   **Lobby Members**: `lobby:{lobbyId}:members` $\rightarrow$ Set
    *   Value: `userId`
*   **Player Readiness**: `lobby:{lobbyId}:readiness` $\rightarrow$ Hash
    *   `userId`: Boolean (true/false)

### 3.2 Persistent Storage (PostgreSQL)
Used for data that must survive server restarts or for analytics.

**Table: `users`**
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier |
| `username` | VARCHAR | Unique | Display name |
| `rank_score` | INT | | For matchmaking |

**Table: `game_sessions`** (Created after lobby transitions to game)
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `session_id` | UUID | PK | Unique session ID |
| `lobby_id` | UUID | Index | Reference to the originating lobby |
| `start_time` | TIMESTAMP | | When the game began |
| `end_time` | TIMESTAMP | | When the game ended |
| `server_id` | VARCHAR | | The ID of the physical server used |

---

## 4. Core API Design

### 4.1 REST Endpoints (Orchestration)

| Endpoint | Method | Payload | Response | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/lobby/create` | `POST` | `{ "userId", "mode", "maxPlayers", "isPrivate" }` | `{ "lobbyId", "token" }` | Creates a new lobby. |
| `/lobby/join` | `POST` | `{ "lobbyId", "userId", "joinToken?" }` | `{ "status": "success", "members": [...] }` | Joins an existing lobby. |
| `/lobby/leave` | `POST` | `{ "lobbyId", "userId" }` | `{ "status": "success" }` | Leaves the lobby. |

### 4.2 WebSocket Events (Real-time)

**Client $\rightarrow$ Server**
*   `SET_READY`: `{ "lobbyId": "L1", "ready": true }`
*   `UPDATE_SETTINGS`: `{ "lobbyId": "L1", "map": "Dust2" }` (Owner only)
*   `SEND_CHAT`: `{ "lobbyId": "L1", "message": "Hello!" }`

**Server $\rightarrow$ Client**
*   `LOBBY_UPDATE`: `{ "lobbyId": "L1", "members": [...], "readyStates": {...} }`
*   `CHAT_MESSAGE`: `{ "userId": "U1", "message": "Hello!", "timestamp": "..." }`
*   `GAME_START`: `{ "ip": "1.2.3.4", "port": 7777, "sessionToken": "abc-123" }`
*   `PLAYER_KICKED`: `{ "userId": "U2" }`

---

## 5. Scalability & Advanced Topics

### 5.1 Concurrency Control
To prevent race conditions (e.g., two players joining the last slot simultaneously), the Lobby Service uses **Redis Lua Scripts**. 
Example Logic:
1. Check `SCARD lobby:{id}:members` (current count).
2. If `count < maxPlayers`, perform `SADD lobby:{id}:members userId`.
3. Return success or failure atomically.

### 5.2 State Distribution & Scaling
*   **Stateless Services**: The Lobby Service instances are stateless. Any instance can handle any request by fetching the state from the shared Redis cluster.
*   **Redis Sharding**: Lobbies are sharded across Redis nodes using the `lobbyId` as the partition key to prevent a single node from becoming a bottleneck.
*   **WebSocket Management**: Since WebSockets are stateful connections, a **Distributed Pub/Sub** (e.g., Redis Pub/Sub) is used. When an update occurs for `Lobby A`, the service publishes a message to channel `lobby:A`. All Lobby Service instances subscribed to that channel will push the update to their locally connected clients.

### 5.3 Fault Tolerance
*   **Heartbeats**: Clients send a heartbeat every 5 seconds. If a heartbeat is missed for 15 seconds, the Lobby Service automatically triggers a `LEAVE_LOBBY` event to clear the slot.
*   **Lobby Migration**: If a Lobby Service instance crashes, clients reconnect to another instance via the Load Balancer and resume their session using the `lobbyId` stored in Redis.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priorities
In the context of a game lobby, we prioritize **Consistency (C)** and **Availability (A)** over Partition Tolerance (P) within a local region. 
*   **Why Consistency?** If the system is eventually consistent, two players might believe they occupied the final slot in a 4-player lobby, leading to a failure when the game server attempts to launch. We use Redis (single-threaded execution for scripts) to ensure linearizability for slot allocation.

### 6.2 Storage Trade-off: Redis vs. SQL
*   **Decision**: Use Redis for active lobby state and SQL for history.
*   **Trade-off**: Using SQL for the "Ready" toggle would result in excessive IOPS and lock contention. Using Redis introduces the risk of data loss if the Redis cluster fails without persistence, but since lobby data is ephemeral (lost once the game starts), this is an acceptable trade-off for the massive performance gain.

### 6.3 Latency vs. Bandwidth
*   **Decision**: Send full lobby state snapshots on join, but send delta updates (incremental changes) via WebSockets.
*   **Trade-off**: Delta updates reduce bandwidth usage and latency but increase the complexity of the client-side state management, as the client must now maintain a local copy of the lobby state and apply patches.
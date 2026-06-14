# Multiplayer Game Lobby LLD

A **Multiplayer Game Lobby** is a critical middleware component in online gaming. It acts as a synchronization point where players gather, configure game settings, and agree to start a session before the heavy lifting of the game engine takes over. Designing this requires a deep understanding of **concurrency**, **state management**, and **event-driven communication**.

---

## 1. Overview & System Requirements

### Core Objective
To design a system that allows players to create, join, and manage game lobbies, ensuring that game sessions start only when specific criteria (e.g., minimum players, all players ready) are met.

### Functional Requirements
- **Lobby Lifecycle**: Players can create a lobby, join an existing one via an ID, or leave a lobby.
- **Role Management**: The creator of the lobby is the **Host**, who has exclusive rights to change settings and start the game.
- **Ready System**: Players must toggle a "Ready" state. The game cannot start until the host triggers it (and usually, all players are ready).
- **Capacity Management**: Lobbies have a maximum player limit.
- **Lobby Discovery**: Ability to list public lobbies.
- **Concurrency**: Handle multiple players attempting to join the same lobby simultaneously without exceeding capacity.

### Non-Functional Requirements
- **Thread Safety**: Prevent race conditions during the `join` and `leave` operations.
- **Scalability**: The `LobbyManager` should handle thousands of active lobbies.
- **Low Latency**: Joining and status updates must be near-instantaneous.

---

## 2. Design Principles & Patterns

### OOP Design Principles
- **Single Responsibility Principle (SRP)**: 
    - `Lobby`: Manages the state of a specific group of players.
    - `LobbyManager`: Manages the collection of all active lobbies.
    - `Player`: Represents the user entity.
- **Open/Closed Principle**: The matchmaking logic is abstracted so that new matchmaking strategies (e.g., Skill-based vs. Random) can be added without modifying the `Lobby` class.

### Design Patterns Applied
| Pattern | Application | Why? |
| :--- | :--- | :--- |
| **Singleton** | `LobbyManager` | Ensures there is one central registry for all active lobbies across the server. |
| **Observer** | `Lobby` $\rightarrow$ `Player` | Notifies all players in a lobby when a new player joins, leaves, or changes their ready status. |
| **Strategy** | `MatchmakingStrategy` | Allows switching between different ways of finding a lobby (Public search, Friend invite, Ranked queue). |
| **State Pattern** | `LobbyStatus` | Manages transitions between `WAITING`, `READY_TO_START`, and `IN_GAME`. |

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
+-------------------+       1       +-------------------+
|   LobbyManager    |<--------------|      Lobby        |
+-------------------+               +-------------------+
| - lobbies: Map    |               | - lobbyId: UUID    |
| + createLobby()   |               | - players: List    |
| + joinLobby()     |               | - host: Player     |
| + getLobby()      |               | - status: Status   |
+-------------------+               | + addPlayer()      |
                                    | + removePlayer()   |
                                    | + setReady()       |
                                    +-------------------+
                                              | *
                                              v
                                    +-------------------+
                                    |      Player       |
                                    +-------------------+
                                    | - playerId: UUID   |
                                    | - username: String |
                                    | - isReady: Boolean |
                                    +-------------------+
```

### Relationships
- **LobbyManager $\rightarrow$ Lobby**: One-to-Many (Composition). The manager owns the lifecycle of the lobbies.
- **Lobby $\rightarrow$ Player**: Many-to-Many (Association). A lobby contains multiple players; a player can be in one lobby at a time.
- **Lobby $\rightarrow$ LobbyStatus**: Composition. Defines the current phase of the lobby.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
import threading
import uuid
from enum import Enum
from typing import Dict, List, Optional

class LobbyStatus(Enum):
    WAITING = 1
    READY_TO_START = 2
    IN_GAME = 3

class Player:
    def __init__(self, username: str):
        self.player_id = uuid.uuid4()
        self.username = username
        self.is_ready = False

    def __repr__(self):
        return f"Player({self.username}, Ready={self.is_ready})"

class Lobby:
    def __init__(self, host: Player, max_capacity: int = 4):
        self.lobby_id = uuid.uuid4()
        self.host = host
        self.max_capacity = max_capacity
        self.players: Dict[uuid.UUID, Player] = {host.player_id: host}
        self.status = LobbyStatus.WAITING
        self._lock = threading.RLock()  # Ensure thread safety for lobby operations

    def add_player(self, player: Player) -> bool:
        with self._lock:
            if len(self.players) >= self.max_capacity:
                print(f"Lobby {self.lobby_id} is full!")
                return False
            self.players[player.player_id] = player
            print(f"{player.username} joined lobby {self.lobby_id}")
            return True

    def remove_player(self, player_id: uuid.UUID):
        with self._lock:
            if player_id in self.players:
                removed_player = self.players.pop(player_id)
                print(f"{removed_player.username} left the lobby.")
                
                # If host leaves, assign a new host
                if player_id == self.host.player_id and self.players:
                    self.host = list(self.players.values())[0]
                    print(f"New host assigned: {self.host.username}")
            return True

    def set_ready(self, player_id: uuid.UUID, ready: bool):
        with self._lock:
            if player_id in self.players:
                self.players[player_id].is_ready = ready
                self._update_status()

    def _update_status(self):
        # If all players are ready, move to READY_TO_START
        if all(p.is_ready for p in self.players.values()) and len(self.players) > 1:
            self.status = LobbyStatus.READY_TO_START
        else:
            self.status = LobbyStatus.WAITING

    def start_game(self, player_id: uuid.UUID):
        with self._lock:
            if player_id != self.host.player_id:
                print("Only the host can start the game!")
                return False
            if self.status != LobbyStatus.READY_TO_START:
                print("Not all players are ready!")
                return False
            
            self.status = LobbyStatus.IN_GAME
            print(f"Game started for lobby {self.lobby_id}!")
            return True

class LobbyManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LobbyManager, cls).__new__(cls)
                cls._instance.lobbies = {}
        return cls._instance

    def create_lobby(self, host: Player) -> Lobby:
        lobby = Lobby(host)
        self.lobbies[lobby.lobby_id] = lobby
        return lobby

    def join_lobby(self, lobby_id: uuid.UUID, player: Player) -> bool:
        lobby = self.lobbies.get(lobby_id)
        if not lobby:
            print("Lobby not found.")
            return False
        return lobby.add_player(player)

    def leave_lobby(self, lobby_id: uuid.UUID, player_id: uuid.UUID):
        lobby = self.lobbies.get(lobby_id)
        if lobby:
            lobby.remove_player(player_id)
            # Cleanup empty lobbies
            if not lobby.players:
                del self.lobbies[lobby_id]

# --- Testing the Implementation ---
if __name__ == "__main__":
    manager = LobbyManager()
    
    p1 = Player("Alice")
    p2 = Player("Bob")
    p3 = Player("Charlie")

    # Alice creates a lobby
    lobby = manager.create_lobby(p1)
    lobby_id = lobby.lobby_id

    # Bob and Charlie join
    manager.join_lobby(lobby_id, p2)
    manager.join_lobby(lobby_id, p3)

    # Players set ready
    lobby.set_ready(p1.player_id, True)
    lobby.set_ready(p2.player_id, True)
    
    # Try to start game (Should fail because Charlie isn't ready)
    lobby.start_game(p1.player_id)

    lobby.set_ready(p3.player_id, True)
    
    # Alice starts the game
    lobby.start_game(p1.player_id)
```

### Logic Walkthrough

1.  **Thread Safety**: I used `threading.RLock()` (Re-entrant Lock) within the `Lobby` class. This ensures that if a method calls another method within the same class (e.g., `set_ready` calls `_update_status`), the thread won't deadlock itself.
2.  **Host Transition**: In `remove_player`, if the `player_id` matches the `host`, the system automatically promotes the next available player to host. This prevents the lobby from becoming "orphaned."
3.  **State Transition**: The `_update_status` method acts as a state checker. It ensures the lobby only moves to `READY_TO_START` when the logical predicate (All players ready $\land$ Count $> 1$) is true.
4.  **Singleton Manager**: The `LobbyManager` uses the `__new__` method to implement the Singleton pattern, ensuring that no matter where in the application the manager is called, it accesses the same pool of lobbies.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Create Lobby** | $O(1)$ | $O(1)$ | Adding to a Hash Map. |
| **Join Lobby** | $O(1)$ | $O(1)$ | Map lookup and list append. |
| **Leave Lobby** | $O(1)$ | $O(1)$ | Map removal. |
| **Set Ready** | $O(P)$ | $O(1)$ | $P$ = Number of players (to check all ready states). |
| **Start Game** | $O(1)$ | $O(1)$ | Simple state check and update. |

---

## 6. Real-World Applications

This LLD pattern is used extensively in:
- **Competitive Gaming (e.g., League of Legends, Valorant)**: The lobby system handles player invites, champion selection (a specialized state), and the final transition to the game server.
- **Virtual Meeting Rooms (e.g., Zoom, Microsoft Teams)**: The "Waiting Room" is essentially a game lobby where the host decides who can enter the main session.
- **Collaborative Tools (e.g., Figma, Google Docs)**: While more seamless, the underlying logic of tracking active users and synchronizing their "presence" (Ready/Away/Typing) follows similar Observer and State patterns.
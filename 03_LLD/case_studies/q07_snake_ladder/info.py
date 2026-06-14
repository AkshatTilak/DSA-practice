INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Snake & Ladder game.',
    'groups': ['OOP Case Studies', 'Game Design'],
    'readme_content': """# Snake & Ladder LLD

## 1. Overview & System Requirements
The Snake & Ladder game is a classic board game where players race to reach the final square of a board. The board contains "snakes" (which move the player backward) and "ladders" (which move the player forward). 

### Core Entities
- **Board**: The grid containing cells and the placement of snakes and ladders.
- **Player**: The participant with a unique identity and a current position on the board.
- **Dice**: The mechanism to generate a random move distance.
- **Jump**: An abstraction for both Snakes and Ladders that changes a player's position.
- **Game**: The orchestrator that manages the game loop, turns, and victory conditions.

### Functional Requirements
- **Configurable Board**: Ability to set the board size and the number of snakes and ladders.
- **Multiplayer Support**: The game should support $N$ number of players.
- **Dice Logic**: A standard 6-sided die. Support for multiple dice can be an extension.
- **Movement Logic**: Players move forward by the dice value. If they land on a ladder, they climb; if they land on a snake, they slide down.
- **Winning Condition**: A player wins by reaching exactly the last cell of the board.
- **Turn Management**: Players take turns in a Round-Robin fashion.

---

## 2. Design Principles & Patterns

### OOP Design Principles
- **Single Responsibility Principle (SRP)**: 
    - `Dice` is only responsible for generating numbers.
    - `Board` is only responsible for the layout and jump mappings.
    - `Game` is only responsible for the game flow and turn management.
- **Open/Closed Principle (OCP)**: The `Jump` class is designed such that we can introduce new types of "special cells" (e.g., Portals, Teleports) without modifying the existing `Board` or `Game` logic.
- **Dependency Inversion**: The `Game` class depends on the `Board` and `Dice` abstractions rather than hardcoded logic, allowing us to swap a `StandardDice` for a `WeightedDice` easily.

### Design Patterns Applied
- **Strategy Pattern**: Used for the dice rolling mechanism. If the game evolves to have different dice types (e.g., 12-sided), the rolling strategy can be swapped.
- **Command/State Management**: The movement of the player can be viewed as a state transition from `current_position` $\to$ `new_position`.
- **Composition**: The `Game` class uses composition by holding references to `Board`, `Dice`, and a queue of `Players`.

---

## 3. Class Structure & Relationships

### Class Diagram (Text-Based)
```mermaid
classDiagram
    class Game {
        - Board board
        - Dice dice
        - Queue players
        - Player winner
        + startGame()
    }
    class Board {
        - int size
        - Map cells
        + getJump(int position)
    }
    class Jump {
        - int start
        - int end
        + getEnd()
    }
    class Player {
        - String name
        - int position
        + getPosition()
        + setPosition()
    }
    class Dice {
        - int sides
        + roll()
    }

    Game --> Board
    Game --> Dice
    Game --> Player
    Board --> Jump
    Jump <|-- Snake
    Jump <|-- Ladder
```

### Attribute Definitions
| Class | Attribute | Type | Description |
| :--- | :--- | :--- | :--- |
| **Player** | `name` | String | Unique identifier for the player. |
| **Player** | `position` | Integer | Current cell index (starts at 0 or 1). |
| **Board** | `size` | Integer | Total cells (e.g., 100). |
| **Board** | `jumps` | Map | Mapping of start cell $\to$ end cell. |
| **Jump** | `start` | Integer | The cell that triggers the jump. |
| **Jump** | `end` | Integer | The destination cell. |
| **Dice** | `sides` | Integer | Max value of a roll (usually 6). |

---

## 4. Step-by-Step Logic & Code Walkthrough

### The Implementation
```python
import random
from collections import deque

class Jump:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class Snake(Jump):
    def __init__(self, start, end):
        super().__init__(start, end)
        if start < end:
            raise ValueError("Snake start must be greater than end")

class Ladder(Jump):
    def __init__(self, start, end):
        super().__init__(start, end)
        if start > end:
            raise ValueError("Ladder start must be less than end")

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0

class Board:
    def __init__(self, size):
        self.size = size
        self.jumps = {}

    def add_jump(self, jump):
        self.jumps[jump.start] = jump.end

    def get_final_position(self, position):
        # If the position is a snake or ladder, return the destination
        return self.jumps.get(position, position)

class Dice:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

class Game:
    def __init__(self, board_size, players_list, snakes, ladders):
        self.board = Board(board_size)
        self.dice = Dice()
        self.players = deque([Player(p) for p in players_list])
        
        for s in snakes: self.board.add_jump(Snake(*s))
        for l in ladders: self.board.add_jump(Ladder(*l))
        
        self.winner = None

    def play(self):
        while not self.winner:
            player = self.players.popleft()
            roll_val = self.dice.roll()
            
            old_pos = player.position
            new_pos = old_pos + roll_val
            
            if new_pos > self.board.size:
                print(f"{player.name} rolled {roll_val} but needs exact number to win. Stays at {old_pos}")
                self.players.append(player)
                continue
            
            # Apply Jump (Snake/Ladder)
            final_pos = self.board.get_final_position(new_pos)
            player.position = final_pos
            
            print(f"{player.name} rolled {roll_val}: {old_pos} -> {new_pos} -> {final_pos}")
            
            if player.position == self.board.size:
                self.winner = player
                print(f"🎉 {player.name} Wins the Game!")
            else:
                self.players.append(player)

# --- Execution ---
if __name__ == "__main__":
    snakes = [(17, 7), (54, 34), (62, 19), (98, 79)]
    ladders = [(3, 38), (24, 33), (42, 63), (72, 91)]
    game = Game(100, ["Alice", "Bob", "Charlie"], snakes, ladders)
    game.play()
```

### Logic Walkthrough
1.  **Initialization**: We initialize a `Board` and populate a map of `jumps`. Snakes and Ladders are treated as the same entity (`Jump`) but validated differently (Snakes go down, Ladders go up).
2.  **Turn Management**: We use a `deque` (Double-Ended Queue) to manage players. The current player is `popleft()`'ed, and if they don't win, they are `append()`'ed back to the end of the queue.
3.  **Movement Logic**:
    - Calculate `new_position = current + roll`.
    - Check if `new_position` exceeds board size (exact win requirement).
    - Check the `jumps` map: If the cell is a key in the map, the player is teleported to the value.
4.  **Termination**: The loop breaks immediately when a player's position equals the `board_size`.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Explanation |
| :--- | :--- | :--- | :--- |
| **Initialization** | $O(S + L)$ | $O(S + L)$ | Where $S$ is snakes and $L$ is ladders. |
| **One Turn** | $O(1)$ | $O(1)$ | Dice roll and map lookup are constant time. |
| **Total Game** | $O(T)$ | $O(P + S + L)$ | $T$ is the number of turns until a win; $P$ is number of players. |

---

## 6. Real-World Applications
While Snake & Ladder is a simple game, the LLD patterns used here are prevalent in production systems:
- **Turn-Based Systems**: The `deque` approach to turn management is used in multiplayer game servers (e.g., Hearthstone, Civilization).
- **Grid-Based Movement**: The logic of "landing on a cell and triggering an event" is the foundation of most RPGs and Strategy games (e.g., Monopoly, Fire Emblem).
- **Event Mapping**: Using a Map to store "special cells" is similar to how **Routing Tables** in networking work, where a specific input (IP/Port) triggers a specific destination (Jump).
- **Validation Logic**: The use of inheritance and `ValueError` in `Snake` vs `Ladder` mirrors how **Domain-Driven Design (DDD)** ensures that business entities are always in a valid state.""",
    'solutions': """# System Design Document: Snake & Ladder Game

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Game Initialization**: Support customizable board sizes (default $10 \times 10$) and a configurable number of snakes and ladders.
*   **Player Management**: Support for 2 or more players.
*   **Gameplay Mechanics**:
    *   Players take turns rolling a 6-sided die.
    *   Players move forward by the number shown on the die.
    *   If a player lands on the head of a **Snake**, they move down to the tail.
    *   If a player lands on the base of a **Ladder**, they move up to the top.
    *   A player must land **exactly** on the final square to win. If the roll exceeds the final square, the player stays in place.
*   **Win Condition**: The first player to reach the final square is declared the winner.
*   **State Persistence**: Ability to track the current position of all players and whose turn it is.

### 1.2 Non-Functional Requirements
*   **Consistency**: The sequence of turns and the movement logic must be strictly consistent.
*   **Low Latency**: Dice rolls and position updates should reflect in real-time (sub-100ms).
*   **Extensibility**: The system should easily support different board sizes, different dice (e.g., 8-sided), or new special tiles (e.g., "roll again" or "skip turn").
*   **Fairness**: Dice rolls must be generated server-side to prevent client-side manipulation.

### 1.3 Scale Estimations
*   **Concurrent Games**: Assume $10^5$ concurrent games.
*   **Traffic**: Average of 1 roll every 5 seconds per player. For a 4-player game, that's $\approx 0.8$ requests per second per game.
*   **Total Load**: $\approx 80,000$ requests per second (RPS) at peak. This necessitates a distributed state management approach.

---

## 2. High-Level Architecture

### 2.1 Core Components
1.  **Game Manager**: Orchestrates game creation, player joining, and turn management.
2.  **Board Engine**: Contains the logic for the grid, snakes, ladders, and boundary checks.
3.  **Dice Service**: A utility to generate cryptographically secure random numbers.
4.  **State Store**: A fast, in-memory store (Redis) to maintain active game sessions.
5.  **Notification Service**: Uses WebSockets/Socket.io to push movement updates to all players in a session.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
sequenceDiagram
    participant P1 as Player 1
    participant P2 as Player 2
    participant GS as Game Server
    participant RS as Redis State Store
    participant WS as WebSocket Service

    P1->>GS: Create Game (BoardSize, NumPlayers)
    GS->>RS: Initialize Game State (Positions=0, Turn=P1)
    GS-->>P1: GameID returned
    P2->>GS: Join Game (GameID)
    GS->>RS: Add Player P2 to GameID
    GS-->>P2: Joined Successfully

    Note over P1, P2: Game Start
    P1->>GS: Roll Dice (GameID)
    GS->>GS: Generate Random(1-6)
    GS->>RS: Update P1 Position & Switch Turn to P2
    RS-->>GS: New State (P1: 15, Turn: P2)
    GS->>WS: Broadcast Update (Player 1 moved to 15)
    WS-->>P1: Position Updated
    WS-->>P2: Position Updated
```

---

## 3. Detailed Database Schema Design

Since active game states are ephemeral and require high-frequency updates, we use a **Hybrid Storage Strategy**:
*   **Redis**: For active game sessions (Hot Data).
*   **PostgreSQL**: For user profiles, game history, and board configurations (Cold Data).

### 3.1 SQL Schema (PostgreSQL)

**Table: `users`**
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier for the player |
| `username` | VARCHAR(50) | Unique, Not Null | Display name |
| `created_at` | TIMESTAMP | Not Null | Account creation date |

**Table: `board_configs`**
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `config_id` | UUID | PK | Unique identifier for a board layout |
| `size` | INT | Not Null | e.g., 100 for $10 \times 10$ |
| `created_at` | TIMESTAMP | Not Null | Layout creation date |

**Table: `special_squares`**
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PK | |
| `config_id` | UUID | FK $\to$ board_configs | Links to a specific board |
| `start_pos` | INT | Not Null | Head of snake or base of ladder |
| `end_pos` | INT | Not Null | Tail of snake or top of ladder |
| `type` | ENUM | 'SNAKE', 'LADDER' | Type of jump |

### 3.2 Redis Schema (NoSQL)
We use a Hash structure for each game session:
**Key**: `game:{game_id}`
**Fields**:
*   `board_size`: Integer
*   `current_turn_player_id`: String
*   `status`: `WAITING` | `ACTIVE` | `FINISHED`
*   `player_positions`: JSON String `{"user_1": 12, "user_2": 5}`
*   `turn_order`: JSON List `["user_1", "user_2"]`

---

## 4. Core API Design

### 4.1 API Endpoints

| Method | Endpoint | Description | Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/game/create` | Initialize a new game | `{ "board_id": "uuid", "players": 2 }` | `{ "game_id": "uuid" }` |
| `POST` | `/api/v1/game/join` | Join an existing game | `{ "game_id": "uuid", "user_id": "uuid" }` | `{ "status": "joined" }` |
| `POST` | `/api/v1/game/roll` | Roll the die for current turn | `{ "game_id": "uuid", "user_id": "uuid" }` | `{ "roll": 4, "new_pos": 18, "next_turn": "user_2" }` |
| `GET` | `/api/v1/game/{id}` | Get current game state | `N/A` | `{ "positions": {...}, "turn": "user_id" }` |

### 4.2 Sample Request/Response (Roll Dice)
**Request:**
```json
{
  "game_id": "game-123",
  "user_id": "user-456"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "dice_value": 4,
    "start_position": 10,
    "end_position": 14,
    "jump_occurred": {
      "type": "LADDER",
      "destination": 25
    },
    "final_position": 25,
    "next_player_id": "user-789",
    "winner": null
  }
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Concurrency Control
To prevent a player from rolling twice or rolling out of turn:
*   **Distributed Locking**: Use Redis `SET NX` (set if not exists) on a key `lock:game:{game_id}` during the processing of a roll. This ensures that only one request is processed per game at a time.
*   **Optimistic Locking**: Version the game state in Redis. If the version changed between the read and write, the request is rejected.

### 5.2 Real-time Updates
*   **WebSocket Integration**: Instead of polling `/game/{id}`, the server pushes the updated state to a WebSocket room identified by `game_id`.
*   **Pub/Sub**: When a Game Server updates the state in Redis, it publishes a message to a Redis Pub/Sub channel. All WebSocket servers subscribed to that channel push the update to connected clients.

### 5.3 Fault Tolerance
*   **State Recovery**: Since the state is in Redis, if a Game Server instance crashes, another instance can pick up the session seamlessly.
*   **Persistence Backup**: Periodically snapshot the Redis state to the SQL database to allow for game resumption after a total cache failure.

### 5.4 Fairness and RNG
*   Use a cryptographically secure pseudo-random number generator (CSPRNG) on the server side to prevent "roll hacking" via client-side scripts.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priorities
In a Snake & Ladder game, **Consistency (C)** and **Availability (A)** are prioritized over **Partition Tolerance (P)** within a single game session.
*   **Why?** It is unacceptable for two players to think it is their turn simultaneously. We use a centralized state store (Redis) to ensure strong consistency for a specific `game_id`.

### 6.2 Latency vs. Storage
*   **Trade-off**: We store the board configuration (snakes/ladders) in a SQL DB but cache it in the Game Server's local memory upon game start.
*   **Reasoning**: Board configurations rarely change. Caching them locally reduces the need to query the DB on every single roll, reducing latency from $\approx 10\text{ms}$ (DB) to $< 1\text{ms}$ (RAM).

### 6.3 WebSocket vs. Long Polling
*   **Trade-off**: WebSockets increase server memory overhead (keeping connections open).
*   **Reasoning**: For a game, the UX of seeing a piece move in real-time is critical. The overhead is justified by the significantly better user experience.

---

## 7. LLD Class Diagram (Conceptual)

```java
class Game {
    GameId id;
    Board board;
    List<Player> players;
    int currentTurnIndex;
    GameStatus status;
    
    void playTurn(Player player) {
        if (player != players.get(currentTurnIndex)) throw new IllegalTurnException();
        int roll = dice.roll();
        int newPos = board.movePlayer(players.get(currentTurnIndex), roll);
        if (newPos == board.getSize()) {
            this.status = GameStatus.FINISHED;
        } else {
            currentTurnIndex = (currentTurnIndex + 1) % players.size();
        }
    }
}

class Board {
    int size;
    Map<Integer, Jump> jumps; // Stores both Snakes and Ladders
    
    int movePlayer(Player p, int roll) {
        int nextPos = p.getPosition() + roll;
        if (nextPos > size) return p.getPosition(); // Must land exactly
        if (jumps.containsKey(nextPos)) {
            return jumps.get(nextPos).getEndPosition();
        }
        return nextPos;
    }
}

abstract class Jump {
    int startPos;
    int endPos;
    abstract String getType();
}

class Snake extends Jump { String getType() { return "SNAKE"; } }
class Ladder extends Jump { String getType() { return "LADDER"; } }
```""",
}

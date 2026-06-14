INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Chess Game.',
    'groups': ['OOP Case Studies', 'Game Design'],
    'readme_content': """# Chess Game LLD

This study guide provides a professional-grade Low-Level Design (LLD) for a Chess Game. Designing Chess is a classic LLD challenge that tests a candidate's ability to handle complex rule sets, state management, and polymorphic behavior.

---

## 1. Overview & System Requirements

The goal is to design a software system that simulates a standard game of Chess. The system must enforce the rules of movement, track the game state, and determine the outcome (Checkmate, Stalemate, or Draw).

### Core Entities
- **Game**: The orchestrator that manages players, turns, and the game loop.
- **Board**: An $8 \times 8$ grid of cells.
- **Cell/Spot**: A specific coordinate on the board that may or may not hold a piece.
- **Piece**: An abstract entity representing a chess piece (King, Queen, Rook, Bishop, Knight, Pawn).
- **Player**: The actor who makes moves.
- **Move**: A record of a piece moving from one cell to another.

### Functional Requirements
- **Initialization**: Setup the board with standard starting positions for white and black.
- **Move Validation**: 
    - Validate based on the specific movement rules of each piece.
    - Prevent moves that leave the player's own King in check.
- **Special Moves**: Support for **Castling**, **En Passant**, and **Pawn Promotion**.
- **Game State**: Detect **Check**, **Checkmate**, and **Stalemate**.
- **Turn Management**: Strict alternation between White and Black.

---

## 2. Design Principles & Patterns

### OOP Principles Applied
- **Single Responsibility Principle (SRP)**: 
    - `Piece` classes only handle *how* they move.
    - `Board` handles *where* pieces are.
    - `Game` handles *when* moves happen and overall win/loss logic.
- **Open/Closed Principle (OCP)**: The system is open for extension. If we wanted to add a "Chess Variant" (e.g., adding a "Chancellor" piece), we can simply extend the `Piece` class without modifying the `Game` or `Board` logic.
- **Liskov Substitution Principle (LSP)**: Any subclass of `Piece` (e.g., `Knight`) can be used wherever a `Piece` object is expected without breaking the system.

### Design Patterns
| Pattern | Application | Why? |
| :--- | :--- | :--- |
| **Strategy Pattern** | Move Validation | Each piece implements its own movement strategy. The `Board` doesn't need to know the rules for a Knight vs. a Bishop. |
| **Factory Pattern** | Piece Creation | A `PieceFactory` can be used to instantiate pieces based on type and color, decoupling the creation logic from the board setup. |
| **Command Pattern** | Move Execution | By encapsulating a move as an object, we can easily implement "Undo" functionality by keeping a stack of `Move` objects. |
| **Singleton Pattern** | Game Instance | Ensuring only one active game session exists per board instance (optional). |

---

## 3. Class Structure & Relationships

### Class Diagram (Text-Based)

```mermaid
classDiagram
    Game "1" --> "1" Board
    Game "1" --> "2" Player
    Board "1" --> "64" Spot
    Spot "1" --> "0..1" Piece
    Piece <|-- King
    Piece <|-- Queen
    Piece <|-- Rook
    Piece <|-- Bishop
    Piece <|-- Knight
    Piece <|-- Pawn
    Move "1" --> "1" Piece
    Move "1" --> "2" Spot
```

### Relationship Details
- **Composition**: `Board` is composed of `Spot` objects.
- **Inheritance**: `King`, `Queen`, etc., inherit from the abstract `Piece` class.
- **Association**: `Move` associates a `Piece`, a starting `Spot`, and an ending `Spot`.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple, Optional

class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece(ABC):
    def __init__(self, color: Color):
        self.color = color

    @abstractmethod
    def can_move(self, board: 'Board', start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        pass

# --- Concrete Piece Implementations ---

class Knight(Piece):
    def can_move(self, board, start, end) -> bool:
        sx, sy = start
        ex, ey = end
        dx, dy = abs(sx - ex), abs(sy - ey)
        # Knight moves in L-shape: (1,2) or (2,1)
        if not ((dx == 1 and dy == 2) or (dx == 2 and dy == 1)):
            return False
        # Check if target is occupied by own piece
        target_piece = board.get_piece(ex, ey)
        if target_piece and target_piece.color == self.color:
            return False
        return True

class Bishop(Piece):
    def can_move(self, board, start, end) -> bool:
        sx, sy = start
        ex, ey = end
        if abs(sx - ex) != abs(sy - ey): return False
        if board.is_path_blocked(start, end): return False
        target_piece = board.get_piece(ex, ey)
        return not (target_piece and target_piece.color == self.color)

class Rook(Piece):
    def can_move(self, board, start, end) -> bool:
        sx, sy = start
        ex, ey = end
        if sx != ex and sy != ey: return False
        if board.is_path_blocked(start, end): return False
        target_piece = board.get_piece(ex, ey)
        return not (target_piece and target_piece.color == self.color)

class Queen(Piece):
    def can_move(self, board, start, end) -> bool:
        # Queen is Rook + Bishop
        return Rook(self.color).can_move(board, start, end) or \
               Bishop(self.color).can_move(board, start, end)

class King(Piece):
    def can_move(self, board, start, end) -> bool:
        sx, sy = start
        ex, ey = end
        if max(abs(sx - ex), abs(sy - ey)) != 1: return False
        target_piece = board.get_piece(ex, ey)
        return not (target_piece and target_piece.color == self.color)

class Pawn(Piece):
    def can_move(self, board, start, end) -> bool:
        sx, sy = start
        ex, ey = end
        direction = -1 if self.color == Color.WHITE else 1
        # Simplified pawn logic for brevity
        if sy == ey and ex == sx + direction:
            return board.get_piece(ex, ey) is None
        # Capture logic
        if abs(sy - ey) == 1 and ex == sx + direction:
            target = board.get_piece(ex, ey)
            return target is not None and target.color != self.color
        return False

# --- Board and Game Orchestration ---

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self._setup_board()

    def _setup_board(self):
        # Standard chess setup logic here
        self.grid[0][0] = Rook(Color.BLACK)
        self.grid[0][1] = Knight(Color.BLACK)
        # ... remaining pieces
        self.grid[7][0] = Rook(Color.WHITE)
        self.grid[7][1] = Knight(Color.WHITE)

    def get_piece(self, x, y) -> Optional[Piece]:
        return self.grid[x][y]

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]):
        sx, sy = start
        ex, ey = end
        self.grid[ex][ey] = self.grid[sx][sy]
        self.grid[sx][sy] = None

    def is_path_blocked(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        sx, sy = start
        ex, ey = end
        dx = 1 if ex > sx else -1 if ex < sx else 0
        dy = 1 if ey > sy else -1 if ey < sy else 0
        
        curr_x, curr_y = sx + dx, sy + dy
        while (curr_x, curr_y) != (ex, ey):
            if self.grid[curr_x][curr_y] is not None:
                return True
            curr_x += dx
            curr_y += dy
        return False

class Game:
    def __init__(self):
        self.board = Board()
        self.turn = Color.WHITE
        self.game_over = False

    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]):
        if self.game_over:
            print("Game is already over.")
            return

        piece = self.board.get_piece(*start)
        if not piece or piece.color != self.turn:
            print("Invalid piece selection.")
            return

        if piece.can_move(self.board, start, end):
            self.board.move_piece(start, end)
            self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
            print(f"Move successful. Next turn: {self.turn.name}")
        else:
            print("Illegal move!")

# --- Execution ---
if __name__ == "__main__":
    chess_game = Game()
    # White Knight moves from (7,1) to (5,2)
    chess_game.make_move((7, 1), (5, 2))
```

### Logic Walkthrough
1.  **`Piece` Hierarchy**: We use an abstract base class `Piece`. Each specific piece implements `can_move`. This ensures that the `Board` doesn't contain a massive `if-elif` block to determine movement rules.
2.  **`Board.is_path_blocked`**: This is a critical helper method. For sliding pieces (Rook, Bishop, Queen), we must check every cell between the start and end coordinates to ensure no other piece is in the way.
3.  **`Game.make_move`**: This acts as the controller. It validates:
    - If the game is still active.
    - If the piece exists and belongs to the current player.
    - If the piece's specific `can_move` logic returns `True`.
4.  **Turn Switching**: After a successful move, the `self.turn` is toggled.

---

## 5. Real-World Applications

While this is a game, the LLD patterns used here are common in enterprise software:

1.  **Strategy Pattern $\rightarrow$ Payment Gateways**: Just as different pieces have different move strategies, different payment methods (PayPal, Stripe, Crypto) have different `process_payment()` strategies.
2.  **Command Pattern $\rightarrow$ Text Editors**: The `Move` object approach is exactly how "Undo/Redo" works in IDEs like VS Code or IntelliJ. Every keystroke/action is encapsulated as a command.
3.  **State Management $\rightarrow$ Workflow Engines**: The turn-based logic of Chess is similar to state machines used in Order Management Systems (e.g., `Ordered` $\rightarrow$ `Paid` $\rightarrow$ `Shipped` $\rightarrow$ `Delivered`).
4.  **Grid-based systems $\rightarrow$ Logistics/Warehouse**: The `Board` and `Spot` logic is used in warehouse management systems to track robot positions and inventory slots in a coordinate system.

## Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Piece Movement** | $O(1)$ | $O(1)$ | Constant time for Knight/King. |
| **Sliding Move Validation** | $O(N)$ | $O(1)$ | Where $N$ is the board dimension (max 8). |
| **Board Initialization** | $O(N^2)$ | $O(N^2)$ | Initializing 64 cells. |
| **Check/Checkmate Detection**| $O(P \times N^2)$ | $O(1)$ | $P$ = number of pieces; must scan all possible moves. |""",
    'solutions': """# System Design Document: Online Chess Game

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Game Lifecycle**: Users should be able to create a game, invite a friend, or join a public matchmaking queue.
*   **Move Validation**: The system must enforce all official FIDE chess rules (e.g., piece movement, castling, en passant, promotion).
*   **Game State Management**: Track turn-based play, check, checkmate, stalemate, and draw conditions (50-move rule, threefold repetition).
*   **Real-time Updates**: Moves must be reflected on the opponent's board in near real-time.
*   **Game History**: Every move must be persisted to allow game replay (PGN format) and analysis.
*   **Player Profiles**: Track player statistics, win/loss ratios, and ELO ratings.
*   **Timer Management**: Support for blitz/rapid clocks with automatic forfeiture on time-out.

### 1.2 Non-Functional Requirements
*   **Low Latency**: Move propagation should be $< 200\text{ms}$ to ensure a seamless experience.
*   **High Consistency**: The board state must be strictly consistent; two players cannot see different versions of the board.
*   **Availability**: The system should be highly available, though consistency takes priority over availability during a move dispute (CAP theorem).
*   **Scalability**: Support millions of concurrent games and users.

### 1.3 Scale Estimations
*   **Concurrent Users**: $10^6$ active users.
*   **Concurrent Games**: $5 \times 10^5$ active games.
*   **Write Volume**: Each game averages 40 moves. $5 \times 10^5$ games $\times$ 40 moves = $2 \times 10^7$ move records per game session.
*   **Read Volume**: High frequency of board state polling or WebSocket pushes.

---

## 2. High-Level Architecture

The system follows a microservices architecture to decouple matchmaking, game logic, and user management.

### 2.1 Core Components
1.  **API Gateway**: Handles authentication, rate limiting, and request routing.
2.  **Matchmaking Service**: Pairs players based on ELO ratings using a queue-based system.
3.  **Game Service**: The "Brain." Validates moves, updates board state, and detects game-over conditions.
4.  **WebSocket Server (Real-time Engine)**: Maintains persistent connections with clients to push moves and clock updates.
5.  **State Store (Redis)**: Stores the active board state for low-latency access.
6.  **Persistence Layer (PostgreSQL)**: Stores user profiles and historical game data.

### 2.2 Architecture Diagram

```mermaid
graph TD
    UserA[Player A] -->|WebSocket/HTTP| AGW[API Gateway]
    UserB[Player B] -->|WebSocket/HTTP| AGW
    AGW --> MatchSvc[Matchmaking Service]
    AGW --> GameSvc[Game Service]
    AGW --> WS[WebSocket Server]
    
    MatchSvc --> RedisQueue[(Redis Match Queue)]
    GameSvc --> RedisState[(Redis Game State)]
    GameSvc --> DB[(PostgreSQL DB)]
    
    WS <--> GameSvc
    WS <--> RedisState
```

### 2.3 Sequence Flow: Making a Move
1.  **Player A** sends a move `(from: e2, to: e4)` via WebSocket.
2.  **WebSocket Server** forwards the request to the **Game Service**.
3.  **Game Service** fetches the current state from **Redis**.
4.  **Game Service** validates the move against Chess rules.
5.  If valid:
    *   Updates the board state in **Redis**.
    *   Appends the move to the **PostgreSQL** move history.
    *   Checks for Checkmate/Stalemate.
6.  **Game Service** notifies the **WebSocket Server**.
7.  **WebSocket Server** pushes the updated state/move to **Player B**.

---

## 3. Detailed Database Schema Design

### 3.1 Storage Strategy
*   **Redis (In-Memory)**: Used for "Hot" data. Active games are stored as FEN (Forsyth-Edwards Notation) strings for compactness.
*   **PostgreSQL (Relational)**: Used for "Cold" data. ACID compliance is required for ELO updates and game records.

### 3.2 Schema

#### Table: `users`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier |
| `username` | VARCHAR(50) | Unique, Index | Display name |
| `elo_rating` | INT | Default 1200 | Current skill rating |
| `created_at` | TIMESTAMP | | Account creation date |

#### Table: `games`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `game_id` | UUID | PK | Unique identifier |
| `white_player_id`| UUID | FK $\rightarrow$ users | Player playing white |
| `black_player_id`| UUID | FK $\rightarrow$ users | Player playing black |
| `status` | ENUM | ACTIVE, WHITE_WIN, BLACK_WIN, DRAW | Current status |
| `start_time` | TIMESTAMP | | Game start time |
| `end_time` | TIMESTAMP | | Game end time |
| `final_pgn` | TEXT | | Full game record in PGN format |

#### Table: `moves`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `move_id` | BIGSERIAL | PK | Unique move ID |
| `game_id` | UUID | FK $\rightarrow$ games, Index | Link to game |
| `move_number` | INT | | Sequence of move (1, 2...) |
| `player_id` | UUID | FK $\rightarrow$ users | Who made the move |
| `move_notation` | VARCHAR(10) | | Standard Algebraic Notation (e.g., "Nf3") |
| `board_state` | TEXT | | FEN string after move |
| `timestamp` | TIMESTAMP | | Execution time |

### 3.3 Indexing Strategy
*   `moves(game_id)`: Essential for reconstructing a game history for replay.
*   `games(white_player_id), games(black_player_id)`: To fetch a user's game history.
*   `users(elo_rating)`: To optimize the matchmaking query.

---

## 4. Core API Design

### 4.1 REST Endpoints

#### `POST /api/v1/games`
*   **Description**: Create a new game.
*   **Payload**: `{"opponent_id": "uuid", "time_control": "10+0"}`
*   **Response**: `201 Created` $\rightarrow$ `{"game_id": "uuid", "color": "white"}`

#### `GET /api/v1/games/{game_id}`
*   **Description**: Fetch current game state.
*   **Response**: `200 OK` $\rightarrow$ `{"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "turn": "black"}`

#### `GET /api/v1/users/{user_id}/stats`
*   **Description**: Get player ELO and history.
*   **Response**: `200 OK` $\rightarrow$ `{"elo": 1540, "wins": 45, "losses": 30, "draws": 10}`

### 4.2 WebSocket Events

| Event | Direction | Payload | Description |
| :--- | :--- | :--- | :--- |
| `join_game` | Client $\rightarrow$ Server | `{"game_id": "uuid"}` | Subscribe to game updates |
| `make_move` | Client $\rightarrow$ Server | `{"game_id": "uuid", "move": "e2e4"}` | Submit a move |
| `move_update` | Server $\rightarrow$ Client | `{"move": "e2e4", "fen": "...", "turn": "black"}` | Notify opponent of move |
| `game_over` | Server $\rightarrow$ Client | `{"winner": "white", "reason": "checkmate"}` | Notify end of game |
| `clock_tick` | Server $\rightarrow$ Client | `{"white_time": 300, "black_time": 305}` | Sync timers |

---

## 5. Scalability & Advanced Topics

### 5.1 Real-time Synchronization & Concurrency
To prevent "race conditions" (e.g., both players moving simultaneously due to lag), the Game Service implements **Optimistic Locking** using a version number in Redis.
*   Each game state in Redis has a `version`.
*   The move request must include the `version` the client saw.
*   If `request_version != current_version`, the move is rejected (Out-of-sync).

### 5.2 Matchmaking Algorithm
For high-scale matchmaking:
1.  Users enter a **Redis Sorted Set** where the `score` is their ELO.
2.  A background worker scans the set for players within a range `[ELO - $\Delta$, ELO + $\Delta$]`.
3.  The range $\Delta$ expands over time (e.g., every 5 seconds) to ensure players eventually find a match.

### 5.3 Clock Management
Timers cannot be managed solely on the client.
*   The server maintains a `last_move_timestamp`.
*   On every move, the server calculates: $\text{TimeUsed} = \text{CurrentTime} - \text{last\_move\_timestamp}$.
*   The server deducts this from the player's remaining time in Redis.
*   A heartbeat mechanism triggers a "Timeout" event if no move is received within the remaining time.

### 5.4 Caching & Performance
*   **Board State**: Always cached in Redis. FEN strings are used because they are standard, compact, and easily parsed by chess engines.
*   **ELO Cache**: User ratings are cached in Redis to avoid frequent DB reads during matchmaking.

---

## 6. Trade-off Analysis

### 6.1 Consistency vs. Availability (CAP)
In a competitive game, **Consistency (C)** is non-negotiable. If the network partitions, we prefer to freeze the game (unavailable) rather than allow divergent board states (where Player A thinks they captured a Queen but Player B thinks the Queen moved). We use a **Strong Consistency** model for move validation.

### 6.2 State Storage: SQL vs. NoSQL
*   **Why Redis for Active Games?** Extreme low latency is required for turn-based updates. A relational DB would introduce too much overhead for every single move.
*   **Why PostgreSQL for History?** Game archives and ELO statistics are relational and require complex queries (e.g., "Average ELO of opponents defeated in the last 30 days"). ACID transactions ensure that ELO gains/losses for both players are atomic.

### 6.3 Latency vs. Storage (FEN vs. Move List)
We store the **FEN string** after every move in the `moves` table. 
*   **Trade-off**: This increases storage usage compared to storing only the move notation (e.g., "e4").
*   **Benefit**: It allows the system to restore the board state instantly at any move number without re-simulating the entire game from move 1, significantly reducing latency for "Go back to move X" features.""",
}

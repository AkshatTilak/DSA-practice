# Tic Tac Toe LLD

Tic Tac Toe is a classic case study in Low-Level Design (LLD). While the game logic is simple, the goal of an LLD interview is to demonstrate **extensibility**, **separation of concerns**, and the application of **OOP principles**. A professional implementation should not just work for a 3x3 grid but should be adaptable for an $N \times N$ board and varying numbers of players.

---

## 1. Overview & System Requirements

### Functional Requirements
- **Game Initialization**: Support a configurable board size ($N \times N$).
- **Player Management**: Support two or more players with unique markers (e.g., X, O, Y).
- **Move Validation**: Ensure a player cannot move into an occupied cell or outside board boundaries.
- **Win Detection**: Identify if a player has completed a row, column, or diagonal.
- **Draw Detection**: Identify when the board is full and no winner exists.
- **Turn Management**: Cycle through players sequentially.

### Non-Functional Requirements
- **Extensibility**: Easy to add different winning strategies (e.g., 4-in-a-row on a 5x5 board).
- **Maintainability**: Clear separation between the game engine, the board state, and the players.

---

## 2. Design Principles & Patterns

### OOP Principles Applied
- **Single Responsibility Principle (SRP)**: 
    - `Board` class is only responsible for managing the grid state.
    - `Game` class handles the orchestration of turns and game flow.
    - `Player` class maintains player identity and pieces.
- **Open/Closed Principle (OCP)**: The system is open for extension (e.g., adding a `BotPlayer` via inheritance from `Player`) but closed for modification of the core `Game` loop.
- **Dependency Inversion**: The `Game` class depends on the `Board` abstraction rather than a hardcoded 2D array.

### Design Patterns
- **Strategy Pattern**: Used for the `WinningStrategy`. By encapsulating the win-check logic in a separate strategy, we can change the winning condition (e.g., from "full line" to "four corners") without changing the `Board` or `Game` classes.
- **Factory Pattern (Optional)**: Could be used to instantiate different types of players (Human vs. AI).

---

## 3. Class Structure & Relationships

### Class Diagram (Text-based)
```text
+------------------+          +-------------------+          +-------------------+
|      Game        |<>-------->|      Board        |--------->|  WinningStrategy  |
+------------------+          +-------------------+          +-------------------+
| - players: List  |          | - grid: char[][]  |          | + checkWin()      |
| - board: Board   |          | - size: int       |          +-------------------+
| - turn: int      |          +-------------------+
+------------------+          | + makeMove()      |
| + play()         |          | + isFull()        |
| - nextPlayer()   |          +-------------------+
+------------------+
       |
       | (Composition)
       v
+------------------+
|      Player      |
+------------------+
| - name: String   |
| - piece: Piece   |
+------------------+
```

### Relationships
- **Game $\to$ Player**: Composition (A game consists of players).
- **Game $\to$ Board**: Composition (A game manages one board).
- **Board $\to$ WinningStrategy**: Association (The board uses a strategy to verify if a move resulted in a win).

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from typing import List, Optional
from enum import Enum

class Piece(Enum):
    X = "X"
    O = "O"
    Y = "Y" # For N > 3 players

class Player:
    def __init__(self, name: str, piece: Piece):
        self.name = name
        self.piece = piece

    def __str__(self):
        return f"{self.name} ({self.piece.value})"

class Board:
    def __init__(self, size: int):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]

    def make_move(self, row: int, col: int, piece: Piece) -> bool:
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        if self.grid[row][col] is not None:
            return False
        
        self.grid[row][col] = piece
        return True

    def is_full(self) -> bool:
        for row in self.grid:
            if None in row:
                return False
        return True

    def display(self):
        for row in self.grid:
            print(" | ".join([cell.value if cell else " " for cell in row]))
            print("-" * (self.size * 4 - 1))

class TicTacToeGame:
    def __init__(self, size: int, players: List[Player]):
        self.board = Board(size)
        self.players = players
        self.current_player_idx = 0

    def play(self):
        while True:
            self.board.display()
            player = self.players[self.current_player_idx]
            print(f"Current Turn: {player}")
            
            try:
                row, col = map(int, input("Enter row and col (e.g., 0 1): ").split())
            except ValueError:
                print("Invalid input. Please enter two integers.")
                continue

            if self.board.make_move(row, col, player.piece):
                if self._check_winner(row, col, player.piece):
                    self.board.display()
                    print(f"Congratulations! {player} wins!")
                    break
                
                if self.board.is_full():
                    self.board.display()
                    print("It's a draw!")
                    break
                
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            else:
                print("Invalid move! Try again.")

    def _check_winner(self, row: int, col: int, piece: Piece) -> bool:
        size = self.board.size
        grid = self.board.grid

        # Check Row
        if all(grid[row][i] == piece for i in range(size)):
            return True
        # Check Column
        if all(grid[i][col] == piece for i in range(size)):
            return True
        # Check Main Diagonal
        if row == col and all(grid[i][i] == piece for i in range(size)):
            return True
        # Check Anti-Diagonal
        if row + col == size - 1 and all(grid[i][size - 1 - i] == piece for i in range(size)):
            return True
            
        return False

# Execution
if __name__ == "__main__":
    p1 = Player("Alice", Piece.X)
    p2 = Player("Bob", Piece.O)
    game = TicTacToeGame(3, [p1, p2])
    game.play()
```

### Logic Breakdown
1.  **Move Application**: When a player enters coordinates, the `Game` class asks the `Board` to `make_move`. The board validates boundaries and occupancy before updating the state.
2.  **Efficient Win Checking**: Instead of scanning the entire $N \times N$ board after every turn, the `_check_winner` method only checks the specific row, column, and diagonals intersecting the **last move**. This reduces the check from $O(N^2)$ to $O(N)$.
3.  **Turn Rotation**: Using modulo arithmetic `(idx + 1) % len(players)` allows the game to scale to any number of players seamlessly.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Explanation |
| :--- | :--- | :--- | :--- |
| **Make Move** | $O(1)$ | $O(1)$ | Direct index access in the 2D array. |
| **Check Win** | $O(N)$ | $O(1)$ | We check 1 row, 1 column, and 2 diagonals of length $N$. |
| **Check Draw** | $O(N^2)$ | $O(1)$ | Must scan the grid to ensure no `None` values remain. |
| **Total Space** | - | $O(N^2)$ | Required to store the game board state. |

---

## 6. Real-World Applications

The LLD patterns used here are applied in several production scenarios:

1.  **Turn-Based Strategy Games**: The orchestration logic (Player $\to$ Board $\to$ Turn Manager) is the foundation for games like Chess or Civilization.
2.  **UI State Management**: In frameworks like React or Redux, the "Board" acts as the **State**, and the "Game" logic acts as the **Reducer/Dispatcher**, ensuring state transitions are valid.
3.  **Grid-based Validation Systems**: Similar logic is used in warehouse management systems (slotting) or seating reservation systems where a coordinate must be validated and locked for a specific user.
4.  **Rule Engines**: The separation of `WinningStrategy` mirrors how business rule engines work—separating the data (Board) from the logic that evaluates that data (The Win Condition).
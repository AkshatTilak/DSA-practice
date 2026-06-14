# Splitwise Expense Sharing LLD

This study guide provides a professional low-level design (LLD) for a Splitwise-like expense sharing application. The goal is to create a system that can track expenses, handle different splitting strategies, and maintain a ledger of balances between users.

---

## 1. Overview & System Requirements

The Splitwise system allows a group of users to track shared expenses. When a user pays for something, the cost is distributed among the participants based on a specific split logic. The system must track the net balance for every pair of users.

### Functional Requirements
- **User Management**: Ability to add and manage users.
- **Expense Creation**: Ability to create an expense paid by one user and split among multiple users.
- **Splitting Strategies**: Support for multiple types of splits:
    - **Equal**: The amount is divided equally among all participants.
    - **Exact**: Specific amounts are assigned to each participant.
    - **Percent**: Participants pay a certain percentage of the total amount.
- **Balance Tracking**: Maintain a real-time ledger showing who owes whom and how much.
- **View Balances**: Retrieve the total amount a user owes or is owed.

### Non-Functional Requirements
- **Extensibility**: Adding a new split strategy (e.g., "Split by shares") should not require changing existing business logic.
- **Accuracy**: Financial calculations must be precise.
- **Scalability**: The system should handle a growing number of users and expenses efficiently.

---

## 2. Design Principles & Patterns

To ensure the system is maintainable and robust, the following OOP principles and patterns are applied:

### Design Principles (SOLID)
- **Single Responsibility Principle (SRP)**: The `Expense` class handles the data of a transaction, the `Split` classes handle the calculation logic, and the `ExpenseManager` orchestrates the system.
- **Open/Closed Principle (OCP)**: The system is open for extension (new `Split` types) but closed for modification. We achieve this using the **Strategy Pattern**.
- **Liskov Substitution Principle (LSP)**: Any concrete split (e.g., `PercentSplit`) can be used wherever the base `Split` class is expected without breaking the system.
- **Dependency Inversion Principle (DIP)**: The `ExpenseManager` depends on the `Split` abstraction rather than concrete split implementations.

### Design Patterns
- **Strategy Pattern**: Used to encapsulate different splitting algorithms (Equal, Exact, Percent). This allows the system to switch splitting logic at runtime.
- **Factory Pattern**: Used to instantiate the correct `Expense` and `Split` objects based on the user's input type.
- **Singleton Pattern**: The `ExpenseManager` is implemented as a singleton to ensure a single source of truth for the balance sheet across the application.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
+-------------------+          +---------------------+
|   ExpenseManager   | <------> |       User          |
+-------------------+          +---------------------+
| - users: Map       |          | - userId: String    |
| - balances: Map    |          | - name: String      |
| - expenses: List   |          +---------------------+
| + addExpense()     |                      ^
| + showBalances()   |                      |
+-------------------+                      |
          |                                |
          v                                |
+-------------------+          +---------------------+
|     Expense       | -------->|       Split         | (Abstract)
+-------------------+          +---------------------+
| - id: String       |          | - user: User        |
| - amount: Double   |          | - amount: Double    |
| - paidBy: User     |          +---------------------+
| - splits: List<S>  |                      ^
+-------------------+                      |
                                           |
                 +-------------------------+-------------------------+
                 |                         |                         |
        +-------------------+     +-------------------+     +-------------------+
        |    EqualSplit     |     |    ExactSplit     |     |    PercentSplit   |
        +-------------------+     +-------------------+     +-------------------+
        | (Calculation logic)|     | (Calculation logic)|     | (Calculation logic)|
        +-------------------+     +-------------------+     +-------------------+
```

### Relationship Summary
- **ExpenseManager $\rightarrow$ User**: One-to-Many (Aggregation).
- **Expense $\rightarrow$ User**: Many-to-One (The payer).
- **Expense $\rightarrow$ Split**: One-to-Many (Composition).
- **Split $\rightarrow$ User**: Many-to-One (The person who owes).

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List, Dict

# --- Entities ---
class User:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return f"{self.name}"

class Split(ABC):
    def __init__(self, user: User, amount: float = 0.0):
        self.user = user
        self.amount = amount

class EqualSplit(Split):
    pass

class ExactSplit(Split):
    pass

class PercentSplit(Split):
    def __init__(self, user: User, percent: float):
        super().__init__(user)
        self.percent = percent

# --- Expense Logic ---
class Expense:
    def __init__(self, id: str, amount: float, paid_by: User, splits: List[Split]):
        self.id = id
        self.amount = amount
        self.paid_by = paid_by
        self.splits = splits

# --- Manager (Orchestrator) ---
class ExpenseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExpenseManager, cls).__new__(cls)
            cls._instance.users = {}
            cls._instance.balance_sheet = {} # Map<UserId, Map<UserId, Amount>>
        return cls._instance

    def addUser(self, user: User):
        self.users[user.user_id] = user
        self.balance_sheet[user.user_id] = {}

    def addExpense(self, id: str, amount: float, paid_by_id: str, split_type: str, splits_data: List):
        paid_by = self.users[paid_by_id]
        splits = []
        
        # 1. Calculate amounts based on Strategy
        if split_type == "EQUAL":
            num_users = len(splits_data)
            share = amount / num_users
            for user_id in splits_data:
                splits.append(EqualSplit(self.users[user_id], share))
        
        elif split_type == "EXACT":
            for user_id, amt in splits_data:
                splits.append(ExactSplit(self.users[user_id], amt))
        
        elif split_type == "PERCENT":
            for user_id, pct in splits_data:
                share = (amount * pct) / 100
                splits.append(PercentSplit(self.users[user_id], share))

        # 2. Create Expense object
        expense = Expense(id, amount, paid_by, splits)

        # 3. Update Balance Sheet
        for split in splits:
            # The person who paid gets money from the person in the split
            # Note: We exclude the payer from their own split balance
            if split.user.user_id != paid_by.user_id:
                # User owes Payer
                self.balance_sheet[split.user.user_id][paid_by.user_id] = \
                    self.balance_sheet[split.user.user_id].get(paid_by.user_id, 0) + split.amount
                
                # Payer is owed by User
                self.balance_sheet[paid_by.user_id][split.user.user_id] = \
                    self.balance_sheet[paid_by.user_id].get(split.user.user_id, 0) - split.amount

    def showBalances(self):
        for user_id, balances in self.balance_sheet.items():
            user_name = self.users[user_id].name
            print(f"Balances for {user_name}:")
            for other_id, amount in balances.items():
                other_name = self.users[other_id].name
                if amount > 0:
                    print(f"  Owes {other_name}: {amount:.2f}")
                elif amount < 0:
                    print(f"  Is owed by {other_name}: {abs(amount):.2f}")

# --- Execution ---
def solve():
    manager = ExpenseManager()
    
    # Add Users
    u1 = User("1", "Alice")
    u2 = User("2", "Bob")
    u3 = User("3", "Charlie")
    manager.addUser(u1)
    manager.addUser(u2)
    manager.addUser(u3)

    # Scenario 1: Alice pays 300, split equally among Alice, Bob, Charlie
    manager.addExpense("e1", 300, "1", "EQUAL", ["1", "2", "3"])

    # Scenario 2: Bob pays 100, split exactly (Alice 20, Charlie 80)
    manager.addExpense("e2", 100, "2", "EXACT", [("1", 20), ("3", 80)])

    # Scenario 3: Charlie pays 200, split by percentage (Alice 70%, Bob 30%)
    manager.addExpense("e3", 200, "3", "PERCENT", [("1", 70), ("2", 30)])

    manager.showBalances()

if __name__ == "__main__":
    solve()
```

### Logic Walkthrough
1.  **Initialization**: `ExpenseManager` initializes a nested map `balance_sheet`. If Alice owes Bob \$10, `balance_sheet['Alice']['Bob'] = 10` and `balance_sheet['Bob']['Alice'] = -10`.
2.  **Calculation**: Depending on the `split_type`, the code iterates through the participants and calculates the individual share.
3.  **Ledger Update**: 
    - For every split, the system identifies the `paid_by` user and the `split.user`.
    - It increments the debt of the `split.user` towards the `paid_by` user.
    - It decrements the balance for the `paid_by` user to indicate a credit.
4.  **Complexity**: 
    - Adding an expense takes $O(N)$ where $N$ is the number of participants in that expense.
    - Showing balances takes $O(U^2)$ in the worst case where $U$ is the total number of users.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Description |
| :--- | :--- | :--- | :--- |
| `addUser` | $O(1)$ | $O(1)$ | Adding a user to the hash map. |
| `addExpense` | $O(N)$ | $O(N)$ | $N$ is the number of people splitting the expense. |
| `showBalances`| $O(U^2)$ | $O(1)$ | $U$ is total users; iterates through the balance matrix. |
| **Overall Space**| - | $O(U^2 + E)$ | $U$ users, $E$ total expenses tracked. |

---

## 6. Real-World Applications

This LLD pattern is widely used in systems involving **multi-tenant cost allocation**:
1.  **FinTech Apps**: Applications like Splitwise, Venmo, or Zelle for peer-to-peer debt tracking.
2.  **Cloud Infrastructure**: AWS or Azure "Cost Explorer" where a single corporate account is billed, but costs are split across different departments (Cost Centers) based on percentage of resource usage.
3.  **ERP Systems**: Enterprise Resource Planning software where shared overhead costs (rent, electricity) are allocated to different product lines based on "Exact" or "Percent" strategies.
4.  **Co-working Spaces**: Systems that bill a main company but split the desks' costs among various employees or sub-contractors.
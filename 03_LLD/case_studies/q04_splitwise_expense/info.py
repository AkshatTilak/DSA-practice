INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/design-splitwise-low-level-design/',
    'description': 'Expense share calculations.',
    'type': 'design',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Splitwise Expense Sharing LLD

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
4.  **Co-working Spaces**: Systems that bill a main company but split the desks' costs among various employees or sub-contractors.""",
    'solutions': """# System Design Document: Splitwise Expense Management System

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **User Management**: Users can create profiles, search for other users, and manage their settings.
*   **Group Management**: Users can create groups, invite members, and manage group membership.
*   **Expense Tracking**:
    *   A user can add an expense, specify the total amount, and designate a "payer."
    *   **Split Methods**:
        *   **Equal**: Amount divided equally among participants.
        *   **Exact**: Specific amounts assigned to each participant.
        *   **Percentage**: Percentage of total assigned to each participant.
    *   Expenses can be added to a group or as a non-group transaction.
*   **Balance Tracking**:
    *   The system must track how much each user owes others.
    *   Ability to view "Net Balance" (total owed to the user minus total user owes).
*   **Settlements**: Users can record payments to settle debts.
*   **Debt Simplification**: An algorithm to minimize the number of transactions required to settle all debts within a group (e.g., if A owes B \$10 and B owes C \$10, A just owes C \$10).

### 1.2 Non-Functional Requirements
*   **Consistency**: Financial data must be strictly consistent (ACID properties). No "lost updates" on balances.
*   **Availability**: High availability for reading balances and adding expenses.
*   **Precision**: No floating-point errors. All currency must be handled as integers (e.g., cents).
*   **Scalability**: Ability to handle millions of users and high volumes of transactions during peak times (e.g., holiday seasons).

### 1.3 Scale Estimations
*   **Users**: 10 Million Monthly Active Users (MAU).
*   **Expenses**: Average 5 expenses per user per month $\approx$ 50M expenses/month.
*   **Read/Write Ratio**: High read-to-write ratio (users check balances more often than they add expenses).

---

## 2. High-Level Architecture

### 2.1 Core Components
*   **API Gateway**: Handles authentication, rate limiting, and request routing.
*   **User Service**: Manages user profiles and friendship graphs.
*   **Group Service**: Manages group metadata and membership.
*   **Expense Service**: Handles the business logic for creating and splitting expenses.
*   **Balance Service**: Manages the "Ledger." It computes the current state of debts and handles the Debt Simplification logic.
*   **Settlement Service**: Processes payments and updates the ledger.
*   **Notification Service**: Alerts users when they are added to an expense or when a debt is simplified.

### 2.2 System Workflow (Mermaid)

```mermaid
sequenceDiagram
    participant User
    participant APIGateway
    participant ExpenseService
    participant BalanceService
    participant DB
    participant NotificationService

    User->>APIGateway: POST /expenses (amount, payer, split_details)
    APIGateway->>ExpenseService: Create Expense Request
    ExpenseService->>DB: Save Expense & Split Details (Transaction)
    ExpenseService->>BalanceService: Update Balances(payer, participants, amounts)
    BalanceService->>DB: Atomic Update of User-to-User Balances
    BalanceService-->>ExpenseService: Success
    ExpenseService-->>APIGateway: Expense Created
    APIGateway-->>User: 201 Created
    ExpenseService->>NotificationService: Trigger "You are owed money" notification
    NotificationService->>User: Push Notification
```

---

## 3. Detailed Database Schema Design

### 3.1 Rationale
A **Relational Database (PostgreSQL)** is chosen over NoSQL because:
1.  **ACID Compliance**: Crucial for financial transactions to prevent balance mismatches.
2.  **Complex Queries**: Ability to join Users, Groups, and Expenses for detailed reporting.
3.  **Strong Typing**: Ensuring monetary values are stored as `BIGINT` to prevent rounding errors.

### 3.2 Schema Tables

#### `users`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique user identifier |
| `name` | VARCHAR | NOT NULL | Full name |
| `email` | VARCHAR | UNIQUE | User email |
| `currency` | VARCHAR | NOT NULL | Default currency (e.g., USD) |

#### `groups`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `group_id` | UUID | PK | Unique group identifier |
| `name` | VARCHAR | NOT NULL | Group name |
| `created_at` | TIMESTAMP | NOT NULL | Creation date |

#### `group_members`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `group_id` | UUID | FK $\rightarrow$ groups | Group identifier |
| `user_id` | UUID | FK $\rightarrow$ users | User identifier |
| `joined_at` | TIMESTAMP | NOT NULL | Date of joining |
| **PK** | (group_id, user_id) | | Composite Primary Key |

#### `expenses`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `expense_id` | UUID | PK | Unique expense identifier |
| `group_id` | UUID | FK $\rightarrow$ groups (NULLable) | Group ID (NULL for non-group) |
| `description` | TEXT | NOT NULL | Description of expense |
| `total_amount`| BIGINT | NOT NULL | Amount in cents |
| `payer_id` | UUID | FK $\rightarrow$ users | Who paid the bill |
| `split_type` | ENUM | EQUAL, EXACT, PERCENT | Type of split |
| `created_at` | TIMESTAMP | NOT NULL | Timestamp |

#### `expense_splits`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `expense_id` | UUID | FK $\rightarrow$ expenses | Reference to expense |
| `user_id` | UUID | FK $\rightarrow$ users | User who owes money |
| `amount_owed` | BIGINT | NOT NULL | Amount user owes in cents |
| **PK** | (expense_id, user_id) | | Composite Primary Key |

#### `user_balances`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_from` | UUID | FK $\rightarrow$ users | Debtor |
| `user_to` | UUID | FK $\rightarrow$ users | Creditor |
| `amount` | BIGINT | NOT NULL | Current net balance in cents |
| **PK** | (user_from, user_to) | | Composite Primary Key |
| **Index** | user_from | | For fast lookup of debts owed |
| **Index** | user_to | | For fast lookup of money owed to user |

---

## 4. Core API Design

### 4.1 Create Expense
`POST /api/v1/expenses`

**Request Body:**
```json
{
  "description": "Dinner at Nobu",
  "total_amount": 15000, // $150.00
  "payer_id": "user_uuid_1",
  "group_id": "group_uuid_abc", // Optional
  "split_type": "PERCENT",
  "splits": [
    {"user_id": "user_uuid_1", "value": 50},
    {"user_id": "user_uuid_2", "value": 25},
    {"user_id": "user_uuid_3", "value": 25}
  ]
}
```
**Response:** `201 Created`

### 4.2 Get User Balances
`GET /api/v1/users/{userId}/balances`

**Response:**
```json
{
  "userId": "user_uuid_1",
  "net_balance": 5000,
  "details": [
    {"user_id": "user_uuid_2", "balance": 7500, "type": "OWED_TO_ME"},
    {"user_id": "user_uuid_3", "balance": -2500, "type": "I_OWE"}
  ]
}
```

### 4.3 Settle Up
`POST /api/v1/settlements`

**Request Body:**
```json
{
  "payer_id": "user_uuid_2",
  "payee_id": "user_uuid_1",
  "amount": 7500
}
```
**Response:** `200 OK`

---

## 5. Scalability & Advanced Topics

### 5.1 Debt Simplification Algorithm
To minimize transactions, we use a **Net Balance Approach**:
1.  Calculate the net balance for every user in a group (Total Credit - Total Debit).
2.  Create two heaps: `debtors` (negative balance) and `creditors` (positive balance).
3.  While both heaps are not empty:
    *   Pop the largest debtor and largest creditor.
    *   Settle the minimum of the two absolute values.
    *   Update balances and push back into heaps if they still have remaining balances.
    *   Complexity: $O(N \log N)$ where $N$ is the number of users in the group.

### 5.2 Caching Strategy
*   **Balance Cache**: Use Redis to store the `user_balances` for highly active groups.
*   **Cache Invalidation**: Use a **Write-Through Cache** strategy. When an expense is added, the Balance Service updates the DB and immediately invalidates/updates the corresponding Redis keys.

### 5.3 Concurrency Control
To prevent race conditions when multiple users add expenses to the same group:
*   **Pessimistic Locking**: `SELECT FOR UPDATE` on the `user_balances` row for the specific `user_from` and `user_to` pair.
*   **Sequence**:
    1.  Start Transaction.
    2.  Lock rows in `user_balances` (ordered by UUID to avoid deadlocks).
    3.  Update balances.
    4.  Commit Transaction.

### 5.4 Sharding & Partitioning
*   **Database Sharding**: Shard the `expenses` and `expense_splits` tables by `group_id`. Since most queries are group-centric, this ensures all data for a group resides on one shard.
*   **Partitioning**: Use time-based partitioning for the `expenses` table (e.g., monthly partitions) to keep indexes small and manageable.

---

## 6. Trade-off Analysis

| Trade-off | Decision | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs Availability** | **Consistency (CP)** | In a financial app, showing an incorrect balance is worse than a momentary timeout. We prioritize ACID compliance. |
| **Normalization vs Denormalization**| **Partial Denormalization** | While balances can be computed from `expense_splits` (normalized), we maintain a `user_balances` table (denormalized) to avoid $O(N)$ summation on every read. |
| **Floating Point vs Integer** | **Integer (Cents)** | `Double` or `Float` types lead to precision errors (e.g., $0.1 + 0.2 \neq 0.3$). Integers ensure absolute accuracy. |
| **Synchronous vs Asynchronous Update** | **Hybrid** | Expense creation and Balance updates are synchronous (atomic transaction). Debt simplification and Notifications are asynchronous (via Message Queue) to reduce API latency. |""",
}

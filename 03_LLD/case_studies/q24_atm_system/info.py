INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design ATM / Banking System.',
    'groups': ['OOP Case Studies'],
    'readme_content': """# ATM System Low-Level Design (LLD)

## 1. Overview & System Requirements
The ATM (Automated Teller Machine) system is a classic LLD problem that tests a developer's ability to manage **state transitions**, **hardware-software abstraction**, and **complex business logic** (like currency denomination).

### Core Actors
- **User/Customer**: Interacts with the ATM to perform banking operations.
- **Bank Server**: The central authority that validates credentials and manages account balances.
- **ATM Administrator**: Maintains the machine, refills cash, and handles technical errors.

### Functional Requirements
1. **Authentication**: User must insert a card and provide a valid PIN.
2. **Balance Inquiry**: Users can check the current balance of their account.
3. **Cash Withdrawal**: 
    - Must validate sufficient funds.
    - Must dispense cash using the optimal combination of available denominations.
4. **Cash Deposit**: Users can deposit cash or checks into their account.
5. **Transaction History**: Ability to print or view a summary of recent transactions.
6. **Card Management**: Card ejection after transaction or session timeout.

### Non-Functional Requirements
- **Consistency**: Account balance must be updated atomically (Transaction ACID properties).
- **Security**: PINs and sensitive data must not be stored in plain text.
- **Availability**: The system should handle "Out of Cash" or "Server Down" scenarios gracefully.

---

## 2. Design Principles & Patterns

### Design Patterns Applied
| Pattern | Why it is applied | Problem Solved |
| :--- | :--- | :--- |
| **State Pattern** | The ATM behaves differently based on its current state (Idle, HasCard, Authenticated, Dispensing). | Avoids massive `if-else` or `switch` blocks to check the current status of the machine. |
| **Chain of Responsibility** | Used for the `CashDispenser` to determine how many notes of \$100, \$50, \$20, etc., to give. | Decouples the withdrawal request from the specific logic of note counting. |
| **Singleton Pattern** | The `BankServer` or the `ATM` instance itself should be a single point of truth. | Prevents multiple inconsistent instances of the machine/server interface. |
| **Strategy Pattern** | Different authentication methods (PIN, Biometric, NFC) can be plugged in. | Allows the system to evolve authentication methods without changing the core ATM logic. |

### SOLID Principles
- **Single Responsibility (SRP)**: `CashDispenser` handles money, `Account` handles balance, `ATMState` handles flow control.
- **Open/Closed Principle (OCP)**: Adding a new transaction type (e.g., "Pay Bill") only requires adding a new state or method without modifying existing core logic.
- **Dependency Inversion (DIP)**: The `ATM` class depends on the `ATMState` interface, not on concrete state implementations like `IdleState`.

---

## 3. Class Structure & Relationships

### Class Diagram (Conceptual)
```text
+-------------------+          +-------------------+
|      ATM          |<>--------|    ATMState       | (Interface)
+-------------------+          +-------------------+
| - currentState    |          | + insertCard()    |
| - cashDispenser   |          | + authenticate()   |
| - bankServer      |          | + withdraw()       |
+-------------------+          | + ejectCard()     |
          |                    +-------------------+
          |                               ^
          |                               | (Inherits)
          |                    +----------+----------+
          |                    |          |          |
          |              +----------+ +----------+ +----------+
          |              | IdleState| | CardState| | AuthState|
          |              +----------+ +----------+ +----------+
          |
          v
+-------------------+          +-------------------+
|   CashDispenser   |--------->|  DispenseHandler  | (Chain)
+-------------------+          +-------------------+
| - availableCash   |          | - nextHandler     |
| + dispense(amount)|          | + handle(amount)  |
+-------------------+          +-------------------+
          |
          v
+-------------------+          +-------------------+
|    BankServer     |--------->|     Account       |
+-------------------+          +-------------------+
| + validate(pin)   |          | - accountNumber   |
| + updateBalance() |          | - balance         |
+-------------------+          +-------------------+
```

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation in Python

```python
from abc import ABC, abstractmethod
from typing import List, Dict

# --- State Pattern ---
class ATMState(ABC):
    @abstractmethod
    def insert_card(self, atm): pass
    @abstractmethod
    def authenticate_pin(self, atm, pin): pass
    @abstractmethod
    def withdraw_cash(self, atm, amount): pass
    @abstractmethod
    def eject_card(self, atm): pass

class IdleState(ATMState):
    def insert_card(self, atm):
        print("Card inserted. Please enter your PIN.")
        atm.set_state(atm.has_card_state)
    def authenticate_pin(self, atm, pin): print("Insert card first.")
    def withdraw_cash(self, atm, amount): print("Insert card first.")
    def eject_card(self, atm): print("No card to eject.")

class HasCardState(ATMState):
    def insert_card(self, atm): print("Card already inserted.")
    def authenticate_pin(self, atm, pin):
        if atm.bank_server.validate_pin(atm.current_card, pin):
            print("Authentication successful.")
            atm.set_state(atm.authenticated_state)
        else:
            print("Invalid PIN. Try again.")
    def withdraw_cash(self, atm, amount): print("Authenticate first.")
    def eject_card(self, atm):
        print("Card ejected.")
        atm.set_state(atm.idle_state)

class AuthenticatedState(ATMState):
    def insert_card(self, atm): print("Card already inserted.")
    def authenticate_pin(self, atm, pin): print("Already authenticated.")
    def withdraw_cash(self, atm, amount):
        if atm.bank_server.check_funds(atm.current_card, amount):
            notes = atm.cash_dispenser.dispense(amount)
            if notes:
                atm.bank_server.update_balance(atm.current_card, amount)
                print(f"Dispensing cash: {notes}")
                atm.set_state(atm.idle_state) # Simplified: return to idle
            else:
                print("ATM insufficient funds.")
        else:
            print("Insufficient account balance.")
    def eject_card(self, atm):
        print("Card ejected.")
        atm.set_state(atm.idle_state)

# --- Chain of Responsibility Pattern for Cash Dispensing ---
class CashHandler(ABC):
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    @abstractmethod
    def handle(self, amount, result): pass

class HundredDollarHandler(CashHandler):
    def handle(self, amount, result):
        notes = amount // 100
        result['$100'] = notes
        remaining = amount % 100
        if self.next_handler and remaining > 0:
            self.next_handler.handle(remaining, result)

class FiftyDollarHandler(CashHandler):
    def handle(self, amount, result):
        notes = amount // 50
        result['$50'] = notes
        remaining = amount % 50
        if self.next_handler and remaining > 0:
            self.next_handler.handle(remaining, result)

class TwentyDollarHandler(CashHandler):
    def handle(self, amount, result):
        notes = amount // 20
        result['$20'] = notes
        remaining = amount % 20
        if self.next_handler and remaining > 0:
            self.next_handler.handle(remaining, result)

# --- Support Classes ---
class CashDispenser:
    def __init__(self):
        # Chain: 100 -> 50 -> 20
        self.chain = HundredDollarHandler(FiftyDollarHandler(TwentyDollarHandler()))
    
    def dispense(self, amount):
        if amount % 10 != 0: # Assuming minimum note is $10 or $20
            print("Amount must be a multiple of 10.")
            return None
        result = {}
        self.chain.handle(amount, result)
        return result

class BankServer:
    def __init__(self):
        self.accounts = {"12345": {"pin": "1111", "balance": 5000}}
    
    def validate_pin(self, card_id, pin):
        return self.accounts.get(card_id, {}).get("pin") == pin
    
    def check_funds(self, card_id, amount):
        return self.accounts.get(card_id, {}).get("balance", 0) >= amount
    
    def update_balance(self, card_id, amount):
        self.accounts[card_id]["balance"] -= amount

# --- Context Class (ATM) ---
class ATM:
    def __init__(self):
        self.idle_state = IdleState()
        self.has_card_state = HasCardState()
        self.authenticated_state = AuthenticatedState()
        
        self.state = self.idle_state
        self.cash_dispenser = CashDispenser()
        self.bank_server = BankServer()
        self.current_card = None

    def set_state(self, state):
        self.state = state

    def insert_card(self, card_id):
        self.current_card = card_id
        self.state.insert_card(self)

    def authenticate(self, pin):
        self.state.authenticate_pin(self, pin)

    def withdraw(self, amount):
        self.state.withdraw_cash(self, amount)

    def eject(self):
        self.state.eject_card(self)

# --- Testing the System ---
if __name__ == "__main__":
    atm = ATM()
    atm.insert_card("12345")
    atm.authenticate("1111")
    atm.withdraw(280)  # Expected: 2x100, 1x50, 1x20, 1x10 (depending on chain)
    atm.eject()
```

### Logic Walkthrough
1. **Initial State**: The `ATM` starts in `IdleState`. Any attempt to withdraw will trigger the `insert card first` message.
2. **Card Insertion**: When `insert_card` is called, the state transitions to `HasCardState`.
3. **Authentication**: The `BankServer` (Singleton-like) is queried to validate the PIN. If successful, the state transitions to `AuthenticatedState`.
4. **Withdrawal Process**:
    - The `ATM` asks the `BankServer` if the account has enough money.
    - If yes, the `CashDispenser` uses a **Chain of Responsibility**. The `HundredDollarHandler` takes as many \$100s as possible, passes the remainder to `FiftyDollarHandler`, and so on.
    - Once cash is "dispensed," the `BankServer` deducts the amount from the account.
5. **Completion**: The state returns to `IdleState` after the card is ejected.

---

## 5. Complexity Analysis & Real-World Applications

### Time and Space Complexity
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Authentication** | $O(1)$ | $O(1)$ | Simple hash map lookup in Bank Server. |
| **Withdrawal (Balance)** | $O(1)$ | $O(1)$ | Simple subtraction. |
| **Cash Dispensing** | $O(N)$ | $O(N)$ | $N$ is the number of denominations (very small constant). |
| **State Transition** | $O(1)$ | $O(1)$ | Simple pointer update. |

### Real-World Applications
- **Hardware Drivers**: The State pattern is used extensively in embedded systems where hardware (like a card reader or sensor) moves through specific operational phases.
- **Payment Gateways**: Stripe or PayPal use similar "Transaction State" machines (Pending $\rightarrow$ Authorized $\rightarrow$ Captured $\rightarrow$ Settled).
- **Vending Machines**: Almost identical LLD to an ATM (Coin insertion $\rightarrow$ Selection $\rightarrow$ Dispensing $\rightarrow$ Change).
- **Workflow Engines**: Tools like Apache Airflow or AWS Step Functions utilize the state machine logic to manage complex business process transitions.""",
    'solutions': """# System Design Document: ATM / Banking System

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Authentication**: User must be able to authenticate using a physical card and a secret PIN.
*   **Balance Inquiry**: Users should be able to check the current available balance of their account.
*   **Cash Withdrawal**: Users can withdraw cash if the account has sufficient funds and the ATM has sufficient cash.
*   **Cash Deposit**: Users can deposit cash/checks into their account.
*   **Fund Transfer**: Users can transfer money between two accounts within the same bank.
*   **ATM Management**: Bank admins must be able to refill cash in the ATM and monitor ATM health/status.
*   **Transaction History**: Users should be able to view a list of recent transactions.

### 1.2 Non-Functional Requirements
*   **Strong Consistency (ACID)**: Financial transactions must be atomic. A user cannot withdraw money that isn't there, and money cannot "disappear" during a transfer.
*   **High Availability**: The system should be available 24/7. However, consistency takes precedence over availability (CP in CAP theorem) for ledger updates.
*   **Security**: End-to-end encryption (TLS), secure PIN hashing (bcrypt/scrypt), and PCI DSS compliance.
*   **Auditability**: Every action must be logged in an immutable audit trail for regulatory compliance.
*   **Idempotency**: Network failures during a withdrawal should not result in double-charging the user or double-dispensing cash.

### 1.3 Scale Estimations
*   **Users**: 10 Million active customers.
*   **ATMs**: 50,000 deployed globally.
*   **TPS (Transactions Per Second)**: 
    *   Average: 1,000 TPS.
    *   Peak: 5,000 TPS (e.g., payday or holiday season).
*   **Storage**: With 10M users and an average of 10 transactions per month, we generate 100M records monthly. This requires a partitioned database strategy.

---

## 2. High-Level Architecture

The system follows a layered architecture: **ATM Client $\rightarrow$ API Gateway $\rightarrow$ Banking Core Services $\rightarrow$ Database**.

### 2.1 Core Components
1.  **ATM Client (Hardware/Software)**: Manages the physical card reader, keypad, cash dispenser, and screen.
2.  **ATM Gateway/Controller**: Acts as a secure proxy. It handles session management and routes requests to the internal banking services.
3.  **Auth Service**: Validates card numbers and PINs.
4.  **Account Service**: Manages account metadata and balance queries.
5.  **Transaction Service**: The core engine that handles the orchestration of deposits, withdrawals, and transfers using distributed transactions.
6.  **ATM Management Service**: Tracks the "Cash Inventory" of each physical ATM machine.
7.  **Notification Service**: Sends SMS/Email alerts for transactions.

### 2.2 Sequence Diagram (Cash Withdrawal)

```mermaid
sequenceDiagram
    participant User
    participant ATM as ATM Machine
    participant Gateway as API Gateway
    participant Auth as Auth Service
    participant Trans as Transaction Service
    participant Acc as Account Service
    participant DB as Database

    User->>ATM: Insert Card & Enter PIN
    ATM->>Gateway: Authenticate(card_id, pin)
    Gateway->>Auth: ValidateCredentials(card_id, pin)
    Auth->>DB: Fetch PinHash(card_id)
    DB-->>Auth: PinHash
    Auth-->>Gateway: Auth Success (SessionToken)
    Gateway-->>ATM: Auth Success
    
    User->>ATM: Request Withdrawal (Amount)
    ATM->>Gateway: Withdraw(SessionToken, amount)
    Gateway->>Trans: InitiateWithdrawal(acc_id, amount)
    Trans->>Acc: LockAccount(acc_id)
    Acc->>DB: SELECT balance FROM accounts WHERE id=acc_id FOR UPDATE
    DB-->>Acc: Balance
    
    alt Balance Sufficient
        Acc-->>Trans: Balance OK
        Trans->>DB: UPDATE accounts SET balance = balance - amount
        Trans->>DB: INSERT INTO transactions (type=WITHDRAW, status=PENDING)
        Trans-->>Gateway: Dispense Cash Authorized
        Gateway-->>ATM: Dispense Cash
        ATM->>User: Deliver Cash
        ATM->>Gateway: Confirm Dispense Success
        Gateway->>Trans: CompleteTransaction(tx_id)
        Trans->>DB: UPDATE transactions SET status=COMPLETED
    else Insufficient Funds
        Acc-->>Trans: Insufficient Funds
        Trans-->>Gateway: Error: Insufficient Funds
        Gateway-->>ATM: Show "Insufficient Balance"
    end
```

---

## 3. Detailed Database Schema Design

A **Relational Database (RDBMS)** like PostgreSQL is chosen because of the absolute requirement for ACID transactions.

### 3.1 Tables

#### `Users`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier for the customer |
| `full_name` | VARCHAR | NOT NULL | User's legal name |
| `email` | VARCHAR | UNIQUE | Contact email |
| `phone` | VARCHAR | UNIQUE | Contact phone |
| `created_at` | TIMESTAMP | NOT NULL | Account creation date |

#### `Accounts`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `account_id` | UUID | PK | Unique account number |
| `user_id` | UUID | FK (Users) | Owner of the account |
| `account_type`| ENUM | ('Savings', 'Current') | Type of account |
| `balance` | DECIMAL(15,2)| NOT NULL, $\ge 0$ | Current balance (Using Decimal for precision) |
| `status` | ENUM | ('Active', 'Frozen') | Account state |
| `version` | INT | NOT NULL | For Optimistic Locking |

#### `Cards`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `card_number` | VARCHAR(16) | PK | 16-digit card number |
| `account_id` | UUID | FK (Accounts) | Linked account |
| `pin_hash` | VARCHAR | NOT NULL | Salted hash of the PIN |
| `expiry_date` | DATE | NOT NULL | Card expiration |
| `cvv_hash` | VARCHAR | NOT NULL | Hashed CVV |
| `status` | ENUM | ('Active', 'Blocked') | Card state |

#### `Transactions`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `tx_id` | UUID | PK | Unique transaction ID |
| `from_acc` | UUID | FK (Accounts) | Source account (null for deposits) |
| `to_acc` | UUID | FK (Accounts) | Target account (null for withdrawals) |
| `amount` | DECIMAL(15,2)| NOT NULL | Transaction amount |
| `tx_type` | ENUM | ('Withdraw', 'Deposit', 'Transfer') | Type of action |
| `status` | ENUM | ('Pending', 'Success', 'Failed') | State of the transaction |
| `atm_id` | UUID | FK (ATMs) | The ATM machine used |
| `timestamp` | TIMESTAMP | INDEX | Transaction time |

#### `ATMs`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `atm_id` | UUID | PK | Unique ATM identifier |
| `location` | TEXT | NOT NULL | Address/GPS |
| `cash_balance`| DECIMAL(15,2)| NOT NULL | Total cash currently in machine |
| `status` | ENUM | ('Online', 'Out of Cash', 'Maintenance')| Machine status |

### 3.2 Indexing Strategy
*   **`Transactions(timestamp)`**: For fast retrieval of history.
*   **`Cards(card_number)`**: For $O(1)$ lookup during authentication.
*   **`Accounts(user_id)`**: To quickly find all accounts belonging to a user.

---

## 4. Core API Design

All endpoints are secured via TLS and require a `SessionToken` (JWT) after authentication.

### 4.1 Authentication
`POST /api/v1/auth/login`
*   **Request**: `{ "card_number": "1234...", "pin": "1234" }`
*   **Response**: `{ "session_token": "eyJ...", "expires_in": 300 }`

### 4.2 Balance Inquiry
`GET /api/v1/account/{account_id}/balance`
*   **Response**: `{ "account_id": "...", "balance": 1500.50, "currency": "USD" }`

### 4.3 Cash Withdrawal
`POST /api/v1/transaction/withdraw`
*   **Request**: `{ "account_id": "...", "amount": 200.00, "atm_id": "..." }`
*   **Response**: `{ "tx_id": "...", "status": "AUTHORIZED", "message": "Please collect cash" }`

### 4.4 Fund Transfer
`POST /api/v1/transaction/transfer`
*   **Request**: `{ "from_account": "...", "to_account": "...", "amount": 500.00 }`
*   **Response**: `{ "tx_id": "...", "status": "SUCCESS" }`

---

## 5. Scalability & Advanced Topics

### 5.1 Concurrency Control
To prevent the "Double Spend" problem:
1.  **Pessimistic Locking**: Use `SELECT FOR UPDATE` in SQL to lock the account row during the transaction. This ensures no other process can modify the balance until the current transaction commits.
2.  **Optimistic Locking**: Use a `version` column. `UPDATE accounts SET balance = balance - 100, version = version + 1 WHERE id = ? AND version = ?`. If the row was modified, the update fails.

### 5.2 Distributed Transactions (The Saga Pattern)
For transfers between accounts residing on different database shards:
*   **Saga Pattern**: 
    1.  Deduct money from Account A (Local Tx).
    2.  Credit money to Account B (Local Tx).
    3.  If Step 2 fails, trigger a **Compensating Transaction** to refund Account A.

### 5.3 Idempotency
Every request from the ATM includes a unique `request_id` (UUID). The backend stores this ID in an `Idempotency` table. If a request with the same ID arrives again, the system returns the cached result of the first operation instead of executing it twice.

### 5.4 Caching Strategy
*   **Redis** is used for:
    *   **Session Management**: Storing `SessionToken` $\rightarrow$ `UserID` mapping.
    *   **ATM Metadata**: Locations and status of ATMs (read-heavy).
*   *Note*: Account balances are **not** cached in Redis to avoid stale data risks.

### 5.5 Fault Tolerance & Reliability
*   **Dead Letter Queues (DLQ)**: If the Notification Service fails to send a transaction alert, the message is moved to a DLQ for retry.
*   **Circuit Breaker**: If the Auth Service is down, the Gateway trips the circuit to prevent cascading failures, returning a "Service Unavailable" message immediately.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Consistency vs. Availability
In a banking system, **Consistency (C)** and **Partition Tolerance (P)** are prioritized over **Availability (A)**. It is better to tell a customer "System Unavailable" than to allow them to withdraw the same $\$100$ twice from two different ATMs due to an eventual consistency lag.

### 6.2 Latency vs. Storage
*   **Audit Logs**: We store every single event (even failed attempts). This increases storage costs significantly but is a mandatory trade-off for regulatory compliance and forensic analysis.
*   **Write Latency**: Using strong ACID transactions and locking increases latency compared to NoSQL. However, the correctness of the ledger is more critical than millisecond-level response times.

### 6.3 SQL vs. NoSQL
*   **SQL (Chosen)**: Essential for multi-row atomic transactions (e.g., moving money from Account A to Account B).
*   **NoSQL (Rejected for Core Ledger)**: While DynamoDB or Cassandra scale better, they typically offer eventual consistency. While they could be used for "Transaction History" (Read-only view), the "Source of Truth" for balances must be relational.""",
}

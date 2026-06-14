# ATM System Low-Level Design (LLD)

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
- **Workflow Engines**: Tools like Apache Airflow or AWS Step Functions utilize the state machine logic to manage complex business process transitions.
INFO = {
    'difficulty': 'Medium',
    'link': 'https://www.geeksforgeeks.org/design-vending-machine-lld/',
    'description': 'Vending state pattern machine.',
    'type': 'design',
    'groups': ['OOP Case Studies', 'Behavioral Patterns'],
    'readme_content': """# Vending Machine LLD (State Pattern)

The **Vending Machine** is a classic Low-Level Design (LLD) problem that demonstrates how to manage complex state transitions. A vending machine behaves differently depending on its current state (e.g., it cannot dispense a product if no money has been inserted). Using the **State Design Pattern**, we can encapsulate state-specific behavior into separate classes, eliminating monolithic `if-else` or `switch-case` blocks.

---

## 1. Overview & System Requirements

### Core Entities
- **Vending Machine (Context):** The main controller that maintains the current state and the inventory.
- **State (Interface):** An abstract layer defining the actions that can be performed in any state.
- **Concrete States:** Specific behaviors for `Idle`, `HasMoney`, and `Dispensing`.
- **Product:** An item containing a name and a price.
- **Inventory:** A management system to track the count of available products.

### Functional Requirements
1. **Insert Money:** The user adds credits to the machine.
2. **Select Product:** The user chooses a product. The machine checks if the balance is sufficient and the item is in stock.
3. **Dispense Product:** The machine delivers the item and returns the remaining change.
4. **Cancel/Refund:** The user can retrieve their money before selecting a product.
5. **State Transitions:** The machine must move logically between states (e.g., `Idle` $\rightarrow$ `HasMoney` $\rightarrow$ `Dispensing` $\rightarrow$ `Idle`).

---

## 2. Design Principles & Patterns

### Design Patterns Applied
- **State Pattern (Behavioral):** This is the primary pattern. Instead of the `VendingMachine` class checking `if (state == IDLE)`, it delegates the action to the current state object (`state.insert_coin()`). This makes the system highly extensible.
- **Singleton Pattern (Creational):** The `VendingMachine` instance is typically a singleton to ensure a single point of control for hardware/inventory.
- **Strategy Pattern (Optional):** Could be used to implement different payment strategies (Cash, Card, UPI).

### SOLID Principles
- **Single Responsibility Principle (SRP):** The `VendingMachine` class manages the context, while each `State` class manages the logic for that specific state.
- **Open/Closed Principle (OCP):** New states (e.g., `OutOfOrderState` or `MaintenanceState`) can be added without modifying the existing state classes or the main context.
- **Liskov Substitution Principle (LSP):** Any concrete state (e.g., `IdleState`) can be used interchangeably wherever the `State` interface is expected.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-------------------+          +-----------------------+
|   VendingMachine  |---------->|       <<Interface>>   |
|-------------------|          |         State         |
| - currentState    |          |-----------------------|
| - inventory       |          | + insert_coin()       |
| - balance         |          | + select_product()    |
|-------------------|          | + dispense()          |
| + setState()      |          | + refund()            |
| + getBalance()    |          +-----------------------+
+-------------------+                      ^
          |                                |
          |          +---------------------+---------------------+
          |          |                     |                     |
          v    +-------------+       +--------------+      +----------------+
    +----------+|  IdleState  |       | HasMoneyState |      | DispensingState |
    | Inventory| + insert_coin()      +--------------+      +----------------+
    +----------+| + refund()          | + select_prod()    | + dispense()
                +-------------+       | + refund()         +----------------+
```

### Relationships
- **Composition:** `VendingMachine` has an `Inventory` and a current `State`.
- **Inheritance:** `IdleState`, `HasMoneyState`, and `DispensingState` inherit from the `State` abstract class.
- **Association:** The `State` objects hold a reference back to the `VendingMachine` context to trigger state transitions (`machine.setState(...)`).

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod

# --- Model Classes ---
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Inventory:
    def __init__(self):
        self.products = {} # Product -> Quantity

    def add_product(self, product, quantity):
        self.products[product] = quantity

    def has_product(self, product):
        return self.products.get(product, 0) > 0

    def deduct_product(self, product):
        self.products[product] -= 1

# --- State Interface ---
class State(ABC):
    @abstractmethod
    def insert_coin(self, machine): pass
    
    @abstractmethod
    def select_product(self, machine, product): pass
    
    @abstractmethod
    def dispense(self, machine): pass
    
    @abstractmethod
    def refund(self, machine): pass

# --- Concrete States ---
class IdleState(State):
    def insert_coin(self, machine):
        print("Coin inserted.")
        machine.set_state(machine.has_money_state)
        
    def select_product(self, machine, product):
        print("Insert coin first!")
        
    def dispense(self, machine):
        print("Payment required first!")
        
    def refund(self, machine):
        print("No money to refund.")

class HasMoneyState(State):
    def insert_coin(self, machine):
        print("Money already inserted.")
        
    def select_product(self, machine, product):
        if not machine.inventory.has_product(product):
            print(f"Sorry, {product.name} is out of stock.")
            return
        
        if machine.balance < product.price:
            print(f"Insufficient funds for {product.name}. Need {product.price - machine.balance} more.")
            return
        
        print(f"Product {product.name} selected.")
        machine.selected_product = product
        machine.set_state(machine.dispensing_state)
        
    def dispense(self, machine):
        print("Select a product first.")
        
    def refund(self, machine):
        print(f"Refunded {machine.balance}. Returning to Idle.")
        machine.balance = 0
        machine.set_state(machine.idle_state)

class DispensingState(State):
    def insert_coin(self, machine):
        print("Please wait, dispensing in progress.")
        
    def select_product(self, machine, product):
        print("Already dispensing a product.")
        
    def dispense(self, machine):
        product = machine.selected_product
        machine.inventory.deduct_product(product)
        change = machine.balance - product.price
        print(f"Dispensing {product.name}. Returning change: {change}")
        machine.balance = 0
        machine.selected_product = None
        machine.set_state(machine.idle_state)
        
    def refund(self, machine):
        print("Cannot refund during dispensing.")

# --- Context ---
class VendingMachine:
    def __init__(self):
        self.inventory = Inventory()
        self.balance = 0
        self.selected_product = None
        
        # Initialize States
        self.idle_state = IdleState()
        self.has_money_state = HasMoneyState()
        self.dispensing_state = DispensingState()
        
        self.state = self.idle_state

    def set_state(self, state):
        self.state = state

    def insert_money(self, amount):
        self.balance += amount
        self.state.insert_coin(self)

    def press_button(self, product):
        self.state.select_product(self, product)

    def dispense(self):
        self.state.dispense(self)

    def cancel(self):
        self.state.refund(self)

# --- Execution ---
def solve():
    vm = VendingMachine()
    coke = Product("Coke", 25)
    pepsi = Product("Pepsi", 35)
    vm.inventory.add_product(coke, 5)
    vm.inventory.add_product(pepsi, 2)

    print("\n--- Scenario 1: Successful Purchase ---")
    vm.insert_money(50) # Idle -> HasMoney
    vm.press_button(coke) # HasMoney -> Dispensing
    vm.dispense()         # Dispensing -> Idle

    print("\n--- Scenario 2: Insufficient Funds ---")
    vm.insert_money(10)
    vm.press_button(pepsi) # Remains in HasMoney
    vm.cancel()            # HasMoney -> Idle

# Run simulation
solve()
```

### Logic Walkthrough
1. **Idle $\rightarrow$ HasMoney:** The `VendingMachine` starts in `IdleState`. When `insert_money()` is called, the state object transitions the context to `HasMoneyState`.
2. **Validation:** In `HasMoneyState`, the `select_product()` method performs two critical checks: **Availability** (from `Inventory`) and **Affordability** (comparing `balance` vs `product.price`).
3. **HasMoney $\rightarrow$ Dispensing:** If checks pass, the machine transitions to `DispensingState`.
4. **Dispensing $\rightarrow$ Idle:** The `dispense()` method handles the final physics: deducting stock, calculating change, and resetting the machine to `IdleState`.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Insert Money** | $O(1)$ | $O(1)$ | Simple state transition. |
| **Select Product** | $O(1)$ | $O(1)$ | Hash map lookup for inventory. |
| **Dispense** | $O(1)$ | $O(1)$ | Simple arithmetic and state reset. |
| **Overall System** | $O(1)$ | $O(P)$ | Space grows linearly with the number of unique products $P$. |

---

## 6. Real-World Applications

The State Pattern used in the Vending Machine LLD is applicable in many production systems:
- **TCP Connection Lifecycle:** A socket moves between `LISTEN`, `SYN_SENT`, `ESTABLISHED`, and `CLOSE_WAIT`.
- **Order Management Systems (E-commerce):** An order transitions from `Placed` $\rightarrow$ `Paid` $\rightarrow$ `Shipped` $\rightarrow$ `Delivered` $\rightarrow$ `Returned`.
- **Game Development:** A character AI switching between `Patrolling`, `Chasing`, and `Attacking` states.
- **ATM Machines:** Similar to vending machines, managing `CardInserted`, `PinEntered`, and `CashWithdrawing` states.""",
    'solutions': """# System Design Document: Vending Machine (State Pattern Implementation)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
The system must simulate a professional vending machine capable of handling the end-to-end lifecycle of a product purchase.

*   **State Management**: The machine must behave differently based on its current state (e.g., you cannot select a product before inserting money).
*   **Product Management**: Support for multiple products with varying prices and stock levels.
*   **Payment Processing**: Ability to accept coins/bills and track the current balance.
*   **Product Dispensing**: Validate product availability and sufficient funds before dispensing.
*   **Transaction Cancellation**: Allow users to cancel a transaction and receive a full refund of the current balance.
*   **Change Return**: Calculate and return the remaining balance after a successful purchase.
*   **Administrative Actions**: Ability to refill stock and collect cash (handled via an admin interface).

### 1.2 Non-Functional Requirements
*   **Thread Safety**: The machine must handle concurrent inputs (e.g., a user pressing a button while the coin mechanism is processing).
*   **Extensibility**: New states (e.g., `MaintenanceState`, `OutOfOrderState`) should be addable without modifying existing state logic (Open/Closed Principle).
*   **Reliability**: Ensure that the system never dispenses a product without payment or takes payment without dispensing (Atomicity).
*   **Low Latency**: Response time for user interactions must be near-instantaneous (< 100ms).

---

## 2. High-Level Architecture

### 2.1 Design Pattern: The State Pattern
The core of this design is the **State Pattern**. Instead of using massive `if-else` or `switch` blocks to check the current status of the machine, we encapsulate state-specific behavior into separate classes.

#### Components:
1.  **VendingMachine (Context)**: Maintains a reference to the current state object and the shared data (inventory, balance).
2.  **State (Interface)**: Defines the contract for all possible actions (`insertMoney()`, `selectProduct()`, `dispense()`, `refund()`).
3.  **Concrete States**: 
    *   `IdleState`: Waiting for money.
    *   `HasMoneyState`: Money inserted, waiting for selection.
    *   `DispensingState`: Processing the release of the product.
    *   `SoldOutState`: Special state when no products are available.

### 2.2 Interaction Diagram (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> IdleState
    IdleState --> HasMoneyState : insertMoney()
    HasMoneyState --> HasMoneyState : insertMoney()
    HasMoneyState --> DispensingState : selectProduct() [if funds >= price]
    HasMoneyState --> IdleState : cancel() [refund money]
    DispensingState --> IdleState : dispense() [return change]
    IdleState --> SoldOutState : checkInventory() [if all empty]
    SoldOutState --> IdleState : refill()
```

---

## 3. Detailed Design

### 3.1 Class Structure (LLD)

#### Core Entities
*   **Product**: `id`, `name`, `price`.
*   **Inventory**: A map of `Product` to `Quantity`.
*   **VendingMachine**: 
    *   `State currentState`
    *   `double currentBalance`
    *   `Inventory inventory`
    *   `setState(State state)`

#### State Interface & Implementation
```java
interface State {
    void insertMoney(VendingMachine vm, double amount);
    void selectProduct(VendingMachine vm, String productId);
    void dispense(VendingMachine vm);
    void refund(VendingMachine vm);
}

class IdleState implements State {
    public void insertMoney(VendingMachine vm, double amount) {
        vm.addBalance(amount);
        vm.setState(new HasMoneyState());
    }
    public void selectProduct(...) { throw new IllegalStateException("Insert money first"); }
    // ... other methods
}
```

### 3.2 Database Schema (For Fleet Management)
While a single machine operates on local state, a fleet of machines requires a centralized database for telemetry and inventory management.

**Reasoning**: SQL is preferred here due to the need for ACID compliance regarding financial transactions and inventory counts.

#### Table: `machines`
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `machine_id` | UUID | PK | Unique identifier for the hardware |
| `location` | String | | Physical placement |
| `status` | Enum | | ONLINE, OFFLINE, MAINTENANCE |

#### Table: `products`
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `product_id` | UUID | PK | Unique product SKU |
| `name` | String | | Display name |
| `base_price` | Decimal | | Standard MSRP |

#### Table: `inventory`
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `machine_id` | UUID | FK | Reference to machine |
| `product_id` | UUID | FK | Reference to product |
| `quantity` | Integer | | Current stock in slot |
| *Index* | `(machine_id, product_id)` | Unique | Fast lookup for stock check |

#### Table: `transactions`
| Field | Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `tx_id` | UUID | PK | Unique transaction ID |
| `machine_id` | UUID | FK | Machine where purchase occurred |
| `product_id` | UUID | FK | Product dispensed |
| `amount_paid` | Decimal | | Total money inserted |
| `change_given` | Decimal | | Balance returned |
| `timestamp` | DateTime | | Time of transaction |

---

## 4. Core API Design (IoT Backend)

The vending machine communicates with a cloud backend via REST or MQTT.

### 4.1 Dispense Event (Telemetry)
**Endpoint**: `POST /api/v1/telemetry/transaction`
**Payload**:
```json
{
  "machine_id": "vm-12345",
  "transaction_id": "tx-98765",
  "product_id": "prod-cola-01",
  "amount_paid": 1.50,
  "change_returned": 0.25,
  "timestamp": "2023-10-27T10:00:00Z"
}
```
**Response**: `202 Accepted`

### 4.2 Inventory Status
**Endpoint**: `GET /api/v1/machines/{machine_id}/inventory`
**Response**:
```json
{
  "machine_id": "vm-12345",
  "items": [
    { "product_id": "prod-cola-01", "quantity": 5, "status": "LOW_STOCK" },
    { "product_id": "prod-chips-02", "quantity": 0, "status": "OUT_OF_STOCK" }
  ]
}
```

### 4.3 Admin Refill
**Endpoint**: `PATCH /api/v1/machines/{machine_id}/refill`
**Payload**:
```json
{
  "refills": [
    { "product_id": "prod-cola-01", "added_quantity": 20 }
  ]
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Concurrency and Thread Safety
In a physical machine, multiple hardware interrupts can occur. 
*   **Locking**: Use a `ReentrantLock` or `synchronized` block around the `setState()` and `currentBalance` updates to prevent race conditions (e.g., two coins being registered at the exact same microsecond).
*   **Atomic Variables**: Use `AtomicInteger` for inventory counts if using a multi-threaded environment.

### 5.2 Fault Tolerance
*   **Local First**: The machine must operate in **Offline Mode**. State transitions and dispensing should happen locally. Sync with the cloud backend should be asynchronous via a **Write-Ahead Log (WAL)** or a local SQLite buffer.
*   **Retry Mechanism**: If the cloud API is down, the machine queues the transaction telemetry and retries using exponential backoff.

### 5.3 Caching Strategy
*   **Local Cache**: The machine caches product prices and IDs locally to avoid network calls during the "Select Product" phase.
*   **CDN/Edge**: For a global fleet, use edge locations to store machine configurations and update firmware.

---

## 6. Trade-off Analysis

### 6.1 State Pattern vs. Conditional Logic
*   **Trade-off**: State Pattern increases the number of classes (Boilerplate) but drastically reduces complexity in the business logic.
*   **Decision**: State Pattern is chosen because vending machines are "State-Heavy." Adding a new state (like `PaymentProcessingState` for Credit Cards) would require zero changes to the `IdleState` or `DispensingState`.

### 6.2 Consistency vs. Availability (CAP Theorem)
*   **Scenario**: Machine loses internet connectivity.
*   **Trade-off**: Should the machine stop selling (Consistency) or continue selling (Availability)?
*   **Decision**: **Availability** is prioritized. A vending machine is a physical utility. We accept "Eventual Consistency" where the backend is updated once the connection is restored.

### 6.3 Database Selection (SQL vs NoSQL)
*   **Trade-off**: NoSQL (like MongoDB) would allow flexible product attributes (e.g., calories, allergens). SQL ensures strict financial auditing.
*   **Decision**: **SQL** is chosen. Transactional integrity (ACID) is paramount when handling money and inventory. Product attributes can be handled via a JSONB column in PostgreSQL if flexibility is needed.""",
}

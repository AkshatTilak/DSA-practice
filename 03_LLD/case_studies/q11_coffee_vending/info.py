INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Coffee Vending Machine.',
    'groups': ['OOP Case Studies', 'Behavioral Patterns'],
    'readme_content': """# Coffee Vending Machine LLD

This study guide provides a professional low-level design (LLD) for a **Coffee Vending Machine**. The goal is to create a system that is modular, extensible (easy to add new coffee types), and robust (handles ingredient shortages and state transitions).

---

## 1. Overview & System Requirements

The Coffee Vending Machine is an automated system that allows a user to select a specific type of beverage, verifies the availability of necessary ingredients, processes the request, and dispenses the drink.

### Core Entities
- **CoffeeMachine**: The central controller (Context) that manages the state and coordinates other components.
- **Inventory**: Manages the stock of ingredients (water, milk, coffee beans, sugar).
- **Beverage/Recipe**: Defines what constitutes a specific drink (e.g., a Latte requires 100ml milk, 20ml water, 10g coffee).
- **State**: Represents the current condition of the machine (Idle, Processing, Out of Order).

### Functional Requirements
1. **Menu Display**: Show a list of available coffee types and their costs.
2. **Selection**: Allow the user to select a coffee type.
3. **Ingredient Validation**: Check if the inventory has enough ingredients to fulfill the recipe.
4. **Dispensing**: Deduct ingredients from inventory and "brew" the coffee.
5. **Maintenance**: Allow a technician to refill ingredients.
6. **Payment**: Process payments before dispensing the drink.

---

## 2. Design Principles & Patterns

To ensure the system is maintainable and scalable, the following principles and patterns are applied:

### OOP Design Principles
- **Single Responsibility Principle (SRP)**: 
    - `InventoryManager` only handles stock levels.
    - `PaymentProcessor` only handles transactions.
    - `CoffeeMachine` coordinates the workflow.
- **Open/Closed Principle (OCP)**: The system is open for extension (adding new coffee types) but closed for modification. Adding a "Mocha" only requires creating a new `Recipe` object, not changing the `CoffeeMachine` logic.
- **Dependency Inversion Principle (DIP)**: The `CoffeeMachine` depends on a `Beverage` abstraction rather than concrete classes like `Espresso` or `Cappuccino`.

### Design Patterns
| Pattern | Application | Reason |
| :--- | :--- | :--- |
| **State Pattern** | `MachineState` $\rightarrow$ `IdleState`, `ProcessingState` | Manages complex transitions. Prevents a user from selecting a drink while the machine is already brewing. |
| **Strategy Pattern** | `BrewingStrategy` | Different coffee types have different brewing logic/recipes. This encapsulates the "how" of making each drink. |
| **Singleton Pattern** | `CoffeeMachine` | Ensures only one instance of the vending machine exists in the system. |
| **Factory Pattern** | `BeverageFactory` | Decouples the creation of beverage objects from the main controller. |

---

## 3. Class Structure & Relationships

### Class Diagram (Text-Based)

```text
+-------------------+          +----------------------+
|   CoffeeMachine   |<>-------->|    InventoryManager  |
|-------------------|          |----------------------|
| - state: State    |          | - stock: Map<Ing, Qty>|
| - inventory: Inv  |          | + checkAvailability() |
| + selectDrink()   |          | + deductIngredients() |
| + refill()        |          +----------------------+
+---------+---------+
          |
          v
+-------------------+          +----------------------+
|     State (I)     |          |   Beverage (Abstract) |
|-------------------|          |----------------------|
| + handleRequest() |          | - name: String       |
+---------+---------+          | - recipe: Recipe     |
          ^                    +----------+-----------+
          |                               ^
    +-----+-----+                         |
    |           |               +---------+---------+
+-----------+ +------------+    |                   |
| IdleState | | ProcessState| +---Espresso---+ +---Latte---+
+-----------+ +------------+  +--------------+ +-----------+
```

### Relationships
- **Composition**: `CoffeeMachine` has an `InventoryManager`.
- **Strategy/Inheritance**: `Espresso` and `Latte` inherit from `Beverage`.
- **State**: `CoffeeMachine` delegates behavior to its current `State` object.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum

# --- Constants & Enums ---
class Ingredient(Enum):
    WATER = "Water"
    MILK = "Milk"
    COFFEE_BEANS = "Coffee Beans"
    SUGAR = "Sugar"

# --- Domain Models ---
class Recipe:
    def __init__(self, ingredients: dict):
        self.ingredients = ingredients  # e.g., {Ingredient.WATER: 100, Ingredient.MILK: 50}

class Beverage(ABC):
    def __init__(self, name: str, price: float, recipe: Recipe):
        self.name = name
        self.price = price
        self.recipe = recipe

class Espresso(Beverage):
    def __init__(self):
        recipe = Recipe({Ingredient.WATER: 50, Ingredient.COFFEE_BEANS: 15})
        super().__init__("Espresso", 2.5, recipe)

class Latte(Beverage):
    def __init__(self):
        recipe = Recipe({Ingredient.WATER: 50, Ingredient.MILK: 100, Ingredient.COFFEE_BEANS: 15})
        super().__init__("Latte", 3.5, recipe)

# --- Inventory Management ---
class InventoryManager:
    def __init__(self):
        self._stock = {
            Ingredient.WATER: 1000,
            Ingredient.MILK: 1000,
            Ingredient.COFFEE_BEANS: 500,
            Ingredient.SUGAR: 500
        }

    def check_availability(self, recipe: Recipe) -> bool:
        for ing, qty in recipe.ingredients.items():
            if self._stock.get(ing, 0) < qty:
                return False
        return True

    def deduct_ingredients(self, recipe: Recipe):
        for ing, qty in recipe.ingredients.items():
            self._stock[ing] -= qty

    def refill(self, ingredient: Ingredient, amount: int):
        self._stock[ingredient] += amount

# --- State Pattern Implementation ---
class State(ABC):
    @abstractmethod
    def select_drink(self, machine, beverage):
        pass

class IdleState(State):
    def select_drink(self, machine, beverage):
        print(f"Selecting {beverage.name}...")
        if machine.inventory.check_availability(beverage.recipe):
            machine.set_state(ProcessingState())
            machine.dispense(beverage)
        else:
            print("Error: Insufficient ingredients!")

class ProcessingState(State):
    def select_drink(self, machine, beverage):
        print("Machine is currently brewing. Please wait...")

# --- Main Controller (Singleton) ---
class CoffeeMachine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoffeeMachine, cls).__new__(cls)
            cls._instance._init_machine()
        return cls._instance

    def _init_machine(self):
        self.inventory = InventoryManager()
        self.state = IdleState()

    def set_state(self, state: State):
        self.state = state

    def select_drink(self, beverage: Beverage):
        self.state.select_drink(self, beverage)

    def dispense(self, beverage: Beverage):
        print(f"Brewing {beverage.name}...")
        self.inventory.deduct_ingredients(beverage.recipe)
        print(f"Your {beverage.name} is ready! ☕")
        self.set_state(IdleState())

# --- Execution ---
if __name__ == "__main__":
    machine = CoffeeMachine()
    espresso = Espresso()
    latte = Latte()

    # Scenario 1: Successful brew
    machine.select_drink(espresso) 
    
    # Scenario 2: Another brew
    machine.select_drink(latte)
```

### Logic Walkthrough
1. **Initialization**: The `CoffeeMachine` is initialized as a Singleton. It starts in `IdleState` with a full `InventoryManager`.
2. **Request**: The user calls `select_drink(beverage)`.
3. **Delegation**: The `CoffeeMachine` delegates the request to the current `State` object.
4. **Validation**: In `IdleState`, the machine checks the `InventoryManager` to see if the `Beverage`'s `Recipe` can be satisfied.
5. **State Transition**: If ingredients are available, the state changes to `ProcessingState` to prevent concurrent orders.
6. **Execution**: The `dispense()` method deducts the ingredients and prints the output.
7. **Completion**: The state resets to `IdleState`.

---

## 5. Real-World Applications

The design patterns used here are common in production systems beyond coffee machines:

- **State Pattern**: Used extensively in **Order Management Systems (OMS)** to track order statuses (e.g., `Placed` $\rightarrow$ `Paid` $\rightarrow$ `Shipped` $\rightarrow$ `Delivered`).
- **Strategy Pattern**: Used in **Payment Gateways** to switch between different payment methods (PayPal, Stripe, Credit Card) at runtime.
- **Inventory Management**: The logic of checking and deducting stock is the core of any **E-commerce Backend** (e.g., Amazon's checkout process).
- **Singleton**: Used for **Configuration Managers** or **Database Connection Pools** where having multiple instances would lead to resource waste or inconsistent states.

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Select Drink** | $O(I)$ | $O(1)$ | $I$ = number of ingredients in a recipe (usually small/constant). |
| **Check Availability** | $O(I)$ | $O(1)$ | Iterates through recipe requirements. |
| **Deduct Ingredients** | $O(I)$ | $O(1)$ | Updates the inventory map. |
| **Refill** | $O(1)$ | $O(1)$ | Simple map update. |""",
    'solutions': """# System Design Document: Coffee Vending Machine

## 1. Requirements & System Constraints

The goal is to design a robust, extensible, and maintainable software system for a Coffee Vending Machine. Modern vending machines are IoT-enabled, meaning they require both local control logic (for hardware interaction) and a cloud-based management layer (for monitoring and payments).

### 1.1 Functional Requirements
- **Beverage Selection**: Users can view a menu of available coffee types (e.g., Espresso, Latte, Cappuccino) and select one.
- **Recipe Management**: Each beverage has a specific recipe (e.g., Latte = 1 shot espresso + 200ml milk + 1 cup).
- **Payment Processing**: Support for multiple payment methods (Cash, Credit Card, Digital Wallet).
- **Inventory Management**: Track levels of ingredients (coffee beans, milk, water, sugar, cups). Prevent selection if ingredients are insufficient.
- **Dispensing Logic**: Orchestrate the hardware to dispense ingredients in the correct order.
- **Administrative Controls**: Allow technicians to refill ingredients, update pricing, and view machine health.
- **Error Handling**: Handle scenarios like payment failure, hardware jams, or ingredient depletion during brewing.

### 1.2 Non-Functional Requirements
- **Reliability**: High availability. The machine should not charge a user if it cannot dispense the drink.
- **Low Latency**: User interface responses must be near-instantaneous.
- **Consistency**: Strict consistency for inventory and payments (no "phantom" ingredients).
- **Extensibility**: Easy to add new beverage types or payment gateways without rewriting core logic.
- **Robustness**: Ability to recover to a safe state after a power failure or hardware crash.

---

## 2. High-Level Architecture

The system follows a **Layered Architecture** combining an embedded control system (on the machine) and a Cloud Backend (for fleet management).

### 2.1 Core Components
- **Machine Controller (Singleton)**: The central brain coordinating the state transitions.
- **State Manager**: Implements the State Design Pattern to handle transitions (Idle $\rightarrow$ Selecting $\rightarrow$ Paying $\rightarrow$ Brewing $\rightarrow$ Dispensing).
- **Inventory Manager**: Tracks real-time stock levels and validates recipe availability.
- **Payment Gateway Interface**: An abstraction layer to handle various payment providers.
- **Brewing Engine**: The low-level hardware abstraction layer (HAL) that sends signals to pumps, heaters, and grinders.
- **Recipe Store**: A registry of beverage compositions.

### 2.2 Sequence Diagram (Ordering Flow)

```mermaid
sequenceDiagram
    participant User
    participant Controller as MachineController
    participant State as StateManager
    participant Inv as InventoryManager
    participant Pay as PaymentProcessor
    participant HW as HardwareEngine

    User->>Controller: Select Beverage (Latte)
    Controller->>Inv: Check Ingredients(LatteRecipe)
    Inv-->>Controller: Ingredients Available
    Controller->>State: Transition to PAYMENT_PENDING
    User->>Controller: Process Payment
    Controller->>Pay: Authorize Transaction
    Pay-->>Controller: Payment Success
    Controller->>State: Transition to BREWING
    Controller->>Inv: Deduct Ingredients(LatteRecipe)
    Controller->>HW: Execute Brew(LatteRecipe)
    HW-->>Controller: Brew Complete
    Controller->>State: Transition to IDLE
    Controller-->>User: Dispense Coffee
```

---

## 3. Detailed Database Schema Design

Since this is an IoT system, data is split between a **Local Cache (SQLite/Key-Value)** for offline operation and a **Cloud Database (PostgreSQL)** for fleet management and analytics.

### 3.1 Cloud Database (Relational - PostgreSQL)
Chosen for ACID compliance, ensuring payment and inventory records are never corrupted.

#### Table: `beverages`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `beverage_id` | UUID | PK | Unique identifier for the drink |
| `name` | VARCHAR(50) | NOT NULL | e.g., "Vanilla Latte" |
| `price` | DECIMAL(10,2) | NOT NULL | Price per unit |
| `is_active` | BOOLEAN | DEFAULT True | Soft delete/availability |

#### Table: `ingredients`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `ingredient_id` | UUID | PK | Unique identifier (e.g., Beans, Milk) |
| `name` | VARCHAR(50) | UNIQUE | Name of the ingredient |
| `unit` | VARCHAR(10) | NOT NULL | ml, grams, units |

#### Table: `recipes`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `recipe_id` | UUID | PK | Unique identifier |
| `beverage_id` | UUID | FK $\rightarrow$ beverages | Link to beverage |
| `ingredient_id`| UUID | FK $\rightarrow$ ingredients | Link to ingredient |
| `quantity` | DECIMAL(10,2) | NOT NULL | Amount required for 1 cup |

#### Table: `machine_inventory`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `machine_id` | UUID | PK/FK | Unique machine identifier |
| `ingredient_id`| UUID | PK/FK | Ingredient identifier |
| `current_qty` | DECIMAL(10,2) | NOT NULL | Current stock in the machine |
| `last_updated` | TIMESTAMP | NOT NULL | For synchronization |

#### Table: `transactions`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `tx_id` | UUID | PK | Transaction ID |
| `machine_id` | UUID | FK | Which machine sold it |
| `beverage_id` | UUID | FK | What was sold |
| `amount` | DECIMAL(10,2) | NOT NULL | Final price paid |
| `status` | ENUM | SUCCESS, FAILED | Transaction status |
| `timestamp` | TIMESTAMP | NOT NULL | Time of purchase |

### 3.2 Indexing Strategy
- **Index on `transactions(machine_id, timestamp)`**: To quickly generate sales reports per machine.
- **Index on `recipes(beverage_id)`**: To quickly fetch all ingredients needed for a selected drink.

---

## 4. Core API Design

The machine communicates with the Cloud Backend via a REST or gRPC API.

### 4.1 Beverage & Inventory API
- **`GET /v1/beverages`**: Fetch the current menu and pricing.
- **`GET /v1/machine/{id}/status`**: Get current ingredient levels and hardware health.
- **`POST /v1/machine/{id}/refill`**: Update inventory levels after a technician visit.

### 4.2 Transaction API
- **`POST /v1/payments/process`**
    - **Request**: `{ "machine_id": "uuid", "amount": 4.50, "payment_token": "tok_...", "beverage_id": "uuid" }`
    - **Response**: `{ "transaction_id": "uuid", "status": "APPROVED" }`

### 4.3 Telemetry API
- **`POST /v1/telemetry/heartbeat`**
    - **Request**: `{ "machine_id": "uuid", "temp": 92, "water_level": 40, "error_code": 0 }`
    - **Response**: `{ "status": "OK", "pending_updates": ["recipe_v2.json"] }`

---

## 5. Scalability & Advanced Topics

### 5.1 Handling Concurrency & State
To prevent "Double Dispensing" or race conditions:
- **Local Mutex**: The `MachineController` uses a mutex lock during the `BREWING` state to ensure no other inputs are processed until the cycle finishes.
- **State Pattern**: By using a state machine, we eliminate complex `if-else` blocks. For example, the `PaymentState` only allows transitions to `BrewingState` (on success) or `IdleState` (on cancel).

### 5.2 Fault Tolerance
- **Atomic Transactions**: The system follows the "Commit then Act" pattern. Payment is authorized $\rightarrow$ Inventory is reserved $\rightarrow$ Brewing starts. If brewing fails, a "Refund" event is triggered automatically.
- **Offline Mode**: The machine caches the menu and recipes locally. If the cloud is unreachable, it can accept cash (if hardware exists) and queue the transaction logs to sync later.
- **Watchdog Timer**: A hardware timer that resets the system if the software hangs during a brew cycle to prevent overheating.

### 5.3 IoT Optimization
- **MQTT for Telemetry**: Instead of HTTP, use MQTT for heartbeats and alerts to reduce overhead and allow the server to "push" price updates to machines in real-time.
- **Edge Computing**: Recipe validation happens at the edge (on the machine) to ensure zero latency for the user.

---

## 6. Trade-off Analysis

### 6.1 State Pattern vs. Simple Conditional Logic
- **Trade-off**: State pattern increases the number of classes (Boilerplate).
- **Decision**: Chosen State Pattern because the machine has distinct, mutually exclusive modes. This makes adding a "Maintenance Mode" or "Cleaning Mode" trivial without breaking existing logic.

### 6.2 Local vs. Cloud Inventory
- **Trade-off**: Updating cloud inventory on every cup dispensed creates high network dependency.
- **Decision**: **Eventual Consistency**. The machine tracks inventory locally for real-time decisions and syncs the aggregate usage to the cloud every 10 transactions or once per hour. This ensures the machine remains functional during network outages.

### 6.3 CAP Theorem Priority
- **Priority**: **Consistency (C) and Partition Tolerance (P)**.
- **Reasoning**: In a vending machine, Availability (A) of the *Cloud* is secondary to Consistency. We cannot risk charging a customer for a drink that doesn't exist (Inventory inconsistency) or failing to record a payment. If the cloud is partitioned, the machine switches to a "Limited Offline Mode."""",
}

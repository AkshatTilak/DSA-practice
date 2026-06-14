# Vending Machine LLD (State Pattern)

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
- **ATM Machines:** Similar to vending machines, managing `CardInserted`, `PinEntered`, and `CashWithdrawing` states.
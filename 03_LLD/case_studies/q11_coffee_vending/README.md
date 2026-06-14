# Coffee Vending Machine LLD

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
| **Refill** | $O(1)$ | $O(1)$ | Simple map update. |
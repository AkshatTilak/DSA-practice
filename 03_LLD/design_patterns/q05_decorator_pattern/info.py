INFO = {
    'difficulty': 'Medium',
    'link': 'https://refactoring.guru/design-patterns/decorator',
    'description': 'Wrapper pattern dynamic additions.',
    'groups': ['Structural Patterns'],
    'readme_content': """# Decorator Pattern LLD

The **Decorator Pattern** is a structural design pattern that allows behavior to be added to an individual object, either statically or dynamically, without affecting the behavior of other objects from the same class. It is often referred to as a **Wrapper**, as it wraps the original object to provide additional functionality.

---

## 1. Overview & System Requirements

### Core Objective
The primary goal is to provide a flexible alternative to sub-classing for extending functionality. Instead of creating a massive inheritance hierarchy to cover every possible combination of features, the Decorator pattern uses **composition** to stack behaviors.

### Functional Requirements
- **Interface Consistency**: The decorator must implement the same interface as the object it wraps, ensuring it remains transparent to the client.
- **Dynamic Extension**: Behaviors should be addable at runtime.
- **Stackability**: Multiple decorators should be able to wrap a single object (nesting), allowing for additive behavior.
- **Non-Intrusiveness**: Adding new decorators should not require modifying the existing base component code.

### Example Scenario: Coffee Ordering System
Imagine a coffee shop. You have a `SimpleCoffee`. However, customers can add `Milk`, `Sugar`, or `WhippedCream`. If we used inheritance, we would need classes like `CoffeeWithMilk`, `CoffeeWithMilkAndSugar`, `CoffeeWithSugarAndCream`, etc., leading to a **class explosion**. The Decorator pattern solves this by wrapping the base coffee in "topping" objects.

---

## 2. Design Principles & Patterns

### Applied SOLID Principles
- **Open/Closed Principle (OCP)**: The system is **open for extension** (we can create new decorators) but **closed for modification** (we don't touch the `ConcreteComponent` or existing decorators to add new ones).
- **Single Responsibility Principle (SRP)**: The base component handles the core logic, while each decorator handles one specific additional feature.

### Design Trade-offs: Composition over Inheritance
| Aspect | Inheritance | Decorator (Composition) |
| :--- | :--- | :--- |
| **Binding** | Static (Compile-time) | Dynamic (Runtime) |
| **Flexibility** | Rigid; leads to class explosion | Flexible; allows mixing and matching |
| **Complexity** | Simpler for single extensions | More classes to manage (many small wrappers) |
| **Relationship** | "Is-a" relationship | "Has-a" relationship (wraps) |

---

## 3. Class Structure & Relationships

### Components
1. **Component (Interface/Abstract Class)**: Defines the interface for objects that can have responsibilities added to them dynamically.
2. **Concrete Component**: The original object to which additional responsibilities can be attached.
3. **Base Decorator**: A class that implements the Component interface and contains a reference to a Component object. It delegates all work to the wrapped object.
4. **Concrete Decorator**: Extends the Base Decorator and adds specific behavior before or after calling the wrapped object's method.

### Relationship Diagram (ASCII)
```text
       +-------------------+
       |    <<Interface>>  |
       |     Component     | <------------------+
       +-------------------+                    |
               ^                                |
               |                                |
      +-------------------+            +-------------------+
      | ConcreteComponent |            |   BaseDecorator   |
      +-------------------+            +-------------------+
                                                ^
                                                |
                                       +-------------------+
                                       | ConcreteDecorator |
                                       +-------------------+
                                                |
                                                v
                                       (Wraps another Component)
```

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation Strategy
1. Define a `Coffee` abstract base class with a `get_cost()` method.
2. Create a `SimpleCoffee` class that returns the base price.
3. Create a `CoffeeDecorator` that also inherits from `Coffee` and stores a `Coffee` instance.
4. Create specific decorators (e.g., `MilkDecorator`) that add their own cost to the result of the wrapped coffee's `get_cost()`.

### Complete Implementation

```python
from abc import ABC, abstractmethod

# 1. Component Interface
class Coffee(ABC):
    @abstractmethod
    def get_cost(self) -> float:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

# 2. Concrete Component
class SimpleCoffee(Coffee):
    def get_cost(self) -> float:
        return 2.0

    def get_description(self) -> str:
        return "Simple Coffee"

# 3. Base Decorator
class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._decorated_coffee = coffee

    def get_cost(self) -> float:
        return self._decorated_coffee.get_cost()

    def get_description(self) -> str:
        return self._decorated_coffee.get_description()

# 4. Concrete Decorators
class MilkDecorator(CoffeeDecorator):
    def get_cost(self) -> float:
        # Base cost + Milk cost
        return super().get_cost() + 0.5

    def get_description(self) -> str:
        return super().get_description() + ", Milk"

class SugarDecorator(CoffeeDecorator):
    def get_cost(self) -> float:
        # Base cost + Sugar cost
        return super().get_cost() + 0.2

    def get_description(self) -> str:
        return super().get_description() + ", Sugar"

class WhipDecorator(CoffeeDecorator):
    def get_cost(self) -> float:
        # Base cost + Whip cost
        return super().get_cost() + 0.7

    def get_description(self) -> str:
        return super().get_description() + ", Whipped Cream"

# Solution Wrapper
def solve():
    # Scenario: Customer wants Simple Coffee + Milk + Sugar
    my_coffee = SimpleCoffee()
    print(f"Order: {my_coffee.get_description()} | Cost: ${my_coffee.get_cost():.2f}")

    # Add Milk
    my_coffee = MilkDecorator(my_coffee)
    print(f"Order: {my_coffee.get_description()} | Cost: ${my_coffee.get_cost():.2f}")

    # Add Sugar
    my_coffee = SugarDecorator(my_coffee)
    print(f"Order: {my_coffee.get_description()} | Cost: ${my_coffee.get_cost():.2f}")
    
    # Final Result: Order: Simple Coffee, Milk, Sugar | Cost: $2.70

if __name__ == "__main__":
    solve()
```

### Execution Logic Walkthrough
1. **`SimpleCoffee()`**: Creates the core object. `get_cost()` returns `2.0`.
2. **`MilkDecorator(SimpleCoffee)`**: Wraps the core object. When `get_cost()` is called, it calls `SimpleCoffee.get_cost()` (2.0) and adds `0.5`. Total: `2.5`.
3. **`SugarDecorator(MilkDecorator(SimpleCoffee))`**: Wraps the Milk-wrapped coffee. When `get_cost()` is called, it calls `MilkDecorator.get_cost()` (2.5) and adds `0.2`. Total: `2.7`.
4. **Recursion/Delegation**: The call travels down the chain to the innermost `ConcreteComponent` and then accumulates values as the stack unwinds.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Adding a Decorator** | $O(1)$ | $O(1)$ | Simply wrapping an object in another. |
| **Method Invocation** | $O(N)$ | $O(N)$ | $N$ is the number of decorators. Each call triggers a recursive chain. |
| **Memory Usage** | $O(N)$ | $O(N)$ | Each decorator is a new object instance on the heap. |

---

## 6. Real-World Applications

1. **Java I/O Streams**: This is the most textbook example.
   - `BufferedInputStream(FileInputStream(File))`
   - The `FileInputStream` reads raw bytes, while `BufferedInputStream` adds buffering logic without changing the `InputStream` interface.
2. **Python Function Decorators**: While Python's `@decorator` syntax is a language feature, it implements the same concept: wrapping a function to add pre-processing or post-processing logic (e.g., `@logging`, `@auth_required`).
3. **Web Middleware**: In frameworks like Express.js or Django, middleware acts as decorators. A request passes through a series of wrappers (Auth $\rightarrow$ Logging $\rightarrow$ Compression) before reaching the final route handler.
4. **UI Component Tooltips**: In GUI frameworks, a `BorderDecorator` or `ScrollDecorator` can be wrapped around a `Panel` to add visual borders or scrollbars without modifying the `Panel` class logic.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1) for cost calculation.
# Space Complexity: O(1).
# The naive approach uses a single class with boolean flags to represent additions. 
# This violates the Open/Closed Principle because every time a new ingredient is added, 
# the core Coffee class must be modified. It leads to a "God Object" that knows too much 
# about every possible variation.

from typing import List

class NaiveCoffee:
    def __init__(self, base_cost: float = 2.0):
        self.base_cost = base_cost
        self.has_milk = False
        self.has_sugar = False
        self.has_vanilla = False

    def add_milk(self):
        self.has_milk = True

    def add_sugar(self):
        self.has_sugar = True

    def add_vanilla(self):
        self.has_vanilla = True

    def get_cost(self) -> float:
        cost = self.base_cost
        if self.has_milk:
            cost += 0.5
        if self.has_sugar:
            cost += 0.2
        if self.has_vanilla:
            cost += 0.7
        return cost

    def get_description(self) -> str:
        desc = "Simple Coffee"
        if self.has_milk:
            desc += ", Milk"
        if self.has_sugar:
            desc += ", Sugar"
        if self.has_vanilla:
            desc += ", Vanilla"
        return desc

def solve_naive():
    coffee = NaiveCoffee()
    coffee.add_milk()
    coffee.add_sugar()
    print(f"{coffee.get_description()} costs {coffee.get_cost()}")

# --- APPROACH 2: Optimal (Decorator Pattern) ---
# Time Complexity: O(N) where N is the number of decorators applied.
# Space Complexity: O(N) to maintain the chain of decorator objects.
# This approach is optimal because it follows the Open/Closed Principle. 
# We can add new decorators (e.g., Caramel, Whipped Cream) without modifying 
# existing classes. It allows for dynamic composition of behaviors at runtime 
# and avoids the class explosion problem encountered with inheritance.

from abc import ABC, abstractmethod

class Coffee(ABC):
    \"\"\"The Component interface defines operations that can be altered by decorators.\"\"\"
    @abstractmethod
    def get_cost(self) -> float:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

class SimpleCoffee(Coffee):
    \"\"\"A Concrete Component provides the basic implementation of the operations.\"\"\"
    def get_cost(self) -> float:
        return 2.0

    def get_description(self) -> str:
        return "Simple Coffee"

class CoffeeDecorator(Coffee):
    \"\"\"The base Decorator class follows the same interface as the other components.\"\"\"
    def __init__(self, coffee: Coffee):
        self._decorated_coffee = coffee

    def get_cost(self) -> float:
        return self._decorated_coffee.get_cost()

    def get_description(self) -> str:
        return self._decorated_coffee.get_description()

class MilkDecorator(CoffeeDecorator):
    \"\"\"Concrete Decorator: Adds milk functionality.\"\"\"
    def get_cost(self) -> float:
        return super().get_cost() + 0.5

    def get_description(self) -> str:
        return super().get_description() + ", Milk"

class SugarDecorator(CoffeeDecorator):
    \"\"\"Concrete Decorator: Adds sugar functionality.\"\"\"
    def get_cost(self) -> float:
        return super().get_cost() + 0.2

    def get_description(self) -> str:
        return super().get_description() + ", Sugar"

class VanillaDecorator(CoffeeDecorator):
    \"\"\"Concrete Decorator: Adds vanilla functionality.\"\"\"
    def get_cost(self) -> float:
        return super().get_cost() + 0.7

    def get_description(self) -> str:
        return super().get_description() + ", Vanilla"

def solve_optimal():
    # Start with a simple coffee
    my_coffee = SimpleCoffee()
    
    # Dynamically wrap it with decorators
    my_coffee = MilkDecorator(my_coffee)
    my_coffee = SugarDecorator(my_coffee)
    my_coffee = VanillaDecorator(my_coffee)
    
    print(f"{my_coffee.get_description()} costs {my_coffee.get_cost()}")

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package design_patterns;

/**
 * Java implementation of the Decorator Pattern for a Coffee Shop scenario.
 */

interface Coffee {
    double getCost();
    String getDescription();
}

class SimpleCoffee implements Coffee {
    @Override
    public double getCost() {
        return 2.0;
    }

    @Override
    public String getDescription() {
        return "Simple Coffee";
    }
}

abstract class CoffeeDecorator implements Coffee {
    protected Coffee decoratedCoffee;

    public CoffeeDecorator(Coffee coffee) {
        this.decoratedCoffee = coffee;
    }

    public double getCost() {
        return decoratedCoffee.getCost();
    }

    public String getDescription() {
        return decoratedCoffee.getDescription();
    }
}

class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) {
        super(coffee);
    }

    @Override
    public double getCost() {
        return super.getCost() + 0.5;
    }

    @Override
    public String getDescription() {
        return super.getDescription() + ", Milk";
    }
}

class SugarDecorator extends CoffeeDecorator {
    public SugarDecorator(Coffee coffee) {
        super(coffee);
    }

    @Override
    public double getCost() {
        return super.getCost() + 0.2;
    }

    @Override
    public String getDescription() {
        return super.getDescription() + ", Sugar";
    }
}

public class DecoratorPattern {
    public static void main(String[] args) {
        Coffee myCoffee = new SimpleCoffee();
        myCoffee = new MilkDecorator(myCoffee);
        myCoffee = new SugarDecorator(myCoffee);
        
        System.out.println(myCoffee.getDescription() + " costs " + myCoffee.getCost());
    }
}
\"\"\"""",
}

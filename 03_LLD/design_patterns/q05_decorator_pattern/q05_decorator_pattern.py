"""
Challenge: q05_decorator_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/decorator

Problem:
Wrapper pattern dynamic additions.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
    """The Component interface defines operations that can be altered by decorators."""
    @abstractmethod
    def get_cost(self) -> float:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

class SimpleCoffee(Coffee):
    """A Concrete Component provides the basic implementation of the operations."""
    def get_cost(self) -> float:
        return 2.0

    def get_description(self) -> str:
        return "Simple Coffee"

class CoffeeDecorator(Coffee):
    """The base Decorator class follows the same interface as the other components."""
    def __init__(self, coffee: Coffee):
        self._decorated_coffee = coffee

    def get_cost(self) -> float:
        return self._decorated_coffee.get_cost()

    def get_description(self) -> str:
        return self._decorated_coffee.get_description()

class MilkDecorator(CoffeeDecorator):
    """Concrete Decorator: Adds milk functionality."""
    def get_cost(self) -> float:
        return super().get_cost() + 0.5

    def get_description(self) -> str:
        return super().get_description() + ", Milk"

class SugarDecorator(CoffeeDecorator):
    """Concrete Decorator: Adds sugar functionality."""
    def get_cost(self) -> float:
        return super().get_cost() + 0.2

    def get_description(self) -> str:
        return super().get_description() + ", Sugar"

class VanillaDecorator(CoffeeDecorator):
    """Concrete Decorator: Adds vanilla functionality."""
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
"""
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
"""

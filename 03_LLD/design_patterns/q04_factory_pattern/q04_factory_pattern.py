"""
Challenge: q04_factory_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/factory-method

Problem:
Factory method class instantiations.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N) where N is the number of concrete types to check in the if-else chain.
# Space Complexity: O(1) excluding the space for the instantiated object.
# This approach uses a simple conditional chain to determine which class to instantiate. 
# It violates the Open/Closed Principle because adding a new shape requires modifying the factory method.

from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def draw(self) -> str:
        pass

class Circle(Shape):
    def draw(self) -> str:
        return "Drawing a Circle"

class Square(Shape):
    def draw(self) -> str:
        return "Drawing a Square"

class Rectangle(Shape):
    def draw(self) -> str:
        return "Drawing a Rectangle"

class ShapeFactoryNaive:
    def get_shape(self, shape_type: str) -> Shape:
        shape_type = shape_type.upper()
        if shape_type == "CIRCLE":
            return Circle()
        elif shape_type == "SQUARE":
            return Square()
        elif shape_type == "RECTANGLE":
            return Rectangle()
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

def solve_naive(shape_type: str):
    factory = ShapeFactoryNaive()
    try:
        shape = factory.get_shape(shape_type)
        return shape.draw()
    except ValueError as e:
        return str(e)

# --- APPROACH 2: Optimal (Registry-based Factory) ---
# Time Complexity: O(1) for object instantiation via dictionary lookup.
# Space Complexity: O(K) where K is the number of registered shapes in the mapping.
# This approach is optimal because it uses a registry (dictionary) to map identifiers to class constructors.
# It adheres to the Open/Closed Principle; new shapes can be registered without modifying the core 
# logic of the get_shape method.

from abc import ABC, abstractmethod
from typing import Dict, Type

class Shape(ABC):
    @abstractmethod
    def draw(self) -> str:
        pass

class Circle(Shape):
    def draw(self) -> str:
        return "Drawing a Circle"

class Square(Shape):
    def draw(self) -> str:
        return "Drawing a Square"

class Rectangle(Shape):
    def draw(self) -> str:
        return "Drawing a Rectangle"

class ShapeFactoryOptimal:
    def __init__(self):
        # Registry mapping type names to class references
        self._shapes_registry: Dict[str, Type[Shape]] = {
            "CIRCLE": Circle,
            "SQUARE": Square,
            "RECTANGLE": Rectangle
        }

    def register_shape(self, shape_type: str, shape_class: Type[Shape]):
        """Allows adding new shapes at runtime without modifying the factory class."""
        self._shapes_registry[shape_type.upper()] = shape_class

    def get_shape(self, shape_type: str) -> Shape:
        shape_type = shape_type.upper()
        shape_class = self._shapes_registry.get(shape_type)
        if not shape_class:
            raise ValueError(f"Unknown shape type: {shape_type}")
        return shape_class()

def solve_optimal(shape_type: str):
    factory = ShapeFactoryOptimal()
    try:
        shape = factory.get_shape(shape_type)
        return shape.draw()
    except ValueError as e:
        return str(e)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package design_patterns;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

// Product Interface
interface Shape {
    String draw();
}

// Concrete Products
class Circle implements Shape {
    @Override
    public String draw() {
        return "Drawing a Circle";
    }
}

class Square implements Shape {
    @Override
    public String draw() {
        return "Drawing a Square";
    }
}

class Rectangle implements Shape {
    @Override
    public String draw() {
        return "Drawing a Rectangle";
    }
}

// Factory Class
public class ShapeFactory {
    private static final Map<String, Supplier<Shape>> registry = new HashMap<>();

    static {
        registry.put("CIRCLE", Circle::new);
        registry.put("SQUARE", Square::new);
        registry.put("RECTANGLE", Rectangle::new);
    }

    public static void registerShape(String type, Supplier<Shape> supplier) {
        registry.put(type.toUpperCase(), supplier);
    }

    public Shape getShape(String shapeType) {
        Supplier<Shape> shapeSupplier = registry.get(shapeType.toUpperCase());
        if (shapeSupplier == null) {
            throw new IllegalArgumentException("Unknown shape type: " + shapeType);
        }
        return shapeSupplier.get();
    }

    public static void main(String[] args) {
        ShapeFactory factory = new ShapeFactory();
        Shape circle = factory.getShape("CIRCLE");
        System.out.println(circle.draw());
        
        Shape square = factory.getShape("SQUARE");
        System.out.println(square.draw());
    }
}
"""

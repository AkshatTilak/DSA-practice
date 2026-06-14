# Food Ordering & Ratings System (Zomato/Swiggy) LLD

## 1. Overview & System Requirements

The goal is to design a Low-Level Design (LLD) for a food delivery platform similar to Zomato or Swiggy. The system must handle the complexities of restaurant management, menu curation, order processing, payment integration, delivery tracking, and a feedback loop via ratings.

### Core Actors
- **Customer**: Searches for restaurants, places orders, makes payments, and rates the experience.
- **Restaurant Owner**: Manages the restaurant profile, updates the menu, and accepts/prepares orders.
- **Delivery Partner**: Accepts delivery requests and updates the delivery status.
- **Admin**: Manages the overall platform, handles disputes, and manages user accounts.

### Functional Requirements
- **Restaurant Management**: Ability to add/update restaurants and their menus (items, prices, categories).
- **Search & Discovery**: Search for restaurants by name or cuisine.
- **Order Workflow**: 
    - Add items to a cart.
    - Place an order and process payment.
    - Update order status (Placed $\rightarrow$ Confirmed $\rightarrow$ Preparing $\rightarrow$ Out for Delivery $\rightarrow$ Delivered).
- **Payment System**: Support multiple payment modes (UPI, Credit Card, Wallet).
- **Delivery Assignment**: Assign a delivery partner to a confirmed order.
- **Rating System**: Customers can rate restaurants and delivery partners.

---

## 2. Design Principles & Patterns

To ensure the system is scalable and maintainable, the following OOP principles and design patterns are applied:

### SOLID Principles
- **Single Responsibility Principle (SRP)**: The `PaymentProcessor` only handles transactions; the `OrderManager` only handles order state transitions; the `SearchService` only handles filtering.
- **Open/Closed Principle (OCP)**: The `Payment` class is abstract. New payment methods (e.g., Crypto) can be added by extending the base class without modifying existing order logic.
- **Liskov Substitution Principle (LSP)**: Any specific user type (`Customer`, `DeliveryPartner`) can be treated as a `User` without breaking the system.
- **Interface Segregation Principle (ISP)**: Different roles have different interfaces (e.g., `IDeliveryActions` for partners vs `ICustomerActions` for customers).
- **Dependency Inversion Principle (DIP)**: High-level `OrderManager` depends on the `Payment` abstraction, not concrete classes like `UPIPayment`.

### Design Patterns
- **Strategy Pattern**: Used for **Payment Processing** and **Pricing Strategies** (e.g., calculating delivery fees based on distance or surge pricing).
- **Observer Pattern**: Used to notify the Customer and Restaurant when the order status changes (e.g., "Your food is out for delivery").
- **Singleton Pattern**: The `FoodOrderingSystem` (or the `OrderManager`) is implemented as a Singleton to ensure a centralized point of coordination.
- **Factory Pattern**: Used to create different types of `Payment` objects based on user selection.

---

## 3. Class Structure & Relationships

### ASCII Class Diagram
```text
+-------------------+       +-------------------+       +-------------------+
|      User         |<------|     Customer      |------>|      Order       |
+-------------------+       +-------------------+       +-------------------+
| - userId          |       | - email           |       | - orderId        |
| - name            |       | - address         |       | - items          |
| - phone           |       +-------------------+       | - totalAmount    |
+--------^----------+                                   | - status         |
         |                                              +---------+---------+
         |                                                            |
         +-------------------+-------------------+                    |
         |                   |                   |                    v
+-------------------+ +-------------------+ +-------------------+ +-------------------+
| RestaurantOwner   | |  DeliveryPartner  | |    Restaurant     | |      Payment      |
+-------------------+ +-------------------+ +-------------------+ +-------------------+
| - restaurantId    | | - vehicleDetails  | | - restaurantId    | | - paymentId       |
+-------------------+ +-------------------+ | - menu (List)     | | - amount          |
                                            +---------+---------+ +---------^---------+
                                                      |                     |
                                            +-------------------+   +-------+-------+
                                            |      Menu         |   | UPI | Card | Wallet |
                                            +-------------------+   +---------------+
                                            | - foodItems (List)|
                                            +-------------------+
```

### Key Entities & Attributes
| Class | Responsibility | Key Attributes |
| :--- | :--- | :--- |
| `User` | Base class for all platform participants | `userId`, `name`, `phone` |
| `Restaurant` | Stores restaurant details and menu | `restaurantId`, `menu`, `avgRating` |
| `FoodItem` | Represents a single dish | `itemId`, `name`, `price`, `category` |
| `Order` | Tracks the lifecycle of a food order | `orderId`, `items`, `status`, `customer` |
| `Payment` | Abstract class for financial transactions | `transactionId`, `amount`, `status` |
| `Rating` | Stores feedback for restaurants/drivers | `ratingValue`, `comment`, `targetId` |

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict

# --- Enums & Constants ---
class OrderStatus(Enum):
    PLACED = 1
    CONFIRMED = 2
    PREPARING = 3
    OUT_FOR_DELIVERY = 4
    DELIVERED = 5
    CANCELLED = 6

# --- Payment Strategy ---
class Payment(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class UPIPayment(Payment):
    def process_payment(self, amount: float) -> bool:
        print(f"Processing UPI payment of ${amount}...")
        return True

class CardPayment(Payment):
    def process_payment(self, amount: float) -> bool:
        print(f"Processing Card payment of ${amount}...")
        return True

# --- Core Entities ---
class FoodItem:
    def __init__(self, item_id: str, name: str, price: float):
        self.item_id = item_id
        self.name = name
        self.price = price

class Menu:
    def __init__(self):
        self.items: Dict[str, FoodItem] = {}

    def add_item(self, item: FoodItem):
        self.items[item.item_id] = item

    def get_item(self, item_id: str) -> FoodItem:
        return self.items.get(item_id)

class Restaurant:
    def __init__(self, restaurant_id: str, name: str):
        self.restaurant_id = restaurant_id
        self.name = name
        self.menu = Menu()
        self.ratings: List[int] = []

    def add_food_item(self, item: FoodItem):
        self.menu.add_item(item)

    def get_average_rating(self) -> float:
        return sum(self.ratings) / len(self.ratings) if self.ratings else 0.0

    def add_rating(self, score: int):
        self.ratings.append(score)

class User:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name

class Customer(User):
    def __init__(self, user_id: str, name: str, address: str):
        super().__init__(user_id, name)
        self.address = address

class DeliveryPartner(User):
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name)
        self.is_available = True

# --- Order Management ---
class Order:
    def __init__(self, order_id: str, customer: Customer, restaurant: Restaurant, items: List[FoodItem]):
        self.order_id = order_id
        self.customer = customer
        self.restaurant = restaurant
        self.items = items
        self.status = OrderStatus.PLACED
        self.total_amount = sum(item.price for item in items)
        self.delivery_partner = None

    def update_status(self, new_status: OrderStatus):
        self.status = new_status
        print(f"Order {self.order_id} updated to {new_status.name}")

# --- System Orchestrator (Singleton) ---
class FoodOrderingSystem:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FoodOrderingSystem, cls).__new__(cls)
            cls._instance.restaurants = {}
            cls._instance.orders = {}
            cls._instance.delivery_partners = []
        return cls._instance

    def add_restaurant(self, restaurant: Restaurant):
        self.restaurants[restaurant.restaurant_id] = restaurant

    def add_delivery_partner(self, partner: DeliveryPartner):
        self.delivery_partners.append(partner)

    def place_order(self, order_id: str, customer: Customer, restaurant_id: str, 
                    item_ids: List[str], payment_method: Payment) -> Order:
        restaurant = self.restaurants.get(restaurant_id)
        if not restaurant:
            raise Exception("Restaurant not found")

        items = [restaurant.menu.get_item(iid) for iid in item_ids]
        order = Order(order_id, customer, restaurant, items)

        if payment_method.process_payment(order.total_amount):
            order.update_status(OrderStatus.CONFIRMED)
            self.orders[order_id] = order
            return order
        else:
            raise Exception("Payment failed")

    def assign_delivery_partner(self, order_id: str):
        order = self.orders.get(order_id)
        for partner in self.delivery_partners:
            if partner.is_available:
                order.delivery_partner = partner
                partner.is_available = False
                order.update_status(OrderStatus.OUT_FOR_DELIVERY)
                return partner
        raise Exception("No delivery partners available")

# --- Execution Flow ---
if __name__ == "__main__":
    # Initialize System
    system = FoodOrderingSystem()

    # Setup Restaurants and Menu
    res1 = Restaurant("R1", "Burger King")
    res1.add_food_item(FoodItem("I1", "Whopper", 10.0))
    res1.add_food_item(FoodItem("I2", "Fries", 5.0))
    system.add_restaurant(res1)

    # Setup Users
    customer = Customer("C1", "Alice", "123 Maple St")
    driver = DeliveryPartner("D1", "Bob")
    system.add_delivery_partner(driver)

    # Step 1: Place Order using UPI
    try:
        my_order = system.place_order("O101", customer, "R1", ["I1", "I2"], UPIPayment())
        print(f"Order placed successfully! Total: ${my_order.total_amount}")

        # Step 2: Assign Driver
        system.assign_delivery_partner("O101")
        
        # Step 3: Complete Order
        my_order.update_status(OrderStatus.DELIVERED)

        # Step 4: Rating
        res1.add_rating(5)
        print(f"Restaurant average rating: {res1.get_average_rating()}")

    except Exception as e:
        print(f"Error: {e}")
```

### Logic Walkthrough
1.  **Initialization**: The `FoodOrderingSystem` creates a registry of available restaurants and drivers.
2.  **Ordering**: The `place_order` method acts as the coordinator. It fetches the restaurant, calculates the price based on the `FoodItem` list, and triggers the `Payment` strategy.
3.  **Decoupling**: Notice that `place_order` takes a `Payment` object. It doesn't care if it's `UPIPayment` or `CardPayment`—it only calls `process_payment()`. This is the **Strategy Pattern**.
4.  **Fulfillment**: The `assign_delivery_partner` method searches for the first available driver, mimicking a basic dispatch system.
5.  **Feedback**: The `Restaurant` object manages its own rating list, allowing for a simple calculation of the average rating.

---

## 5. Real-World Applications

This LLD structure is the foundation for several production-grade systems:

- **Hyper-local Delivery**: Used by **DoorDash, UberEats, and Zomato** to manage the complex state machine of an order (Pending $\rightarrow$ Accepted $\rightarrow$ Preparing $\rightarrow$ Picked Up $\rightarrow$ Delivered).
- **Marketplace Platforms**: The separation of User roles (Customer, Provider, Driver) is a standard pattern in multi-sided marketplaces.
- **Payment Gateways**: The use of the Strategy Pattern for payments allows these apps to integrate Stripe, PayPal, or Razorpay without changing the core order logic.
- **Dynamic Pricing**: In real systems, the `total_amount` calculation would be handled by a `PricingEngine` class that implements different strategies for surge pricing, coupons, and delivery fees based on geolocation.

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Place Order** | $O(I)$ | $O(I)$ | $I$ = number of items in the order. |
| **Search Restaurant**| $O(1)$ | $O(R)$ | Using a Hashmap for $R$ restaurants. |
| **Assign Driver** | $O(D)$ | $O(1)$ | Linear search through $D$ delivery partners. |
| **Calculate Rating** | $O(N)$ | $O(N)$ | $N$ = number of ratings received. |
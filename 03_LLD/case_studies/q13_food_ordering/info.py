INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Food Ordering and Ratings (Zomato/Swiggy).',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Food Ordering & Ratings System (Zomato/Swiggy) LLD

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
| **Calculate Rating** | $O(N)$ | $O(N)$ | $N$ = number of ratings received. |""",
    'solutions': """# System Design Document: Food Ordering and Ratings System (Zomato/Swiggy)

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **User Management:** Users can create profiles, manage addresses, and view order history.
*   **Restaurant Management:** Restaurant owners can manage their profiles, update menus (items, prices, availability), and manage order requests.
*   **Search & Discovery:** Users can search for restaurants by name, cuisine, or location. Search must be filtered by distance/geography.
*   **Ordering System:** Users can add items to a cart, apply coupons, and place an order.
*   **Payment Integration:** Secure payment processing through third-party gateways.
*   **Delivery Management:** Automatic assignment of the nearest available delivery partner to an order. Real-time tracking of the delivery partner.
*   **Ratings & Reviews:** Users can rate the restaurant and the delivery partner after order completion.
*   **Notifications:** Real-time updates on order status (Placed $\rightarrow$ Preparing $\rightarrow$ Out for Delivery $\rightarrow$ Delivered).

### 1.2 Non-Functional Requirements
*   **High Availability:** The system must be available 24/7, especially during peak meal times.
*   **Low Latency:** Search results and menu loading must be near-instantaneous.
*   **Consistency:** 
    *   **Strong Consistency:** Required for payments and order status.
    *   **Eventual Consistency:** Acceptable for restaurant ratings and search index updates.
*   **Scalability:** Must handle sudden spikes (e.g., weekends, holidays, sports events).
*   **Reliability:** No order should be lost; payment must be idempotent.

### 1.3 Scale Estimations (High-Level)
*   **Daily Active Users (DAU):** 10 Million.
*   **Orders per Day:** 2 Million.
*   **Peak QPS (Queries Per Second):** 50k - 100k during lunch/dinner peaks.
*   **Data Growth:** Millions of ratings and orders monthly, requiring a robust partitioning strategy.

---

## 2. High-Level Architecture

The system follows a **Microservices Architecture** to decouple the domain logic and allow independent scaling of high-traffic services (like Search and Ordering).

### 2.1 Core Components
*   **API Gateway:** Entry point for all clients. Handles Authentication, Rate Limiting, and Request Routing.
*   **User Service:** Manages user profiles and addresses.
*   **Restaurant Service:** Manages restaurant metadata and menu catalogs.
*   **Search Service:** Powered by Elasticsearch for geo-spatial queries and full-text search.
*   **Order Service:** Manages the order lifecycle, state transitions, and cart logic.
*   **Payment Service:** Handles transactions and interacts with external gateways (Stripe/PayPal).
*   **Delivery/Dispatch Service:** Manages delivery partner availability and matching using geo-sharding.
*   **Rating Service:** Collects and aggregates ratings for restaurants and drivers.
*   **Notification Service:** Sends Push/SMS/Email via a message queue.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    Client[Mobile/Web App] --> AGW[API Gateway]
    
    AGW --> UserSvc[User Service]
    AGW --> RestSvc[Restaurant Service]
    AGW --> SearchSvc[Search Service]
    AGW --> OrderSvc[Order Service]
    AGW --> RatingSvc[Rating Service]
    
    SearchSvc --> ES[(Elasticsearch)]
    RestSvc --> RestDB[(Restaurant DB)]
    UserSvc --> UserDB[(User DB)]
    OrderSvc --> OrderDB[(Order DB)]
    RatingSvc --> RateDB[(Rating DB)]
    
    OrderSvc --> Kafka{Message Queue}
    Kafka --> PaySvc[Payment Service]
    Kafka --> NotifSvc[Notification Service]
    Kafka --> DeliverySvc[Delivery Service]
    
    DeliverySvc --> RedisGeo[(Redis Geo-Index)]
    PaySvc --> ExtPay[External Payment Gateway]
```

---

## 3. Detailed Database Schema Design

### 3.1 Database Selection
*   **Relational DB (PostgreSQL):** Used for User, Restaurant, and Order services. These require ACID properties for transactions (especially payments and order status).
*   **NoSQL (Elasticsearch):** Used for the Search service to handle complex geo-spatial queries (e.g., "find Italian restaurants within 5km").
*   **In-Memory (Redis):** Used for caching menus, session management, and storing real-time coordinates of delivery partners.

### 3.2 Schema Tables

#### Restaurant Service (SQL)
| Table | Fields | Keys/Indexes |
| :--- | :--- | :--- |
| `restaurants` | `id` (PK), `name`, `cuisine`, `address`, `lat`, `long`, `avg_rating`, `is_active` | Index on `(lat, long)` |
| `menu_items` | `id` (PK), `restaurant_id` (FK), `name`, `description`, `price`, `category`, `is_available` | Index on `restaurant_id` |

#### Order Service (SQL)
| Table | Fields | Keys/Indexes |
| :--- | :--- | :--- |
| `orders` | `id` (PK), `user_id` (FK), `restaurant_id` (FK), `total_amount`, `status`, `created_at`, `delivery_address` | Index on `user_id`, `status` |
| `order_items` | `id` (PK), `order_id` (FK), `menu_item_id` (FK), `quantity`, `price_at_time` | Index on `order_id` |

#### Delivery Service (SQL + Redis)
| Table | Fields | Keys/Indexes |
| :--- | :--- | :--- |
| `delivery_partners` | `id` (PK), `name`, `phone`, `vehicle_type`, `current_status` (IDLE, BUSY) | Index on `current_status` |
| `deliveries` | `id` (PK), `order_id` (FK), `partner_id` (FK), `assigned_at`, `delivered_at` | Index on `order_id` |
| **Redis Geo** | `key: partner_locations`, `member: partner_id`, `coord: (lat, long)` | Geo-spatial index |

#### Rating Service (NoSQL - MongoDB/Cassandra)
*Reasoning: Ratings are write-heavy and don't require complex joins. A document store allows flexible schema for reviews.*
| Collection | Fields | Index |
| :--- | :--- | :--- |
| `ratings` | `rating_id`, `order_id`, `user_id`, `target_id` (Rest/Partner), `score` (1-5), `comment`, `timestamp` | Index on `target_id` |

---

## 4. Core API Design

### 4.1 Search & Discovery
`GET /v1/restaurants?lat={lat}&long={long}&radius=5&cuisine=italian`
*   **Response:** `200 OK`
*   **Payload:** `[{"id": "r1", "name": "Pasta Place", "rating": 4.5, "distance": "1.2km"}, ...]`

### 4.2 Ordering
`POST /v1/orders`
*   **Request:**
    ```json
    {
      "restaurant_id": "r1",
      "items": [{"menu_item_id": "m1", "quantity": 2}, {"menu_item_id": "m5", "quantity": 1}],
      "address_id": "addr_123",
      "payment_method": "CREDIT_CARD"
    }
    ```
*   **Response:** `201 Created` $\rightarrow$ `{"order_id": "ord_999", "status": "PENDING_PAYMENT"}`

### 4.3 Ratings
`POST /v1/ratings`
*   **Request:**
    ```json
    {
      "order_id": "ord_999",
      "restaurant_rating": 5,
      "restaurant_comment": "Delicious food!",
      "partner_rating": 4,
      "partner_comment": "Fast delivery."
    }
    ```
*   **Response:** `200 OK`

---

## 5. Scalability & Advanced Topics

### 5.1 Geo-Spatial Indexing (Delivery Matching)
To find the nearest delivery partner, the system cannot query a SQL DB with `ORDER BY distance` for every order.
*   **Solution:** Use **Google S2 Geometry** or **Uber H3**. Divide the map into hexagonal/rectangular cells. 
*   **Redis GeoHash:** Store partner locations in Redis using `GEOADD`. When an order is placed, use `GEORADIUS` to find partners within $X$ kilometers.

### 5.2 Handling Peak Traffic
*   **Read Path:** Cache restaurant menus and search results in Redis. Use a **CDN** for static images of food.
*   **Write Path:** Use **Kafka** to decouple the Order service from Payment, Notification, and Delivery services. This prevents a bottleneck in the payment gateway from crashing the order placement flow.
*   **Database Sharding:** Shard the `orders` table by `user_id` or `order_date` to distribute the load.

### 5.3 Delivery Partner Assignment (The "Matching" Problem)
*   Use a **State Machine** to track order status.
*   **Dispatch Logic:** When an order is "Ready," the Dispatcher queries Redis for the 10 nearest `IDLE` partners and sends a request. If the first partner rejects, it moves to the second. This is handled asynchronously via a worker pool.

### 5.4 Rating Aggregation
Updating the `avg_rating` in the `restaurants` table on every single review would cause lock contention.
*   **Strategy:** Write ratings to a NoSQL store. Use a **Scheduled Job (Cron)** or a **Stream Processor (Flink/Spark)** to aggregate ratings every 15-30 minutes and update the main `restaurants` table in bulk.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priorities
*   **Ordering/Payment:** Prioritize **Consistency (C)** and **Partition Tolerance (P)**. We cannot have a scenario where a user is charged but the order is not recorded.
*   **Search/Discovery:** Prioritize **Availability (A)** and **Partition Tolerance (P)**. It is acceptable if a user sees a restaurant that just went offline or a rating that is 10 minutes old.

### 6.2 Latency vs. Storage
*   **Trade-off:** We store redundant data (Denormalization). For example, the `orders` table stores `price_at_time` instead of just linking to the `menu_items` table. 
*   **Reasoning:** Menu prices change. To maintain a historical record of the transaction, we trade storage space for data integrity and faster read performance (no need to join with a versioned menu table).

### 6.3 Synchronous vs. Asynchronous Processing
*   **Synchronous:** User $\rightarrow$ Order Service $\rightarrow$ Payment (Wait for Success).
*   **Asynchronous:** Order Success $\rightarrow$ Kafka $\rightarrow$ [Notification, Delivery Dispatch, Analytics].
*   **Reasoning:** This reduces the API response time for the user and ensures that a failure in the Notification service does not roll back a successful payment.""",
}

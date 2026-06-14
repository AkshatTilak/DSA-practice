INFO = {
    'difficulty': 'Medium',
    'type': 'design',
    'description': 'Design Hotel Management System.',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Hotel Management System LLD

## 1. Overview & System Requirements

The **Hotel Management System (HMS)** is a classic Low-Level Design problem that focuses on managing the lifecycle of a room reservation, from searching for available rooms to checkout and billing. The system must handle multiple room types, guests, and booking statuses while ensuring that no room is double-booked.

### Core Actors
- **Guest**: The customer who searches for rooms, makes bookings, and pays bills.
- **Receptionist/Admin**: The staff member who manages room assignments, handles check-ins/outs, and updates room statuses.
- **System/Hotel Manager**: The core engine that orchestrates the interaction between rooms, bookings, and payments.

### Functional Requirements
- **Room Management**: Ability to categorize rooms (e.g., Single, Double, Suite) and track their status (Available, Occupied, Cleaning).
- **Booking Engine**: Search for available rooms based on date ranges and room types; create and cancel reservations.
- **Check-in/Check-out**: Process the physical arrival and departure of guests.
- **Billing & Payment**: Generate bills based on the duration of stay and room rate; support multiple payment methods.
- **Housekeeping**: Mark rooms as "Under Maintenance" or "Cleaning" after checkout.

---

## 2. Design Principles & Patterns

To ensure the system is scalable and maintainable, the following OOP principles and design patterns are applied:

### Design Principles (SOLID)
- **Single Responsibility Principle (SRP)**: The `BookingManager` handles only the logic of reservations, while the `PaymentProcessor` handles financial transactions.
- **Open/Closed Principle (OCP)**: The system is open for extension (e.g., adding a new `LuxurySuite` room type) without modifying the existing `Room` base class.
- **Liskov Substitution Principle (LSP)**: Any subclass of `Room` (e.g., `DeluxeRoom`) can be used wherever a `Room` object is expected without breaking the system.
- **Interface Segregation**: Payment methods are defined via a `PaymentStrategy` interface, so the system doesn't depend on specific payment provider implementations.

### Design Patterns
| Pattern | Application | Reason |
| :--- | :--- | :--- |
| **Singleton** | `Hotel` Class | Ensures there is only one instance of the hotel management system managing the global state of rooms and bookings. |
| **Factory Method** | `RoomFactory` | Decouples the creation of specific room types (Standard, Deluxe, Suite) from the main business logic. |
| **Strategy Pattern** | `PaymentStrategy` | Allows the system to switch between payment methods (Credit Card, PayPal, UPI) at runtime. |
| **State Pattern** | `RoomStatus` | Manages the transition of a room from `Available` $\rightarrow$ `Booked` $\rightarrow$ `Occupied` $\rightarrow$ `Cleaning`. |

---

## 3. Class Structure & Relationships

### Class Diagram (Conceptual)

```mermaid
classDiagram
    class Hotel {
        -List~Room~ rooms
        -List~Booking~ bookings
        +searchRooms(type, dates)
        +makeBooking(guest, room, dates)
    }
    class Room {
        <<abstract>>
        -int roomNumber
        -RoomStatus status
        -double basePrice
        +calculatePrice(days)
    }
    class StandardRoom { }
    class DeluxeRoom { }
    class Suite { }
    class Booking {
        -String bookingId
        -Guest guest
        -Room room
        -Date checkIn
        -Date checkOut
        -BookingStatus status
    }
    class Guest {
        -String name
        -String email
        -String phone
    }
    class PaymentProcessor {
        +processPayment(amount, strategy)
    }
    class PaymentStrategy {
        <<interface>>
        +pay(amount)
    }

    Hotel "1" *-- "many" Room
    Hotel "1" *-- "many" Booking
    Booking "many" --> "1" Room
    Booking "many" --> "1" Guest
    PaymentProcessor ..> PaymentStrategy : uses
    Room <|-- StandardRoom
    Room <|-- DeluxeRoom
    Room <|-- Suite
```

### Key Attributes & Relationships
- **Composition**: `Hotel` contains `Room` and `Booking` objects.
- **Inheritance**: `StandardRoom`, `DeluxeRoom`, and `Suite` inherit from the abstract `Room` class.
- **Association**: `Booking` links a `Guest` to a specific `Room` for a specific time interval.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation in Python

```python
from abc import ABC, abstractmethod
from enum import Enum
from datetime import date

# --- Enums and Constants ---
class RoomStatus(Enum):
    AVAILABLE = 1
    OCCUPIED = 2
    CLEANING = 3
    MAINTENANCE = 4

class BookingStatus(Enum):
    CONFIRMED = 1
    CHECKED_IN = 2
    COMPLETED = 3
    CANCELLED = 4

# --- Room Hierarchy (Factory + Strategy) ---
class Room(ABC):
    def __init__(self, room_number, base_price):
        self.room_number = room_number
        self.base_price = base_price
        self.status = RoomStatus.AVAILABLE

    @abstractmethod
    def get_price(self, days):
        pass

class StandardRoom(Room):
    def get_price(self, days):
        return self.base_price * days

class DeluxeRoom(Room):
    def get_price(self, days):
        return (self.base_price * 1.5) * days

class Suite(Room):
    def get_price(self, days):
        return (self.base_price * 2.0) * days

class RoomFactory:
    @staticmethod
    def create_room(room_type, room_number, base_price):
        if room_type == "Standard": return StandardRoom(room_number, base_price)
        if room_type == "Deluxe": return DeluxeRoom(room_number, base_price)
        if room_type == "Suite": return Suite(room_number, base_price)
        raise ValueError("Invalid Room Type")

# --- Entities ---
class Guest:
    def __init__(self, guest_id, name, email):
        self.guest_id = guest_id
        self.name = name
        self.email = email

class Booking:
    def __init__(self, booking_id, guest, room, check_in, check_out):
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.status = BookingStatus.CONFIRMED

# --- Payment Strategy ---
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid ${amount} using Credit Card.")

class UPIPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid ${amount} using UPI.")

# --- Singleton Hotel Management System ---
class Hotel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Hotel, cls).__new__(cls)
            cls._instance.rooms = {}
            cls._instance.bookings = {}
        return cls._instance

    def add_room(self, room):
        self.rooms[room.room_number] = room

    def search_available_rooms(self, room_type=None):
        # Simplified search: returns rooms that are currently AVAILABLE
        return [r for r in self.rooms.values() if r.status == RoomStatus.AVAILABLE 
                and (room_type is None or type(r).__name__ == f"{room_type}Room")]

    def create_booking(self, booking_id, guest, room_number, check_in, check_out):
        room = self.rooms.get(room_number)
        if room and room.status == RoomStatus.AVAILABLE:
            booking = Booking(booking_id, guest, room, check_in, check_out)
            room.status = RoomStatus.OCCUPIED # Simplified state transition
            self.bookings[booking_id] = booking
            return booking
        return None

    def checkout(self, booking_id, payment_strategy):
        booking = self.bookings.get(booking_id)
        if booking:
            days = (booking.check_out - booking.check_in).days
            amount = booking.room.get_price(days)
            payment_strategy.pay(amount)
            booking.status = BookingStatus.COMPLETED
            booking.room.status = RoomStatus.CLEANING
            print(f"Checkout successful for Room {booking.room.room_number}")

# --- Execution ---
if __name__ == "__main__":
    hotel = Hotel()
    
    # Setup Rooms
    hotel.add_room(RoomFactory.create_room("Standard", 101, 100))
    hotel.add_room(RoomFactory.create_room("Deluxe", 201, 200))
    
    # Guest Action
    guest1 = Guest("G1", "Alice", "alice@example.com")
    available = hotel.search_available_rooms("Deluxe")
    
    if available:
        room_to_book = available[0]
        hotel.create_booking("B1", guest1, room_to_book.room_number, date(2023, 10, 1), date(2023, 10, 5))
        print(f"Booking confirmed for {guest1.name} in Room {room_to_book.room_number}")

    # Checkout Process
    hotel.checkout("B1", UPIPayment())
```

### Logic Walkthrough
1.  **Room Creation**: The `RoomFactory` ensures that when we add rooms to the `Hotel`, we create the specific subclass (Standard/Deluxe) which carries its own pricing logic.
2.  **Booking Flow**: The `Hotel` singleton checks if the requested `room_number` exists and is `AVAILABLE`. If so, it creates a `Booking` object and marks the room as `OCCUPIED`.
3.  **Dynamic Pricing**: During checkout, the `Booking` object refers to the `Room` object. The `Room` object calculates the total cost based on its specific subclass implementation of `get_price()`.
4.  **Payment Execution**: The `checkout` method accepts a `PaymentStrategy`. This allows the guest to pay via UPI or Credit Card without the `Hotel` class knowing the internal details of the payment gateway.
5.  **Post-Stay State**: Once checked out, the room status moves to `CLEANING` instead of immediately becoming `AVAILABLE`, simulating a real-world operational flow.

---

## 5. Real-World Applications

The architectural patterns used in this Hotel Management LLD are prevalent in several production-grade systems:

- **Airbnb / Booking.com**: Use similar "Availability Search" patterns and "Payment Strategy" patterns to handle global currencies and payment methods.
- **Cloud Resource Management (AWS/Azure)**: The concept of "Room Types" is similar to "Instance Types" (t2.micro, m5.large). The "Booking" is similar to "Provisioning" a resource for a specific duration.
- **Ride-Hailing Apps (Uber/Lyft)**: The `RoomFactory` is analogous to the `VehicleFactory` (UberX, UberBlack, UberPool), where pricing is calculated differently based on the vehicle type.
- **Hospital Management Systems**: Managing bed availability, patient check-ins, and billing based on ward types (General, Semi-Private, ICU).

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Search Room** | $O(R)$ | $O(1)$ | $R$ = Total number of rooms. |
| **Create Booking** | $O(1)$ | $O(1)$ | Direct lookup via Room ID. |
| **Checkout** | $O(1)$ | $O(1)$ | Direct lookup via Booking ID. |
| **Room Storage** | $O(R)$ | $O(R)$ | Stored in a hash map for fast access. |""",
    'solutions': """# Hotel Management System (HMS) - System Design Document

## 1. Requirements & System Constraints

The Hotel Management System is designed to handle the end-to-end lifecycle of hotel operations, from room inventory management and guest bookings to check-in/check-out and billing.

### 1.1 Functional Requirements
*   **Room Management:**
    *   Administrators can add, update, and remove room types (e.g., Deluxe, Suite, Single) and individual rooms.
    *   Ability to manage room pricing dynamically (seasonal pricing).
*   **Booking Management:**
    *   Users can search for available rooms based on dates, location, and guest count.
    *   Users can book, modify, or cancel reservations.
    *   **Concurrency Control:** Prevent double-booking of the same room for overlapping dates.
*   **Guest Management:**
    *   Maintain guest profiles, contact details, and booking history.
    *   Handle check-in and check-out processes.
*   **Billing & Payments:**
    *   Generate invoices based on room rates, taxes, and additional services.
    *   Integrate with payment gateways for secure transactions.
*   **Housekeeping:**
    *   Staff can update room status (e.g., Clean, Dirty, Under Maintenance).

### 1.2 Non-Functional Requirements
*   **Strong Consistency:** Booking status must be consistent. Two users cannot book the same room for the same slot.
*   **High Availability:** The booking engine must be available 24/7.
*   **Low Latency:** Room search and availability checks should be near-instant.
*   **Scalability:** System should support multiple hotel properties across different regions.

### 1.3 Scale Estimations (Medium Scale)
*   **Hotels:** 1,000 properties.
*   **Rooms per Hotel:** Average 100 $\rightarrow$ Total $10^5$ rooms.
*   **Daily Bookings:** $\sim 50,000$ bookings.
*   **Peak Load:** During holidays, search queries may spike 10x.

---

## 2. High-Level Architecture

The system follows a **Modular Monolith** or **Microservices** architecture to decouple the booking engine from the administrative and payment modules.

### 2.1 Core Components
1.  **API Gateway:** Entry point for all clients (Web/Mobile), handling authentication and rate limiting.
2.  **Search Service:** Handles queries for room availability using a read-optimized cache.
3.  **Booking Service:** Manages the reservation lifecycle and ensures transactional integrity.
4.  **Room/Inventory Service:** Manages room metadata, types, and current status.
5.  **Payment Service:** Handles third-party payment gateway integrations and invoice generation.
6.  **Notification Service:** Asynchronous service for sending booking confirmations via Email/SMS.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    Client[Guest/Admin App] --> Gateway[API Gateway]
    Gateway --> SearchSvc[Search Service]
    Gateway --> BookingSvc[Booking Service]
    Gateway --> RoomSvc[Room/Inventory Service]
    Gateway --> PaymentSvc[Payment Service]
    
    SearchSvc --> Redis[(Redis Cache)]
    SearchSvc --> DB[(Primary SQL DB)]
    
    BookingSvc --> DB
    BookingSvc --> Kafka{Message Queue}
    
    RoomSvc --> DB
    
    PaymentSvc --> ExternalPay[Payment Gateway]
    PaymentSvc --> DB
    
    Kafka --> NotificationSvc[Notification Service]
    NotificationSvc --> EmailSvc[Email/SMS Provider]
```

---

## 3. Detailed Database Schema Design

A Relational Database (RDBMS) like **PostgreSQL** is chosen because the system requires **ACID transactions** to prevent double-booking and maintain financial integrity.

### 3.1 Tables Design

#### `Hotels`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `hotel_id` | UUID | PK | Unique identifier for the hotel |
| `name` | VARCHAR(255) | NOT NULL | Hotel name |
| `address` | TEXT | NOT NULL | Physical address |
| `city` | VARCHAR(100) | INDEX | For search filtering |
| `star_rating` | INT | CHECK(1-5) | Hotel rating |

#### `RoomTypes`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `type_id` | UUID | PK | Unique identifier for room type |
| `hotel_id` | UUID | FK $\rightarrow$ Hotels | Reference to hotel |
| `type_name` | VARCHAR(50) | NOT NULL | e.g., "Deluxe King" |
| `base_price` | DECIMAL | NOT NULL | Standard price per night |
| `capacity` | INT | NOT NULL | Max guests allowed |

#### `Rooms`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `room_id` | UUID | PK | Unique identifier for the room |
| `type_id` | UUID | FK $\rightarrow$ RoomTypes | Reference to type |
| `room_number` | VARCHAR(10) | NOT NULL | Physical room number |
| `status` | ENUM | NOT NULL | AVAILABLE, OCCUPIED, DIRTY, MAINTENANCE |

#### `Guests`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `guest_id` | UUID | PK | Unique identifier for guest |
| `first_name` | VARCHAR(100) | NOT NULL | Guest first name |
| `email` | VARCHAR(255) | UNIQUE, INDEX | Contact email |
| `phone` | VARCHAR(20) | NOT NULL | Contact phone |

#### `Bookings`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `booking_id` | UUID | PK | Unique identifier for booking |
| `guest_id` | UUID | FK $\rightarrow$ Guests | Guest who booked |
| `room_id` | UUID | FK $\rightarrow$ Rooms | Specific room allocated |
| `check_in` | DATE | NOT NULL | Check-in date |
| `check_out` | DATE | NOT NULL | Check-out date |
| `total_amount`| DECIMAL | NOT NULL | Total cost |
| `status` | ENUM | NOT NULL | PENDING, CONFIRMED, CANCELLED, COMPLETED |
| `created_at` | TIMESTAMP | DEFAULT NOW | Booking timestamp |

#### `Payments`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `payment_id` | UUID | PK | Unique identifier for payment |
| `booking_id` | UUID | FK $\rightarrow$ Bookings | Reference to booking |
| `amount` | DECIMAL | NOT NULL | Amount paid |
| `payment_status`| ENUM | NOT NULL | SUCCESS, FAILED, REFUNDED |
| `transaction_id`| VARCHAR(255) | UNIQUE | Gateway transaction ID |

### 3.2 Indexing Strategy
*   **`Hotels(city)`**: To speed up searches by location.
*   **`Bookings(guest_id)`**: To retrieve booking history for a guest.
*   **`Bookings(room_id, check_in, check_out)`**: A composite index to quickly check room availability for a date range.

---

## 4. Core API Design

### 4.1 Room Search
`GET /api/v1/rooms/search?city=London&checkin=2023-12-01&checkout=2023-12-05&guests=2`

**Response:**
```json
[
  {
    "hotel_name": "Grand Plaza",
    "room_type": "Deluxe King",
    "price_per_night": 200.00,
    "available_rooms": 5,
    "room_type_id": "uuid-123"
  }
]
```

### 4.2 Create Booking
`POST /api/v1/bookings`

**Request:**
```json
{
  "guest_id": "uuid-guest-1",
  "room_id": "uuid-room-101",
  "check_in": "2023-12-01",
  "check_out": "2023-12-05",
  "payment_method": "CREDIT_CARD"
}
```

**Response:**
```json
{
  "booking_id": "uuid-book-999",
  "status": "PENDING",
  "total_price": 800.00,
  "message": "Booking initiated. Please complete payment."
}
```

### 4.3 Check-in/Check-out
`PATCH /api/v1/bookings/{booking_id}/status`

**Request:**
```json
{
  "status": "CHECKED_IN" // or "CHECKED_OUT"
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Handling Concurrency (Preventing Double Booking)
To prevent two people from booking the same room at the exact same millisecond, we use **Optimistic Locking** or **Pessimistic Locking**.

*   **Pessimistic Locking:** Use `SELECT ... FOR UPDATE` in SQL. This locks the room row until the transaction is committed. Best for high-contention scenarios.
*   **Optimistic Locking:** Add a `version` column to the `Rooms` or `RoomAvailability` table. Update only if the version matches the one read.

### 5.2 Caching Strategy
*   **Availability Cache:** Use **Redis** to store availability bit-maps for rooms. A bit-map where each bit represents a day of the year allows for extremely fast `AND` operations to find available dates.
*   **Hotel Metadata:** Cache hotel details, room descriptions, and images using a CDN or Redis since they rarely change.

### 5.3 Asynchronous Processing
*   **Payment & Notifications:** Once a booking is confirmed, the `Booking Service` publishes an event to **Kafka/RabbitMQ**. The `Notification Service` consumes this to send emails, and the `Analytics Service` consumes it to track revenue.

### 5.4 Database Sharding
As the system grows to thousands of hotels:
*   **Sharding Key:** `hotel_id`. Since most queries are scoped to a specific hotel or city, sharding by `hotel_id` ensures that all data for one hotel resides on one shard, avoiding cross-shard joins.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priority
In a Hotel Management System, **Consistency (C)** and **Partition Tolerance (P)** are prioritized over Availability (A).
*   **Why?** It is better to tell a user "System is temporarily unavailable" or "Booking failed" than to allow two guests to be assigned to the same room (Overbooking), which creates a poor guest experience and operational chaos.

### 6.2 Latency vs. Storage
*   **Denormalization:** We may denormalize `RoomType` names into the `Bookings` table. This increases storage usage but reduces the need for complex joins during invoice generation, lowering read latency.

### 6.3 SQL vs. NoSQL
*   **SQL (Chosen):** Used for bookings and payments due to the need for ACID transactions.
*   **NoSQL (Alternative):** Could be used for **Guest Preferences** (e.g., "prefers high floor", "extra pillows") where the schema is flexible and doesn't require strict transactional integrity.""",
}

INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Airline Reservation System.',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Airline Reservation System LLD

The **Airline Reservation System** is a classic high-complexity Low-Level Design problem. It requires managing a high volume of concurrent requests (seat bookings), handling complex entity relationships (flights, aircraft, seats, passengers), and implementing robust business logic for pricing, payments, and cancellations.

---

## 1. Overview & System Requirements

### Core Objective
To build a scalable, maintainable system that allows users to search for flights, reserve seats, make payments, and manage bookings, while allowing administrators to manage flight schedules and aircraft.

### Actors
- **Customer**: Searches for flights, books tickets, manages their profile, and cancels reservations.
- **Admin**: Adds/removes flights, manages aircraft assignments, and updates schedules.
- **System/Payment Gateway**: Handles transaction processing and sends notifications.

### Functional Requirements
- **Flight Management**: Ability to add, update, and delete flights.
- **Search**: Find flights based on source, destination, and date.
- **Seat Management**: Track seat availability by class (Economy, Business, First Class).
- **Booking Workflow**: Reserve a seat $\rightarrow$ Process Payment $\rightarrow$ Confirm Ticket.
- **Cancellation**: Cancel a booking and trigger a refund based on a policy.
- **Concurrency Control**: Prevent double-booking of the same seat.

---

## 2. Design Principles & Patterns

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: Separate classes for `PaymentProcessor`, `BookingManager`, and `FlightSearchService`. The `Flight` class only holds flight data, not payment logic.
- **Open/Closed Principle (OCP)**: Using a `PricingStrategy` interface allows the system to introduce dynamic pricing (e.g., holiday surges) without modifying the existing booking logic.
- **Liskov Substitution Principle (LSP)**: Different types of `Passenger` (e.g., `FrequentFlyerPassenger`) can be used interchangeably with the base `Passenger` class.
- **Interface Segregation Principle (ISP)**: Separate interfaces for `AdminActions` and `UserActions` so clients aren't forced to depend on methods they don't use.
- **Dependency Inversion Principle (DIP)**: The `BookingService` depends on a `PaymentInterface` rather than a concrete `StripePayment` or `PayPalPayment` class.

### Design Patterns
| Pattern | Application | Reason |
| :--- | :--- | :--- |
| **Singleton** | `AirlineSystem` | Ensures a single point of coordination for the entire system. |
| **Strategy** | `PricingStrategy` | Allows switching between Fixed, Dynamic, and Discounted pricing at runtime. |
| **Observer** | `NotificationService` | Notifies passengers via Email/SMS when flight status changes or booking is confirmed. |
| **State Pattern** | `BookingStatus` | Manages transitions between `PENDING`, `CONFIRMED`, and `CANCELLED`. |
| **Factory** | `SeatFactory` | Encapsulates the logic of creating different seat types (Economy, Business). |

---

## 3. Class Structure & Relationships

### ASCII Class Diagram
```text
+------------------+       +------------------+       +------------------+
|     Airport      | <---- |      Flight      | <---- |     Aircraft     |
+------------------+       +------------------+       +------------------+
| - code: String   |       | - flightNo: String|       | - aircraftId: Str|
| - city: String   |       | - departure: Date |       | - model: String  |
+------------------+       +------------------+       +------------------+
                                    | 1
                                    |
                                    | *
                           +------------------+       +------------------+
                           |       Seat       | <---- |    SeatClass     |
                           +------------------+       +------------------+
                           | - seatNo: String |       | - type: Enum     |
                           | - status: Status |       | - basePrice: Float|
                           +------------------+       +------------------+
                                    | 1
                                    |
                                    | 1
                           +------------------+       +------------------+
                           |     Booking      | ----> |    Passenger     |
                           +------------------+       +------------------+
                           | - bookingId: Str |       | - name: String   |
                           | - status: Status |       | - email: String  |
                           +------------------+       +------------------+
                                    | 1
                                    | 1
                           +------------------+
                           |     Payment      |
                           +------------------+
                           | - amount: Float  |
                           | - status: Status |
                           +------------------+
```

### Relationship Definitions
- **Flight $\rightarrow$ Aircraft**: Association (A flight is operated by one aircraft).
- **Flight $\rightarrow$ Seat**: Composition (Seats cannot exist without a flight/aircraft).
- **Booking $\rightarrow$ Passenger**: Association (A booking is linked to a specific passenger).
- **Booking $\rightarrow$ Seat**: Association (A booking reserves one or more seats).
- **Booking $\rightarrow$ Payment**: Composition (A booking has a corresponding payment record).

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from enum import Enum
from abc import ABC, abstractmethod
from threading import Lock
from datetime import datetime

# --- Enums & Value Objects ---
class SeatClass(Enum):
    ECONOMY = 1
    BUSINESS = 2
    FIRST = 3

class BookingStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3

# --- Strategies for Pricing ---
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_price):
        pass

class RegularPricing(PricingStrategy):
    def calculate_price(self, base_price):
        return base_price

class HolidayPricing(PricingStrategy):
    def calculate_price(self, base_price):
        return base_price * 1.5

# --- Core Entities ---
class Seat:
    def __init__(self, seat_number, seat_class, base_price):
        self.seat_number = seat_number
        self.seat_class = seat_class
        self.base_price = base_price
        self.is_reserved = False
        self.lock = Lock()  # To prevent double booking

class Flight:
    def __init__(self, flight_id, source, destination, departure_time):
        self.flight_id = flight_id
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.seats = []

    def add_seat(self, seat):
        self.seats.append(seat)

    def get_available_seats(self, seat_class):
        return [s for s in self.seats if s.seat_class == seat_class and not s.is_reserved]

class Passenger:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class Booking:
    def __init__(self, booking_id, passenger, flight, seat):
        self.booking_id = booking_id
        self.passenger = passenger
        self.flight = flight
        self.seat = seat
        self.status = BookingStatus.PENDING

# --- Services ---
class PaymentProcessor:
    @staticmethod
    def process_payment(amount):
        print(f"Processing payment of ${amount}...")
        return True  # Mock success

class BookingService:
    def __init__(self, pricing_strategy: PricingStrategy):
        self.pricing_strategy = pricing_strategy
        self.bookings = {}

    def create_booking(self, booking_id, passenger, flight, seat_class):
        # 1. Search for available seat
        available_seats = flight.get_available_seats(seat_class)
        if not available_seats:
            print("No seats available in this class.")
            return None

        target_seat = available_seats[0]

        # 2. Concurrency Control: Lock the seat
        with target_seat.lock:
            if target_seat.is_reserved:
                print("Seat was just taken!")
                return None
            
            # Temporarily reserve
            target_seat.is_reserved = True
            
            # 3. Calculate Price
            final_price = self.pricing_strategy.calculate_price(target_seat.base_price)
            
            # 4. Payment
            if PaymentProcessor.process_payment(final_price):
                booking = Booking(booking_id, passenger, flight, target_seat)
                booking.status = BookingStatus.CONFIRMED
                self.bookings[booking_id] = booking
                print(f"Booking {booking_id} confirmed for {passenger.name}!")
                return booking
            else:
                # Rollback seat reservation if payment fails
                target_seat.is_reserved = False
                print("Payment failed. Seat released.")
                return None

# --- Execution ---
if __name__ == "__main__":
    # Setup
    flight_101 = Flight("AI101", "NYC", "LON", datetime(2023, 12, 25))
    flight_101.add_seat(Seat("1A", SeatClass.FIRST, 1000))
    flight_101.add_seat(Seat("12B", SeatClass.ECONOMY, 200))

    passenger_alice = Passenger("Alice", "alice@example.com")
    
    # Use Holiday Pricing Strategy
    holiday_service = BookingService(HolidayPricing())
    
    # Process Booking
    holiday_service.create_booking("B001", passenger_alice, flight_101, SeatClass.FIRST)
```

### Logic Walkthrough

1.  **Seat Selection**: The `Flight` object provides a list of seats filtered by `SeatClass` and `is_reserved` status.
2.  **Concurrency Handling**: The use of `threading.Lock` (or in a real DB, a `SELECT FOR UPDATE` row lock) ensures that if two users attempt to book the same seat simultaneously, only one succeeds.
3.  **Price Calculation**: The `BookingService` doesn't hardcode the price. It delegates this to the `PricingStrategy`. If it's a holiday, the `HolidayPricing` class increases the cost.
4.  **Transactional Integrity**: The seat is marked as `is_reserved = True` *before* payment. If the payment fails, the seat is immediately released (Rollback), preventing "zombie" reservations.
5.  **State Management**: The `Booking` starts as `PENDING` and moves to `CONFIRMED` only upon payment success.

---

## 5. Real-World Applications & Complexity

### Production-Grade Considerations
- **Distributed Locking**: In a microservices environment, `threading.Lock` is insufficient. Redis-based distributed locks (Redlock) or ZooKeeper would be used to manage seat locks across multiple server instances.
- **Database Transactions**: Use ACID transactions to ensure that the `Booking` record creation and `Seat` status update happen atomically.
- **Caching**: Flight schedules and seat maps are read-heavy. Using Redis to cache available seats can significantly reduce DB load.
- **Asynchronous Notifications**: The `Observer` pattern would be implemented via a Message Queue (RabbitMQ/Kafka) to send emails without blocking the booking thread.

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Search Flights** | $O(F)$ | $O(1)$ | $F$ = number of flights. |
| **Find Available Seat**| $O(S)$ | $O(1)$ | $S$ = number of seats in a flight. |
| **Booking Process** | $O(1)$ | $O(1)$ | Constant time operations once seat is found. |
| **Cancellation** | $O(1)$ | $O(1)$ | Direct lookup via `bookingId`. |

### Summary Checklist for Interviews
- [x] Did I handle concurrency (Double Booking)?
- [x] Did I use a Strategy pattern for pricing?
- [x] Is the payment process decoupled from the booking logic?
- [x] Are the seat classes handled polymorphically/via Enums?
- [x] Is there a clear path for payment failure (Rollback)?""",
    'solutions': """# System Design Document: Airline Reservation System

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Flight Search:** Users can search for available flights based on origin, destination, date, and class (Economy, Business, First).
*   **Seat Selection:** Users can view a real-time seat map and select specific seats.
*   **Booking Management:** 
    *   Reserve a seat temporarily (TTL) to prevent others from booking it during the payment process.
    *   Confirm booking upon successful payment.
    *   Cancel or modify existing bookings.
*   **Payment Integration:** Process payments through third-party gateways.
*   **Flight Management (Admin):** Administrators can add/update flights, manage aircraft assignments, and handle scheduling.
*   **Notifications:** Send booking confirmations and flight updates via Email/SMS.

### 1.2 Non-Functional Requirements
*   **Strong Consistency:** Double-booking of the same seat must be impossible (ACID compliance is critical).
*   **High Availability:** The search and browsing functionality must be available 24/7.
*   **Low Latency:** Flight searches should return results in milliseconds.
*   **Scalability:** The system must handle massive spikes in traffic during holiday seasons or promotional sales.
*   **Reliability:** Payment and booking state transitions must be durable and recoverable.

### 1.3 Scale Estimations (HLD Context)
*   **Daily Active Users (DAU):** 1 Million.
*   **Search Queries:** 100k requests per minute (Read-heavy).
*   **Bookings:** 10k requests per minute (Write-heavy during peaks).
*   **Data Volume:** Millions of flight segments and booking records per year.

---

## 2. High-Level Architecture

The system follows a **Microservices Architecture** to decouple the read-heavy search functionality from the write-heavy booking logic.

### 2.1 Core Components
*   **API Gateway:** Handles authentication, rate limiting, and request routing.
*   **Flight Search Service:** Manages flight schedules and availability. Optimized for reads using a distributed cache.
*   **Booking Service:** Manages the lifecycle of a reservation (Pending $\rightarrow$ Confirmed $\rightarrow$ Cancelled).
*   **Inventory Service:** Tracks seat-level availability. Uses distributed locking to prevent overbooking.
*   **Payment Service:** Integrates with external PSPs (Stripe, PayPal) and manages transaction states.
*   **Notification Service:** Asynchronously sends alerts via a Message Queue.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    User((User)) --> Gateway[API Gateway]
    Gateway --> SearchSvc[Flight Search Service]
    Gateway --> BookingSvc[Booking Service]
    Gateway --> PaymentSvc[Payment Service]
    
    SearchSvc --> FlightDB[(Flight DB)]
    SearchSvc --> RedisCache[(Redis Cache)]
    
    BookingSvc --> InventorySvc[Inventory Service]
    BookingSvc --> BookingDB[(Booking DB)]
    
    InventorySvc --> InvDB[(Inventory DB)]
    
    PaymentSvc --> ExtPayment[External Payment Gateway]
    PaymentSvc --> PaymentDB[(Payment DB)]
    
    BookingSvc --> MQ[Message Queue - Kafka/RabbitMQ]
    MQ --> NotifSvc[Notification Service]
    NotifSvc --> EmailSMS[Email/SMS Gateway]
```

---

## 3. Detailed Database Schema Design

### 3.1 Reasoning: SQL vs NoSQL
*   **Relational Database (PostgreSQL):** Used for Bookings, Payments, and Inventory. These require **ACID** properties to ensure that a seat is not sold twice and that payments are mapped correctly to bookings.
*   **NoSQL/Cache (Redis):** Used for flight availability and session management to ensure low-latency search results.

### 3.2 Schema Definition

#### `Airports`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| airport_id | UUID | PK | Unique Identifier |
| iata_code | VARCHAR(3) | Unique, Indexed | e.g., JFK, LHR |
| city | VARCHAR(100) | Not Null | City Name |
| timezone | VARCHAR(50) | Not Null | UTC Offset |

#### `Flights`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| flight_id | UUID | PK | Unique Identifier |
| flight_number | VARCHAR(10) | Indexed | e.g., AA101 |
| departure_airport_id| UUID | FK $\rightarrow$ Airports | Origin |
| arrival_airport_id | UUID | FK $\rightarrow$ Airports | Destination |
| departure_time | TIMESTAMP | Indexed | Scheduled departure |
| arrival_time | TIMESTAMP | Not Null | Scheduled arrival |
| aircraft_id | UUID | FK $\rightarrow$ Aircraft | Aircraft type/ID |

#### `Seats`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| seat_id | UUID | PK | Unique Identifier |
| flight_id | UUID | FK $\rightarrow$ Flights | Associated flight |
| seat_number | VARCHAR(5) | Not Null | e.g., 12A |
| class | ENUM | Economy, Business, First | Seat Class |
| status | ENUM | Available, Reserved, Booked | Current state |
| version | INT | Not Null | For Optimistic Locking |

#### `Bookings`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| booking_id | UUID | PK | Unique Identifier |
| user_id | UUID | FK $\rightarrow$ Users | Customer ID |
| flight_id | UUID | FK $\rightarrow$ Flights | Flight ID |
| status | ENUM | Pending, Confirmed, Cancelled | Booking state |
| total_amount | DECIMAL | Not Null | Final price |
| created_at | TIMESTAMP | Not Null | Booking timestamp |

#### `Tickets`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| ticket_id | UUID | PK | Unique Identifier |
| booking_id | UUID | FK $\rightarrow$ Bookings | Booking reference |
| seat_id | UUID | FK $\rightarrow$ Seats | Assigned seat |
| passenger_name | VARCHAR(100) | Not Null | Passenger detail |

---

## 4. Core API Design

### 4.1 Flight Search
`GET /api/v1/flights/search?from=SFO&to=JFK&date=2023-12-01&class=Economy`
**Response:**
```json
[
  {
    "flight_id": "f123",
    "flight_number": "AA101",
    "departure": "2023-12-01T10:00Z",
    "arrival": "2023-12-01T18:00Z",
    "price": 450.00,
    "available_seats": 15
  }
]
```

### 4.2 Reserve Seat (Temporary Lock)
`POST /api/v1/bookings/reserve`
**Request:**
```json
{
  "flight_id": "f123",
  "seat_id": "s456",
  "user_id": "u789"
}
```
**Response:** `201 Created`
```json
{
  "booking_id": "b987",
  "expires_at": "2023-12-01T10:15Z",
  "status": "Pending"
}
```

### 4.3 Confirm Booking (Payment)
`POST /api/v1/bookings/confirm`
**Request:**
```json
{
  "booking_id": "b987",
  "payment_method_id": "pm_123",
  "amount": 450.00
}
```
**Response:** `200 OK`
```json
{
  "ticket_id": "t001",
  "status": "Confirmed",
  "confirmation_code": "XYZ789"
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Preventing Double Booking (Concurrency Control)
To prevent two users from booking the same seat simultaneously, the system employs a two-layer strategy:
1.  **Distributed Locking (Redis):** When a user selects a seat, a key is created: `lock:flight_{id}:seat_{id}` with a TTL of 10-15 minutes. If the lock exists, other users cannot reserve it.
2.  **Optimistic Locking (Database):** The `Seats` table contains a `version` column.
    `UPDATE Seats SET status = 'Booked', version = version + 1 WHERE seat_id = :id AND version = :old_version;`
    If the update returns 0 rows, a concurrent modification occurred, and the request is rejected.

### 5.2 Caching Strategy
*   **Flight Schedules:** Cached in Redis with a long TTL, as schedules change infrequently.
*   **Availability:** Cached with short TTLs. The "Search Service" reads from Redis; the "Inventory Service" updates Redis whenever a seat status changes (Write-through cache).

### 5.3 Handling Payment Failures & Timeouts
*   **Saga Pattern:** Since Booking and Payment are separate services, a Saga pattern (Choreography) is used. 
    *   `BookingSvc` creates a "Pending" booking $\rightarrow$ `PaymentSvc` processes payment.
    *   If payment fails, `PaymentSvc` emits a `PaymentFailed` event $\rightarrow$ `BookingSvc` marks booking as "Cancelled" and `InventorySvc` releases the seat.

### 5.4 Sharding & Partitioning
*   **Booking DB:** Sharded by `user_id` to distribute the load.
*   **Inventory DB:** Sharded by `flight_id` to ensure all seats for a specific flight reside on the same partition, making transactions more efficient.

---

## 6. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs Availability** | **Consistency (CP)** | In a reservation system, availability of the *search* is important, but consistency of the *booking* is non-negotiable. Double-booking leads to severe business loss and customer dissatisfaction. |
| **Latency vs Storage** | **Latency** | We use denormalized views in Redis for flight searches to avoid complex joins across `Flights`, `Airports`, and `Seats` tables during peak search times. |
| **Synchronous vs Asynchronous** | **Mixed** | Booking and Payment are synchronous (user needs immediate confirmation). Notifications are asynchronous (Email can arrive 30 seconds later without impacting UX). |
| **Pessimistic vs Optimistic Locking** | **Optimistic** | Since the probability of two users clicking the *exact* same seat at the *exact* same millisecond is relatively low compared to total traffic, optimistic locking reduces database lock contention. |""",
}

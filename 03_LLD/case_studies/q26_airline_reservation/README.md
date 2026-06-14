# Airline Reservation System LLD

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
- [x] Is there a clear path for payment failure (Rollback)?
# Movie Booking System LLD

## 1. Overview & System Requirements

The goal is to design a scalable, robust, and concurrency-safe online movie ticket booking system (similar to BookMyShow or Fandango). The system must handle multiple users searching for movies across different cities and booking seats in real-time.

### Core Actors
- **User**: Searches for movies, selects shows, chooses seats, and makes payments.
- **Admin**: Manages movies, cinemas, screens, and show timings.
- **System**: Handles seat locking, payment verification, and booking confirmations.

### Functional Requirements
- **Search**: Users can search for movies by title, genre, or city.
- **Cinema Management**: The system manages multiple cinemas, each having multiple screens.
- **Show Scheduling**: A screen can host multiple shows of different movies at different times.
- **Seat Selection**: Users can view available seats and select specific ones.
- **Concurrency Control**: Prevent two users from booking the same seat simultaneously (**Double Booking Prevention**).
- **Booking & Payment**: Lock seats temporarily while the user completes the payment.
- **Notifications**: Send confirmation once the booking is successful.

### Non-Functional Requirements
- **High Availability**: The system must be available 24/7.
- **Consistency**: Strong consistency is required for seat bookings to avoid overbooking.
- **Scalability**: Must handle traffic spikes during blockbuster movie releases.

---

## 2. Design Principles & Patterns

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: Separate classes for `PaymentProcessor`, `BookingManager`, and `CinemaManager`. The `Booking` class only manages booking state, not payment logic.
- **Open/Closed Principle (OCP)**: The payment system is designed using an interface (`PaymentStrategy`), allowing new payment methods (e.g., Crypto, Apple Pay) to be added without modifying existing booking logic.
- **Liskov Substitution Principle (LSP)**: Different seat types (Silver, Gold, Platinum) inherit from a base `Seat` class and can be used interchangeably.
- **Interface Segregation Principle (ISP)**: The system uses specific interfaces for `Searchable` and `Payable` to ensure classes only implement methods they actually need.
- **Dependency Inversion Principle (DIP)**: `BookingManager` depends on the `PaymentStrategy` abstraction rather than a concrete `CreditCardPayment` class.

### Design Patterns
- **Singleton Pattern**: Used for the `MovieBookingSystem` coordinator to ensure there is one central point of truth for the system state.
- **Strategy Pattern**: Used for the `PaymentStrategy`. This allows the user to choose between different payment gateways at runtime.
- **State Pattern**: Used to manage `SeatStatus` (Available $\rightarrow$ Locked $\rightarrow$ Booked).
- **Factory Pattern**: Used to create `Seat` objects based on the seat category (e.g., `SeatFactory.createSeat("GOLD")`).

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+----------------+       +----------------+       +----------------+
|     Movie      |<------+    Show        |<------+    Screen      |
+----------------+       +----------------+       +----------------+
| - movieId      |       | - showId       |       | - screenId     |
| - title        |       | - movie        |       | - numSeats     |
| - genre        |       | - startTime    |       | - list<Seat>   |
+----------------+       | - screen       |       +----------------+
                         | - showSeats    |                ^
                                |                          |
                                v                          |
                         +----------------+       +----------------+
                         |    ShowSeat    |------>|      Seat      |
                         +----------------+       +----------------+
                         | - seat         |       | - seatId       |
                         | - status       |       | - row, col     |
                         | - price        |       | - seatType     |
                         +----------------+       +----------------+
                                ^
                                |
                         +----------------+       +----------------+
                         |    Booking     |------>|    Payment     |
                         +----------------+       +----------------+
                         | - bookingId    |       | - txId         |
                         | - user         |       | - amount       |
                         | - showSeats    |       | - status       |
                         +----------------+       +----------------+
```

### Key Relationships
- **Cinema $\rightarrow$ Screen**: One-to-Many (Composition).
- **Screen $\rightarrow$ Seat**: One-to-Many (Composition).
- **Show $\rightarrow$ ShowSeat**: One-to-Many (Composition). A `ShowSeat` is a mapping of a physical `Seat` to a specific `Show` with a specific `Status`.
- **Booking $\rightarrow$ ShowSeat**: One-to-Many (Association).

---

## 4. Step-by-Step Logic & Code Walkthrough

### The "Concurrency Problem" Solution
To prevent double booking, we implement a **Two-Phase Lock**:
1. **Temporary Lock**: When a user selects seats, the status changes from `AVAILABLE` to `LOCKED`. A timestamp is attached. If payment isn't received within 10 minutes, a background worker reverts it to `AVAILABLE`.
2. **Permanent Lock**: Once payment is successful, the status changes to `BOOKED`.

### Implementation

```python
from enum import Enum
from threading import Lock
from datetime import datetime, timedelta

# --- Enums and Value Objects ---
class SeatStatus(Enum):
    AVAILABLE = 1
    LOCKED = 2
    BOOKED = 3

class SeatType(Enum):
    SILVER = 1
    GOLD = 2
    PLATINUM = 3

# --- Core Entities ---
class Seat:
    def __init__(self, seat_id, row, col, seat_type):
        self.seat_id = seat_id
        self.row = row
        self.col = col
        self.seat_type = seat_type

class ShowSeat:
    def __init__(self, seat, price):
        self.seat = seat
        self.price = price
        self.status = SeatStatus.AVAILABLE
        self.lock_time = None
        self.lock = Lock() # Thread-safety for this specific seat

    def lock_seat(self, duration_minutes=10):
        with self.lock:
            if self.status == SeatStatus.AVAILABLE:
                self.status = SeatStatus.LOCKED
                self.lock_time = datetime.now() + timedelta(minutes=duration_minutes)
                return True
            return False

    def confirm_booking(self):
        with self.lock:
            self.status = SeatStatus.BOOKED
            self.lock_time = None

    def release_seat(self):
        with self.lock:
            self.status = SeatStatus.AVAILABLE
            self.lock_time = None

class Show:
    def __init__(self, show_id, movie, screen, start_time):
        self.show_id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        # Initialize ShowSeats based on Screen's physical seats
        self.show_seats = {s.seat_id: ShowSeat(s, 100) for s in screen.seats}

class Movie:
    def __init__(self, movie_id, title, genre):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre

class Screen:
    def __init__(self, screen_id, seats):
        self.screen_id = screen_id
        self.seats = seats # List of Seat objects

# --- Payment Strategy Pattern ---
class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid {amount} using Credit Card.")
        return True

class UPIPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid {amount} using UPI.")
        return True

# --- Booking Manager (The Orchestrator) ---
class BookingManager:
    def __init__(self):
        self.bookings = {}

    def create_booking(self, user, show, seat_ids, payment_strategy):
        # 1. Try to lock all selected seats
        locked_seats = []
        for sid in seat_ids:
            show_seat = show.show_seats[sid]
            if show_seat.lock_seat():
                locked_seats.append(show_seat)
            else:
                # Rollback: release already locked seats if one fails
                for ls in locked_seats:
                    ls.release_seat()
                print("One or more seats are unavailable.")
                return None

        # 2. Calculate total price
        total_price = sum(s.price for s in locked_seats)

        # 3. Process Payment
        if payment_strategy.pay(total_price):
            # 4. Confirm booking
            for s in locked_seats:
                s.confirm_booking()
            
            booking_id = f"BK{len(self.bookings) + 1}"
            self.bookings[booking_id] = {"user": user, "seats": locked_seats}
            print(f"Booking successful! ID: {booking_id}")
            return booking_id
        else:
            # Rollback: Release seats on payment failure
            for s in locked_seats:
                s.release_seat()
            print("Payment failed. Seats released.")
            return None

# --- Execution ---
def solve():
    # Setup Data
    movie = Movie(1, "Inception", "Sci-Fi")
    seats = [Seat(f"S{i}", 1, i, SeatType.SILVER) for i in range(10)]
    screen = Screen(1, seats)
    show = Show(101, movie, screen, "2023-12-01 18:00")
    
    manager = BookingManager()
    user_a = "Alice"
    
    # Alice tries to book seats S1 and S2 using UPI
    payment_method = UPIPayment()
    manager.create_booking(user_a, show, ["S1", "S2"], payment_method)

if __name__ == "__main__":
    solve()
```

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| **Searching Movie** | $O(M)$ or $O(1)$ | $O(1)$ | $O(M)$ for linear scan, $O(1)$ if indexed by Map. |
| **Locking Seats** | $O(S)$ | $O(1)$ | $S$ is the number of seats being booked. |
| **Booking Confirmation** | $O(S)$ | $O(S)$ | Updating status for $S$ seats and creating a booking record. |
| **Payment Processing** | $O(1)$ | $O(1)$ | Constant time for external API call. |

---

## 5. Real-World Applications

This LLD pattern is utilized in several high-concurrency booking systems:

1. **Ticketing Platforms**: BookMyShow, Ticketmaster, and Eventbrite use similar "Temporary Lock" mechanisms to prevent race conditions where two users pay for the same seat.
2. **Airline Reservation Systems**: Systems like Amadeus or Sabre use a similar state transition ($\text{Available} \rightarrow \text{Held} \rightarrow \text{Ticketed}$) to manage seat inventory.
3. **Hotel Booking Engines**: Platforms like Expedia or Booking.com implement similar patterns to ensure room availability during the checkout process.
4. **Inventory Management (E-commerce)**: Flash sale systems (like Amazon Prime Day) use a "Reserve" pattern where an item is held in the cart for a few minutes before being released back to the pool.
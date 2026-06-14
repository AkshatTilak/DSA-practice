INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/design-movie-ticket-booking-system-online-bookmyshow-lld/',
    'description': 'Design online ticket booker.',
    'type': 'design',
    'groups': ['OOP Case Studies'],
    'readme_content': """# Movie Booking System LLD

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
4. **Inventory Management (E-commerce)**: Flash sale systems (like Amazon Prime Day) use a "Reserve" pattern where an item is held in the cart for a few minutes before being released back to the pool.""",
    'solutions': """# System Design: Online Movie Ticket Booking System

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Movie Catalog:** Users should be able to browse movies currently showing or coming soon, filter by city, genre, and language.
*   **Cinema & Show Discovery:** Users can select a cinema and view available showtimes for a specific movie.
*   **Seat Selection:** Users can view a real-time seat map of a cinema hall and select one or more seats.
*   **Temporary Seat Locking:** When a user selects seats, they must be locked for a limited time (e.g., 5–10 minutes) to prevent double-booking while the user completes payment.
*   **Payment Integration:** Integration with third-party payment gateways to confirm the booking.
*   **Ticket Generation:** Upon successful payment, a ticket/QR code is generated and sent to the user.
*   **Cancellation:** Users can cancel bookings based on the cinema's refund policy.

### 1.2 Non-Functional Requirements
*   **Strong Consistency:** No two users should be able to book the same seat for the same show (Atomic transactions).
*   **High Availability:** The system must be available for browsing and searching even during peak loads.
*   **Low Latency:** Seat map retrieval and seat locking must be extremely fast to provide a smooth user experience.
*   **Scalability:** The system must handle massive traffic spikes during the release of blockbuster movies.

### 1.3 Scale Estimations (HLD Context)
*   **Daily Active Users (DAU):** 10 Million.
*   **Peak Concurrent Users:** 1 Million (during major releases).
*   **Total Theaters:** 10,000 worldwide.
*   **Average Seats per Hall:** 200.
*   **Booking Volume:** ~50k requests per second (RPS) during peak bursts.

---

## 2. High-Level Architecture

The system follows a **Microservices Architecture** to decouple the catalog management from the high-concurrency booking engine.

### 2.1 Core Components
1.  **Movie Service:** Manages movie metadata, ratings, and release dates.
2.  **Cinema/Show Service:** Manages theater details, screen layouts, and showtime scheduling.
3.  **Booking Service:** Handles the critical path of seat selection, temporary locking, and booking state management.
4.  **Payment Service:** Interfaces with external payment providers (Stripe, PayPal, etc.).
5.  **Notification Service:** Asynchronous service to send tickets via Email/SMS/Push.
6.  **Cache Layer (Redis):** Stores real-time seat availability and temporary locks.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    User((User)) --> Gateway[API Gateway]
    Gateway --> MovieSvc[Movie Service]
    Gateway --> CinemaSvc[Cinema/Show Service]
    Gateway --> BookingSvc[Booking Service]
    
    MovieSvc --> MovieDB[(Movie DB)]
    CinemaSvc --> CinemaDB[(Cinema DB)]
    
    BookingSvc --> Redis[(Redis Cache - Seat Locks)]
    BookingSvc --> BookingDB[(Booking DB)]
    
    BookingSvc --> PaymentSvc[Payment Service]
    PaymentSvc --> ExtPayment[External Payment Gateway]
    
    PaymentSvc --> MsgQueue[Message Queue - Kafka/RabbitMQ]
    MsgQueue --> NotificationSvc[Notification Service]
    NotificationSvc --> User
```

---

## 3. Detailed Database Schema Design

A **Relational Database (RDBMS)** like PostgreSQL is chosen because the system requires **ACID compliance**, specifically for transactions involving seat bookings.

### 3.1 Tables & Schema

#### `Movies`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `movie_id` | UUID | PK | Unique Movie ID |
| `title` | VARCHAR | NOT NULL | Movie Title |
| `genre` | VARCHAR | | Action, Comedy, etc. |
| `duration` | INT | | Duration in minutes |
| `release_date` | DATE | | Date of release |

#### `Theaters`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `theater_id` | UUID | PK | Unique Theater ID |
| `name` | VARCHAR | NOT NULL | Theater Name |
| `city` | VARCHAR | INDEX | City for filtering |

#### `Screens`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `screen_id` | UUID | PK | Unique Screen ID |
| `theater_id` | UUID | FK | Reference to `Theaters` |
| `name` | VARCHAR | | Screen Name/Number |

#### `Seats`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `seat_id` | UUID | PK | Unique Seat ID |
| `screen_id` | UUID | FK | Reference to `Screens` |
| `row` | VARCHAR | | Row Identifier (e.g., 'A') |
| `col` | INT | | Column Identifier (e.g., 12) |
| `type` | ENUM | | Silver, Gold, Platinum |

#### `Shows`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `show_id` | UUID | PK | Unique Show ID |
| `movie_id` | UUID | FK | Reference to `Movies` |
| `screen_id` | UUID | FK | Reference to `Screens` |
| `start_time` | DATETIME | INDEX | Start time of the show |
| `end_time` | DATETIME | | End time of the show |

#### `ShowSeats` (The High-Contention Table)
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `show_seat_id`| UUID | PK | Unique ID for a seat in a show |
| `show_id` | UUID | FK | Reference to `Shows` |
| `seat_id` | UUID | FK | Reference to `Seats` |
| `status` | ENUM | | Available, Locked, Booked |
| `price` | DECIMAL | | Price for this specific show |
| `version` | INT | | For Optimistic Locking |

#### `Bookings`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `booking_id` | UUID | PK | Unique Booking ID |
| `user_id` | UUID | FK | User who booked |
| `show_id` | UUID | FK | Reference to `Shows` |
| `total_price` | DECIMAL | | Total amount paid |
| `status` | ENUM | | Pending, Confirmed, Cancelled |
| `timestamp` | DATETIME | | Booking time |

### 3.2 Indexing Strategy
*   **`Shows(movie_id, start_time)`**: Composite index to quickly find showtimes for a movie.
*   **`Theaters(city)`**: To filter theaters by location.
*   **`ShowSeats(show_id, status)`**: To quickly fetch available seats for a specific screen.

---

## 4. Core API Design

### 4.1 Movie & Show Discovery
`GET /v1/movies?city={city}&genre={genre}`
*   **Response:** `[{ "movie_id": "...", "title": "...", "shows": [...] }]`

`GET /v1/shows/{show_id}/seats`
*   **Response:** `[{ "seat_id": "...", "row": "A", "col": 5, "status": "Available", "price": 12.0 }]`

### 4.2 Booking Flow
`POST /v1/bookings/reserve`
*   **Payload:**
    ```json
    {
      "show_id": "show-123",
      "user_id": "user-456",
      "seat_ids": ["seat-1", "seat-2"]
    }
    ```
*   **Response:** `201 Created` with `booking_id` and `expires_at` timestamp.
*   **Logic:** Atomic update to `ShowSeats` changing status from `Available` $\rightarrow$ `Locked`.

`POST /v1/bookings/{booking_id}/confirm`
*   **Payload:**
    ```json
    {
      "payment_method_id": "pm_...",
      "transaction_id": "txn_..."
    }
    ```
*   **Response:** `200 OK` with Ticket QR code.
*   **Logic:** Changes status from `Locked` $\rightarrow$ `Booked`.

---

## 5. Scalability & Advanced Topics

### 5.1 Handling the "Double Booking" Problem
This is the most critical challenge. Two strategies can be employed:

1.  **Optimistic Locking (DB Level):**
    Use the `version` column in `ShowSeats`.
    `UPDATE ShowSeats SET status = 'Locked', version = version + 1 WHERE show_seat_id = ? AND version = ? AND status = 'Available';`
    If the update returns 0 rows affected, another user has already locked the seat.

2.  **Distributed Locking (Redis Level):**
    Use Redis `SETNX` (Set if Not Exists) with a TTL (Time-to-Live) for each seat key: `lock:show_{id}:seat_{id}`.
    *   If `SETNX` succeeds, the user locks the seat for 10 minutes.
    *   If the user pays, the lock is converted to a permanent DB record.
    *   If the TTL expires, the seat automatically becomes available again.

### 5.2 Caching Strategy
*   **Read-Heavy Data:** Movie details and cinema layouts are cached in Redis with long TTLs.
*   **Write-Heavy Data:** Seat availability is cached using a **BitMap** in Redis. Each bit represents a seat (0=Available, 1=Occupied). This allows for extremely fast retrieval of the seat map for thousands of users.

### 5.3 Handling High Bursts (Blockbusters)
*   **Virtual Queue (Waiting Room):** For highly anticipated movies, implement a queue (e.g., using Kafka or a Redis-based queue) to throttle the number of users entering the seat selection page.
*   **Read Replicas:** Use database read replicas to handle the heavy traffic of users browsing movies and shows.

### 5.4 Fault Tolerance
*   **Payment Timeout:** If the Payment Service does not receive a callback from the gateway within the TTL, a worker process marks the `Booking` as `Expired` and releases the `ShowSeats`.
*   **Idempotency:** All payment and booking APIs must accept an `idempotency_key` to prevent double-charging users during network retries.

---

## 6. Trade-off Analysis

### 6.1 Consistency vs. Availability (CAP Theorem)
In the context of seat booking, **Consistency (C)** is prioritized over **Availability (A)**. We cannot allow double-booking. Therefore, we use a **CP system** for the booking transaction. If the booking database is partitioned or unavailable, we would rather reject a booking request than risk selling the same seat twice.

### 6.2 Latency vs. Storage
By using Redis BitMaps for seat availability, we trade a small amount of memory (storage) for significant gains in latency. Fetching a bit-string is orders of magnitude faster than querying a SQL table with millions of rows for every seat-map refresh.

### 6.3 SQL vs. NoSQL
*   **SQL (PostgreSQL):** Used for Bookings and Seats because of ACID transactions and the relational nature of movies $\rightarrow$ shows $\rightarrow$ seats.
*   **NoSQL (Redis):** Used for session management, distributed locking, and caching to handle high-throughput low-latency requirements.""",
}

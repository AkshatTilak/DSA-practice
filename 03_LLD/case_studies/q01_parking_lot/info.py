INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/design-parking-lot-low-level-design/',
    'description': 'Design object models for multi-level parking lot including spot size constraints, ticket calculations.',
    'groups': ['OOP Case Studies'],
    'starter_code': """class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type):
        self.id = id
        self.spot_type = spot_type
        self.is_free = True""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(L * S) where L is the number of levels and S is the number of spots per level.
# Space Complexity: O(L * S) to store the parking lot layout.
# This approach uses simple linear search to find the first available parking spot that satisfies the size constraint.
# It lacks thread safety and efficient lookup, making it unsuitable for high-concurrency environments.

import time
import math

class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type):
        self.id = id
        self.spot_type = spot_type
        self.is_free = True
        self.vehicle = None

class Vehicle:
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type # Should match SpotType

class Ticket:
    def __init__(self, vehicle, spot):
        self.vehicle = vehicle
        self.spot = spot
        self.start_time = time.time()

class ParkingLotNaive:
    def __init__(self, levels, spots_per_level):
        self.levels = []
        for l in range(levels):
            level_spots = []
            for s in range(spots_per_level):
                # Distribute spot types evenly for simplicity in naive approach
                stype = SpotType.SMALL if s % 3 == 0 else (SpotType.COMPACT if s % 3 == 1 else SpotType.LARGE)
                level_spots.append(ParkingSpot(f"{l}-{s}", stype))
            self.levels.append(level_spots)

    def park_vehicle(self, vehicle):
        # Linear search through levels and spots
        for level in self.levels:
            for spot in level:
                if spot.is_free and spot.spot_type >= vehicle.vehicle_type:
                    spot.is_free = False
                    spot.vehicle = vehicle
                    return Ticket(vehicle, spot)
        return None

    def unpark_vehicle(self, ticket):
        spot = ticket.spot
        duration = time.time() - ticket.start_time
        spot.is_free = True
        spot.vehicle = None
        # Naive pricing: $2 per hour
        cost = math.ceil(duration / 3600) * 2
        return cost

# --- APPROACH 2: Optimal (Priority Queues & Strategy Pattern) ---
# Time Complexity: 
#   - park_vehicle: O(log S) to extract the best spot from the PriorityQueue.
#   - unpark_vehicle: O(log S) to push the spot back into the PriorityQueue.
#   - calculate_cost: O(1).
# Space Complexity: O(L * S) to store all spots in the priority queues.
# This approach is optimal because it uses Min-Heaps (PriorityQueues) to ensure the nearest available spot is always selected.
# It employs a Strategy Pattern for flexible pricing based on vehicle type and uses a Thread Lock to ensure 
# atomicity in a multi-threaded environment, making it production-ready.

import heapq
import time
import math
from threading import Lock
from abc import ABC, abstractmethod

class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type, level_id):
        self.id = id
        self.spot_type = spot_type
        self.level_id = level_id
        self.is_free = True

    # Define comparison for PriorityQueue to prioritize lower level, then lower spot id
    def __lt__(self, other):
        if self.level_id != other.level_id:
            return self.level_id < other.level_id
        return self.id < other.id

class Vehicle:
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type # 1: Small, 2: Compact, 3: Large

class Ticket:
    def __init__(self, vehicle, spot):
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = time.time()

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, duration_hours, vehicle_type):
        pass

class StandardPricingStrategy(PricingStrategy):
    def __init__(self):
        self.rates = {SpotType.SMALL: 1.0, SpotType.COMPACT: 2.0, SpotType.LARGE: 5.0}

    def calculate_cost(self, duration_hours, vehicle_type):
        rate = self.rates.get(vehicle_type, 2.0)
        return math.ceil(duration_hours) * rate

class ParkingLotOptimal:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ParkingLotOptimal, cls).__new__(cls)
        return cls._instance

    def __init__(self, config=None):
        # Prevent re-initialization in singleton
        if hasattr(self, 'initialized'): return
        self.initialized = True
        self.lock = Lock()
        self.pricing_strategy = StandardPricingStrategy()
        
        # available_spots maps SpotType -> MinHeap of ParkingSpots
        self.available_spots = {
            SpotType.SMALL: [],
            SpotType.COMPACT: [],
            SpotType.LARGE: []
        }
        
        if config:
            self._setup_parking_lot(config)

    def _setup_parking_lot(self, config):
        # config: list of levels, where each level is a list of (spot_id, spot_type)
        for level_id, spots in enumerate(config):
            for spot_id, spot_type in spots:
                spot = ParkingSpot(spot_id, spot_type, level_id)
                heapq.heappush(self.available_spots[spot_type], spot)

    def park_vehicle(self, vehicle):
        with self.lock:
            # A vehicle can park in a spot of its size or any larger spot
            # Order: Small -> Compact -> Large
            for size in range(vehicle.vehicle_type, SpotType.LARGE + 1):
                if self.available_spots[size]:
                    spot = heapq.heappop(self.available_spots[size])
                    spot.is_free = False
                    return Ticket(vehicle, spot)
            return None # No available spot

    def unpark_vehicle(self, ticket):
        with self.lock:
            spot = ticket.spot
            spot.is_free = True
            heapq.heappush(self.available_spots[spot.spot_type], spot)
            
            duration_seconds = time.time() - ticket.entry_time
            duration_hours = duration_seconds / 3600
            return self.pricing_strategy.calculate_cost(duration_hours, ticket.vehicle.vehicle_type)

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package case_studies;

import java.util.*;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.concurrent.locks.ReentrantLock;
import java.time.Duration;
import java.time.Instant;

enum SpotType {
    SMALL(1), COMPACT(2), LARGE(3);
    final int value;
    SpotType(int value) { this.value = value; }
}

class ParkingSpot implements Comparable<ParkingSpot> {
    String id;
    SpotType type;
    int level;

    public ParkingSpot(String id, SpotType type, int level) {
        this.id = id;
        this.type = type;
        this.level = level;
    }

    @Override
    public int compareTo(ParkingSpot other) {
        if (this.level != other.level) {
            return Integer.compare(this.level, other.level);
        }
        return this.id.compareTo(other.id);
    }
}

class Vehicle {
    String licensePlate;
    SpotType type;

    public Vehicle(String licensePlate, SpotType type) {
        this.licensePlate = licensePlate;
        this.type = type;
    }
}

class Ticket {
    Vehicle vehicle;
    ParkingSpot spot;
    Instant entryTime;

    public Ticket(Vehicle vehicle, ParkingSpot spot) {
        this.vehicle = vehicle;
        this.spot = spot;
        this.entryTime = Instant.now();
    }
}

interface PricingStrategy {
    double calculateCost(long hours, SpotType type);
}

class StandardPricing implements PricingStrategy {
    private final Map<SpotType, Double> rates = new EnumMap<>(SpotType.class);

    public StandardPricing() {
        rates.put(SpotType.SMALL, 1.0);
        rates.put(SpotType.COMPACT, 2.0);
        rates.put(SpotType.LARGE, 5.0);
    }

    @Override
    public double calculateCost(long hours, SpotType type) {
        return hours * rates.getOrDefault(type, 2.0);
    }
}

public class ParkingLot {
    private static ParkingLot instance;
    private final ReentrantLock lock = new ReentrantLock();
    private final Map<SpotType, PriorityQueue<ParkingSpot>> availableSpots;
    private final PricingStrategy pricingStrategy;

    private ParkingLot() {
        availableSpots = new EnumMap<>(SpotType.class);
        for (SpotType type : SpotType.values()) {
            availableSpots.put(type, new PriorityQueue<>());
        }
        this.pricingStrategy = new StandardPricing();
    }

    public static synchronized ParkingLot getInstance() {
        if (instance == null) {
            instance = new ParkingLot();
        }
        return instance;
    }

    public void addSpot(String id, SpotType type, int level) {
        lock.lock();
        try {
            availableSpots.get(type).add(new ParkingSpot(id, type, level));
        } finally {
            lock.unlock();
        }
    }

    public Ticket parkVehicle(Vehicle vehicle) {
        lock.lock();
        try {
            // Try searching for spot from vehicle's size upwards
            for (SpotType type : SpotType.values()) {
                if (type.value >= vehicle.type.value && !availableSpots.get(type).isEmpty()) {
                    ParkingSpot spot = availableSpots.get(type).poll();
                    return new Ticket(vehicle, spot);
                }
            }
            return null;
        } finally {
            lock.unlock();
        }
    }

    public double unparkVehicle(Ticket ticket) {
        lock.lock();
        try {
            ParkingSpot spot = ticket.spot;
            availableSpots.get(spot.type).add(spot);
            
            long hours = Duration.between(ticket.entryTime, Instant.now()).toHours();
            if (hours == 0) hours = 1; // Minimum 1 hour charge
            
            return pricingStrategy.calculateCost(hours, ticket.vehicle.type);
        } finally {
            lock.unlock();
        }
    }
}
\"\"\"""",
    'test_code': """def test_parking():
    pass""",
    'readme_content': """# Parking Lot LLD

This study guide provides a professional-grade Low-Level Design (LLD) for a multi-level parking lot. This is a classic OOP interview question that tests a candidate's ability to handle inheritance, composition, and the application of design patterns to solve real-world constraints.

---

## 1. Overview & System Requirements

The goal is to design a software system to manage a multi-level parking lot. The system must handle vehicles of different sizes, allocate appropriate spots, and calculate fees based on the duration of stay.

### Core Actors
- **Driver**: Parks the vehicle, pays the fee, and exits.
- **Parking Attendant/System**: Manages ticket issuance and spot allocation.
- **Admin**: Adds/removes parking levels or modifies pricing strategies.

### Functional Requirements
1. **Multi-level Support**: The lot should have multiple floors.
2. **Spot Size Constraints**:
   - **Small Spots**: For Motorbikes.
   - **Compact Spots**: For Cars.
   - **Large Spots**: For Trucks/Buses.
   - *Constraint*: A vehicle can only park in a spot of its size or larger (depending on business rules), but typically it must match exactly or be the smallest available that fits.
3. **Ticketing**: A ticket must be generated upon entry containing the entry time and spot ID.
4. **Fare Calculation**: Fees are calculated based on vehicle type and time spent.
5. **Availability Tracking**: The system must be able to tell if a spot is available for a specific vehicle type.

---

## 2. Design Principles & Patterns

### OOP Principles (SOLID)
- **Single Responsibility Principle (SRP)**: The `ParkingLot` class manages the overall structure, the `PaymentSystem` handles money, and the `Ticket` class handles record-keeping.
- **Open/Closed Principle (OCP)**: The system is open for new vehicle types (e.g., Electric Cars) by extending the `Vehicle` base class without modifying the `ParkingLot` logic.
- **Liskov Substitution Principle (LSP)**: Any subclass of `ParkingSpot` (Small, Compact, Large) can be treated as a `ParkingSpot` by the `Floor` manager.
- **Interface Segregation**: We separate the `Payment` logic into a strategy to allow for different payment methods (Credit Card, Cash, UPI).

### Design Patterns Applied
| Pattern | Application | Why? |
| :--- | :--- | :--- |
| **Singleton** | `ParkingLot` | Ensures there is only one instance of the parking lot manager across the entire application. |
| **Factory Pattern** | `VehicleFactory` | Decouples the creation of vehicle objects from the main logic. |
| **Strategy Pattern** | `PricingStrategy` | Allows the parking lot to change pricing rules (e.g., holiday rates vs. weekday rates) dynamically. |
| **Observer Pattern** | `AvailabilityDisplay` | Updates electronic displays across the lot whenever a spot is filled or vacated. |

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-------------------+           +-------------------+
|    ParkingLot     |<>-------->|      Floor        |
|-------------------|           |-------------------|
| - floors: List    |           | - floorNum: int   |
| - instance: static|           | - spots: List     |
+---------+---------+           +---------+---------+
          |                               |
          |                      +--------v---------+
          |                      |   ParkingSpot    | (Abstract)
          |                      |------------------|
          |                      | - spotId: int    |
          |                      | - isFree: bool   |
          |                      +--------+---------+
          |                               |
          |             +-----------------+-----------------+
          |             |                 |                 |
          |      +------+------+   +------+------+   +------+------+
          |      |  SmallSpot  |   |  CompactSpot|   |   LargeSpot |
          |      +-------------+   +-------------+   +-------------+
          |
+---------v---------+           +-------------------+
|  TicketSystem     |---------->|      Ticket       |
|-------------------|           |-------------------|
| - issueTicket()   |           | - ticketId: str   |
| - processExit()   |           | - entryTime: Time |
+-------------------+           | - spot: Spot      |
                                +-------------------+
```

### Key Relationships
- **Composition**: `ParkingLot` has many `Floors`; `Floor` has many `ParkingSpots`.
- **Inheritance**: `Motorbike`, `Car`, and `Truck` inherit from `Vehicle`.
- **Association**: `Ticket` is associated with both a `Vehicle` and a `ParkingSpot`.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import math

# --- Constants & Enums ---
class SpotType:
    SMALL = 1
    COMPACT = 2
    LARGE = 3

class VehicleType:
    MOTORBIKE = 1
    CAR = 2
    TRUCK = 3

# --- Vehicle Hierarchy ---
class Vehicle(ABC):
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

class Motorbike(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, VehicleType.MOTORBIKE)

class Car(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, VehicleType.CAR)

class Truck(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, VehicleType.TRUCK)

# --- Spot Hierarchy ---
class ParkingSpot:
    def __init__(self, id, spot_type):
        self.id = id
        self.spot_type = spot_type
        self.vehicle = None

    def is_free(self):
        return self.vehicle is None

    def assign_vehicle(self, vehicle):
        self.vehicle = vehicle

    def remove_vehicle(self):
        self.vehicle = None

# --- Pricing Strategy ---
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, duration_hours, vehicle_type):
        pass

class StandardPricing(PricingStrategy):
    def calculate_cost(self, duration_hours, vehicle_type):
        rates = {VehicleType.MOTORBIKE: 10, VehicleType.CAR: 20, VehicleType.TRUCK: 50}
        return math.ceil(duration_hours) * rates.get(vehicle_type, 20)

# --- Core System ---
class Ticket:
    def __init__(self, ticket_id, vehicle, spot):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()

class Floor:
    def __init__(self, floor_id):
        self.floor_id = floor_id
        self.spots = []

    def add_spot(self, spot):
        self.spots.append(spot)

    def find_available_spot(self, vehicle_type):
        # Mapping vehicle type to required spot type
        type_map = {VehicleType.MOTORBIKE: SpotType.SMALL, 
                    VehicleType.CAR: SpotType.COMPACT, 
                    VehicleType.TRUCK: SpotType.LARGE}
        
        required_type = type_map[vehicle_type]
        for spot in self.spots:
            if spot.is_free() and spot.spot_type == required_type:
                return spot
        return None

class ParkingLot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParkingLot, cls).__new__(cls)
            cls._instance.floors = []
            cls._instance.pricing_strategy = StandardPricing()
        return cls._instance

    def add_floor(self, floor):
        self.floors.append(floor)

    def park_vehicle(self, vehicle):
        for floor in self.floors:
            spot = floor.find_available_spot(vehicle.vehicle_type)
            if spot:
                spot.assign_vehicle(vehicle)
                ticket_id = f"TKT-{vehicle.license_plate}-{datetime.now().timestamp()}"
                return Ticket(ticket_id, vehicle, spot)
        raise Exception("No available parking spot for this vehicle type!")

    def unpark_vehicle(self, ticket):
        spot = ticket.spot
        vehicle = ticket.vehicle
        
        # Calculate duration
        exit_time = datetime.now()
        duration = exit_time - ticket.entry_time
        hours = duration.total_seconds() / 3600
        
        cost = self.pricing_strategy.calculate_cost(hours, vehicle.vehicle_type)
        spot.remove_vehicle()
        return cost

# --- Execution Example ---
if __name__ == "__main__":
    # Initialize Parking Lot
    lot = ParkingLot()
    
    # Setup Floor 1
    f1 = Floor(1)
    f1.add_spot(ParkingSpot(101, SpotType.SMALL))
    f1.add_spot(ParkingSpot(102, SpotType.COMPACT))
    lot.add_floor(f1)
    
    # Scenario: Park a Car
    my_car = Car("ABC-123")
    try:
        ticket = lot.park_vehicle(my_car)
        print(f"Vehicle parked. Ticket ID: {ticket.ticket_id}")
        
        # Simulate time passing for pricing (manually adjusting entry time for demo)
        ticket.entry_time = datetime.now() - timedelta(hours=3)
        
        # Exit
        fee = lot.unpark_vehicle(ticket)
        print(f"Vehicle exited. Total Fee: ${fee}")
    except Exception as e:
        print(e)
```

### Logic Walkthrough
1. **Entry**: When `park_vehicle` is called, the system iterates through floors $\rightarrow$ searches for a `ParkingSpot` that is both `free` and matches the `VehicleType` required.
2. **Allocation**: Once found, the spot is marked as occupied, and a `Ticket` object is created to link the vehicle, the spot, and the timestamp.
3. **Exit**: When `unpark_vehicle` is called, the system retrieves the `entry_time` from the ticket, calculates the time delta, and passes it to the `PricingStrategy`.
4. **Payment**: The `PricingStrategy` returns the cost based on the vehicle's specific rate. The spot is then set back to `is_free = True`.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Explanation |
| :--- | :--- | :--- | :--- |
| **Park Vehicle** | $O(F \times S)$ | $O(1)$ | $F$ = Floors, $S$ = Spots per floor. We search linearly for a spot. |
| **Unpark Vehicle**| $O(1)$ | $O(1)$ | We have a direct reference to the spot via the ticket. |
| **Calculate Fee** | $O(1)$ | $O(1)$ | Simple mathematical calculation. |
| **Overall System**| - | $O(F \times S)$ | Storage for all spot objects in the lot. |

*Optimization Note: To reduce `Park Vehicle` to $O(1)$, we could maintain a `Queue` or `Set` of available spot IDs for each `SpotType` per floor.*

---

## 6. Real-World Applications

This design pattern is widely used in production systems beyond simple parking lots:
- **Cloud Resource Allocation**: Assigning a Virtual Machine (VM) to a physical server based on resource constraints (CPU/RAM $\approx$ Spot Size).
- **Airport Gate Management**: Assigning aircraft to gates based on plane size (Regional vs. Wide-body).
- **Warehouse Slotting**: Assigning packages to bins based on dimensions and weight limits.
- **Hospital Bed Management**: Assigning patients to beds (ICU vs. General Ward) based on medical needs.""",
}

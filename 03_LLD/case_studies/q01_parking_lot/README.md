# Parking Lot LLD

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
- **Hospital Bed Management**: Assigning patients to beds (ICU vs. General Ward) based on medical needs.
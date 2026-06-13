# Low-Level Design Case Studies

Low-Level Design (LLD) focuses on software class structure, object-oriented relationships, SOLID design principles, and component-level code boundaries. LLD interviews assess how you translate business requirements into modular, reusable, testable, and thread-safe class blueprints.

---

## 🗺️ Class Blueprint: Parking Lot System

Below is the ASCII UML class diagram mapping entities, attributes, and relationships for a multi-level **Parking Lot** system:

```text
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│   ParkingLot    │◇─────>│      Level      │◇─────>│   ParkingSpot    │
├─────────────────┤       ├─────────────────┤       ├──────────────────┤
│ - levels: List  │       │ - floorNum: int │       │ - spotId: String │
├─────────────────┤       │ - spots: List   │       │ - type: SpotType │
│ + parkVehicle() │       ├─────────────────┤       │ - isFree: boolean│
│ + freeSpot()    │       │ + findFreeSpot()│       ├──────────────────┤
└─────────────────┘       └─────────────────┘       │ + occupy()       │
                                                    │ + vacate()       │
                                                    └──────────────────┘
                                                              ▲
                                                              │
                                                    ┌──────────────────┐
                                                    │     Vehicle      │
                                                    ├──────────────────┤
                                                    │ - plateNum:String│
                                                    │ - type: VehicleTy│
                                                    └──────────────────┘
```

---

## 🏗️ Design Decisions & Patterns Used

| Problem | Design Pattern / Structure | Rationale |
| :--- | :--- | :--- |
| Thread-Safe Spot Allocation | ReentrantLock / Synchronized | Avoids race conditions when multiple cars attempt to occupy the same spot simultaneously. |
| Spot Sizing Hierarchy | Polymorphism / Enum comparisons | Allows parking compact cars in large spots, but prevents large trucks from occupying compact spots. |
| Cost Billing Engine | Strategy Pattern | Decouples parking fee calculation rules (Hourly vs. Flat rate vs. Member discount) from the ticket entity. |

---

## 🏢 Real-World Production Use-Case

### Transportation: Airport Smart Parking Entry Gates
Airport entry gates manage automated ticketing and vehicle spot assignment under heavy, concurrent traffic spikes.
1. When a car drives up to the gate, an OCR camera scans the license plate and determines the vehicle classification.
2. The gate controller triggers the **ParkingLot** instance (modeled as a thread-safe Singleton).
3. The allocator searches active **Level** structures to lock and reserve a free **ParkingSpot** matching the vehicle size.
4. An entry ticket is generated with a timestamp and spot code. Because spot search and updates are optimized in-memory, the gate opens in under 100ms, preventing lane congestion.
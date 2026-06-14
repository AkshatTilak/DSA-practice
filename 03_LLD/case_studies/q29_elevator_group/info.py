INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Advanced Elevator Group Control.',
    'groups': ['OOP Case Studies', 'Concurrency'],
    'readme_content': """# Elevator Group Control LLD

Designing an **Elevator Group Control System** is a classic "Hard" LLD challenge because it transitions from a simple state-machine problem (single elevator) to a complex **resource allocation and optimization problem** (multiple elevators). The primary goal is to minimize the **Average Waiting Time (AWT)** and **Average Travel Time (ATT)** while maximizing energy efficiency.

---

## 1. Overview & System Requirements

### Core Entities
- **Elevator Group**: A collection of elevators serving the same set of floors.
- **Elevator Car**: The physical unit that moves between floors.
- **Floor/Hall**: The landing area where users request elevators.
- **Dispatch Controller**: The "brain" that decides which elevator handles which request.
- **Request**: A signal indicating a desire to move (External: Floor $\rightarrow$ Direction; Internal: Floor $\rightarrow$ Target).

### Functional Requirements
1. **Request Handling**: 
   - External requests (Up/Down buttons on a floor).
   - Internal requests (Destination buttons inside the car).
2. **Dispatching Logic**: Efficiently assign the "best" elevator based on distance, direction, and current load.
3. **Movement Control**: Elevators must stop at all requested floors in their path (SCAN algorithm).
4. **State Management**: Track whether an elevator is `IDLE`, `MOVING_UP`, `MOVING_DOWN`, or `OUT_OF_SERVICE`.
5. **Concurrency**: Handle simultaneous requests from multiple floors and multiple cars reporting their positions.

### Non-Functional Requirements
- **Scalability**: Ability to add more elevators or floors without rewriting the controller.
- **Reliability**: Ensuring no request is "forgotten" (guaranteed delivery).
- **Efficiency**: Minimizing the number of stops and empty travels.

---

## 2. Design Principles & Patterns

### OOP Design Principles
- **Single Responsibility Principle (SRP)**: The `Elevator` class handles movement and state; the `Dispatcher` handles the logic of assignment; the `Request` class encapsulates the data.
- **Open/Closed Principle (OCP)**: The system is open for new dispatching strategies (e.g., changing from "Nearest Car" to "Zoning") without modifying the `Elevator` class.
- **Interface Segregation**: Dispatch strategies are defined via an interface, allowing the controller to swap algorithms at runtime.

### Design Patterns Applied
| Pattern | Application | Reason |
| :--- | :--- | :--- |
| **Strategy Pattern** | `DispatchStrategy` | Allows switching between different algorithms (e.g., FCFS, SCAN, Optimal) based on building traffic patterns. |
| **State Pattern** | `ElevatorState` | Manages the transition between `IDLE`, `UP`, and `DOWN`, ensuring that an elevator doesn't suddenly change direction without stopping. |
| **Observer Pattern** | `Elevator` $\rightarrow$ `Controller` | The Controller observes the elevators to know when they have reached a floor to trigger the next assignment. |
| **Singleton Pattern** | `ElevatorController` | There is typically only one central controller managing a specific group of elevators. |

---

## 3. Class Structure & Relationships

### Class Diagram (Text-Based)

```mermaid
classDiagram
    class ElevatorController {
        -List<Elevator> elevators
        -DispatchStrategy strategy
        +requestElevator(floor, direction)
        +updateElevatorStatus(elevatorId, floor)
    }
    
    class DispatchStrategy {
        <<interface>>
        +findBestElevator(request, elevators)
    }
    
    class NearestCarStrategy {
        +findBestElevator(request, elevators)
    }
    
    class Elevator {
        -int id
        -int currentFloor
        -Direction direction
        -PriorityQueue targets
        +move()
        +addStop(floor)
    }
    
    class Request {
        -int floor
        -Direction direction
        -RequestType type
    }

    ElevatorController "1" *-- "many" Elevator : manages
    ElevatorController "1" *-- "1" DispatchStrategy : uses
    DispatchStrategy <|-- NearestCarStrategy : implements
    Elevator "1" *-- "many" Request : processes
```

### Key Attributes
- **Elevator**: 
    - `targets`: A `PriorityQueue` or two sets (one for up, one for down) to manage stops.
    - `currentFloor`: Integer tracking position.
- **Request**: 
    - `type`: `INTERNAL` (car button) or `EXTERNAL` (hall button).
    - `direction`: `UP`, `DOWN`, or `NONE`.

---

## 4. Step-by-Step Logic & Code Walkthrough

### The Dispatching Algorithm (The "Hard" Part)
The core logic lies in the `findBestElevator` method. A naive approach is "Nearest Car," but an advanced system uses a **Cost Function**:

$$Cost = \text{Distance} + \text{Direction Penalty} + \text{Stop Penalty}$$

1. **Distance**: Absolute difference between `elevator.currentFloor` and `request.floor`.
2. **Direction Penalty**:
    - If Elevator is `IDLE`: Penalty = 0.
    - If Elevator is moving toward the request floor in the same direction: Penalty = 0.
    - If Elevator is moving away: Penalty = High (must complete current trip first).
    - If Elevator is moving toward the floor but in the opposite direction: Penalty = Medium.
3. **Stop Penalty**: Each existing stop the elevator must make before reaching the new request adds a small penalty.

### Code Implementation Logic

```python
from enum import Enum
from heapq import heappush, heappop

class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class Request:
    def __init__(self, floor, direction=Direction.IDLE):
        self.floor = floor
        self.direction = direction

class Elevator:
    def __init__(self, id):
        self.id = id
        self.current_floor = 0
        self.direction = Direction.IDLE
        self.stops = [] # Min-heap for UP, Max-heap for DOWN

    def add_stop(self, floor):
        self.stops.append(floor)
        self.stops.sort() # Simplified: keep stops sorted

    def move(self):
        if not self.stops:
            self.direction = Direction.IDLE
            return
        
        target = self.stops[0]
        if target > self.current_floor:
            self.direction = Direction.UP
            self.current_floor += 1
        elif target < self.current_floor:
            self.direction = Direction.DOWN
            self.current_floor -= 1
        
        if self.current_floor == target:
            self.stops.pop(0)
            print(f"Elevator {self.id} stopped at floor {self.current_floor}")

class ElevatorController:
    def __init__(self, elevators):
        self.elevators = elevators

    def handle_external_request(self, floor, direction):
        best_elevator = self.select_best_elevator(floor, direction)
        best_elevator.add_stop(floor)
        print(f"Assigned Elevator {best_elevator.id} to floor {floor}")

    def select_best_elevator(self, floor, direction):
        # Implementation of Cost Function
        min_cost = float('inf')
        selected = self.elevators[0]

        for e in self.elevators:
            cost = abs(e.current_floor - floor)
            # Penalty if elevator is moving away
            if (e.direction == Direction.UP and floor < e.current_floor) or \
               (e.direction == Direction.DOWN and floor > e.current_floor):
                cost += 20 # High penalty
            
            if cost < min_cost:
                min_cost = cost
                selected = e
        return selected
```

### Concurrency Handling
In a real production system, the `ElevatorController` would operate on a **Priority Queue** of requests and utilize **Mutex Locks** (or `synchronized` blocks in Java) when updating `elevator.current_floor` or `elevator.stops` to prevent race conditions where two threads assign the same elevator to conflicting tasks.

---

## 5. Real-World Applications

1. **Smart Building Management**: Modern skyscrapers use "Destination Control Systems" (DCS). Instead of pressing Up/Down, users enter their destination floor at a kiosk. The controller groups users going to the same floor into the same car, significantly reducing the number of stops.
2. **Warehouse Automation (Kiva/Amazon Robotics)**: The "Elevator Group" logic is used to dispatch robots to pick up pods. The "Cost Function" is used to determine which robot is closest and has the least congestion in its path.
3. **Cloud Resource Scheduling**: Assigning a task (request) to a server (elevator) based on current load (stops) and proximity/latency (distance).

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Dispatching** | $O(E)$ | $O(1)$ | $E$ = Number of elevators in the group. |
| **Stop Management** | $O(\log S)$ | $O(S)$ | $S$ = Number of stops; using Priority Queues. |
| **Movement** | $O(1)$ | $O(1)$ | Constant time per floor tick. |""",
    'solutions': """# Solution Guide: Advanced Elevator Group Control System

## 1. Requirements & System Constraints

The goal is to design a group control system (GCS) that manages a fleet of elevators in a high-rise building to optimize passenger throughput, minimize average wait times, and reduce energy consumption.

### 1.1 Functional Requirements
*   **Request Handling**:
    *   **External Call**: Passengers press "Up" or "Down" buttons at a floor.
    *   **Internal Call**: Passengers select a destination floor inside the cabin.
*   **Dispatching Logic**: The system must intelligently assign an elevator to an external call based on proximity, direction, and current load.
*   **Group Optimization**: 
    *   Minimize Average Wait Time (AWT).
    *   Minimize Average Time to Destination (ATD).
*   **Capacity Management**: Elevators should stop accepting calls if they reach weight capacity (overload sensor).
*   **Special Modes**:
    *   **Emergency Mode**: Fire alarm triggers all elevators to descend to the ground floor and open doors.
    *   **VIP/Service Mode**: Dedicated elevator for priority access.
    *   **Maintenance Mode**: Ability to take a specific elevator offline.
    *   **Energy Saving**: Elevators park at strategic floors during low-traffic periods.
*   **Zoning**: Ability to divide a building into zones (e.g., Floors 1-20 served by Group A, 21-40 by Group B).

### 1.2 Non-Functional Requirements
*   **Reliability & Safety**: The system must be fail-safe. Hardware interrupts must override software commands.
*   **Low Latency**: The dispatching decision must be made in milliseconds.
*   **High Availability**: The Group Controller should not be a single point of failure (SPOF).
*   **Scalability**: Support varying building heights (10 to 100+ floors) and group sizes (2 to 20+ elevators).

### 1.3 Constraints & Scale
*   **Typical Building**: 50 floors, 6-8 elevators.
*   **Peak Load**: Morning rush (all going up), Evening rush (all going down).
*   **Response Time**: $< 200\text{ms}$ for request processing.

---

## 2. High-Level Architecture

The system follows a hierarchical control pattern: **Group Controller $\rightarrow$ Elevator Controller $\rightarrow$ Actuators**.

### 2.1 Core Components
1.  **Group Dispatcher (The Brain)**: Implements the allocation algorithm. It maintains the global state of all elevators and pending requests.
2.  **Elevator Controller (The Executor)**: Manages the local state of a single cabin (current floor, direction, door status, weight).
3.  **Floor Panel Interface**: Handles inputs from the hall buttons and outputs to the floor displays.
4.  **Cabin Panel Interface**: Handles floor selections inside the elevator.
5.  **Safety Monitor**: A hard-wired subsystem that monitors door sensors, cable tension, and emergency stops.

### 2.2 Architecture Diagram (Mermaid)

```mermaid
graph TD
    subgraph "Passenger Interface"
        FP[Floor Panels]
        CP[Cabin Panels]
    end

    subgraph "Control Layer"
        GD[Group Dispatcher]
        SC[State Coordinator - Redis]
    end

    subgraph "Execution Layer"
        EC1[Elevator Controller 1]
        EC2[Elevator Controller 2]
        ECn[Elevator Controller N]
    end

    subgraph "Hardware Layer"
        M1[Motor/Brake/Door 1]
        M2[Motor/Brake/Door 2]
        Mn[Motor/Brake/Door N]
    end

    FP -->|Request Floor/Dir| GD
    CP -->|Set Destination| EC1
    GD -->|Assign Job| EC1
    GD -->|Assign Job| EC2
    GD -->|Assign Job| ECn
    
    EC1 <--> SC
    EC2 <--> SC
    ECn <--> SC
    
    EC1 --> M1
    EC2 --> M2
    ECn --> Mn
    
    GD -.->|Read State| SC
```

### 2.3 Dispatching Algorithm: Cost-Based Allocation
Instead of a simple SCAN (Elevator) algorithm, we use a **Cost Function** to assign the "best" elevator $E$ for a request $R$:

$$\text{Cost}(E, R) = w_1 \cdot \text{Distance} + w_2 \cdot \text{StopCount} + w_3 \cdot \text{DirectionPenalty} + w_4 \cdot \text{LoadFactor}$$

*   **Distance**: Absolute difference between current floor and request floor.
*   **StopCount**: Number of existing stops the elevator must make before reaching $R$.
*   **DirectionPenalty**: High cost if the elevator is moving away from $R$.
*   **LoadFactor**: High cost if the elevator is nearly full.

---

## 3. Detailed Database Schema Design

Since elevator state changes every second, we use a hybrid approach: **Redis** for real-time state and **PostgreSQL** for configuration and auditing.

### 3.1 Real-Time State (Redis - Key-Value/Hash)
Redis is used for the "Current State of the World."
*   **Key**: `elevator:{id}` $\rightarrow$ **Value**: `{floor: 12, direction: UP, status: MOVING, load: 450kg, target_floors: [15, 20, 25]}`
*   **Key**: `floor_requests` $\rightarrow$ **Value**: `Sorted Set {floor: request_time}`

### 3.2 Persistent Store (PostgreSQL)
Used for auditing, maintenance logs, and building configuration.

#### Table: `elevators`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Unique elevator ID |
| `group_id` | UUID | FK | Reference to group |
| `max_capacity` | INT | NOT NULL | Max weight in kg |
| `status` | ENUM | NOT NULL | ACTIVE, MAINTENANCE, OUT_OF_SERVICE |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Installation date |

#### Table: `floor_configs`
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `floor_number` | INT | PK | Floor index |
| `zone_id` | INT | INDEX | Zoning for group distribution |
| `is_emergency_exit`| BOOL | DEFAULT FALSE | Special floor properties |

#### Table: `request_logs` (Partitioned by Date)
| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `request_id` | BIGINT | PK | Unique request ID |
| `floor` | INT | NOT NULL | Requesting floor |
| `direction` | ENUM | NOT NULL | UP, DOWN |
| `assigned_elevator`| UUID | FK | Which elevator took the call |
| `wait_time` | INT | - | Time from press to arrival (ms) |
| `timestamp` | TIMESTAMP | INDEX | For analytics |

---

## 4. Core API Design

The system uses a mix of REST for configuration and WebSockets for real-time updates.

### 4.1 External Call API
`POST /api/v1/requests`
*   **Payload**:
    ```json
    {
      "floor": 15,
      "direction": "UP",
      "timestamp": "2023-10-27T10:00:00Z"
    }
    ```
*   **Response**: `202 Accepted` (Dispatcher acknowledges and begins allocation).

### 4.2 Internal Destination API
`POST /api/v1/elevator/{id}/destination`
*   **Payload**:
    ```json
    {
      "destination_floor": 22
    }
    ```
*   **Response**: `200 OK` (Elevator adds floor to its internal queue).

### 4.3 System Status API
`GET /api/v1/status`
*   **Response**:
    ```json
    {
      "elevators": [
        { "id": "E1", "floor": 10, "direction": "UP", "load": "300kg", "stops": [12, 15] },
        { "id": "E2", "floor": 1, "direction": "IDLE", "load": "0kg", "stops": [] }
      ],
      "pending_requests": [ { "floor": 5, "direction": "DOWN" } ]
    }
    ```

---

## 5. Scalability & Advanced Topics

### 5.1 Fault Tolerance & High Availability
*   **Active-Passive Dispatchers**: Two Group Dispatchers run in parallel. The Passive one monitors a heartbeat from the Active one. If the heartbeat fails, the Passive takes over via a virtual IP (VIP).
*   **Local Intelligence**: If the Group Dispatcher fails entirely, Elevator Controllers fall back to a "Simple SCAN" mode, where they independently pick up requests from their current floor and direction.

### 5.2 Message Queues for Asynchronous Processing
To prevent the API from blocking during heavy traffic, a Message Queue (e.g., RabbitMQ/Kafka) is used:
`Floor Panel` $\rightarrow$ `Request API` $\rightarrow$ `Request Queue` $\rightarrow$ `Dispatcher` $\rightarrow$ `Elevator Controller`.

### 5.3 Traffic Pattern Optimization (Machine Learning)
*   **Predictive Parking**: Analyze historical data to identify patterns (e.g., 8:00 AM $\rightarrow$ Most people go from Floor 1 to 10-30). The system pre-positions elevators at the ground floor.
*   **Dynamic Zoning**: During peak hours, automatically shift Elevator E3 from Group B to Group A to handle higher demand.

### 5.4 Safety Interlocks (Hard-Wired)
The software cannot override safety sensors. If a "Door Obstructed" signal is received at the hardware level, the `Elevator Controller` is physically prevented from engaging the motor, regardless of the `Group Dispatcher` command.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Consistency vs. Availability
In this system, **Consistency (CP)** is prioritized over Availability. It is better for an elevator to stop moving for a second while resolving a state conflict than to move to the wrong floor or open doors between floors, which would be a critical safety failure.

### 6.2 Latency vs. Optimal Allocation
*   **Greedy Approach**: Assign the first available elevator. (Low latency, high AWT).
*   **Global Optimization**: Calculate costs for all elevators. (Slightly higher latency, low AWT).
*   **Decision**: We use the **Cost-Based Approach** because the computation time ($O(N)$ where $N$ is the number of elevators) is negligible compared to the mechanical travel time of the elevator.

### 6.3 Storage: SQL vs. NoSQL
*   **SQL**: Used for `elevators` and `floor_configs` because these require ACID properties and relational integrity (e.g., you cannot assign a request to a non-existent elevator).
*   **NoSQL (Redis)**: Used for the real-time state because the write-volume is extremely high (updates every few milliseconds as the elevator moves). Relational databases would suffer from lock contention.""",
}

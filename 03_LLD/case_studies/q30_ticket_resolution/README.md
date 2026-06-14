# Ticket Resolution System LLD

A Ticket Resolution System (or Help Desk System) is a critical piece of enterprise infrastructure used to manage customer grievances, technical bugs, and service requests. The goal is to ensure that every request is captured, categorized, assigned to the right expert, and resolved within a specified timeframe (SLA).

## 1. Overview & System Requirements

### Core Actors
- **Customer**: The user who creates a ticket to report an issue.
- **Support Agent**: The technical staff member who works on the ticket to provide a resolution.
- **Admin/Manager**: The user who manages agents, departments, and monitors system-wide performance.

### Functional Requirements
- **Ticket Creation**: Customers can create tickets with a title, description, priority, and category.
- **Ticket Assignment**: Tickets must be assigned to available agents. This can be done via:
    - **Manual Assignment**: Admin assigns a specific agent.
    - **Automatic Assignment**: System assigns based on a strategy (e.g., Round Robin or Least Loaded).
- **Lifecycle Management**: Tickets transition through states: `Open` $\rightarrow$ `InProgress` $\rightarrow$ `Resolved` $\rightarrow$ `Closed`.
- **Priority Handling**: High-priority tickets should be surfaced or handled first.
- **Notifications**: Users should be notified when a ticket is assigned or its status changes.
- **Categorization**: Tickets are grouped by departments (e.g., Billing, Technical, Sales).

---

## 2. Design Principles & Patterns

### SOLID Principles Applied
- **Single Responsibility Principle (SRP)**: We separate the `Ticket` (data), `TicketManager` (orchestration), and `AssignmentStrategy` (logic).
- **Open/Closed Principle (OCP)**: By using the **Strategy Pattern** for ticket assignment, we can add new assignment algorithms (e.g., Skill-based routing) without modifying the existing `TicketManager` code.
- **Dependency Inversion Principle (DIP)**: The `TicketManager` depends on the `AssignmentStrategy` interface, not concrete implementations.

### Design Patterns Used
| Pattern | Purpose | Why it solves the problem |
| :--- | :--- | :--- |
| **Strategy Pattern** | Assignment Logic | Decouples the "who gets the ticket" logic from the "how to create a ticket" logic. |
| **Observer Pattern** | Notifications | Allows multiple notification channels (Email, SMS, Push) to react to status changes without coupling the Ticket class to notification services. |
| **Factory Pattern** | Ticket Creation | Simplifies the creation of different ticket types (e.g., Bug vs. Feature Request) if specific defaults are needed. |
| **Singleton Pattern** | TicketSystem | Ensures a single point of truth for managing the global state of all active tickets. |

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-------------------+        +-----------------------+        +-----------------------+
|      User         |<-------|     TicketManager     |<-------|   AssignmentStrategy  |
+-------------------+        +-----------------------+        +-----------------------+
| - userId          |        | - tickets: Map        |        | + assign(ticket, agents)|
| - name            |        | - agents: List        |        +-----------^-----------+
+--------^----------+        +-----------+-----------+                    |
         |                               |                        +-------+-------+
         +-------------------------------+                        |               |
         |                               |               +----------------+ +----------------+
 +-------+-------+               +-------v-------+       | RoundRobinStrat | | LeastLoadedStrat|
 | Customer      |               |    Ticket     |       +----------------+ +----------------+
 +---------------+               +---------------+
 | + createTicket|               | - ticketId    |
 +---------------+               | - status      |
                                 | - priority    |
                                 | - assignee    |
                                 +---------------+
```

### Relationships
- **Composition**: `TicketManager` contains a collection of `Ticket` objects.
- **Aggregation**: `Ticket` is associated with a `User` (creator) and an `Agent` (assignee).
- **Strategy**: `TicketManager` holds a reference to an `AssignmentStrategy` interface.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from collections import deque

# --- Enums ---
class TicketStatus(Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class TicketPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

# --- Core Entities ---
class User:
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

class Agent(User):
    def __init__(self, user_id: str, name: str, email: str, expertise: str):
        super().__init__(user_id, name, email)
        self.expertise = expertise
        self.assigned_tickets_count = 0

    def increment_load(self):
        self.assigned_tickets_count += 1

    def decrement_load(self):
        self.assigned_tickets_count -= 1

class Ticket:
    def __init__(self, ticket_id: str, title: str, description: str, 
                 priority: TicketPriority, creator: User):
        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.priority = priority
        self.creator = creator
        self.status = TicketStatus.OPEN
        self.assignee: Optional[Agent] = None

    def update_status(self, new_status: TicketStatus):
        print(f"Ticket {self.ticket_id} moving from {self.status.value} to {new_status.value}")
        self.status = new_status

    def assign_to(self, agent: Agent):
        self.assignee = agent
        self.status = TicketStatus.IN_PROGRESS

# --- Assignment Strategies (Strategy Pattern) ---
class AssignmentStrategy(ABC):
    @abstractmethod
    def assign(self, ticket: Ticket, agents: List[Agent]) -> Optional[Agent]:
        pass

class RoundRobinStrategy(AssignmentStrategy):
    def __init__(self):
        self.index = 0

    def assign(self, ticket: Ticket, agents: List[Agent]) -> Optional[Agent]:
        if not agents: return None
        agent = agents[self.index % len(agents)]
        self.index += 1
        return agent

class LeastLoadedStrategy(AssignmentStrategy):
    def assign(self, ticket: Ticket, agents: List[Agent]) -> Optional[Agent]:
        if not agents: return None
        # Find agent with the minimum number of assigned tickets
        return min(agents, key=lambda a: a.assigned_tickets_count)

# --- Ticket System (The Facade/Manager) ---
class TicketSystem:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TicketSystem, cls).__new__(cls)
            cls._instance.tickets = {}
            cls._instance.agents = []
            cls._instance.strategy = RoundRobinStrategy() # Default
        return cls._instance

    def set_strategy(self, strategy: AssignmentStrategy):
        self.strategy = strategy

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def create_ticket(self, ticket_id: str, title: str, desc: str, 
                      priority: TicketPriority, user: User) -> Ticket:
        ticket = Ticket(ticket_id, title, desc, priority, user)
        self.tickets[ticket_id] = ticket
        
        # Auto-assign ticket
        agent = self.strategy.assign(ticket, self.agents)
        if agent:
            ticket.assign_to(agent)
            agent.increment_load()
            print(f"Ticket {ticket_id} auto-assigned to Agent {agent.name}")
        
        return ticket

    def resolve_ticket(self, ticket_id: str):
        if ticket_id in self.tickets:
            ticket = self.tickets[ticket_id]
            ticket.update_status(TicketStatus.RESOLVED)
            if ticket.assignee:
                ticket.assignee.decrement_load()

# --- Execution ---
if __name__ == "__main__":
    system = TicketSystem()
    
    # Setup Agents
    alice = Agent("A1", "Alice", "alice@support.com", "Technical")
    bob = Agent("A2", "Bob", "bob@support.com", "Billing")
    system.add_agent(alice)
    system.add_agent(bob)

    # Setup Customer
    customer = User("C1", "John Doe", "john@gmail.com")

    # Scenario 1: Round Robin
    print("--- Scenario 1: Round Robin ---")
    system.create_ticket("T1", "Login Issue", "Cannot login", TicketPriority.HIGH, customer)
    system.create_ticket("T2", "Payment Fail", "Card declined", TicketPriority.MEDIUM, customer)
    system.create_ticket("T3", "UI Bug", "Button missing", TicketPriority.LOW, customer)

    # Scenario 2: Change Strategy to Least Loaded
    print("\n--- Scenario 2: Least Loaded ---")
    system.set_strategy(LeastLoadedStrategy())
    # Resolve T1 so Alice (A1) becomes the least loaded
    system.resolve_ticket("T1") 
    system.create_ticket("T4", "API Timeout", "408 Error", TicketPriority.URGENT, customer)
```

### Logic Walkthrough
1.  **Initialization**: The `TicketSystem` is a Singleton. It maintains a registry of all `agents` and `tickets`.
2.  **Ticket Creation**: When `create_ticket` is called, a `Ticket` object is instantiated. 
3.  **Dynamic Assignment**: The system calls `self.strategy.assign()`. Because we use the Strategy pattern, the system doesn't care *how* the agent is chosen—it only cares that it gets an `Agent` object back.
4.  **Load Tracking**: The `Agent` class tracks `assigned_tickets_count`. This allows the `LeastLoadedStrategy` to make data-driven decisions.
5.  **State Transition**: When `resolve_ticket` is called, the status changes to `RESOLVED` and the agent's load is decremented, making them available for more urgent tickets.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Description |
| :--- | :--- | :--- | :--- |
| **Create Ticket** | $O(1)$ or $O(A)$ | $O(1)$ | $O(1)$ for Round Robin; $O(A)$ for Least Loaded where $A$ is the number of agents. |
| **Assign Ticket** | $O(A)$ | $O(1)$ | Finding the agent with the minimum load requires scanning the agent list. |
| **Resolve Ticket** | $O(1)$ | $O(1)$ | Direct lookup in the ticket map. |
| **Overall Storage**| $O(T + A)$ | $O(T + A)$ | $T$ is total tickets, $A$ is total agents. |

---

## 6. Real-World Applications

This LLD pattern is the foundation for several production-grade systems:
- **Customer Support Tools**: Zendesk and Freshdesk use similar assignment strategies to distribute tickets among support tiers (L1, L2, L3).
- **Bug Tracking Systems**: Jira Service Management uses custom "Issue Type" factories and "Assignment Schemes" (similar to our Strategy pattern).
- **Cloud Load Balancers**: The `LeastLoadedStrategy` is conceptually identical to the "Least Connections" algorithm used in Nginx or AWS ELB to distribute network traffic to servers.
- **Ride-Sharing Apps**: Uber/Lyft use an evolved version of this to assign the "best" driver (Agent) to a rider (Customer) based on proximity (Strategy).
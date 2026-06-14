# Adapter Pattern LLD

The **Adapter Pattern** is a structural design pattern that allows objects with incompatible interfaces to collaborate. It acts as a wrapper between two objects: it catches calls for one object and transforms them into a format and interface that the second object recognizes.

---

## 1. Overview & System Requirements

### Core Intent
The primary goal of the Adapter pattern is to provide a bridge between a **Client** (which expects a specific interface) and an **Adaptee** (a legacy or third-party class that provides the required functionality but has an incompatible interface).

### Functional Requirements
- **Interface Translation**: Convert the interface of the `Adaptee` class into an interface the `Client` expects.
- **Non-Intrusive Integration**: Integrate a third-party library or legacy system without modifying its source code (preserving the integrity of the original component).
- **Decoupling**: Ensure the client is not tightly coupled to the specific implementation details of the legacy system.

### Actors & Entities
| Entity | Role | Responsibility |
| :--- | :--- | :--- |
| **Client** | Consumer | Contains the business logic and calls methods on the `Target` interface. |
| **Target** | Interface | Defines the domain-specific interface that the Client uses. |
| **Adaptee** | Legacy/Third-Party | The class that needs adapting; it has the functionality but the wrong interface. |
| **Adapter** | Wrapper | Implements the `Target` interface and translates calls to the `Adaptee`. |

---

## 2. Design Principles & Patterns

### Applied OOP Principles
1. **Open-Closed Principle (OCP)**: The Adapter pattern allows us to introduce new adapters without breaking existing client code. The `Adaptee` remains "closed" for modification, while the system remains "open" for extension.
2. **Single Responsibility Principle (SRP)**: The translation logic is isolated within the `Adapter` class, ensuring that the business logic in the `Client` and the core logic in the `Adaptee` remain separate.
3. **Dependency Inversion Principle**: The `Client` depends on an abstraction (`Target` interface) rather than a concrete implementation (`Adaptee`), making the system modular.

### Why use this over Inheritance?
While one could theoretically use inheritance to make a class fit an interface, the **Object Adapter** (using composition) is preferred because:
- It follows the "Composition over Inheritance" principle.
- It allows the adapter to wrap any subclass of the `Adaptee`.
- It avoids the "fragile base class" problem.

---

## 3. Class Structure & Relationships

### Relationship Diagram
The Adapter pattern typically utilizes **Composition**. The Adapter implements the Target interface and holds a reference to the Adaptee.

```text
+------------------+             +-------------------+
|      Client      | ----------> |   Target (Intf)   |
+------------------+             +-------------------+
                                           ^
                                           | (Implements)
                                           |
                                 +-------------------+
                                 |      Adapter      |
                                 +-------------------+
                                           |
                                           | (Composes/Wraps)
                                           v
                                 +-------------------+
                                 |      Adaptee      |
                                 +-------------------+
```

### Key Relationships
- **Client $\rightarrow$ Target**: Dependency (Client uses the interface).
- **Adapter $\rightarrow$ Target**: Realization (Adapter implements the interface).
- **Adapter $\rightarrow$ Adaptee**: Association/Composition (Adapter holds an instance of the Adaptee).

---

## 4. Step-by-Step Logic & Code Walkthrough

Imagine a scenario where our system expects data in **XML** format, but we are integrating a modern 3rd-party analytics library that only provides data in **JSON**.

### Implementation

```python
from abc import ABC, abstractmethod
import json

# 1. Target Interface
# This is what the Client expects.
class XMLTarget(ABC):
    @abstractmethod
    def get_data_as_xml(self) -> str:
        pass

# 2. Adaptee (The legacy or 3rd party system)
# This has the functionality we need, but the wrong interface.
class JSONAnalyticsProvider:
    def fetch_json_data(self) -> str:
        # Simulating a JSON response from an API
        return '{"status": "success", "value": 42}'

# 3. Adapter
# Bridges the gap between JSONAnalyticsProvider and XMLTarget.
class AnalyticsAdapter(XMLTarget):
    def __init__(self, adaptee: JSONAnalyticsProvider):
        self.adaptee = adaptee

    def get_data_as_xml(self) -> str:
        # Step A: Get data from the adaptee
        json_data = self.adaptee.fetch_json_data()
        
        # Step B: Translate/Transform JSON to XML
        data = json.loads(json_data)
        xml_output = f"<response><status>{data['status']}</status><value>{data['value']}</value></response>"
        
        return xml_output

# 4. Client Logic
def client_code(target: XMLTarget):
    print(f"Client: I can only work with XML. Result: {target.get_data_as_xml()}")

def solve():
    # The Adaptee we want to use
    adaptee = JSONAnalyticsProvider()
    
    # The Adapter that makes it compatible
    adapter = AnalyticsAdapter(adaptee)
    
    # Client uses the adapter seamlessly
    client_code(adapter)

if __name__ == "__main__":
    solve()
```

### Logic Walkthrough
1. **Initialization**: The `Client` creates an instance of the `Adaptee` (`JSONAnalyticsProvider`).
2. **Wrapping**: The `Adaptee` is passed into the `Adapter` constructor. The adapter now "wraps" the legacy object.
3. **Request**: The `Client` calls `get_data_as_xml()` on the adapter, believing it is talking to a standard XML provider.
4. **Translation**: The `Adapter` internally calls `fetch_json_data()` on the `Adaptee`, receives a JSON string, and converts it into the XML format required by the `Target` interface.
5. **Return**: The converted XML string is returned to the `Client`.

---

## 5. Complexity Analysis

| Aspect | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | $O(T)$ | Where $T$ is the time taken to translate the data. The adapter adds a constant overhead for the method call and the translation logic. |
| **Space Complexity** | $O(1)$ | The adapter only maintains a reference to the adaptee object; no significant additional memory is used regardless of input size. |

---

## 6. Real-World Applications

1. **Database Drivers**: JDBC (Java Database Connectivity) acts as an adapter. The Java application uses a standard JDBC interface, and the driver (the adapter) translates those calls into the specific protocol of the database (MySQL, PostgreSQL, Oracle).
2. **Payment Gateways**: An e-commerce site may define a `PaymentProcessor` interface. It then creates `StripeAdapter` and `PayPalAdapter` to handle the differing APIs of these two providers.
3. **UI Frameworks**: In Android development, `RecyclerView.Adapter` converts a data source (like a List or Database query) into View objects that can be displayed on the screen.
4. **Legacy System Migration**: When moving from a monolithic system to microservices, adapters are used to allow new services to communicate with old legacy APIs without rewriting the entire legacy codebase.
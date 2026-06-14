INFO = {
    'difficulty': 'Medium',
    'link': 'https://refactoring.guru/design-patterns/command',
    'description': 'Encapsulate executable operations.',
    'groups': ['Behavioral Patterns'],
    'readme_content': """# Command Design Pattern LLD

The **Command Pattern** is a behavioral design pattern that turns a request into a stand-alone object that contains all information about the request. This transformation allows you to pass requests as a method argument, delay or queue a request's execution, and support undoable operations.

---

## 1. Overview & System Requirements

### Core Intent
The primary goal of the Command pattern is to **decouple the object that invokes the operation (Invoker) from the object that knows how to perform its operation (Receiver).**

### Functional Requirements
- **Encapsulation**: Every single request must be encapsulated as an object.
- **Abstraction**: The Invoker should not know the internal details of the Receiver or the specific logic of the operation.
- **Extensibility**: The system should allow adding new commands without changing existing code.
- **Reversibility**: (Optional but common) The system should be able to track history to support `undo` operations.

### Key Actors
| Actor | Role | Responsibility |
| :--- | :--- | :--- |
| **Command** | Interface | Declares an interface for executing an operation. |
| **ConcreteCommand** | Implementation | Defines the binding between a Receiver and an action. |
| **Receiver** | Business Logic | The object that performs the actual work. |
| **Invoker** | Trigger | Asks the command to carry out the request. |
| **Client** | Orchestrator | Creates ConcreteCommand and associates it with a Receiver. |

---

## 2. Design Principles & Patterns

### Applied SOLID Principles
1. **Single Responsibility Principle (SRP)**: The `Invoker` is only responsible for triggering the command, while the `Receiver` is only responsible for the business logic. The `Command` object handles the mapping.
2. **Open/Closed Principle (OCP)**: You can introduce new commands (e.g., `DimLightCommand`) without modifying the `Invoker` or the existing `Receiver` logic.
3. **Dependency Inversion Principle (DIP)**: The `Invoker` depends on the `Command` interface rather than concrete command classes, reducing tight coupling.

### Why this pattern?
In a naive implementation, a UI Button (Invoker) might call `Light.turnOn()` directly. This creates a tight coupling where the Button must know exactly what a `Light` is. If you later want the Button to open a garage door, you have to rewrite the Button class. The Command pattern solves this by introducing an intermediary object.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)
```text
+-------------------+           +-----------------------+
|      Client       |           |      Invoker          |
+-------------------+           +-----------------------+
| - setup()         |---------->| - command: Command    |
+-------------------+           | + executeCommand()    |
          |                     +-----------------------+
          |                                   |
          |                                   v
          |                     +-----------------------+
          |                     |       <<Interface>>   |
          |                     |        Command        |
          |                     +-----------------------+
          |                     | + execute()           |
          |                     | + undo()              |
          |                     +-----------------------+
          |                                   ^
          |                                   |
          |                     +-----------------------+
          |                     |    ConcreteCommand    |
          |                     +-----------------------+
          +-------------------> | - receiver: Receiver  |
                                | + execute()           |
                                +-----------------------+
                                            |
                                            v
                                +-----------------------+
                                |       Receiver        |
                                +-----------------------+
                                | + action1()           |
                                | + action2()           |
                                +-----------------------+
```

### Relationships
- **Composition**: `ConcreteCommand` *has-a* `Receiver`.
- **Aggregation**: `Invoker` *has-a* `Command` (can be swapped at runtime).
- **Implementation**: `ConcreteCommand` *implements* the `Command` interface.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation
Below is the professional implementation of a Smart Home system using the Command Pattern.

```python
from abc import ABC, abstractmethod
from typing import List

# --- Receiver ---
# The Receiver contains the actual business logic.
class Light:
    def turn_on(self):
        print("The light is ON")

    def turn_off(self):
        print("The light is OFF")

# --- Command Interface ---
# All commands must implement this interface.
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

# --- Concrete Commands ---
# These classes bind the Receiver to a specific action.
class LightOnCommand(Command):
    def __init__(self, light: Light):
        self._light = light

    def execute(self):
        self._light.turn_on()

    def undo(self):
        self._light.turn_off()

class LightOffCommand(Command):
    def __init__(self, light: Light):
        self._light = light

    def execute(self):
        self._light.turn_off()

    def undo(self):
        self._light.turn_on()

# --- Invoker ---
# The Invoker doesn't know what the command does; it just calls execute().
class RemoteControl:
    def __init__(self):
        self._history: List[Command] = []

    def submit(self, command: Command):
        print(f"Invoker: Executing command...")
        command.execute()
        self._history.append(command)

    def undo_last(self):
        if not self._history:
            print("Nothing to undo.")
            return
        
        command = self._history.pop()
        print(f"Invoker: Undoing last command...")
        command.undo()

# --- Client ---
def solve():
    # 1. Create the Receiver
    living_room_light = Light()

    # 2. Create Concrete Commands and associate them with the Receiver
    light_on = LightOnCommand(living_room_light)
    light_off = LightOffCommand(living_room_light)

    # 3. Create the Invoker
    remote = RemoteControl()

    # 4. Execute operations
    remote.submit(light_on)  # Output: The light is ON
    remote.submit(light_off) # Output: The light is OFF
    
    # 5. Undo operation
    remote.undo_last()        # Output: The light is ON (undoes light_off)
    remote.undo_last()        # Output: The light is OFF (undoes light_on)

if __name__ == "__main__":
    solve()
```

### Logic Flow
1. **Instantiation**: The `Client` initializes the `Light` (Receiver).
2. **Binding**: The `Client` wraps the `Light` inside a `LightOnCommand`. This "packages" the request.
3. **Triggering**: The `RemoteControl` (Invoker) receives the command object. It doesn't know if it's a light, a fan, or a door; it only knows the object has an `.execute()` method.
4. **Execution**: When `remote.submit()` is called, the command's `.execute()` method is triggered, which in turn calls `light.turn_on()`.
5. **Undo Logic**: The Invoker maintains a stack (`_history`). To undo, it pops the last command and calls its `.undo()` method, which contains the inverse logic of the original action.

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Execution** | $O(1)$ | $O(1)$ | Direct method call through interface. |
| **Undo** | $O(1)$ | $O(1)$ | Popping from a stack. |
| **Memory** | - | $O(N)$ | $N$ is the number of commands stored in history. |

---

## 5. Real-World Applications

### 1. GUI Frameworks
Every button in a modern UI (like Java Swing or WPF) uses a variation of the Command pattern. The button (Invoker) is assigned an `ActionListener` or `Command` object. The button doesn't know what happens when it is clicked; it simply executes the command assigned to it.

### 2. Database Transaction Logs
Databases use a "Command Log" (Write-Ahead Logging). Every change to the DB is encapsulated as a command object. If the system crashes, the DB can "replay" these commands to restore the state. If a transaction is rolled back, the `undo` logic of the command is applied.

### 3. Text Editors (Undo/Redo)
Software like VS Code or Microsoft Word implements every keystroke or formatting change as a command object. These objects are pushed onto a stack, enabling the `Ctrl+Z` (Undo) and `Ctrl+Y` (Redo) functionality.

### 4. Job Queues / Task Schedulers
Distributed systems (like Celery or RabbitMQ) treat tasks as commands. The producer creates a "command" (task name + arguments), sends it to a queue, and a worker (Invoker) executes it later without knowing the internal logic of the task.""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1) per operation
# Space Complexity: O(1)
# In this naive approach, we avoid the Command Pattern entirely and use direct method calls.
# While simple, this couples the Invoker (the user/client) directly to the Receiver (the light),
# making it impossible to queue operations, log them, or implement undo functionality easily.

class Light:
    \"\"\"The Receiver class.\"\"\"
    def __init__(self):
        self.is_on = False

    def turn_on(self):
        self.is_on = True
        print("Light is ON")

    def turn_off(self):
        self.is_on = False
        print("Light is OFF")

def solve_naive():
    # Direct interaction without encapsulation
    light = Light()
    
    # The "Invoker" logic is just direct calls
    light.turn_on()
    light.turn_off()

# --- APPROACH 2: Optimal (Command Design Pattern) ---
# Time Complexity: O(1) for execution and undo operations.
# Space Complexity: O(N) where N is the number of commands stored in the history stack for undo.
# This is the optimal approach because it encapsulates a request as an object. 
# This decoupling allows the invoker to remain agnostic of the receiver's implementation, 
# enables the implementation of Undo/Redo functionality via a command history stack, 
# and allows for composite commands (Macros).

from abc import ABC, abstractmethod
from typing import List

class Command(ABC):
    \"\"\"The Command interface.\"\"\"
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class Light:
    \"\"\"The Receiver class that contains the actual business logic.\"\"\"
    def __init__(self, name: str):
        self.name = name
        self.is_on = False

    def turn_on(self) -> None:
        self.is_on = True
        print(f"{self.name} light is ON")

    def turn_off(self) -> None:
        self.is_on = False
        print(f"{self.name} light is OFF")

class LightOnCommand(Command):
    \"\"\"Concrete Command for turning the light on.\"\"\"
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_on()

    def undo(self) -> None:
        self.light.turn_off()

class LightOffCommand(Command):
    \"\"\"Concrete Command for turning the light off.\"\"\"
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_off()

    def undo(self) -> None:
        self.light.turn_on()

class RemoteControl:
    \"\"\"The Invoker class.\"\"\"
    def __init__(self):
        self._history: List[Command] = []

    def submit(self, command: Command) -> None:
        \"\"\"Executes a command and saves it to history.\"\"\"
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        \"\"\"Reverts the last executed command.\"\"\"
        if not self._history:
            print("Nothing to undo")
            return
        
        command = self._history.pop()
        command.undo()

def solve_optimal():
    # Receiver
    living_room_light = Light("Living Room")
    
    # Commands
    light_on = LightOnCommand(living_room_light)
    light_off = LightOffCommand(living_room_light)
    
    # Invoker
    remote = RemoteControl()
    
    # Execution
    remote.submit(light_on)   # Living Room light is ON
    remote.submit(light_off)  # Living Room light is OFF
    
    # Undo operations
    remote.undo()             # Living Room light is ON (Undo off)
    remote.undo()             # Living Room light is OFF (Undo on)

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package design_patterns;

import java.util.Stack;

// Command Interface
interface Command {
    void execute();
    void undo();
}

// Receiver
class Light {
    private String name;
    private boolean isOn = false;

    public Light(String name) {
        this.name = name;
    }

    public void turnOn() {
        isOn = true;
        System.out.println(name + " light is ON");
    }

    public void turnOff() {
        isOn = false;
        System.out.println(name + " light is OFF");
    }
}

// Concrete Command 1
class LightOnCommand implements Command {
    private Light light;

    public LightOnCommand(Light light) {
        this.light = light;
    }

    @Override
    public void execute() {
        light.turnOn();
    }

    @Override
    public void undo() {
        light.turnOff();
    }
}

// Concrete Command 2
class LightOffCommand implements Command {
    private Light light;

    public LightOffCommand(Light light) {
        this.light = light;
    }

    @Override
    public void execute() {
        light.turnOff();
    }

    @Override
    public void undo() {
        light.turnOn();
    }
}

// Invoker
class RemoteControl {
    private Stack<Command> history = new Stack<>();

    public void submit(Command command) {
        command.execute();
        history.push(command);
    }

    public void undo() {
        if (history.isEmpty()) {
            System.out.println("Nothing to undo");
            return;
        }
        Command command = history.pop();
        command.undo();
    }
}

public class CommandPattern {
    public static void main(String[] args) {
        Light livingRoomLight = new Light("Living Room");
        Command lightOn = new LightOnCommand(livingRoomLight);
        Command lightOff = new LightOffCommand(livingRoomLight);

        RemoteControl remote = new RemoteControl();
        
        remote.submit(lightOn);
        remote.submit(lightOff);
        
        remote.undo(); // Undoes off -> On
        remote.undo(); // Undoes on -> Off
    }
}
\"\"\"""",
}

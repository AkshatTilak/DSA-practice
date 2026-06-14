"""
Challenge: q07_command_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/command

Problem:
Encapsulate executable operations.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1) per operation
# Space Complexity: O(1)
# In this naive approach, we avoid the Command Pattern entirely and use direct method calls.
# While simple, this couples the Invoker (the user/client) directly to the Receiver (the light),
# making it impossible to queue operations, log them, or implement undo functionality easily.

class Light:
    """The Receiver class."""
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
    """The Command interface."""
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class Light:
    """The Receiver class that contains the actual business logic."""
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
    """Concrete Command for turning the light on."""
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_on()

    def undo(self) -> None:
        self.light.turn_off()

class LightOffCommand(Command):
    """Concrete Command for turning the light off."""
    def __init__(self, light: Light):
        self.light = light

    def execute(self) -> None:
        self.light.turn_off()

    def undo(self) -> None:
        self.light.turn_on()

class RemoteControl:
    """The Invoker class."""
    def __init__(self):
        self._history: List[Command] = []

    def submit(self, command: Command) -> None:
        """Executes a command and saves it to history."""
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        """Reverts the last executed command."""
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
"""
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
"""

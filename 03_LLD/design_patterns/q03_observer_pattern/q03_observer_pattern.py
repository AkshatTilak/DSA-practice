"""
Challenge: q03_observer_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/observer

Problem:
Implement Publish-Subscribe dynamic messaging engine via Observer Pattern.
"""

# --- STARTER TEMPLATE FOR USER ---
class Subject:
    def __init__(self):
        self._observers = []
    def register(self, obs):
        self._observers.append(obs)
    def notify(self, event: str):
        for o in self._observers: o.update(event)

class Observer:
    def update(self, event: str):
        pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1) for register, O(N) for notify
# Space Complexity: O(N) where N is the number of observers
# This implementation follows the starter code exactly. It uses a list to store observers, 
# which allows duplicate registrations and does not provide a way to unregister.

class Observer:
    def update(self, event: str):
        pass

class Subject:
    def __init__(self):
        self._observers = []

    def register(self, obs):
        self._observers.append(obs)

    def notify(self, event: str):
        for o in self._observers:
            o.update(event)

# --- APPROACH 2: Optimal (Set-based with Error Handling) ---
# Time Complexity: O(1) for register, O(1) for unregister, O(N) for notify
# Space Complexity: O(N) where N is the number of observers
# This approach is optimal for a production environment because:
# 1. It uses a 'set' to ensure observers are unique and unregistration is O(1).
# 2. It utilizes an Abstract Base Class (ABC) to enforce the Observer interface.
# 3. It creates a copy of the observer set during notification to prevent 'RuntimeError' 
#    if an observer tries to unregister itself during the update call.
# 4. It wraps observer updates in a try-except block so that one failing observer 
#    doesn't stop notifications for others.

from abc import ABC, abstractmethod
import logging

class Observer(ABC):
    @abstractmethod
    def update(self, event: str):
        """Handle the event received from the subject."""
        pass

class Subject:
    def __init__(self):
        # Using a set for O(1) removal and to prevent duplicate registrations
        self._observers = set()

    def register(self, obs: Observer):
        """Registers an observer. Raises TypeError if obs does not implement Observer."""
        if not isinstance(obs, Observer):
            raise TypeError("The provided observer must inherit from the Observer base class.")
        self._observers.add(obs)

    def unregister(self, obs: Observer):
        """Removes an observer from the registry."""
        self._observers.discard(obs)

    def notify(self, event: str):
        """Notifies all registered observers of an event."""
        # We iterate over a copy of the set to ensure thread-safety/mutation-safety 
        # in case an observer calls unregister() during the update loop.
        for observer in list(self._observers):
            try:
                observer.update(event)
            except Exception as e:
                # Log error instead of crashing the entire notification chain
                logging.error(f"Failed to notify observer {observer}: {e}")

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package design_patterns;

import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class ObserverPattern {
    private static final Logger LOGGER = Logger.getLogger(ObserverPattern.class.getName());

    /**
     * Observer interface defining the contract for subscribers.
     */
    public interface Observer {
        void update(String event);
    }

    /**
     * Subject class maintaining the list of observers and broadcasting events.
     */
    public static class Subject {
        private final Set<Observer> observers = new HashSet<>();

        public void register(Observer obs) {
            if (obs != null) {
                observers.add(obs);
            }
        }

        public void unregister(Observer obs) {
            observers.remove(obs);
        }

        /**
         * We use notifyObservers instead of notify because 
         * notify() is a final method in java.lang.Object used for thread synchronization.
         */
        public void notifyObservers(String event) {
            // Create a copy to avoid ConcurrentModificationException 
            // if an observer unregisters during the iteration.
            List<Observer> currentObservers = new ArrayList<>(observers);
            for (Observer obs : currentObservers) {
                try {
                    obs.update(event);
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error notifying observer: " + e.getMessage(), e);
                }
            }
        }
    }

    // Example usage
    public static void main(String[] args) {
        Subject subject = new Subject();
        Observer loggerObserver = event -> System.out.println("Logger received: " + event);
        Observer mailObserver = event -> System.out.println("Email sent for: " + event);

        subject.register(loggerObserver);
        subject.register(mailObserver);
        subject.notifyObservers("System_Startup");
    }
}
"""

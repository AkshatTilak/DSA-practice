"""
LLD Pattern: Thread-Safe Singleton (Metaclass Approach)
Difficulty: Medium
Category: Design Patterns

Problem:
Implement a thread-safe Singleton class using a metaclass.
Multiple threads accessing the class must receive the exact same object instance.
Your implementation should minimize locking overhead (using double-checked locking equivalent or metaclass locks).

Curriculum Link: https://www.geeksforgeeks.org/dsa/top-100-data-structure-and-algorithms-dsa-interview-questions-topic-wise/
"""

import threading

# --- STARTER TEMPLATE FOR USER ---
class SingletonMeta(type):
    """
    A thread-safe implementation of Singleton using a Metaclass.
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Write your double-checked locking instantiation logic here
        pass


class DatabaseConnectionPool(metaclass=SingletonMeta):
    def __init__(self):
        self.connection_string = "postgresql://localhost:5432/db"


# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1)
# Space Complexity: O(1)
# This approach is not thread-safe. In a multi-threaded environment, multiple instances 
# could be created if two threads enter the 'if' block simultaneously.
import threading

class SingletonMeta_naive(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Race condition occurs here in multi-threaded environments
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

# --- APPROACH 2: Optimal (Double-Checked Locking) ---
# Time Complexity: O(1)
# Space Complexity: O(1)
# This is the optimal approach because it implements Double-Checked Locking. 
# It avoids the overhead of acquiring a lock every time the instance is requested. 
# The lock is only acquired if the instance hasn't been created yet, and the 
# second check inside the lock ensures that only one thread creates the instance 
# even if multiple threads passed the first check.
import threading

class SingletonMeta(type):
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # First check: avoid locking if the instance already exists
        if cls not in cls._instances:
            # Synchronize access to the instance creation process
            with cls._lock:
                # Second check: ensure another thread didn't create the instance 
                # while this thread was waiting for the lock
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package design_patterns;

/**
 * Java implementation of a thread-safe Singleton using Double-Checked Locking.
 * The 'volatile' keyword is critical here to ensure that multiple threads 
 * handle the instance variable correctly when it is being initialized.
 */
public class Singleton {
    private static volatile Singleton instance;
    private static final Object lock = new Object();

    private Singleton() {
        // Private constructor to prevent instantiation from other classes
    }

    public static Singleton getInstance() {
        // First check: avoid synchronization overhead if instance is already initialized
        if (instance == null) {
            synchronized (lock) {
                // Second check: verify no other thread initialized it while waiting for lock
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
"""

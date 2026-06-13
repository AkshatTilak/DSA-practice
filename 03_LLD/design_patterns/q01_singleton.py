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

# --- APPROACH 1: Naive (Locked call without check) ---
# Time Complexity: O(1) on creation, but incurs Lock overhead on EVERY call.
# Space Complexity: O(1)
class SingletonMetaNaive(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Naive: Acquire lock for every instantiation request (bottleneck)
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]


# --- APPROACH 2: Optimal Thread-Safe Double-Checked Locking ---
# Time Complexity: O(1) creation, O(1) retrieval with NO lock overhead after creation.
# Space Complexity: O(1)
class SingletonMetaOptimal(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Check 1: If instance already exists, return immediately without locking
        if cls not in cls._instances:
            # Check 2: Lock only when creating the instance
            with cls._lock:
                # Double check inside the lock
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# --- APPROACH 3: Secondary Language (Java Double-Checked Locking) ---
"""
package design_patterns;

public class DatabaseConnectionPool {
    private static volatile DatabaseConnectionPool instance;
    private static final Object lock = new Object();
    
    private String connectionString;

    private DatabaseConnectionPool() {
        this.connectionString = "jdbc:postgresql://localhost:5432/db";
    }

    public static DatabaseConnectionPool getInstance() {
        // Double-Checked Locking
        if (instance == null) {
            synchronized (lock) {
                if (instance == null) {
                    instance = new DatabaseConnectionPool();
                }
            }
        }
        return instance;
    }
}
"""

"""
Challenge: q01_parking_lot
Difficulty: Hard
Link: https://www.geeksforgeeks.org/design-parking-lot-low-level-design/

Problem:
Design object models for multi-level parking lot including spot size constraints, ticket calculations.
"""

# --- STARTER TEMPLATE FOR USER ---
class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type):
        self.id = id
        self.spot_type = spot_type
        self.is_free = True

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(L * S) where L is the number of levels and S is the number of spots per level.
# Space Complexity: O(L * S) to store the parking lot layout.
# This approach uses simple linear search to find the first available parking spot that satisfies the size constraint.
# It lacks thread safety and efficient lookup, making it unsuitable for high-concurrency environments.

import time
import math

class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type):
        self.id = id
        self.spot_type = spot_type
        self.is_free = True
        self.vehicle = None

class Vehicle:
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type # Should match SpotType

class Ticket:
    def __init__(self, vehicle, spot):
        self.vehicle = vehicle
        self.spot = spot
        self.start_time = time.time()

class ParkingLotNaive:
    def __init__(self, levels, spots_per_level):
        self.levels = []
        for l in range(levels):
            level_spots = []
            for s in range(spots_per_level):
                # Distribute spot types evenly for simplicity in naive approach
                stype = SpotType.SMALL if s % 3 == 0 else (SpotType.COMPACT if s % 3 == 1 else SpotType.LARGE)
                level_spots.append(ParkingSpot(f"{l}-{s}", stype))
            self.levels.append(level_spots)

    def park_vehicle(self, vehicle):
        # Linear search through levels and spots
        for level in self.levels:
            for spot in level:
                if spot.is_free and spot.spot_type >= vehicle.vehicle_type:
                    spot.is_free = False
                    spot.vehicle = vehicle
                    return Ticket(vehicle, spot)
        return None

    def unpark_vehicle(self, ticket):
        spot = ticket.spot
        duration = time.time() - ticket.start_time
        spot.is_free = True
        spot.vehicle = None
        # Naive pricing: $2 per hour
        cost = math.ceil(duration / 3600) * 2
        return cost

# --- APPROACH 2: Optimal (Priority Queues & Strategy Pattern) ---
# Time Complexity: 
#   - park_vehicle: O(log S) to extract the best spot from the PriorityQueue.
#   - unpark_vehicle: O(log S) to push the spot back into the PriorityQueue.
#   - calculate_cost: O(1).
# Space Complexity: O(L * S) to store all spots in the priority queues.
# This approach is optimal because it uses Min-Heaps (PriorityQueues) to ensure the nearest available spot is always selected.
# It employs a Strategy Pattern for flexible pricing based on vehicle type and uses a Thread Lock to ensure 
# atomicity in a multi-threaded environment, making it production-ready.

import heapq
import time
import math
from threading import Lock
from abc import ABC, abstractmethod

class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type, level_id):
        self.id = id
        self.spot_type = spot_type
        self.level_id = level_id
        self.is_free = True

    # Define comparison for PriorityQueue to prioritize lower level, then lower spot id
    def __lt__(self, other):
        if self.level_id != other.level_id:
            return self.level_id < other.level_id
        return self.id < other.id

class Vehicle:
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type # 1: Small, 2: Compact, 3: Large

class Ticket:
    def __init__(self, vehicle, spot):
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = time.time()

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, duration_hours, vehicle_type):
        pass

class StandardPricingStrategy(PricingStrategy):
    def __init__(self):
        self.rates = {SpotType.SMALL: 1.0, SpotType.COMPACT: 2.0, SpotType.LARGE: 5.0}

    def calculate_cost(self, duration_hours, vehicle_type):
        rate = self.rates.get(vehicle_type, 2.0)
        return math.ceil(duration_hours) * rate

class ParkingLotOptimal:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ParkingLotOptimal, cls).__new__(cls)
        return cls._instance

    def __init__(self, config=None):
        # Prevent re-initialization in singleton
        if hasattr(self, 'initialized'): return
        self.initialized = True
        self.lock = Lock()
        self.pricing_strategy = StandardPricingStrategy()
        
        # available_spots maps SpotType -> MinHeap of ParkingSpots
        self.available_spots = {
            SpotType.SMALL: [],
            SpotType.COMPACT: [],
            SpotType.LARGE: []
        }
        
        if config:
            self._setup_parking_lot(config)

    def _setup_parking_lot(self, config):
        # config: list of levels, where each level is a list of (spot_id, spot_type)
        for level_id, spots in enumerate(config):
            for spot_id, spot_type in spots:
                spot = ParkingSpot(spot_id, spot_type, level_id)
                heapq.heappush(self.available_spots[spot_type], spot)

    def park_vehicle(self, vehicle):
        with self.lock:
            # A vehicle can park in a spot of its size or any larger spot
            # Order: Small -> Compact -> Large
            for size in range(vehicle.vehicle_type, SpotType.LARGE + 1):
                if self.available_spots[size]:
                    spot = heapq.heappop(self.available_spots[size])
                    spot.is_free = False
                    return Ticket(vehicle, spot)
            return None # No available spot

    def unpark_vehicle(self, ticket):
        with self.lock:
            spot = ticket.spot
            spot.is_free = True
            heapq.heappush(self.available_spots[spot.spot_type], spot)
            
            duration_seconds = time.time() - ticket.entry_time
            duration_hours = duration_seconds / 3600
            return self.pricing_strategy.calculate_cost(duration_hours, ticket.vehicle.vehicle_type)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package case_studies;

import java.util.*;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.concurrent.locks.ReentrantLock;
import java.time.Duration;
import java.time.Instant;

enum SpotType {
    SMALL(1), COMPACT(2), LARGE(3);
    final int value;
    SpotType(int value) { this.value = value; }
}

class ParkingSpot implements Comparable<ParkingSpot> {
    String id;
    SpotType type;
    int level;

    public ParkingSpot(String id, SpotType type, int level) {
        this.id = id;
        this.type = type;
        this.level = level;
    }

    @Override
    public int compareTo(ParkingSpot other) {
        if (this.level != other.level) {
            return Integer.compare(this.level, other.level);
        }
        return this.id.compareTo(other.id);
    }
}

class Vehicle {
    String licensePlate;
    SpotType type;

    public Vehicle(String licensePlate, SpotType type) {
        this.licensePlate = licensePlate;
        this.type = type;
    }
}

class Ticket {
    Vehicle vehicle;
    ParkingSpot spot;
    Instant entryTime;

    public Ticket(Vehicle vehicle, ParkingSpot spot) {
        this.vehicle = vehicle;
        this.spot = spot;
        this.entryTime = Instant.now();
    }
}

interface PricingStrategy {
    double calculateCost(long hours, SpotType type);
}

class StandardPricing implements PricingStrategy {
    private final Map<SpotType, Double> rates = new EnumMap<>(SpotType.class);

    public StandardPricing() {
        rates.put(SpotType.SMALL, 1.0);
        rates.put(SpotType.COMPACT, 2.0);
        rates.put(SpotType.LARGE, 5.0);
    }

    @Override
    public double calculateCost(long hours, SpotType type) {
        return hours * rates.getOrDefault(type, 2.0);
    }
}

public class ParkingLot {
    private static ParkingLot instance;
    private final ReentrantLock lock = new ReentrantLock();
    private final Map<SpotType, PriorityQueue<ParkingSpot>> availableSpots;
    private final PricingStrategy pricingStrategy;

    private ParkingLot() {
        availableSpots = new EnumMap<>(SpotType.class);
        for (SpotType type : SpotType.values()) {
            availableSpots.put(type, new PriorityQueue<>());
        }
        this.pricingStrategy = new StandardPricing();
    }

    public static synchronized ParkingLot getInstance() {
        if (instance == null) {
            instance = new ParkingLot();
        }
        return instance;
    }

    public void addSpot(String id, SpotType type, int level) {
        lock.lock();
        try {
            availableSpots.get(type).add(new ParkingSpot(id, type, level));
        } finally {
            lock.unlock();
        }
    }

    public Ticket parkVehicle(Vehicle vehicle) {
        lock.lock();
        try {
            // Try searching for spot from vehicle's size upwards
            for (SpotType type : SpotType.values()) {
                if (type.value >= vehicle.type.value && !availableSpots.get(type).isEmpty()) {
                    ParkingSpot spot = availableSpots.get(type).poll();
                    return new Ticket(vehicle, spot);
                }
            }
            return null;
        } finally {
            lock.unlock();
        }
    }

    public double unparkVehicle(Ticket ticket) {
        lock.lock();
        try {
            ParkingSpot spot = ticket.spot;
            availableSpots.get(spot.type).add(spot);
            
            long hours = Duration.between(ticket.entryTime, Instant.now()).toHours();
            if (hours == 0) hours = 1; // Minimum 1 hour charge
            
            return pricingStrategy.calculateCost(hours, ticket.vehicle.type);
        } finally {
            lock.unlock();
        }
    }
}
"""

"""
Challenge: q01_consistent_hashing
Difficulty: Hard
Link: https://www.systemdesignprimer.com/consistent-hashing

Problem:
Implement consistent hashing ring with virtual nodes configuration.
"""

# --- STARTER TEMPLATE FOR USER ---
import hashlib

class ConsistentHashRing:
    def __init__(self, replicas=3):
        self.replicas = replicas
        self.ring = {} # hash -> node
        self.sorted_keys = []

    def add_node(self, node: str) -> None:
        pass
    def remove_node(self, node: str) -> None:
        pass
    def get_node(self, key: str) -> str:
        pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: 
#   add_node: O(R * log(R*N)) - where R is replicas and N is number of nodes (due to sorting).
#   remove_node: O(R * N) - searching and removing elements from the ring.
#   get_node: O(R*N) - linear search through the sorted keys to find the successor.
# Space Complexity: O(R * N) - to store the hash ring and mapping.
# [Short explanation]
# This approach implements the ring using a simple list of sorted keys. The `get_node` method 
# performs a linear scan to find the first node with a hash greater than or equal to the 
# request's hash, which is inefficient for large rings.

import hashlib

class ConsistentHashRing_naive:
    def __init__(self, replicas=3):
        self.replicas = replicas
        self.ring = {} # hash -> node
        self.sorted_keys = []

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        for i in range(self.replicas):
            virtual_node_name = f"{node}:{i}"
            h = self._hash(virtual_node_name)
            self.ring[h] = node
            self.sorted_keys.append(h)
        self.sorted_keys.sort()

    def remove_node(self, node: str) -> None:
        for i in range(self.replicas):
            virtual_node_name = f"{node}:{i}"
            h = self._hash(virtual_node_name)
            if h in self.ring:
                del self.ring[h]
                self.sorted_keys.remove(h)

    def get_node(self, key: str) -> str:
        if not self.ring:
            return None
        
        key_hash = self._hash(key)
        # Naive linear search for the successor
        for h in self.sorted_keys:
            if h >= key_hash:
                return self.ring[h]
        
        # Wrap around to the first node
        return self.ring[self.sorted_keys[0]]

# --- APPROACH 2: Optimal (Binary Search / Bisect) ---
# Time Complexity:
#   add_node: O(R * R * N) - Using insort takes O(R*N) per replica.
#   remove_node: O(R * R * N) - Finding and popping from a list takes O(R*N).
#   get_node: O(log(R * N)) - Binary search (bisect_right) to find the successor.
# Space Complexity: O(R * N) - to store the hash ring and mapping.
# [Short explanation]
# The optimal approach uses the `bisect` module to perform binary search on the sorted 
# ring keys. This reduces the lookup time from linear to logarithmic, which is critical 
# for high-throughput distributed systems. We also maintain a mapping of physical nodes 
# to their virtual hashes to make removals more targeted.

import hashlib
import bisect

class ConsistentHashRing_optimal:
    def __init__(self, replicas=3):
        self.replicas = replicas
        self.ring = {} # hash -> node
        self.sorted_keys = []
        self.node_hashes = {} # node -> list of hashes

    def _hash(self, key: str) -> int:
        # Using SHA-256 for better distribution and fewer collisions
        return int(hashlib.sha256(key.encode()).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        if node in self.node_hashes:
            return
        
        hashes = []
        for i in range(self.replicas):
            virtual_node_name = f"{node}:{i}"
            h = self._hash(virtual_node_name)
            self.ring[h] = node
            bisect.insort(self.sorted_keys, h)
            hashes.append(h)
        self.node_hashes[node] = hashes

    def remove_node(self, node: str) -> None:
        if node not in self.node_hashes:
            return
        
        for h in self.node_hashes[node]:
            # Use bisect_left to find the index of the hash in O(log N)
            idx = bisect.bisect_left(self.sorted_keys, h)
            if idx < len(self.sorted_keys) and self.sorted_keys[idx] == h:
                self.sorted_keys.pop(idx)
            del self.ring[h]
        
        del self.node_hashes[node]

    def get_node(self, key: str) -> str:
        if not self.ring:
            return None
        
        key_hash = self._hash(key)
        # Binary search for the first hash >= key_hash
        idx = bisect.bisect_right(self.sorted_keys, key_hash)
        
        # If idx is at the end, wrap around to the first node
        if idx == len(self.sorted_keys):
            idx = 0
            
        return self.ring[self.sorted_keys[idx]]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package system_components;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.TreeMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

public class ConsistentHashing {
    private final int replicas;
    private final TreeMap<Long, String> ring = new TreeMap<>();
    private final Map<String, List<Long>> nodeHashes = new HashMap<>();

    public ConsistentHashing(int replicas) {
        this.replicas = replicas;
    }

    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(key.getBytes());
            // Use first 8 bytes to create a long for the ring key
            long res = 0;
            for (int i = 0; i < 8; i++) {
                res = (res << 8) | (digest[i] & 0xFF);
            }
            return res;
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public void addNode(String node) {
        if (nodeHashes.containsKey(node)) return;
        
        List<Long> hashes = new ArrayList<>();
        for (int i = 0; i < replicas; i++) {
            long h = hash(node + ":" + i);
            ring.put(h, node);
            hashes.add(h);
        }
        nodeHashes.put(node, hashes);
    }

    public void removeNode(String node) {
        if (!nodeHashes.containsKey(node)) return;
        
        for (Long h : nodeHashes.get(node)) {
            ring.remove(h);
        }
        nodeHashes.remove(node);
    }

    public String getNode(String key) {
        if (ring.isEmpty()) return null;
        
        long keyHash = hash(key);
        // ceilingEntry returns the least key greater than or equal to the given key
        Map.Entry<Long, String> entry = ring.ceilingEntry(keyHash);
        
        if (entry == null) {
            // Wrap around: return the first entry in the map
            return ring.firstEntry().getValue();
        }
        return entry.getValue();
    }

    public static void main(String[] args) {
        ConsistentHashing ch = new ConsistentHashing(3);
        ch.addNode("NodeA");
        ch.addNode("NodeB");
        System.out.println("Key1 -> " + ch.getNode("Key1"));
        System.out.println("Key2 -> " + ch.getNode("Key2"));
        ch.removeNode("NodeA");
        System.out.println("Key1 after remove -> " + ch.getNode("Key1"));
    }
}
"""

INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.systemdesignprimer.com/consistent-hashing',
    'description': 'Implement consistent hashing ring with virtual nodes configuration.',
    'groups': ['Distributed Systems', 'Hashing'],
    'starter_code': """import hashlib

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
        pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_hashing():
    pass""",
    'readme_content': """# Consistent Hashing HLD

Consistent hashing is a specialized hashing technique used in distributed systems to distribute data across a cluster of nodes in a way that minimizes reorganization when nodes are added or removed. Unlike traditional modulo hashing, where adding a node forces nearly every key to be remapped, consistent hashing ensures that only $K/n$ keys need to be moved on average (where $K$ is the number of keys and $n$ is the number of nodes).

---

## 1. Overview & System Requirements

### Functional Requirements
- **Key Mapping**: Map a unique key (e.g., a User ID or Request ID) to a specific server node.
- **Dynamic Scaling**: Support the addition of new nodes (scaling up) and removal of nodes (scaling down/failure) without causing a massive "cache storm" or data migration wave.
- **Load Balancing**: Ensure that data is distributed uniformly across all available nodes to prevent "hotspots."

### Non-Functional Requirements
- **Low Latency**: The lookup time for a node given a key must be extremely fast (sub-millisecond).
- **High Availability**: The system must function correctly even as the membership of the node cluster changes.
- **Scalability**: Support thousands of physical nodes and millions of keys.

### Scale Assumptions
- **QPS**: High read/write volume (e.g., 100k+ requests per second in a distributed cache like Memcached or Redis).
- **Node Churn**: Nodes may enter or leave the cluster frequently due to autoscaling or hardware failure.

---

## 2. High-Level System Architecture

The architecture revolves around a **Hash Ring**. Instead of mapping keys directly to a fixed number of slots, we map both the **servers** and the **data keys** onto a conceptual circle (the ring).

### The Ring Concept
1. **The Range**: The hash function produces a value in a fixed range (e.g., $0$ to $2^{32}-1$). This range is wrapped around to form a circle.
2. **Node Placement**: Each server node is hashed and placed at a specific position on this ring.
3. **Key Placement**: Each data key is hashed and placed on the same ring.
4. **Assignment**: To find which node owns a key, we move **clockwise** from the key's position on the ring until we encounter the first server node.

### Component Diagram (Conceptual)
`[Client Request]` $\rightarrow$ `[Consistent Hash Ring]` $\rightarrow$ `[Target Node]`
- **Hash Function**: (e.g., MD5 or SHA-256) Converts strings to a large integer space.
- **Sorted Key List**: Maintains the clockwise order of nodes for binary search.
- **Virtual Nodes (Vnodes)**: Maps one physical node to multiple positions on the ring to ensure uniformity.

---

## 3. Key HLD Concepts & Component Design

### The Problem with Basic Consistent Hashing
In a basic implementation, if you have only 3 nodes, they might be placed unevenly on the ring. This leads to **unbalanced partitions**, where one node is responsible for 70% of the ring while others handle 15% each.

### Solution: Virtual Nodes (Vnodes)
Virtual nodes solve the distribution problem. Instead of placing a physical node $P_1$ once, we place it $R$ times (where $R$ is the number of replicas).
- $P_1 \rightarrow \text{hash}(P_1\text{\_}0), \text{hash}(P_1\text{\_}1), \dots, \text{hash}(P_1\text{\_}R-1)$
- This spreads the physical node's presence across the ring.
- If $P_1$ fails, its load is distributed across multiple other nodes rather than falling entirely on one single neighbor.

### Technology Choices
- **Hash Function**: `MD5` or `SHA-1` are preferred over Python's built-in `hash()` because they are deterministic across different process restarts and provide a more uniform distribution.
- **Search Structure**: A sorted list (or a Red-Black Tree) is used to store the positions of the nodes. This allows the use of **Binary Search** to find the successor node in $O(\log N)$ time.

---

## 4. Data Flows & Implementation

### Step-by-Step Walkthrough: `get_node(key)`
1. **Hash the Key**: The input key (e.g., `"user_123"`) is hashed to a value $H_{key}$.
2. **Binary Search**: The system searches the sorted list of all virtual node hashes to find the first hash $H_{node}$ such that $H_{node} \ge H_{key}$.
3. **Wrap Around**: If $H_{key}$ is greater than the largest hash in the ring, it "wraps around" to the first node in the sorted list (the 0th index).
4. **Return Physical Node**: The virtual node hash maps back to the original physical node ID.

### Implementation

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, replicas=3):
        \"\"\"
        Initialize the consistent hash ring.
        :param replicas: Number of virtual nodes per physical node.
        \"\"\"
        self.replicas = replicas
        self.ring = {}           # Maps hash -> physical_node_name
        self.sorted_keys = []    # Sorted list of all hashes in the ring

    def _hash(self, key: str) -> int:
        \"\"\"Helper to generate a consistent integer hash using MD5.\"\"\"
        # MD5 provides a 128-bit hash; we convert it to an integer.
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: str) -> None:
        \"\"\"Adds a physical node and its virtual replicas to the ring.\"\"\"
        for i in range(self.replicas):
            # Create a unique string for each virtual node (e.g., "node1_0", "node1_1")
            vnode_key = f"{node}_{i}"
            vnode_hash = self._hash(vnode_key)
            
            self.ring[vnode_hash] = node
            bisect.insort(self.sorted_keys, vnode_hash)

    def remove_node(self, node: str) -> None:
        \"\"\"Removes a physical node and all its virtual replicas from the ring.\"\"\"
        for i in range(self.replicas):
            vnode_key = f"{node}_{i}"
            vnode_hash = self._hash(vnode_key)
            
            if vnode_hash in self.ring:
                del self.ring[vnode_hash]
                # Binary search to find and remove the hash from the sorted list
                idx = bisect.bisect_left(self.sorted_keys, vnode_hash)
                if idx < len(self.sorted_keys) and self.sorted_keys[idx] == vnode_hash:
                    self.sorted_keys.pop(idx)

    def get_node(self, key: str) -> str:
        \"\"\"Returns the physical node responsible for the given key.\"\"\"
        if not self.ring:
            return None
        
        key_hash = self._hash(key)
        
        # Find the first node hash >= key_hash (Clockwise search)
        idx = bisect.bisect_right(self.sorted_keys, key_hash)
        
        # If idx == len, we wrap around to the first node (index 0)
        if idx == len(self.sorted_keys):
            idx = 0
            
        return self.ring[self.sorted_keys[idx]]
```

---

## 5. Complexity Analysis

Let $N$ be the number of physical nodes and $R$ be the number of replicas (virtual nodes).

| Operation | Time Complexity | Space Complexity | Reason |
| :--- | :--- | :--- | :--- |
| `add_node` | $O(R \cdot N)$ | $O(R \cdot N)$ | Inserting $R$ items into a sorted list of size $R \cdot N$ takes $O(N \cdot R)$ due to list shifts. |
| `remove_node`| $O(R \cdot N)$ | $O(1)$ | Removing $R$ items from a sorted list takes $O(N \cdot R)$. |
| `get_node` | $O(\log(R \cdot N))$ | $O(1)$ | Binary search (`bisect_right`) on the sorted hash list. |

*Note: If a balanced BST or SkipList were used instead of a Python list, `add_node` and `remove_node` would improve to $O(R \log(RN))$.*

---

## 6. Production Trade-offs & Considerations

### CAP Theorem Perspective
Consistent Hashing is primarily used to achieve **Availability** and **Partition Tolerance (AP)**. In a distributed cache, we accept that during a node addition, some keys will temporarily map to the "wrong" node (resulting in a cache miss), but the system remains available and doesn't crash.

### Trade-off: $R$ (Replicas) vs. Memory
- **Low $R$**: Lower memory overhead, faster node addition/removal, but higher risk of **unbalanced load** (some nodes getting way more traffic).
- **High $R$**: Better distribution (more uniform), but higher memory usage and slower updates to the ring.

### Fault Tolerance
- **Replication**: In a real-world system (like DynamoDB or Cassandra), the key isn't just stored on the *first* node encountered clockwise, but on the *first $N$ nodes* encountered clockwise. This ensures that if the primary node crashes, the data is already present on the next few nodes in the ring.
- **Gossip Protocol**: To keep the ring state synchronized across all clients in a decentralized system, nodes often use a Gossip Protocol to share their membership status.""",
}

# Arrays & Hashing

Arrays and Hash Maps form the foundation of efficient data retrieval. An array stores elements sequentially, allowing $O(1)$ index access but $O(N)$ searches. A Hash Map (or Dictionary) uses a hash function to map keys to values, achieving average $O(1)$ search, insertion, and deletion times.

---

## 🗺️ ASCII Execution Flow: Two Sum

Here is a visual execution mapping of the **Two Sum** problem, searching for a `target = 9` within the array `[2, 7, 11, 15]`:

```text
[Input Array]  ──>  [ 2,  7, 11, 15 ]
                     ▲   ▲
                     │   │
                     │   └─ Complement (9 - 7 = 2) ── Found in Map! ──> [Success: Return indices [0, 1]]
                     │
                     └─ Current element = 2, Complement = 7
                        Store in Map: { 2: 0 }

[Hash Map State Progression]
Iteration 0 (num = 2):
  - Complement = 9 - 2 = 7 (Not in map)
  - Map Update ──> { 2: 0 }

Iteration 1 (num = 7):
  - Complement = 9 - 7 = 2 (Found in map at index 0!)
  - Output ──> [0, 1]
```

---

## 🏢 Real-World Production Use-Case

### Uber: Real-time Driver-to-Passenger Dispatch
When a passenger requests a ride, Uber's dispatch system must match the passenger with nearby drivers.
1. The driver locations are indexed geographically using space-filling curves (like H3 or S2 geohashes).
2. The active driver locations are stored in-memory using **Hash Maps** where the keys are geohash grids and the values are lists of driver IDs currently active in that grid.
3. Using a hash lookup, the dispatch service accesses the target grid in $O(1)$ average time, filtering available drivers dynamically without scanning the entire global driver list.

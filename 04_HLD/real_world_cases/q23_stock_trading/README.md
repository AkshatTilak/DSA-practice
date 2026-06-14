# Stock Trading Platform HLD

Designing a Stock Trading Platform (or Exchange) is one of the most challenging HLD problems because it demands a rare combination of **ultra-low latency**, **strict linearizability (consistency)**, and **massive throughput**. Unlike a social media feed where eventual consistency is acceptable, a trading engine must be deterministic: if User A places a buy order before User B, User A must get the stock.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Order Placement**: Users can place **Limit Orders** (buy/sell at a specific price) and **Market Orders** (buy/sell at the current best available price).
*   **Order Cancellation**: Users can cancel pending orders before they are filled.
*   **Order Matching**: An automated engine that matches buy and sell orders based on **Price-Time Priority**.
*   **Portfolio Management**: Real-time tracking of user holdings and cash balances.
*   **Market Data Feed**: Real-time streaming of the "Order Book" (L2 data) and "Ticker" (L1 data) to users via WebSockets.
*   **Trade Execution/Settlement**: Ensuring that once a match occurs, ownership of assets and cash is transferred atomically.

### Non-Functional Requirements
*   **Ultra-Low Latency**: The matching process must happen in microseconds ($\mu s$) to milliseconds ($ms$).
*   **Strict Consistency**: No "double spending" of cash or "ghost" shares. The system must be ACID compliant regarding trade execution.
*   **High Determinism**: Given the same set of inputs in the same order, the system must produce the exact same state.
*   **High Availability**: The exchange cannot go down during trading hours.
*   **Durability**: Every order and trade must be persisted to a journal for audit and recovery.

### Scale Assumptions
| Metric | Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | 10 Million |
| **Peak Order Volume** | 1 Million orders per second (Ops/sec) |
| **Matching Latency** | $< 1 \text{ms}$ (P99) |
| **Data Retention** | 7+ years (Regulatory requirement) |

---

## 2. High-Level System Architecture

The architecture is split into the **Trading Path** (Hot Path) and the **Management Path** (Cold Path).

### Architecture Diagram Concept
`Client` $\rightarrow$ `API Gateway` $\rightarrow$ `Order Gateway` $\rightarrow$ `Sequencer` $\rightarrow$ `Matching Engine` $\rightarrow$ `Trade Publisher` $\rightarrow$ `Portfolio/Settlement`

### Component Roles
1.  **API Gateway**: Handles authentication, rate limiting, and request routing.
2.  **Order Gateway**: Validates the order (e.g., does the user have enough funds/shares?). It converts the request into a standardized internal "Order Event."
3.  **Sequencer**: This is the most critical component for determinism. It assigns a **global sequence number** to every incoming order. This ensures that the Matching Engine processes orders in a strict, linear order.
4.  **Matching Engine**: The "brain" of the exchange. It maintains an in-memory **Order Book** and matches buy/sell orders. It is typically single-threaded per symbol to avoid locking overhead.
5.  **Trade Publisher**: An event bus (e.g., Kafka) that broadcasts executed trades to other services.
6.  **Portfolio/Settlement Service**: Updates user balances and holdings asynchronously after a trade is matched.
7.  **Market Data Service**: Aggregates trades and order book changes to push updates to clients via WebSockets.

---

## 3. Key HLD Concepts & Component Design

### A. The Order Book Design
The Order Book maintains two sets of orders for every stock symbol:
*   **Buy Side (Bids)**: Sorted by price (descending), then by time (ascending).
*   **Sell Side (Asks)**: Sorted by price (ascending), then by time (ascending).

**Data Structure Choice**:
*   **Bids**: `TreeMap<Price, LinkedList<Order>>` or a **Max-Heap**.
*   **Asks**: `TreeMap<Price, LinkedList<Order>>` or a **Min-Heap**.
*   A `HashMap<OrderID, Order>` is used for $O(1)$ lookup during order cancellations.

### B. The LMAX Disruptor Pattern (Matching Engine Concurrency)
Traditional locking (Mutex/Synchronized) is too slow for high-frequency trading due to context switching and cache misses.
*   **The Strategy**: Use a **Single-Threaded Execution Model** for the Matching Engine.
*   **How it works**: The Sequencer pushes orders into a **Ring Buffer** (LMAX Disruptor). A single thread reads from this buffer and updates the Order Book.
*   **Why?**: This eliminates lock contention and maximizes CPU cache efficiency. Since a single symbol's book is handled by one thread, we achieve absolute determinism.

### C. Persistence & Event Sourcing
We cannot use a traditional SQL `UPDATE` for every match; it's too slow.
*   **Journaling**: Every sequenced order is written to a high-speed sequential append-only log (AOF - Append Only File) before it hits the Matching Engine.
*   **Snapshotting**: Periodically, the engine saves the entire state of the Order Book to disk.
*   **Recovery**: If the engine crashes, it loads the last snapshot and replays the journal from that point forward to reconstruct the state.

### D. Technology Stack Selection
| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Matching Engine** | C++ / Java (Low GC) | Maximum performance, memory control. |
| **Inter-service Comm** | gRPC / Aeron | Low latency, binary serialization. |
| **Event Streaming** | Kafka | High throughput, durable audit log. |
| **User Data** | PostgreSQL | ACID compliance for account balances. |
| **Market Data Cache** | Redis | Low latency read for current price/ticker. |

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Order Flow (Limit Buy Order)
1.  **Submission**: User sends `Buy 10 AAPL @ $150` $\rightarrow$ **API Gateway**.
2.  **Validation**: **Order Gateway** checks if User has $\ge \$1500$. It "locks" the funds in the Portfolio service.
3.  **Sequencing**: **Sequencer** assigns `SeqID: 1001` and persists it to the **Journal**.
4.  **Matching**: **Matching Engine** picks up `SeqID: 1001`. It checks the **Ask Side** of the AAPL Order Book.
    *   *If Match Found*: Generates a `TradeEvent`.
    *   *If No Match*: Adds the order to the **Bid Side** (Max-Heap).
5.  **Broadcast**: **Trade Publisher** sends `TradeEvent` to Kafka.
6.  **Settlement**: **Portfolio Service** consumes the event, moves 10 AAPL from Seller to Buyer and $\$1500$ from Buyer to Seller.
7.  **Market Data**: **Market Data Service** updates the current price of AAPL to $\$150$ and pushes to all subscribed clients.

### Handling Failures
*   **Matching Engine Crash**: A **Hot Standby** (Secondary) engine consumes the same sequenced stream from the Journal. If the Primary fails, the Secondary takes over immediately.
*   **Sequencer Failure**: Use **Raft or Paxos** consensus to elect a leader sequencer to ensure no gaps or duplicates in sequence numbers.
*   **Network Partition**: The system prioritizes **Consistency** over **Availability** (CP in CAP). It is better to stop trading for a few seconds than to execute a trade twice or at the wrong price.

---

## 5. Production Trade-offs

### Consistency vs. Latency (The Great Divide)
In most systems, we use asynchronous writes to increase speed. In an exchange, we use **Synchronous Journaling**. We cannot acknowledge an order to the user until the Sequencer has persisted it to disk. This adds a few milliseconds of latency but prevents the "lost order" problem.

### Memory vs. Disk
To achieve $\mu s$ latency, the entire active Order Book must reside in **RAM**. This limits the number of symbols a single matching engine instance can handle. To scale, we **shard by Symbol** (e.g., Engine 1 handles AAPL and MSFT, Engine 2 handles TSLA and GOOG).

### Complexity Analysis
| Operation | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| **Place Order (Matching)** | $O(1)$ to $O(\log N)$ | $O(N)$ where $N$ is open orders |
| **Cancel Order** | $O(1)$ with HashMap | $O(1)$ |
| **Order Book Update** | $O(\log N)$ | $O(N)$ |
| **Recovery from Log** | $O(J)$ where $J$ is journal size | $O(N)$ |

### Summary Checklist for Interview
- [x] **Price-Time Priority** (Max-Heap/Min-Heap).
- [x] **Determinism** (Sequencer $\rightarrow$ Single-threaded engine).
- [x] **LMAX Disruptor** (Ring Buffer for low latency).
- [x] **Event Sourcing** (Journaling + Snapshotting).
- [x] **Sharding by Symbol** (Horizontal scalability).
- [x] **ACID for Settlement** (Portfolio management).
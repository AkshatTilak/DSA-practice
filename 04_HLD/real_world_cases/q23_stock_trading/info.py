INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Stock Trading Platform / Exchange.',
    'groups': ['Real-World Systems', 'Concurrency'],
    'readme_content': """# Stock Trading Platform HLD

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
- [x] **ACID for Settlement** (Portfolio management).""",
    'solutions': """# System Design: High-Frequency Stock Trading Platform

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Order Management:** Users must be able to place, modify, and cancel buy/sell orders (Market and Limit orders).
*   **Matching Engine:** A core engine that matches buy and sell orders based on price-time priority.
*   **Portfolio & Ledger:** Real-time tracking of user balances (cash) and holdings (shares).
*   **Market Data Feed:** Real-time broadcasting of the "Ticker" (last traded price) and the "Order Book" (L2 data: bids and asks).
*   **Trade Execution:** Atomically update balances and holdings once a match is found.
*   **Order History:** Users must be able to view their past trades and pending orders.

### 1.2 Non-Functional Requirements
*   **Ultra-Low Latency:** The matching engine must process orders in microseconds/milliseconds to prevent slippage.
*   **Strong Consistency:** Financial transactions must be ACID compliant. No "double-spending" of cash or "ghost-selling" of shares.
*   **High Availability:** The system must be available during market hours. A failure in the matching engine must trigger a fast failover.
*   **Determinism:** Given the same sequence of orders, the matching engine must always produce the same result.
*   **Scalability:** Support millions of users and hundreds of thousands of orders per second (TPS).

### 1.3 Scale Estimations (HLD)
*   **Users:** 10 Million registered users.
*   **Active Users:** 1 Million concurrent users during peak hours.
*   **Order Volume:** 100k to 500k orders per second (TPS).
*   **Market Data Updates:** Millions of updates per second across all symbols.
*   **Storage:** Trade history grows linearly; requires petabytes of storage over years (Time-series data).

---

## 2. High-Level Architecture

The system is designed using a **Distributed Event-Driven Architecture**. To achieve ultra-low latency, the Matching Engine is decoupled from the API and Database layers and operates primarily in-memory.

### 2.1 Architecture Diagram

```mermaid
graph TD
    User((User/Client)) -->|WebSocket/REST| AGW[API Gateway]
    AGW -->|Auth/Rate Limit| OS[Order Service]
    
    subgraph "Trading Core (Low Latency Zone)"
        OS -->|Validate/Check Balance| RS[Risk & Validation Service]
        RS -->|Sequenced Order Event| SEQ[Sequencer/Order Log]
        SEQ -->|Deterministic Stream| ME[Matching Engine - In-Memory]
        ME -->|Trade Event| TES[Trade Execution Service]
    end
    
    subgraph "Persistence & Settlement"
        TES -->|Update| Ledger[(Account Ledger DB)]
        TES -->|Update| Portfolio[(Portfolio DB)]
        ME -->|Archive| OrderDB[(Order History DB)]
    end
    
    subgraph "Market Data Pipeline"
        ME -->|Price Update| MDS[Market Data Service]
        MDS -->|Pub/Sub| RedisPub[Redis Pub/Sub / Kafka]
        RedisPub -->|Push| User
    end

    SEQ -.->|WAL| Disk[(Write Ahead Log)]
```

### 2.2 Component Descriptions
1.  **API Gateway:** Handles authentication, SSL termination, and rate limiting.
2.  **Order Service:** Validates basic order syntax and forwards requests to the Risk Service.
3.  **Risk & Validation Service:** Checks if the user has enough funds (for Buy) or enough shares (for Sell) *before* the order enters the matching engine to prevent "junk" orders from clogging the engine.
4.  **Sequencer:** A critical component that assigns a global sequence number to every order. This ensures determinism across replicas.
5.  **Matching Engine (ME):** The heart of the exchange. It maintains an in-memory Order Book (Bids/Asks) for each symbol. It matches orders using a **Price-Time Priority** algorithm.
6.  **Trade Execution Service (TES):** Listens for "Match" events from the ME and performs the actual movement of assets in the Ledger and Portfolio databases.
7.  **Market Data Service:** Aggregates trades and order book changes to push real-time updates to clients via WebSockets.

---

## 3. Detailed Database Schema Design

Given the requirements, a hybrid database approach is used: **RDBMS** for financial consistency and **Time-Series/NoSQL** for market history.

### 3.1 Relational Database (PostgreSQL/CockroachDB)
Used for the Ledger and Portfolios where ACID properties are non-negotiable.

#### Table: `users`
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK | Unique identifier |
| `email` | VARCHAR | Unique | User login |
| `created_at` | TIMESTAMP | NOT NULL | Account creation date |

#### Table: `accounts` (Ledger)
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `account_id` | UUID | PK | Unique identifier |
| `user_id` | UUID | FK | Link to `users` |
| `currency` | VARCHAR(3) | NOT NULL | e.g., USD |
| `balance` | DECIMAL(20, 8) | CHECK > 0 | Current available cash |
| `version` | BIGINT | NOT NULL | Optimistic Locking version |

#### Table: `portfolios`
| Field | Type | Constraint | Note |
| :--- | :--- | :--- | :--- |
| `portfolio_id`| UUID | PK | Unique identifier |
| `user_id` | UUID | FK | Link to `users` |
| `symbol` | VARCHAR(10) | FK | e.g., AAPL, TSLA |
| `quantity` | DECIMAL(20, 8) | CHECK > 0 | Number of shares owned |

### 3.2 Order & Trade Store (Cassandra or MongoDB)
Orders are high-volume. We use a NoSQL store partitioned by `user_id` or `symbol`.

#### Table: `orders`
*   `order_id` (PK), `user_id` (Index), `symbol` (Index), `side` (BUY/SELL), `type` (LIMIT/MARKET), `price`, `quantity`, `filled_quantity`, `status` (PENDING, FILLED, CANCELLED), `timestamp`.

#### Table: `trades`
*   `trade_id` (PK), `buy_order_id`, `sell_order_id`, `symbol`, `price`, `quantity`, `timestamp`.

### 3.3 Market Data (InfluxDB / KDB+)
Time-series database used for OHLC (Open, High, Low, Close) candles and tick-by-tick historical data.

---

## 4. Core API Design

### 4.1 Order Placement
`POST /api/v1/orders`
**Request:**
```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "type": "LIMIT",
  "quantity": 10,
  "price": 150.25,
  "time_in_force": "GTC" 
}
```
**Response:** `202 Accepted`
```json
{
  "order_id": "ord_12345",
  "status": "PENDING",
  "timestamp": "2023-10-01T10:00:00Z"
}
```

### 4.2 Order Cancellation
`DELETE /api/v1/orders/{order_id}`
**Response:** `200 OK` or `400 Bad Request` (if already filled).

### 4.3 Portfolio Snapshot
`GET /api/v1/portfolio`
**Response:** `200 OK`
```json
{
  "cash_balance": 5000.00,
  "holdings": [
    {"symbol": "AAPL", "quantity": 10, "average_price": 145.00},
    {"symbol": "TSLA", "quantity": 5, "average_price": 700.00}
  ]
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 The Matching Engine: Low Latency Secrets
To handle 500k TPS, the ME cannot query a database.
*   **In-Memory Order Book:** Use two priority queues (or balanced BSTs/B-Trees) per symbol. One for Bids (Max-Heap) and one for Asks (Min-Heap).
*   **LMAX Disruptor Pattern:** Instead of using traditional locks (Mutex), use a **Ring Buffer** to pass events between the Sequencer and the ME. This eliminates lock contention and reduces cache misses.
*   **Single-Threaded Execution:** To avoid context switching and locking, assign one thread per symbol (or group of symbols). Since the state is local to the thread, it runs at CPU cache speeds.

### 5.2 Sharding Strategy
*   **Symbol-Based Sharding:** The Matching Engine is sharded by `symbol`. `AAPL` and `MSFT` may be handled by Engine Node A, while `TSLA` and `AMZN` are handled by Engine Node B.
*   **User-Based Sharding:** The Account/Ledger DB is sharded by `user_id` to distribute the load of balance updates.

### 5.3 Fault Tolerance & Recovery
*   **Event Sourcing:** The Sequencer writes every incoming order to a **Write-Ahead Log (WAL)** on disk (e.g., using Apache Kafka or a replicated journal).
*   **Snapshotting:** Periodically, the ME takes a snapshot of the Order Book and saves it to disk.
*   **Recovery:** On crash, the ME loads the last snapshot and replays the WAL from that point forward to reconstruct the exact state.

### 5.4 Market Data Distribution
*   **WebSocket Push:** Use a Pub/Sub model. The ME publishes "Trade" events $\rightarrow$ Market Data Service $\rightarrow$ Redis Pub/Sub $\rightarrow$ WebSocket Server $\rightarrow$ Client.
*   **Throttling:** Instead of pushing every single tick to every user (which would crash the browser), the Market Data Service can "conflate" updates (e.g., send a snapshot every 100ms).

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem: Consistency vs Availability
In a trading system, **Consistency (C)** and **Partition Tolerance (P)** are prioritized over Availability (A). We cannot allow a "split-brain" scenario where two different matching engines believe they have matched the same share to two different buyers. If the system cannot guarantee consistency, it must halt trading.

### 6.2 Latency vs. Durability
*   **The Conflict:** Writing to disk (Durability) is slow; keeping data in RAM (Latency) is risky.
*   **The Solution:** We use **Asynchronous Persistence** for the Order History but **Synchronous Sequencing** for the WAL. The order is acknowledged to the user only after it is persisted in the Sequencer's log, but before the Matching Engine has finished the trade.

### 6.3 Memory vs. Storage
*   **Trade-off:** Keeping all active orders in RAM is expensive.
*   **Optimization:** Only "Active" (Open) orders reside in the Matching Engine's RAM. "Filled" or "Cancelled" orders are immediately evicted from the ME and moved to the Order History DB.""",
}

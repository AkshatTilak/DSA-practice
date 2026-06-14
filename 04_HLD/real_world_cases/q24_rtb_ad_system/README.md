# Real-Time Bidding (RTB) Ad System HLD

## 1. Overview & System Requirements

A **Real-Time Bidding (RTB)** system is a complex distributed ecosystem that allows advertisers to bid on ad impressions in real-time. When a user visits a website, the site (Publisher) puts the ad slot up for auction. Multiple advertisers (via Demand-Side Platforms) bid for that slot, and the winner's ad is displayed—all within a window of **100 to 200 milliseconds**.

### Functional Requirements
- **Bid Request Handling**: The system must process incoming bid requests from an Ad Exchange.
- **Targeting & Filtering**: Match the user profile and context (device, location, site) against active ad campaigns.
- **Bidding Engine**: Calculate the optimal bid price based on the value of the user and campaign goals.
- **Auction Participation**: Submit a bid response to the exchange within the strict time limit.
- **Budget Management**: Track spending in real-time to ensure campaigns do not exceed their allocated budget (Budget Capping).
- **Tracking & Analytics**: Log impressions, clicks, and conversions for billing and ML model optimization.

### Non-Functional Requirements (SLAs)
- **Ultra-Low Latency**: The "hot path" (Bid Request $\rightarrow$ Bid Response) must typically complete in **< 100ms**.
- **Massive Scalability**: Must handle millions of Queries Per Second (QPS) during peak traffic.
- **High Availability**: Ad revenue is lost every second the system is down; target 99.99% availability.
- **Eventual Consistency**: Reporting and analytics can be eventually consistent, but budget capping must be highly accurate to prevent massive overspending.

### Scale Assumptions
| Metric | Assumption |
| :--- | :--- |
| **Daily Active Users (DAU)** | 500 Million |
| **Requests Per Second (QPS)** | 1 Million to 10 Million |
| **Average Bid Response Time** | < 50ms (internal processing) |
| **Data Volume** | Terabytes of logs generated per hour |
| **User Profiles** | Billions of records |

---

## 2. High-Level System Architecture

The system is split into two primary paths: the **Hot Path** (Request-Response) and the **Cold Path** (Data Pipeline/ML).

### Architecture Diagram Components

1.  **Ad Exchange (External)**: The marketplace that receives requests from Publishers (SSPs) and sends them to DSPs.
2.  **Bidder Service (The Hot Path)**: A stateless fleet of services that receive requests and decide whether to bid and how much.
3.  **User Profile Store**: A low-latency NoSQL store containing user demographics, interests, and historical behavior.
4.  **Campaign Manager**: A CRUD interface for advertisers to set budgets, targeting rules, and creative assets.
5.  **Budget Service**: A high-performance counter system to track spend in real-time.
6.  **Event Logger/Collector**: An ingestion layer (Kafka) that captures impressions and clicks.
7.  **Analytics & ML Pipeline**: Processes logs to calculate ROI and update bidding models.

### The Request-Response Flow
`Ad Exchange` $\rightarrow$ `Bidder Service` $\rightarrow$ `(Fetch User Profile + Check Budget)` $\rightarrow$ `Bidding Logic` $\rightarrow$ `Bid Response` $\rightarrow$ `Ad Exchange`.

---

## 3. Key HLD Concepts & Component Design

### A. The Bidder Service (Latency Optimization)
To achieve $<100\text{ms}$ latency, the Bidder Service must minimize network hops.
- **In-Memory Caching**: Local caches for campaign metadata (targeting rules) are refreshed periodically from the DB to avoid a network call per request.
- **Asynchronous I/O**: Use non-blocking frameworks (e.g., Netty, Go routines, or Node.js) to handle thousands of concurrent connections.

### B. User Profile Store (The Data Layer)
Standard relational databases cannot handle the QPS and latency required for user lookups.
- **Technology Choice**: **Aerospike** or **Redis**. 
    - *Why?* Aerospike is optimized for Flash/SSD and provides sub-millisecond lookups for billions of keys, making it the industry standard for RTB.
- **Data Model**: Key-Value store where `Key = UserID` and `Value = {Interests: [], Device: "iOS", Geo: "US", Segment: "HighValue"}`.

### C. Real-Time Budget Capping
Preventing "Overspend" is a critical challenge. If a campaign has a $\$1,000$ limit and the system has a 5-second lag in updating the budget, the system could spend thousands over the limit at 1M QPS.
- **Distributed Counters**: Use **Redis** with `DECRBY` operations.
- **Budget Sharding**: To avoid a single Redis hot-key for a popular campaign, the budget is split into "buckets" across multiple Redis nodes. The bidder randomly picks a bucket to decrement.
- **Local Budget Buffering**: The bidder fetches a "chunk" of budget (e.g., $\$10$) from the central store and manages it locally. Once the $\$10$ is spent, it requests another chunk. This reduces the pressure on the central Redis store.

### D. Bidding Logic & ML
The bid price is often determined by:
$$\text{Bid Price} = \text{Value of Impression} \times \text{Probability of Click (pCTR)} \times \text{Probability of Conversion (pCVR)}$$
- **pCTR/pCVR Models**: Pre-computed by ML pipelines (using Spark/TensorFlow) and stored as weights in the User Profile or a Feature Store.

### E. Data Pipeline (The Cold Path)
- **Kafka**: Acts as the buffer. Every "Bid Won," "Impression," and "Click" is pushed to Kafka.
- **Flink/Spark Streaming**: Aggregates these events to update the Budget Service and provide real-time dashboards.
- **Data Lake (S3/HDFS)**: Stores raw logs for long-term ML training.

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Request Walkthrough
1.  **Bid Request**: Ad Exchange sends a JSON request containing `AuctionID`, `SlotSize`, `UserAgent`, and `UserID`.
2.  **Enrichment**: The Bidder fetches the `User Profile` from **Aerospike** using the `UserID`.
3.  **Filtering**: The Bidder filters campaigns based on targeting (e.g., "Only show this ad to users in New York using Android").
4.  **Budget Check**: The Bidder checks the local budget buffer. If the budget is exhausted, it drops the request immediately.
5.  **Price Calculation**: The bidder uses the pCTR model to calculate the bid value.
6.  **Response**: The Bidder returns a response: `BidPrice`, `AdCreativeURL`, and `CampaignID`.
7.  **Closing the Loop**: If the bid wins, the Exchange sends a "Win Notice." The Bidder logs this to Kafka, which eventually decrements the global budget.

### Fault Tolerance & Resilience
- **Timeout Strategy**: If the User Profile store doesn't respond within $10\text{ms}$, the Bidder falls back to a "Generic Bid" (non-targeted) to avoid losing the opportunity.
- **Circuit Breakers**: If the Budget Service is lagging, the Bidder can switch to a "conservative bidding" mode where it bids lower amounts to mitigate overspend risk.
- **Replication**: User profiles are replicated across multiple zones to ensure that the failure of one data center doesn't stop the bidding process.

---

## 5. Production Trade-offs

### CAP Theorem: Availability vs. Consistency
In RTB, **Availability and Partition Tolerance (AP)** are prioritized over Strong Consistency.
- **Reasoning**: If the budget service is slightly inconsistent (e.g., shows $\$105$ spent instead of $\$100$), it is acceptable. However, if the budget service becomes unavailable and causes the Bidder to stop bidding, the company loses millions in potential revenue.

### Database Trade-offs
| Technology | Choice | Trade-off |
| :--- | :--- | :--- |
| **SQL (Postgres)** | Campaign Management | Strong consistency for setting budgets; too slow for the bid path. |
| **NoSQL (Aerospike)** | User Profiles | Extremely fast reads; lacks complex join capabilities. |
| **Redis** | Budget Capping | Atomic operations and speed; data is volatile (requires persistence config). |
| **Kafka** | Log Ingestion | High throughput and decoupling; introduces a slight lag in reporting. |

### Latency Budget Breakdown
To stay under the $100\text{ms}$ total limit, the internal budget is strictly allocated:
- **Network Transit (Exchange $\leftrightarrow$ DSP)**: $40\text{ms}$
- **User Profile Lookup**: $10\text{ms}$
- **Targeting & Filtering**: $10\text{ms}$
- **Bidding Logic/ML Scoring**: $20\text{ms}$
- **Budget Check**: $5\text{ms}$
- **Buffer/Overhead**: $15\text{ms}$
- **Total**: $\approx 100\text{ms}$
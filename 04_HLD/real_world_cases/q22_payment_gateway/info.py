INFO = {
    'difficulty': 'Hard',
    'type': 'design',
    'description': 'Design Payment Gateway (Stripe, Razorpay).',
    'groups': ['Real-World Systems'],
    'readme_content': """# Payment Gateway HLD

A **Payment Gateway** is a sophisticated financial middleware that authorizes and processes payments between a merchant's website/app and the financial institutions (banks, card networks). Unlike a simple API, it must guarantee **extreme reliability**, **strict consistency**, and **high security** to prevent financial loss or fraud.

---

## 1. Overview & System Requirements

### Functional Requirements
*   **Payment Processing**: Ability to accept various payment methods (Credit/Debit cards, UPI, Digital Wallets).
*   **Payment Status Tracking**: Real-time tracking of payment states (`PENDING`, `SUCCESS`, `FAILED`, `REFUNDED`).
*   **Idempotency**: Ensure that the same payment request sent multiple times results in only one charge.
*   **Merchant Payouts**: Transferring captured funds to the merchant's bank account.
*   **Refunds**: Processing full or partial reversals of transactions.
*   **Webhooks**: Notifying merchants asynchronously about payment status changes.
*   **PCI-DSS Compliance**: Ensuring sensitive card data is never stored in plain text or in unauthorized systems.

### Non-Functional Requirements
*   **Strong Consistency (ACID)**: Financial records must be 100% accurate. No "eventual consistency" for balance updates.
*   **High Availability**: The system must be available 24/7. A downtime of minutes can mean millions in lost revenue.
*   **Low Latency**: The authorization phase must be fast to prevent cart abandonment.
*   **Durability**: Once a transaction is marked as success, it must never be lost.
*   **Scalability**: Handle massive spikes during sales events (e.g., Black Friday).

### Scale Assumptions
| Metric | Value |
| :--- | :--- |
| **Daily Active Users (DAU)** | 10 Million |
| **Transactions per Day** | 100 Million |
| **Average QPS** | $\sim 1,150$ TPS |
| **Peak QPS** | $10\times$ average ($\sim 11,500$ TPS) |
| **Storage** | Transaction logs for 7+ years (Regulatory requirement) |

---

## 2. High-Level System Architecture

The architecture follows a **Microservices Approach** to decouple the payment ingestion, risk assessment, and external banking communication.

### Component Diagram Description
1.  **API Gateway**: Entry point for merchants/customers. Handles Rate Limiting, Authentication, and Routing.
2.  **Payment Service**: The orchestrator. It manages the lifecycle of a payment and coordinates between other services.
3.  **Risk & Fraud Service**: Analyzes transaction patterns to detect fraud (using ML models/rules) before sending the request to the bank.
4.  **Payment Executor/Adapter**: A translation layer that converts internal payment requests into the specific API formats required by different banks/processors (e.g., Stripe, Adyen, Braintree).
5.  **Ledger Service**: A specialized service for **Double-Entry Bookkeeping**. It records every movement of money.
6.  **Webhook Service**: Manages a queue of notifications to be sent to merchant endpoints.
7.  **Database**: A relational database (RDBMS) for transactional integrity.

---

## 3. Key HLD Concepts & Component Design

### A. Idempotency Mechanism
To prevent double-charging a customer due to network retries, we implement an **Idempotency Key** system.
*   The client generates a unique `idempotency_key` (UUID) for every transaction attempt.
*   The server stores this key in a Redis cache or DB table with a TTL (e.g., 24 hours).
*   **Workflow**:
    1.  Request arrives $\rightarrow$ Check if `idempotency_key` exists.
    2.  If **Exists**: Return the cached response of the previous attempt.
    3.  If **Not Exists**: Lock the key $\rightarrow$ Process payment $\rightarrow$ Store result $\rightarrow$ Return response.

### B. The Ledger (Double-Entry Bookkeeping)
We never use a single `balance` column that we increment/decrement. Instead, we use a **Ledger** where every transaction has at least one debit and one credit.
*   **Transaction**: "Customer pays Merchant $100"
    *   Debit: Customer Account (-$100)
    *   Credit: Gateway Escrow Account (+$100)
    *   Credit: Merchant Pending Account (+$100)
    *   Debit: Gateway Fee Account (-$2)
*   **Why?** This provides a complete audit trail and makes it mathematically impossible for money to "disappear."

### C. Database Selection
*   **Primary DB**: **PostgreSQL** or **MySQL**. 
    *   *Reason*: We need **ACID** properties. Transactions must be atomic. We use `SELECT ... FOR UPDATE` for row-level locking during balance updates.
*   **Audit Log**: **Cassandra** or **BigTable**.
    *   *Reason*: High write throughput for immutable logs of every API request/response for regulatory compliance.
*   **Cache**: **Redis**.
    *   *Reason*: Fast lookup for idempotency keys and session tokens.

### D. Security & Tokenization (PCI-DSS)
To minimize the scope of PCI compliance, we use **Tokenization**:
1.  The client sends card details directly to a **Vault Service** (highly secure, isolated).
2.  The Vault stores the card and returns a `payment_token`.
3.  The Payment Service only handles the `payment_token`, never the actual card number (PAN).

---

## 4. Data Flows & Fault Tolerance

### Step-by-Step Payment Flow
1.  **Initiation**: Customer clicks "Pay". Merchant app sends request to `Payment Service` with `idempotency_key`.
2.  **Validation**: Service checks for duplicate requests and validates the merchant's account.
3.  **Fraud Check**: `Risk Service` evaluates the transaction. If high risk, it triggers 3D-Secure (OTP).
4.  **Execution**: `Payment Executor` sends the request to the **Acquiring Bank** via an encrypted tunnel.
5.  **External Response**: The bank responds with `Authorized`, `Declined`, or `Timeout`.
6.  **Ledger Update**: Upon success, the `Ledger Service` records the movements in a single DB transaction.
7.  **Notification**: `Webhook Service` pushes the status update to the merchant.

### Handling Failures & Edge Cases
| Failure Scenario | Mitigation Strategy |
| :--- | :--- |
| **External Bank Timeout** | Use a **Query API** to poll the bank for the status of that specific transaction ID before retrying. |
| **Payment Service Crash** | Use a **State Machine** in the DB. A background "Reconciliation Worker" finds payments stuck in `PENDING` for $> 5$ mins and resolves them. |
| **Webhook Delivery Failure** | Implement **Exponential Backoff** (Retry at 1m, 5m, 30m, 2h). Use a DLQ (Dead Letter Queue) for permanent failures. |
| **Database Deadlock** | Standardize the order of row locks (e.g., always lock the smaller Account ID first). |

---

## 5. Production Trade-offs

### Consistency vs. Availability (CAP Theorem)
In a Payment Gateway, we choose **Consistency (C)** and **Partition Tolerance (P)** over Availability. 
*   If the Ledger database is unavailable, we **must stop** accepting payments. Accepting a payment without being able to record it is a catastrophic financial failure.
*   **Trade-off**: We accept slightly higher latency or occasional downtime to ensure that not a single cent is unaccounted for.

### Synchronous vs. Asynchronous Processing
*   **Synchronous**: Authorization and Fraud Check. The user needs to know immediately if their card was declined.
*   **Asynchronous**: Ledger updates, Webhooks, and Analytics. These are offloaded to **Kafka** to ensure the user-facing response time is kept low.

### Complexity Analysis
| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Payment Initiation** | $O(1)$ | $O(1)$ | Constant time API call. |
| **Idempotency Check** | $O(1)$ | $O(N)$ | Redis lookup; space scales with active transactions. |
| **Reconciliation** | $O(T)$ | $O(1)$ | $T$ = number of pending transactions to scan. |
| **Ledger Query** | $O(\log N)$ | $O(1)$ | Indexed lookup on account ID. |""",
    'solutions': """# System Design Document: Payment Gateway (Stripe, Razorpay)

## 1. Requirements & System Constraints

A Payment Gateway is a critical piece of financial infrastructure that acts as an intermediary between merchants, customers, and financial institutions (Acquiring Banks, Card Networks, and Issuing Banks).

### 1.1 Functional Requirements
*   **Payment Processing:** Support multiple payment methods (Credit/Debit Cards, UPI, Digital Wallets, NetBanking).
*   **Merchant Onboarding:** Allow merchants to register, KYC, and configure their accounts.
*   **Transaction Management:** Handle the full lifecycle of a payment (Initiated $\rightarrow$ Pending $\rightarrow$ Success/Failed $\rightarrow$ Refunded).
*   **Payouts:** Transfer funds from the gateway's escrow/holding account to the merchant's bank account.
*   **Webhooks:** Asynchronously notify merchants of payment status changes.
*   **Refunds:** Support full and partial refunds of transactions.
*   **Reporting/Dashboard:** Provide merchants with transaction history and analytics.

### 1.2 Non-Functional Requirements
*   **Strong Consistency (ACID):** Financial transactions cannot be "eventually consistent." Double-charging or missing records are unacceptable.
*   **High Availability:** The system must be available 24/7. Downtime results in immediate revenue loss for merchants.
*   **Idempotency:** Every request must be processed exactly once, regardless of network retries.
*   **Low Latency:** The checkout experience must be seamless to prevent cart abandonment.
*   **Security & Compliance:** PCI-DSS compliance is mandatory. Sensitive data (CVV, Full PAN) must never be stored in plain text or in the primary database.
*   **Auditability:** Every change in transaction state must be logged in an immutable ledger.

### 1.3 Scale Estimations (HLD)
*   **Traffic:** 10,000 Transactions Per Second (TPS) average, peaking at 50,000 TPS during sales.
*   **Storage:** Assuming 1 billion transactions/year, with each record $\sim 1$ KB, we need $\sim 1$ TB/year for the `payments` table.
*   **Read/Write Ratio:** Write-heavy during payment initiation; Read-heavy during reporting.

---

## 2. High-Level Architecture

### 2.1 Architecture Diagram
The system follows a microservices architecture to decouple the high-risk payment execution from the reporting and onboarding flows.

```mermaid
graph TD
    Customer((Customer)) -->|Payment Request| API_GW[API Gateway]
    Merchant((Merchant)) -->|API/Dashboard| API_GW
    
    API_GW --> Auth[Auth & Rate Limiter]
    Auth --> PaySvc[Payment Service]
    
    PaySvc --> RiskSvc[Risk & Fraud Engine]
    PaySvc --> TokenSvc[Vault/Tokenization Service]
    
    PaySvc --> Executor[Payment Executor]
    Executor --> BankAdapter[Bank/PSP Adapters]
    BankAdapter --> ExternalBank((External Bank/Network))
    
    PaySvc --> LedgerSvc[Ledger Service]
    LedgerSvc --> DB_SQL[(Financial DB - ACID)]
    
    Executor --> EventBus[Message Queue - Kafka]
    EventBus --> WebhookSvc[Webhook Service]
    EventBus --> AnalyticsSvc[Analytics Service]
    
    WebhookSvc --> MerchantServer((Merchant Server))
```

### 2.2 Core Components
1.  **API Gateway:** Handles authentication, SSL termination, and request routing.
2.  **Payment Service:** The orchestrator. It manages the payment state machine and coordinates between risk, tokenization, and execution.
3.  **Vault/Tokenization Service:** A highly secure, isolated service that stores sensitive card data and returns a non-sensitive `token_id`. This minimizes the PCI-DSS scope for other services.
4.  **Risk & Fraud Engine:** Evaluates transactions in real-time using rules or ML models to flag suspicious activities.
5.  **Payment Executor:** The "adapter" layer. Since every bank/PSP has a different API, this service abstracts those differences into a common internal interface.
6.  **Ledger Service:** The source of truth. It implements double-entry bookkeeping to ensure every cent is accounted for.
7.  **Webhook Service:** Reliably delivers event notifications to merchant endpoints using an exponential backoff retry strategy.

---

## 3. Detailed Database Schema Design

We use a **Relational Database (PostgreSQL)** for the core payment and ledger flows due to the requirement for ACID transactions. **NoSQL (Cassandra/ElasticSearch)** is used for logs and analytics.

### 3.1 Database Tables

#### `merchants`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `merchant_id` | UUID | PK | Unique ID for the merchant |
| `api_key` | String | Unique, Indexed | For API authentication |
| `webhook_url` | String | - | Endpoint for notifications |
| `status` | Enum | - | ACTIVE, SUSPENDED, PENDING_KYC |
| `created_at` | Timestamp | - | - |

#### `payments`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `payment_id` | UUID | PK | Unique transaction ID |
| `merchant_id` | UUID | FK, Indexed | Link to merchant |
| `amount` | Decimal(19,4)| - | Precision for currency |
| `currency` | String(3) | - | ISO currency code (e.g., USD) |
| `status` | Enum | Indexed | PENDING, SUCCESS, FAILED, REFUNDED |
| `idempotency_key`| String | Unique, Indexed | Prevents double charging |
| `payment_method_id`| UUID | FK | Link to tokenized method |
| `created_at` | Timestamp | Indexed | - |
| `updated_at` | Timestamp | - | - |

#### `payment_methods` (The Vault)
*Stored in a separate, encrypted database/vault.*
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `method_id` | UUID | PK | Token ID |
| `merchant_id` | UUID | FK | Link to merchant |
| `masked_card` | String | - | e.g., **** **** **** 1234 |
| `encrypted_data` | Blob | - | Encrypted PAN, Expiry, etc. |

#### `ledger` (Double-Entry)
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `ledger_id` | BigInt | PK | - |
| `payment_id` | UUID | FK | Link to payment |
| `account_id` | String | Indexed | e.g., "GATEWAY_ESCROW", "MERCHANT_A" |
| `debit` | Decimal(19,4)| - | Amount deducted |
| `credit` | Decimal(19,4)| - | Amount added |
| `entry_type` | Enum | - | PAYMENT, FEE, PAYOUT |
| `created_at` | Timestamp | - | - |

### 3.2 Reasoning
*   **SQL vs NoSQL:** SQL is non-negotiable for the `ledger` and `payments` tables to avoid data anomalies.
*   **Indexing:** Indices on `merchant_id` and `payment_id` are critical for dashboard queries. An index on `idempotency_key` is required for fast lookups during request deduplication.
*   **Decimal Type:** Never use `float` or `double` for money to avoid rounding errors. `Decimal(19, 4)` is the industry standard.

---

## 4. Core API Design

### 4.1 Create Payment
`POST /v1/payments`
**Headers:** `Idempotency-Key: <uuid>`, `Authorization: Bearer <token>`

**Request Payload:**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "payment_method_id": "pm_12345",
  "description": "Order #9876",
  "callback_url": "https://merchant.com/callback"
}
```
**Response (201 Created):**
```json
{
  "payment_id": "pay_abc123",
  "status": "PENDING",
  "created_at": "2023-10-27T10:00:00Z"
}
```

### 4.2 Get Payment Status
`GET /v1/payments/{payment_id}`

**Response (200 OK):**
```json
{
  "payment_id": "pay_abc123",
  "status": "SUCCESS",
  "amount": 100.00,
  "currency": "USD",
  "updated_at": "2023-10-27T10:00:05Z"
}
```

### 4.3 Process Refund
`POST /v1/refunds`

**Request Payload:**
```json
{
  "payment_id": "pay_abc123",
  "amount": 50.00,
  "reason": "Customer requested partial refund"
}
```

---

## 5. Scalability & Advanced Topics

### 5.1 Idempotency Mechanism
To prevent double-charging, the system uses an **Idempotency Key** (provided by the client):
1.  When a request arrives, the system checks the `payments` table for the `idempotency_key`.
2.  If it exists, it returns the cached response of the original request.
3.  If not, it creates a record with status `PENDING` and proceeds. This prevents race conditions if the client sends two identical requests simultaneously.

### 5.2 Distributed Transactions & The Saga Pattern
Since the process involves multiple services (Payment $\rightarrow$ Risk $\rightarrow$ Bank $\rightarrow$ Ledger), a distributed transaction is needed. We use the **Saga Pattern (Orchestration-based)**:
*   **Step 1:** `PaymentService` reserves the transaction.
*   **Step 2:** `RiskService` approves. (If failed $\rightarrow$ Mark Payment as FAILED).
*   **Step 3:** `Executor` calls Bank API. (If failed $\rightarrow$ Mark Payment as FAILED).
*   **Step 4:** `LedgerService` updates balances. (If failed $\rightarrow$ Trigger Compensating Transaction to void the bank charge).

### 5.3 Fault Tolerance & Availability
*   **Circuit Breakers:** If a specific bank adapter (e.g., Chase API) is timing out, the circuit breaker trips, and the system either fails fast or routes traffic to a backup PSP.
*   **Exponential Backoff:** For Webhooks, if the merchant server is down, the system retries at $2^n$ intervals (e.g., 1m, 2m, 4m... up to 24 hours).
*   **Dead Letter Queues (DLQ):** Any webhook or ledger update that fails after maximum retries is pushed to a DLQ for manual intervention.

### 5.4 Security & Compliance
*   **PCI-DSS:** The `Tokenization Service` is the only component that touches Raw PAN. It resides in a separate VPC with restricted access.
*   **Encryption:** Use AES-256 for data at rest and TLS 1.3 for data in transit.
*   **HMAC Signatures:** Webhooks are signed with a secret key so the merchant can verify the request came from the gateway and wasn't tampered with.

---

## 6. Trade-off Analysis

| Trade-off | Choice | Reasoning |
| :--- | :--- | :--- |
| **Consistency vs Availability** | **CP (Consistency)** | In payments, consistency is paramount. It is better to return a "503 Service Unavailable" than to accidentally charge a customer twice or lose a record of a successful payment. |
| **Latency vs Storage** | **Storage** | We store every single state change in the `ledger` and `payment_audit` tables. This increases storage costs but provides an immutable audit trail required by financial regulators. |
| **Synchronous vs Asynchronous** | **Hybrid** | The initial payment request is synchronous to provide immediate feedback to the user. However, ledger updates, analytics, and webhooks are asynchronous (via Kafka) to keep the critical path latency low. |
| **Database Selection** | **Postgres** | While NoSQL scales better, the complexity of implementing ACID-compliant double-entry bookkeeping in NoSQL outweighs the scaling benefits. Sharding Postgres by `merchant_id` is a viable path for scaling. |""",
}

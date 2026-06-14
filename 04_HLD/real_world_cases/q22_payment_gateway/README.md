# Payment Gateway HLD

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
| **Ledger Query** | $O(\log N)$ | $O(1)$ | Indexed lookup on account ID. |
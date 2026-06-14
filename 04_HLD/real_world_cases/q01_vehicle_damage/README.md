# Automated Vehicle Damage Auto-Penalty Pipeline HLD

## 1. Overview & System Requirements

The **Automated Vehicle Damage Auto-Penalty Pipeline** is a mission-critical system designed to automate the inspection, valuation, and billing process for rental car returns. The core challenge lies in the intersection of heavy binary data processing (High-Res Images), Computer Vision (CV) inference, and financial integrity (Idempotent Billing).

### 1.1 Functional Requirements
*   **Image Ingestion:** Accept high-resolution images from kiosks upon vehicle return.
*   **Damage Detection:** Compare current vehicle state against historical baseline images to identify new scratches, dents, or cracks.
*   **Valuation:** Map detected damages to a cost estimate based on a repair valuation catalog.
*   **Automated Billing:** Charge the customer's stored payment method based on the valuation.
*   **Notification:** Provide the user with a transparent report including "Before" and "After" images and a receipt.

### 1.2 Non-Functional Requirements
*   **Latency:** Processing must complete within **5 minutes** of the vehicle return to ensure the customer can be notified before leaving the premises or shortly after.
*   **Strict Idempotency:** Zero tolerance for duplicate charges. Retries in the billing pipeline must not result in multiple payments for the same damage event.
*   **Scalability:** Handle **50,000 returns per day** globally.
*   **Durability:** Images must be stored reliably for legal and insurance purposes.
*   **Availability:** The ingestion API must be highly available to avoid blocking the physical return process.

### 1.3 Scale Assumptions & Capacity Planning
| Metric | Value | Calculation/Reasoning |
| :--- | :--- | :--- |
| **Daily Volume** | 50,000 returns | Given |
| **Avg. QPS** | $\approx 0.58$ req/sec | $50,000 / 86,400$ seconds |
| **Peak QPS** | $\approx 6 - 10$ req/sec | Assuming $10x-15x$ spikes during peak return hours |
| **Images per Return** | 10 - 20 images | High-res photos of all angles |
| **Avg. Image Size** | 5 MB | High-resolution JPG/PNG |
| **Daily Storage** | $\approx 2.5$ TB | $50,000 \text{ returns} \times 15 \text{ images} \times 5 \text{ MB}$ |
| **Monthly Storage** | $\approx 75$ TB | Requires scalable Object Storage (S3/GCS) |

---

## 2. High-Level System Architecture

The system follows an **Event-Driven Architecture (EDA)** to decouple the heavy image processing and billing logic from the synchronous API response.

### 2.1 Architecture Component Diagram (Logical Flow)
`Kiosk` $\rightarrow$ `API Gateway` $\rightarrow$ `Ingestion Service` $\rightarrow$ `Object Storage (S3)` & `Message Queue (Kafka)` $\rightarrow$ `Damage Detection Worker` $\rightarrow$ `Valuation Service` $\rightarrow$ `Billing Service` $\rightarrow$ `Payment Gateway` $\rightarrow$ `Notification Service`.

### 2.2 Component Roles
*   **Ingestion Service:** A lightweight service that validates the `reservation_id`, generates pre-signed URLs for image uploads to S3, and pushes a "Return Event" to Kafka.
*   **Object Storage (S3):** Stores raw images and historical baseline images. Organized by `vehicle_id/reservation_id/`.
*   **Message Queue (Kafka):** Acts as the buffer. Different topics for `damage-detection-tasks`, `valuation-tasks`, and `billing-tasks`.
*   **Damage Detection Worker:** A GPU-accelerated worker that pulls images, runs a Siamese Network or Difference-Map CV model to find changes, and identifies damage types.
*   **Valuation Service:** A lookup service that queries a database of parts and labor costs to calculate the total penalty.
*   **Billing Service:** The most sensitive component; manages the payment lifecycle and ensures idempotency.
*   **Notification Service:** Sends emails/push notifications via SendGrid/Twilio.

---

## 3. Key HLD Concepts & Component Design

### 3.1 The CV Pipeline (Damage Detection)
Comparing two sets of high-res images is computationally expensive.
1.  **Image Alignment:** Use **ORB (Oriented FAST and Rotated BRIEF)** or **SIFT** to align current images with historical ones to account for slight differences in camera angle.
2.  **Change Detection:** Subtract the baseline image from the current image or use a **Siamese Neural Network** to identify "anomaly" regions.
3.  **Classification:** A secondary model (e.g., Mask R-CNN) classifies the anomaly as a "scratch," "dent," or "crack."

### 3.2 Idempotent Billing Design
To prevent double-charging, the Billing Service implements the **Idempotency Key Pattern**.
*   **Key Generation:** The `reservation_id` (or a composite of `reservation_id` + `return_event_id`) serves as the unique idempotency key.
*   **State Machine:**
    *   `PENDING`: Request received.
    *   `PROCESSING`: Call sent to Payment Gateway (Stripe/PayPal).
    *   `SUCCESS`: Payment confirmed.
    *   `FAILED`: Payment rejected.
*   **Workflow:** Before calling the Payment Gateway, the service checks the database for the status of the key. If `SUCCESS`, it returns the existing receipt immediately.

### 3.3 Database Schema
A relational database (PostgreSQL) is preferred for billing and valuation due to ACID requirements.

**Table: `reservations`**
| Column | Type | Note |
| :--- | :--- | :--- |
| `reservation_id` | UUID (PK) | Unique ID for the rental |
| `vehicle_id` | UUID (FK) | Reference to vehicle |
| `user_id` | UUID (FK) | Reference to customer |
| `status` | Enum | ACTIVE, RETURNED, CLOSED |

**Table: `damage_reports`**
| Column | Type | Note |
| :--- | :--- | :--- |
| `report_id` | UUID (PK) | Unique report ID |
| `reservation_id` | UUID (FK) | Link to reservation |
| `damage_type` | String | Scratch, Dent, etc. |
| `severity` | Enum | LOW, MED, HIGH |
| `estimated_cost` | Decimal | Calculated value |
| `evidence_url` | String | Link to S3 image highlighting damage |

**Table: `billing_transactions`**
| Column | Type | Note |
| :--- | :--- | :--- |
| `txn_id` | UUID (PK) | Internal transaction ID |
| `idempotency_key`| String (Unique)| `reservation_id` |
| `amount` | Decimal | Total charge |
| `status` | Enum | PENDING, SUCCESS, FAILED |
| `gateway_ref` | String | Reference ID from Stripe/PayPal |

---

## 4. Data Flows & Fault Tolerance

### 4.1 End-to-End Request Walkthrough
1.  **Upload:** Kiosk calls `upload_return_telemetry`. The service saves image metadata to DB and returns a 202 Accepted.
2.  **Trigger:** An event is published to `damage-detection-tasks` Kafka topic.
3.  **Analysis:** Worker consumes the event $\rightarrow$ fetches historical images from S3 $\rightarrow$ runs CV model $\rightarrow$ writes findings to `damage_reports`.
4.  **Valuation:** An event is sent to `valuation-tasks`. The service calculates $\sum(\text{costs})$ and updates the report.
5.  **Billing:** The `billing-tasks` worker picks up the total. It checks the `billing_transactions` table for the `idempotency_key`. If not present, it charges the card and marks the transaction as `SUCCESS`.
6.  **Notify:** Notification service sends the final PDF report to the user.

### 4.2 Fault Tolerance & Reliability
*   **Dead Letter Queues (DLQ):** If an image is corrupted and the CV worker fails 3 times, the message is moved to a DLQ for manual human review by an insurance agent.
*   **S3 Versioning:** Enables retrieval of historical "baseline" images even if they were accidentally overwritten.
*   **Retry Strategy:** Billing retries use **Exponential Backoff**. If the Payment Gateway is down, the system retries until a timeout is reached, then alerts an operator.
*   **Circuit Breaker:** If the Valuation Service latency spikes, the Billing Service trips a circuit breaker to prevent cascading failures across the pipeline.

---

## 5. Production Trade-offs

### 5.1 Consistency vs. Latency (CAP Theorem)
*   **Decision:** We prioritize **Eventual Consistency** for the image processing pipeline but **Strong Consistency** for the Billing Service.
*   **Trade-off:** The user might not get the email the *exact* second they return the car (Latency), but we guarantee they are never charged twice (Consistency).

### 5.2 Storage Strategy: Cold vs. Hot
*   **Decision:** Use **S3 Intelligent-Tiering**.
*   **Trade-off:** Current return images are "Hot" for 30 days (for disputes), then moved to "Cold Storage" (Glacier) for 7 years to meet legal requirements, reducing costs by $\approx 70\%$.

### 5.3 ML Accuracy vs. Processing Speed
*   **Decision:** Use a two-stage model (Fast Heuristic $\rightarrow$ Deep Analysis).
*   **Trade-off:** A fast "Difference Map" identifies *if* something changed. If no change is detected, we skip the expensive Mask R-CNN classification, saving GPU costs and reducing latency.

## Complexity Analysis Summary

| Operation | Time Complexity | Space Complexity | Bottleneck |
| :--- | :--- | :--- | :--- |
| **Image Upload** | $O(1)$ | $O(\text{Image Size})$ | Network I/O |
| **CV Comparison** | $O(N \cdot P)$ | $O(P)$ | GPU Compute ($P$ = Pixels) |
| **Billing Lookup** | $O(1)$ | $O(1)$ | DB Index Lookup |
| **Overall Pipeline**| Asynchronous | $O(\text{Daily Storage})$ | S3 Throughput / GPU |
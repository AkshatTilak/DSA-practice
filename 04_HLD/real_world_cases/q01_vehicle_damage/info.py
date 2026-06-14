INFO = {
    'difficulty': 'Hard',
    'link': '',
    'description': 'Design an Automated Vehicle Damage Auto-Penalty Pipeline.',
    'type': 'design',
    'groups': ['Real-World Systems', 'Data Pipelines'],
    'readme_content': """# Automated Vehicle Damage Auto-Penalty Pipeline HLD

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
| **Overall Pipeline**| Asynchronous | $O(\text{Daily Storage})$ | S3 Throughput / GPU |""",
    'solutions': """# System Design: Automated Vehicle Damage Auto-Penalty Pipeline

## 1. Requirements & System Constraints

### 1.1 Functional Requirements
*   **Image/Video Ingestion:** The system must ingest high-resolution images or video streams from vehicle entry/exit portals.
*   **Automated Damage Detection:** Use Computer Vision (CV) to identify damages (scratches, dents, cracks, broken glass).
*   **State Comparison:** Compare the "Post-trip" state against the "Pre-trip" baseline to identify *new* damage.
*   **Penalty Calculation:** Map detected damages to a predefined pricing matrix to calculate a financial penalty.
*   **Automated Billing:** Integrate with a payment gateway to trigger charges.
*   **Human-in-the-Loop (HITL):** Provide a dashboard for administrators to review, override, or approve penalties in case of disputes.
*   **Notification:** Alert the user via Push/Email/SMS regarding the detected damage and the associated charge.

### 1.2 Non-Functional Requirements
*   **High Availability:** The ingestion system must be 99.99% available to avoid blocking vehicle movement at portals.
*   **Scalability:** Support thousands of portals globally and millions of vehicle inspections per day.
*   **Eventual Consistency:** While image ingestion must be fast, the penalty calculation can be asynchronous (processed within minutes).
*   **Durability:** Images must be stored securely for legal and dispute purposes (audit trail).
*   **Accuracy:** Low False Positive Rate (FPR) is critical to avoid customer dissatisfaction.

### 1.3 Scale Estimations (HLD)
*   **Daily Volume:** 1 Million inspections/day.
*   **Images per Inspection:** ~10-20 high-res images.
*   **Storage:** $10^6 \text{ inspections} \times 15 \text{ images} \times 5\text{MB/image} \approx 75\text{TB/day}$.
*   **Peak Load:** 10x average during morning/evening rush hours.

---

## 2. High-Level Architecture

The system follows an event-driven, microservices-based architecture to decouple the heavy compute load (AI inference) from the ingestion and billing processes.

### 2.1 Architecture Diagram

```mermaid
graph TD
    subgraph "Ingestion Layer"
        Portal[IoT Camera Portal] --> API[Ingestion API Gateway]
        API --> S3[Image Blob Store - S3]
        API --> Kafka[Event Bus - Kafka]
    end

    subgraph "Processing Pipeline"
        Kafka --> DamageSvc[Damage Detection Service]
        DamageSvc --> MLModel[ML Inference Cluster - GPU]
        MLModel --> DamageSvc
        DamageSvc --> ComparisonSvc[State Comparison Service]
        ComparisonSvc --> DB[(Metadata DB - PostgreSQL)]
    end

    subgraph "Penalty & Billing"
        ComparisonSvc --> PenaltySvc[Penalty Engine]
        PenaltySvc --> PricingDB[(Pricing Matrix)]
        PenaltySvc --> BillingSvc[Billing Integration Service]
        BillingSvc --> Stripe[Payment Gateway]
    end

    subgraph "Management"
        AdminDash[Admin Review Portal] --> DB
        AdminDash --> PenaltySvc
        PenaltySvc --> NotifSvc[Notification Service]
        NotifSvc --> User[Customer App]
    end
```

### 2.2 Component Interactions
1.  **Ingestion:** The Portal uploads images to S3 and sends a metadata event (VehicleID, TripID, Timestamp) to Kafka.
2.  **Detection:** The `Damage Detection Service` consumes the event, pulls images from S3, and runs them through an ML model to identify damage coordinates and types.
3.  **Comparison:** The `Comparison Service` fetches the baseline (pre-trip) damage records from the DB. It filters out pre-existing damage, leaving only "New Damage."
4.  **Penalization:** The `Penalty Engine` maps "New Damage" (e.g., "Front Bumper Scratch - Medium") to a dollar value using the `Pricing Matrix`.
5.  **Closing the Loop:** The `Billing Service` processes the payment, and the `Notification Service` alerts the user.

---

## 3. Detailed Database Schema Design

We use a hybrid approach: **PostgreSQL** for relational metadata (strong consistency for billing/state) and **S3** for unstructured image data.

### 3.1 Relational Schema (PostgreSQL)

#### Table: `vehicles`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `vehicle_id` | UUID | PK | Unique identifier |
| `vin` | VARCHAR(17) | Unique, Index | Vehicle Identification Number |
| `model_id` | UUID | FK | Reference to vehicle model specs |

#### Table: `inspections`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `inspection_id` | UUID | PK | Unique identifier |
| `vehicle_id` | UUID | FK, Index | Reference to vehicle |
| `trip_id` | UUID | Index | Link to the rental/trip session |
| `type` | ENUM | PRE_TRIP, POST_TRIP | Stage of inspection |
| `timestamp` | TIMESTAMPTZ | Index | When the inspection occurred |
| `s3_folder_path`| TEXT | - | Path to images in S3 |

#### Table: `damage_records`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `damage_id` | UUID | PK | Unique identifier |
| `inspection_id` | UUID | FK, Index | Reference to inspection |
| `damage_type` | VARCHAR(50) | - | e.g., 'dent', 'scratch', 'crack' |
| `severity` | ENUM | LOW, MED, HIGH | Impact level |
| `location` | VARCHAR(50) | - | e.g., 'left_door', 'windshield' |
| `confidence` | FLOAT | - | ML confidence score (0.0 - 1.0) |
| `bbox` | JSONB | - | Bounding box coordinates [x, y, w, h] |

#### Table: `penalties`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `penalty_id` | UUID | PK | Unique identifier |
| `damage_id` | UUID | FK, Unique | Reference to specific damage |
| `amount` | DECIMAL(10,2)| - | Calculated penalty amount |
| `status` | ENUM | PENDING, PAID, DISPUTED, VOID | Payment status |
| `created_at` | TIMESTAMPTZ | - | Record creation time |

### 3.2 Indexing Strategy
*   **B-Tree Index on `vehicle_id` & `trip_id`**: To quickly retrieve the pre-trip state for a specific vehicle during post-trip processing.
*   **B-Tree Index on `timestamp`**: For auditing and reporting.
*   **GIN Index on `damage_records.bbox` (Optional)**: If spatial queries are needed for heatmaps of vehicle damage.

---

## 4. Core API Design

### 4.1 Ingestion API
`POST /v1/inspections`
*   **Payload:**
    ```json
    {
      "vehicle_id": "uuid-123",
      "trip_id": "trip-456",
      "type": "POST_TRIP",
      "images": [
        {"image_id": "img_1", "url": "s3://bucket/path/1.jpg"},
        {"image_id": "img_2", "url": "s3://bucket/path/2.jpg"}
      ],
      "metadata": { "portal_id": "portal_nyc_01", "timestamp": "2023-10-01T10:00:00Z" }
    }
    ```
*   **Response:** `202 Accepted` (Processing is async).

### 4.2 Penalty Management API (Admin/User)
`GET /v1/penalties/{penalty_id}`
*   **Response:**
    ```json
    {
      "penalty_id": "pen-789",
      "amount": 150.00,
      "status": "PENDING",
      "evidence": {
        "pre_trip_image": "s3://.../pre.jpg",
        "post_trip_image": "s3://.../post.jpg",
        "damage_type": "dent",
        "location": "rear_bumper"
      }
    }
    ```

`PATCH /v1/penalties/{penalty_id}/status`
*   **Payload:** `{"status": "VOID", "reason": "Customer provided proof of pre-existing damage"}`
*   **Response:** `200 OK`.

---

## 5. Scalability & Advanced Topics

### 5.1 ML Pipeline Optimization
*   **GPU Batching:** Instead of processing one image at a time, the `Damage Detection Service` should group images into batches to maximize GPU throughput.
*   **Model Tiering:** Use a lightweight "Screening Model" (e.g., MobileNet) to check if *any* damage exists. Only trigger the "Heavy Model" (e.g., Mask R-CNN or ViT) if damage is suspected.

### 5.2 Handling Large Data Volume
*   **S3 Lifecycle Policies:** Move images to *S3 Intelligent-Tiering* or *Glacier* after 90 days, as they are rarely accessed unless a dispute is raised.
*   **Database Sharding:** Shard the `inspections` and `damage_records` tables by `vehicle_id` or `trip_id` to distribute load across multiple PostgreSQL instances.

### 5.3 Fault Tolerance & Reliability
*   **Dead Letter Queues (DLQ):** If the ML service fails to process an image after 3 retries, move the message to a DLQ for manual inspection or system debugging.
*   **Idempotency:** Use `trip_id` as an idempotency key in the Billing Service to ensure a customer isn't charged twice for the same damage.
*   **Circuit Breaker:** Implement a circuit breaker (e.g., Resilience4j) on the Payment Gateway integration to prevent system cascading failure if the gateway is down.

### 5.4 Caching Strategy
*   **Redis:** Cache the `Pricing Matrix` (small, read-heavy) to avoid frequent DB lookups during penalty calculation.
*   **CDN:** Use a CDN (CloudFront) for serving evidence images to the Admin Review Portal to reduce latency.

---

## 6. Trade-off Analysis

### 6.1 CAP Theorem Priorities
The system prioritizes **Availability** and **Partition Tolerance** (AP) during the ingestion phase. It is more important that the vehicle clears the portal than for the penalty to be calculated in real-time. We accept **Eventual Consistency** for the penalty state.

### 6.2 Latency vs. Accuracy
*   **Trade-off:** Higher accuracy in CV requires larger models (Transformers/Deep CNNs) which increase inference latency.
*   **Decision:** We move inference to an asynchronous background pipeline. This removes the latency from the user's critical path (exiting the parking lot) while allowing us to use the most accurate, compute-heavy models.

### 6.3 SQL vs. NoSQL
*   **Decision:** SQL (PostgreSQL) was chosen over NoSQL (MongoDB).
*   **Reasoning:** The relationship between Vehicle $\rightarrow$ Inspection $\rightarrow$ Damage $\rightarrow$ Penalty is highly relational. Financial transactions require ACID compliance to ensure that a penalty is never "lost" or "double-counted," which is more naturally handled by a relational database.""",
}

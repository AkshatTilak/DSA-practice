# System Design Solution: Automated Vehicle Damage Auto-Penalty Pipeline

This document details the production-grade system architecture designed to ingest high-resolution vehicle returns, process computer vision inference asynchronously, and process idempotent billing.

---

## 🗺️ System Architecture Diagram

```text
[Return Kiosk App]
       │  (Upload Images + Metadata)
       ▼
[API Gateway] ──> [Auth & Rate Limiting]
       │
       ├── (Save raw image binary) ──> [Blob Storage (S3 / GCS)]
       │
       └── (Publish return metadata) ──> [Kafka Message Queue (Topic: vehicle-returns)]
                                                  │
             ┌────────────────────────────────────┴────────────────────────────────────┐
             ▼                                                                         ▼
  [Damage Detection Workers]                                                   [Analytics Service]
  (Load current & baseline images from S3)                                     (Tracks turnaround KPIs)
             │
             ├─> [Inference Cluster (YOLOv8/ResNet GPU Pool)]
             │
             ▼
  (Damage Found: Save database record with image offsets)
             │
             ▼
  [Kafka Broker (Topic: vehicle-charges)]
             │
             ▼
  [Idempotent Billing Workers]
             │
             ├── (Lock transaction key in Redis)
             ├── (Charge via Stripe API)
             ├── (Write Payment Ledger to PostgreSQL)
             ▼
  [Kafka Broker (Topic: vehicle-notifications)]
             │
             ▼
  [Notification Service (Sends Email & SMS via Twilio/SendGrid)]
```

---

## 💾 Database Schema (PostgreSQL Relational Storage)

For billing auditability and transactional integrity, a relational PostgreSQL cluster (with primary-replica replication) is used.

### Table: `vehicle_returns`
Tracks metadata for each returned vehicle.
```sql
CREATE TABLE vehicle_returns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id VARCHAR(64) UNIQUE NOT NULL,
    vehicle_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    kiosk_id VARCHAR(64) NOT NULL,
    returned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(32) NOT NULL -- 'pending', 'processed', 'failed'
);
```

### Table: `damages_detected`
Stores findings from the computer vision model.
```sql
CREATE TABLE damages_detected (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id UUID REFERENCES vehicle_returns(id),
    damage_type VARCHAR(64) NOT NULL, -- 'dent', 'scratch', 'crack'
    severity_score NUMERIC(4, 2) NOT NULL, -- 0.00 to 1.00
    evidence_image_url VARCHAR(512) NOT NULL,
    estimated_cost NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Table: `billing_transactions`
Ensures double-charge protection using a unique idempotency key.
```sql
CREATE TABLE billing_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    return_id UUID REFERENCES vehicle_returns(id),
    idempotency_key VARCHAR(128) UNIQUE NOT NULL,
    charge_amount NUMERIC(10, 2) NOT NULL,
    stripe_charge_id VARCHAR(128),
    status VARCHAR(32) NOT NULL, -- 'pending', 'succeeded', 'failed'
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

---

## ⚙️ Core Technical Details & Failure Scenarios

### 1. Image Processing SLA (5 minutes)
- **High-throughput Ingestion**: Raw images are uploaded directly from kiosks to S3 using **presigned URLs** to prevent taxing app server bandwidth.
- **Kafka Decoupling**: Uploading metadata to Kafka allows the API to return $O(1)$ fast response status `enqueued` to the kiosk, decoupling the heavy GPU vision pipeline.
- **Inference Scaling**: Auto-scaling GPU clusters pull messages from Kafka. If lag exceeds thresholds, the cluster scales out dynamically.

### 2. Idempotent Billing (No Double Charges)
- **Idempotency Key Formulation**: Key = `reservation_id` + `damage_hash`.
- **Distributed Lock**: Billing workers acquire a Redis lock on the key. If the key exists, subsequent retries are rejected.
- **Stripe API Double-Check**: The key is passed directly to the Stripe API charge parameters. Stripe natively deduplicates charges sharing identical keys within a 24-hour window.

### 3. Disaster Recovery (Kafka Poison Pill)
- **Dead Letter Queue (DLQ)**: If an image is corrupt and crashes the Computer Vision worker, the worker catches the error, publishes the message to `vehicle-returns-dlq`, and commits the offset. This prevents pipeline stalling.

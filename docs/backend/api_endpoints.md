# api endpoints documentation

all api requests are prefixed with `/api/v1`.

---

## 1. ingest endpoints

### POST `/api/v1/ingest/email`
submits unstructured email updates from a vendor to parse and run tracker/forecaster calculations.

- **request format**: `multipart/form-data` (form parameters)
- **parameters**:
  - `email_text` (string): raw text body of the email.
  - `material_sku` (string): sku code of the material to update.
- **response (200 OK)**:
  ```json
  {
    "message": "Email ingested successfully",
    "parsed_data": {
      "sku": "SKU-482",
      "status": "SHIPPED",
      "current_location": "En route from freight hub, Pune",
      "estimated_delivery_date": "2026-07-18T00:00:00",
      "confidence_weight": 0.85,
      "explanation": "Extracted ship status and date from email text."
    }
  }
  ```

### POST `/api/v1/ingest/vision`
submits delivery photos, packing slips, or labels to verify quantity and condition.

- **request format**: `multipart/form-data` (form parameters & file upload)
- **parameters**:
  - `material_sku` (string): target material sku.
  - `file` (file): binary upload of image (`.jpg`, `.png`).
- **response (200 OK)**:
  ```json
  {
    "message": "Vision photo ingested successfully",
    "parsed_data": {
      "sku": "SKU-482",
      "quantity_verified": 25.0,
      "status": "DELIVERED",
      "condition": "GOOD",
      "explanation": "Image verifies delivery of 25 boxes of steel components in good condition."
    }
  }
  ```

### POST `/api/v1/ingest/schedule`
imports a primavera xml schedule to establish or update activities and relations.

- **request format**: `multipart/form-data` (file upload)
- **parameters**:
  - `file` (file): primavera `.xml` export.
- **response (200 OK)**:
  ```json
  {
    "message": "Schedule ingested successfully",
    "activities_count": 4
  }
  ```

---

## 2. materials endpoints

### GET `/api/v1/materials/`
lists all material orders.

- **response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "sku": "SKU-482",
      "description": "structural steel beams",
      "quantity": 10.0,
      "status": "IN_TRANSIT",
      "current_location": "Mumbai Transit Hub",
      "vendor_name": "SteelCorp Ltd",
      "promised_delivery_date": "2026-07-15T00:00:00",
      "activity_id": 2,
      "forecast_delivery_date": "2026-07-20T00:00:00",
      "delay_probability": 0.78,
      "confidence_score": 0.91
    }
  ]
  ```

### POST `/api/v1/materials/`
creates a new material order to track.

- **request format**: `application/json`
- **payload**:
  ```json
  {
    "sku": "SKU-994",
    "description": "rebar panels",
    "quantity": 50.0,
    "status": "ORDERED",
    "vendor_name": "ConcreteSupply Co",
    "promised_delivery_date": "2026-07-22T12:00:00Z",
    "activity_id": 3
  }
  ```
- **response (200 OK)**: returns created material model object with default scores.

### GET `/api/v1/materials/{material_id}`
returns details of a specific material order.

---

## 3. schedule endpoints

### GET `/api/v1/schedule/activities`
lists all loaded schedule tasks.

### GET `/api/v1/schedule/graph`
returns schedule nodes and links structured for frontend visualization graphs.

- **response (200 OK)**:
  ```json
  {
    "nodes": [
      {
        "id": "1",
        "label": "Foundation Pour",
        "start": "2026-07-06T12:00:00",
        "end": "2026-07-11T12:00:00",
        "is_critical": true,
        "status": "COMPLETED"
      },
      {
        "id": "2",
        "label": "Steel Erection",
        "start": "2026-07-12T12:00:00",
        "end": "2026-07-21T12:00:00",
        "is_critical": true,
        "status": "NOT_STARTED"
      }
    ],
    "links": [
      {
        "source": "1",
        "target": "2",
        "type": "FS"
      }
    ]
  }
  ```

---

## 4. alerts endpoints

### GET `/api/v1/alerts/`
returns all unresolved critical and warning logs.

- **response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "project_id": 1,
      "material_id": 1,
      "message": "Material SKU SKU-482 delay impacts project critical path by 5 days.",
      "severity": "CRITICAL",
      "is_resolved": false,
      "created_at": "2026-07-07T12:30:00"
    }
  ]
  ```

### POST `/api/v1/alerts/{alert_id}/resolve`
marks a specific alert as resolved.

- **response (200 OK)**:
  ```json
  {
    "message": "Alert marked as resolved"
  }
  ```

---

## 5. actions endpoints

### GET `/api/v1/actions/drafts`
lists all auto-drafted actions (like vendor emails) waiting for manager approval.

- **response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "alert_id": 1,
      "action_type": "EMAIL_VENDOR",
      "draft_content": "Subject: URGENT: Delivery Delay Escalation - SKU: SKU-482...",
      "status": "DRAFT",
      "created_at": "2026-07-07T12:30:05"
    }
  ]
  ```

### POST `/api/v1/actions/{action_id}/execute`
executes (simulates sending/dispatching) an approved action.

- **response (200 OK)**:
  ```json
  {
    "message": "Action of type 'EMAIL_VENDOR' was successfully executed (Simulated)"
  }
  ```

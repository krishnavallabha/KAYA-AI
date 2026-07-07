# ingest layer - detailed documentation

responsible for capturing unstructured, multi-modal supply chain inputs and mapping them into the database models (`Signal`, `Material`, `Activity`, `ActivityRelation`).

## 1. email parsing agent (`email_parser.py`)
- **input**: unstructured email text (from logs or direct copy/paste).
- **llm call**: uses `gpt-4o` with `response_format={"type": "json_object"}`.
- **prompt rules**: forces gpt to extract critical fields without conversational filler.
- **extracted json schema**:
  ```json
  {
    "sku": "string",
    "status": "ORDERED | FABRICATING | SHIPPED | IN_TRANSIT | DELIVERED",
    "current_location": "string | null",
    "estimated_delivery_date": "ISO8601 string | null",
    "confidence_weight": "float (0.0 to 1.0)",
    "explanation": "string"
  }
  ```
- **fallback**: if `OPENAI_API_KEY` is empty, it returns a mocked dictionary default to prevent crashes during dry-run demos.

## 2. vision / ocr parser (`vision_parser.py`)
- **input**: raw binary image bytes (photos of deliveries, labels, or packing slips).
- **conversion**: encodes bytes to base64 string using `base64.b64encode`.
- **llm call**: sends base64 string to `gpt-4o` as an image URL payload.
- **extracted json schema**:
  ```json
  {
    "sku": "string",
    "quantity_verified": "float",
    "status": "SHIPPED | DELIVERED",
    "condition": "GOOD | DAMAGED",
    "explanation": "string"
  }
  ```
- **fallback**: generates mocked data if api key is missing.

## 3. document parser (`document_parser.py`)
- **input**: text extracted from procurement logs, bills of lading, or submittal pdfs.
- **llm call**: uses standard text extraction prompt via `gpt-4o` returning raw json.
- **extracted json schema**:
  ```json
  {
    "sku": "string",
    "vendor": "string",
    "quantity": "float",
    "promised_delivery_date": "YYYY-MM-DD",
    "explanation": "string"
  }
  ```

## 4. schedule parser (`schedule_parser.py`)
- **input**: xml string exported from primavera p6 / ms project.
- **processing library**: python standard `xml.etree.ElementTree`.
- **xml logic**:
  - looks up all `<Activity>` tags. extracts `<Id>`, `<Name>`, `<StartDate>`, `<EndDate>`, and `<IsCritical>`.
  - looks up all `<ActivityRelation>` tags. maps predecessor-successor link IDs and `<RelationType>`.
- **fallback**: if xml formatting is invalid or parsing fails, it triggers `create_demo_schedule()` which builds a pre-configured 4-task sequence:
  ```text
  Activity A (Foundation) -> Activity B (Steel) -> Activity C (Decking) -> Activity D (Slab)
  ```

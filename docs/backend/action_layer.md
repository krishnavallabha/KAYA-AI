# action layer - detailed documentation

bridges intelligence analysis and user execution by generating alerts and auto-drafting communications.

## 1. alert triggers
- alerts are created automatically inside the database session when:
  - a delay is detected on any material tracking record.
  - the cascade impact engine identifies that the delay affects a critical path activity.
- alerts are categorized as `CRITICAL` or `WARNING`.

## 2. action & email drafting (`action_drafter.py`)
- **objective**: uses `gpt-4o` to generate tailored escalation emails for supplier management.
- **input arguments**:
  - vendor name
  - material sku
  - calculated delay duration (days)
  - forecast arrival date (eta string)
  - list of impacted downstream task names
- **prompt design**: forces the model to act as a senior contracts manager. the email must:
  - contain a professional, firm tone.
  - outline the exact construction activities that will stall because of the delay.
  - request immediate transit logs and shipping expediting options.
- **fallback**: if no openai api key is active, it falls back to a clean python-formatted string template containing the identical field tokens.

## 3. rest api routes (`api/endpoints/actions.py`)
- **endpoints**:
  - `GET /api/v1/actions/drafts`: lists all active drafts.
  - `POST /api/v1/actions/{action_id}/execute`: updates action status to `SENT` (simulates SMTP email dispatch or database ERP log updates).

## folder structure

```text
backend/
├── main.py                    # Entry point for FastAPI (configures middleware, CORS, and registers routers)
├── config.py                  # Global configurations (API keys, DB paths, and environment settings)
├── database.py                # Database connection, engine initialization, and session helpers
├── models.py                  # SQLAlchemy models (Project, Activity, ActivityRelation, Material, Signal, Alert, Action)
├── schemas.py                 # Pydantic schemas for request/response validation
│
├── ingest/                    # INGESTION LAYER
│   ├── __init__.py
│   ├── email_parser.py        # Extracts structured updates from email text using LLM
│   ├── vision_parser.py       # Extracts PO#, quantities, and status from photos/label scans using Multimodal LLM
│   ├── document_parser.py     # Parses Bills of Lading (BOLs) and submittal log PDFs
│   └── schedule_parser.py     # Parses Primavera XML/CSV files into activities and relationship records
│
├── intelligence/              # INTELLIGENCE LAYER
│   ├── __init__.py
│   ├── material_tracker.py    # Reconciles conflicting data using recency and source credibility weights
│   ├── forecaster.py          # Computes Bayesian dynamic ETA predictions and delay probabilities
│   └── cascade_engine.py      # Builds schedule graph (NetworkX) and runs BFS traversal to detect critical path impact
│
├── action/                    # ACTION LAYER
│   ├── __init__.py
│   └── action_drafter.py      # Generates draft vendor escalation emails & PO amendments using LLM prompts
│
├── api/                       # REST API ENDPOINTS
│   ├── __init__.py
│   └── endpoints/
│       ├── __init__.py
│       ├── ingest.py          # Endpoints for file/text ingestion (schedules, emails, image uploads)
│       ├── materials.py       # CRUD endpoints for material tracking items
│       ├── schedule.py        # Endpoints to query the schedule network graph (nodes and edges)
│       ├── alerts.py          # Endpoints to get, update, and resolve delay alerts
│       └── actions.py         # Endpoints to preview and approve drafted resolutions (e.g., vendor emails)
│
└── tests/                     # AUTOMATED VERIFICATION
    ├── __init__.py
    ├── test_schedule_parser.py
    ├── test_material_tracker.py
    ├── test_cascade_engine.py
    └── test_forecaster.py
```

## command for it:

```bash 
mkdir -p backend/ingest backend/intelligence backend/action backend/api/endpoints backend/tests && \
touch backend/main.py backend/config.py backend/database.py backend/models.py backend/schemas.py \
      backend/ingest/__init__.py backend/ingest/email_parser.py backend/ingest/vision_parser.py backend/ingest/document_parser.py backend/ingest/schedule_parser.py \
      backend/intelligence/__init__.py backend/intelligence/material_tracker.py backend/intelligence/forecaster.py backend/intelligence/cascade_engine.py \
      backend/action/__init__.py backend/action/action_drafter.py \
      backend/api/__init__.py backend/api/endpoints/__init__.py backend/api/endpoints/ingest.py backend/api/endpoints/materials.py backend/api/endpoints/schedule.py backend/api/endpoints/alerts.py backend/api/endpoints/actions.py \
      backend/tests/__init__.py backend/tests/test_schedule_parser.py backend/tests/test_material_tracker.py backend/tests/test_cascade_engine.py backend/tests/test_forecaster.py
```
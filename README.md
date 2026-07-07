# FlowSense AI — Intelligent Construction Supply Chain

FlowSense integrates LLM agents, status consensus tracking, and sequential Bayesian forecasting to automate material-tracking and delay mitigation in project management.

---

## Quick Start (How to Run)

### 1. Installation & Environment Setup
Clone the repository and set up a Python virtual environment:

```bash
# Set up venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

* **Live Mode**: Set your `OPENAI_API_KEY` inside `.env`.
* **Fallback Mode (Hackathon Wi-Fi Proof)**: Leave `OPENAI_API_KEY` blank or unset. Every agent will automatically drop back to local regex/rule extraction, meaning you can demo the entire app offline!

### 3. Start the API Server
Start the development FastAPI backend:

```bash
uvicorn backend.main:app --reload
```

* **API Docs (Swagger UI)**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to interactively test endpoints (`/ingest/email`, `/ingest/vision`, `/ingest/schedule`).

### 4. Run the Test Suite
Verify that everything is operating correctly:

```bash
PYTHONPATH=. ./venv/bin/pytest backend/tests/
```

---

## Hackathon Pitch & Demo Commands

### Recreating/Resetting the Database
To clear all existing materials, status records, alerts, and actions before presenting or recording a clean demo walkthrough:

```bash
rm flowsense.db
```
*(The server will automatically recreate a fresh, clean database schema upon the next API request.)*

### snappy Response Times (pitch tuning)
To keep the presentation fast and avoid waiting 5+ seconds for response streams, toggle the model in `config.py` to `gpt-4o-mini`:

```python
EMAIL_MODEL = "gpt-4o-mini"
VISION_MODEL = "gpt-4o-mini"
DOC_MODEL = "gpt-4o-mini"
```

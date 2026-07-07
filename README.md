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
Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

* **Live Mode (OpenAI)**: Set your `OPENAI_API_KEY` inside `.env`.
* **Live Mode (Groq - Free Tier/Cheap)**: If you don't have OpenAI credits, set your `GROQ_API_KEY` inside `.env` instead. The pipeline will automatically route completions to Groq's open-source Llama models (`llama-3.1-70b-versatile` / `llama-3.2-11b-vision-preview`) using the same OpenAI client wrapper.
* **Fallback Mode (Hackathon Offline)**: Leave both keys blank. Every agent will automatically drop back to local regex/rule extraction, meaning you can demo the entire app offline!

### 3. Start the API Server
Start the development FastAPI backend:

```bash
uvicorn backend.main:app --reload
```

* **API Docs (Swagger UI)**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to interactively test endpoints (`/ingest/email`, `/ingest/vision`, `/ingest/schedule`).

### 4. Run the Test Suite
You can execute all backend unit and integration tests using either the direct `pytest` command or the provided test runner script:

* **Using the Test Runner Script**:
  ```bash
  ./run_tests.sh
  ```
  *(You can pass standard pytest flags, e.g. `./run_tests.sh -v` for verbose output, or `./run_tests.sh -s` to view the JSON request payloads and server outputs live during execution.)*

* **Using the direct Pytest command**:
  ```bash
  PYTHONPATH=. ./venv/bin/pytest backend/tests/
  ```

The test suite runs our end-to-end integration test (`test_ml_integration`), verifying:
* Signal database insertion.
* Reconciled status voting consensus.
* Sequential Bayesian delay and ETA predictions.
* Signal conflict alerting and resolution triggers.

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

# FlowSense AI — Intelligent Construction Supply Chain

FlowSense integrates LLM agents, status consensus tracking, and sequential Bayesian forecasting to automate material-tracking and delay mitigation in project management. 

This repository contains both the **Backend (Intelligence Layer)** and the **Frontend (Action Layer)** of the FlowSense platform.

---

## Architecture & System Overview
- **Backend (Intelligence Layer)**: Built with FastAPI, SQLite (via SQLAlchemy), and OpenAI/Groq APIs. It orchestrates document parsers, vision-based status verification, a cascading schedule impact engine, and a Bayesian delay risk forecaster.
- **Frontend (Action Layer)**: A React-based project manager command center dashboard styled with Tailwind CSS and utilizing React Flow + dagre for CPM schedule visualization, alongside Recharts for analytics.

---

## Frontend (Action Layer)

The frontend consumes the FlowSense FastAPI backend to surface order tracking, delay forecasting, critical path schedule impact, alerts, and one-click AI-drafted vendor actions.

### Features
- **Command Center dashboard** — KPIs, order-status mix (donut), delay-risk ranking, at-risk orders, and live alerts.
- **Material Orders** — searchable/filterable table with forecast ETA, delay probability, confidence score, lifecycle stepper, and a create-order form.
- **Schedule Graph** — interactive activity network (React Flow + dagre auto-layout) with the critical path highlighted and per-activity material drill-down.
- **Alerts** — severity-filtered feed with one-click resolve.
- **Action Drafts** — review AI-generated vendor escalation emails and execute (simulated send) in one click.
- **Ingest** — feed vendor emails, delivery photos, and Primavera XML schedules into the pipeline.
- **Dark / light theme** — toggle in the top bar; preference is remembered.
- **Demo-safe** — if the backend is unreachable, the UI transparently falls back to bundled demo data so it always renders.

### Tech Stack
React 18 · Vite 5 · Tailwind CSS 3 · React Router 6 · Recharts · React Flow + dagre · lucide-react.

### Getting Started (Frontend)
Prerequisites: Node.js 18+ and npm.

```bash
# 1. Install dependencies
npm install

# 2. Configure the backend URL (optional — defaults to http://localhost:8000)
cp .env.example .env
# then edit VITE_API_BASE_URL if your API runs elsewhere

# 3. Start the dev server
npm run dev          # serves on http://localhost:5173

# Production build + local preview
npm run build
npm run preview
```

---

## Backend (Intelligence Layer)

The backend provides the database schema, cognitive agents (email parser, photo verifier), Bayesian delay logic, and API endpoints.

### Getting Started (Backend)
Prerequisites: Python 3.10+.

#### 1. Installation & Environment Setup
Set up a Python virtual environment and install dependencies:

```bash
# Set up venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill out your keys:
```bash
cp .env.example .env
```
* **Live Mode (OpenAI)**: Set your `OPENAI_API_KEY` inside `.env`.
* **Live Mode (Groq)**: Set your `GROQ_API_KEY` instead to route completions to Groq's open-source Llama models.
* **Fallback Mode (Hackathon Offline)**: Leave keys blank to default to rule-based regex extraction.

#### 3. Start the API Server
Start the development FastAPI backend:

```bash
uvicorn backend.main:app --reload
```
* **API Docs (Swagger UI)**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

#### 4. Run the Test Suite
```bash
# Using the test runner script
./run_tests.sh

# Using the direct Pytest command
PYTHONPATH=. ./venv/bin/pytest backend/tests/
```

---

## Hackathon Pitch & Demo Commands

### Recreating/Resetting the Database
To clear all existing data before presenting a clean demo walkthrough:
```bash
rm flowsense.db
```
*(The server will automatically recreate a fresh database schema upon the next API request.)*

### Snappy Response Times (Model Tuning)
To speed up LLM response times for demo purposes, set the model in `config.py` to `gpt-4o-mini`:
```python
EMAIL_MODEL = "gpt-4o-mini"
VISION_MODEL = "gpt-4o-mini"
DOC_MODEL = "gpt-4o-mini"
```

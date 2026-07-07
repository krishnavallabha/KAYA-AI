# FlowSense — Frontend (Action Layer)

AI-powered supply chain intelligence for construction. This is the **frontend / live PM dashboard** — the Action Layer of the FlowSense platform built for the Kaya AI IIT India Hackathon 2026 (Supply Chain track).

It consumes the FlowSense FastAPI backend and surfaces order tracking, delay forecasting, schedule cascade impact, proactive alerts, and one-click AI-drafted actions.

## Features

- **Command Center dashboard** — KPIs, order-status mix (donut), delay-risk ranking, at-risk orders, and live alerts.
- **Material Orders** — searchable/filterable table with forecast ETA, delay probability, confidence score, lifecycle stepper, and a create-order form.
- **Schedule Graph** — interactive activity network (React Flow + dagre auto-layout) with the critical path highlighted and per-activity material drill-down.
- **Alerts** — severity-filtered feed with one-click resolve.
- **Action Drafts** — review AI-generated vendor escalation emails and execute (simulated send) in one click.
- **Ingest** — feed vendor emails, delivery photos, and Primavera XML schedules into the pipeline.
- **Dark / light theme** — toggle in the top bar; preference is remembered.
- **Demo-safe** — if the backend is unreachable, the UI transparently falls back to bundled demo data so it always renders.

## Tech stack

React 18 · Vite 5 · Tailwind CSS 3 · React Router 6 · Recharts · React Flow + dagre · lucide-react.

## Getting started

Prerequisites: Node.js 18+ and npm.

```bash
# 1. install dependencies
npm install

# 2. configure the backend URL (optional — defaults to http://localhost:8000)
cp .env.example .env
#   then edit VITE_API_BASE_URL if your API runs elsewhere

# 3. start the dev server
npm run dev          # http://localhost:5173

# production build + local preview
npm run build
npm run preview
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL of the FlowSense FastAPI backend. The app appends `/api/v1` automatically. |

## Backend connection & demo mode

The top bar shows a live connection pill:

- **Live API** — the backend responded; all data is real.
- **Demo data** — the backend was unreachable (timeout / network error), so the app served bundled demo data from `src/data/mockData.js`. Interactions (resolve alert, execute action, create order, ingest) still work against an in-memory demo store, so the full flow is demo-able without a running backend.

To run against the real backend, start it (from the repo root):

```bash
uvicorn backend.main:app --reload   # serves on http://localhost:8000
```

CORS is already open on the backend (`allow_origins=["*"]`).

## API endpoints consumed

All under `${VITE_API_BASE_URL}/api/v1`:

| Method | Path | Used by |
|---|---|---|
| GET | `/materials/` | Dashboard, Materials, Schedule, Alerts |
| POST | `/materials/` | Materials → New Order |
| GET | `/schedule/graph` | Schedule graph |
| GET | `/alerts/` | Dashboard, Alerts |
| POST | `/alerts/{id}/resolve` | Alerts → Resolve |
| GET | `/actions/drafts` | Dashboard, Actions |
| POST | `/actions/{id}/execute` | Actions → Approve & Execute |
| POST | `/ingest/email` | Ingest → Vendor Email |
| POST | `/ingest/vision` | Ingest → Delivery Photo |
| POST | `/ingest/schedule` | Ingest → Project Schedule |

Response shapes mirror `backend/schemas.py`.

## Project structure

```text
frontend/
├── index.html                 # entry, pre-paint theme script, fonts
├── vite.config.js             # Vite + optional dev proxy
├── tailwind.config.js         # class dark mode + semantic color tokens
├── src/
│   ├── main.jsx               # React root + providers + router
│   ├── App.jsx                # routes
│   ├── index.css              # Tailwind layers + light/dark CSS variables
│   ├── api/client.js          # fetch wrapper + graceful demo fallback
│   ├── data/mockData.js       # bundled demo dataset
│   ├── context/ThemeContext.jsx
│   ├── hooks/                 # useApi (polling), useChartColors
│   ├── lib/format.js          # date/number/status helpers
│   ├── components/
│   │   ├── layout/            # Sidebar, Topbar, AppLayout
│   │   ├── ui/                # Card, Badge, StatCard, Modal, Meter, Spinner…
│   │   ├── charts/            # StatusDonut, DelayRiskChart (Recharts)
│   │   ├── schedule/          # ScheduleGraph (React Flow + dagre)
│   │   ├── StatusBadges.jsx
│   │   └── ThemeToggle.jsx
│   └── pages/                 # Dashboard, Materials, Schedule, Alerts, Actions, Ingest
└── public/favicon.svg
```

## Theming

Colors are defined as semantic CSS variables in `src/index.css` for both `:root` (light) and `.dark`, and exposed to Tailwind as tokens (`bg`, `surface`, `content`, `primary`, `ok`, `warn`, `danger`, `info`). Toggling the theme flips the `.dark` class on `<html>`; charts re-read the variables via `useChartColors`.

## Deployment

Any static host works (Vercel, Netlify, Render static site, GitHub Pages). Build with `npm run build` and serve the `dist/` folder. Set `VITE_API_BASE_URL` to your deployed backend URL at build time.

---

Part of the FlowSense platform — the supply chain brain construction has been waiting for.

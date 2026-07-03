# FlowSense — Architecture Document
### AI-Powered Supply Chain Intelligence for Construction
**Hackathon:** Kaya AI IIT India Hackathon 2026 | **Track:** Supply Chain

---

## 1. Problem Statement

Construction supply chains fail silently. Materials are ordered, then visibility disappears until something goes wrong — a delayed shipment, a missed fabrication window, a cascading schedule impact that nobody caught in time. By the time a project manager knows there's a problem, it's already too late to recover without cost.

**Three questions remain unanswered on every project:**
- Where exactly is this material right now, across every source?
- When will it actually arrive, given fabrication and logistics reality?
- If it's late, what else breaks — and what should we do first?

FlowSense answers all three, in real time.

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLOWSENSE PLATFORM                        │
│                                                                   │
│   ┌─────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│   │  INGEST     │───▶│  INTELLIGENCE    │───▶│  ACTION       │  │
│   │  LAYER      │    │  LAYER           │    │  LAYER        │  │
│   └─────────────┘    └──────────────────┘    └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1 — Ingest Layer

Responsible for pulling raw, messy, multi-modal data from every source where material information lives.

```
┌──────────────────────────────────────────────────────────────┐
│                        INGEST LAYER                           │
│                                                               │
│  ┌─────────────────┐   ┌──────────────────┐                  │
│  │  Email Agent    │   │  Document Parser │                  │
│  │                 │   │                  │                  │
│  │ • Vendor emails │   │ • Packing slips  │                  │
│  │ • Delay notices │   │ • BOL documents  │                  │
│  │ • Confirmations │   │ • Submittal logs │                  │
│  └────────┬────────┘   └────────┬─────────┘                  │
│           │                     │                             │
│  ┌────────▼────────┐   ┌────────▼─────────┐                  │
│  │  Vision Agent   │   │  Schedule Parser │                  │
│  │                 │   │                  │                  │
│  │ • Delivery photos│  │ • Primavera XML  │                  │
│  │ • Site receipts │   │ • MS Project     │                  │
│  │ • Label scans   │   │ • CSV schedules  │                  │
│  └────────┬────────┘   └────────┬─────────┘                  │
│           │                     │                             │
│           └──────────┬──────────┘                             │
│                      ▼                                         │
│             ┌─────────────────┐                               │
│             │  Unified Event  │                               │
│             │  Stream (Kafka) │                               │
│             └─────────────────┘                               │
└──────────────────────────────────────────────────────────────┘
```

### Ingest Components

| Component | What It Does | Tech |
|---|---|---|
| **Email Agent** | Monitors vendor inboxes, extracts structured status from unstructured text | LangChain Agent + GPT-4o |
| **Vision Agent** | Reads delivery photos, packing slips, label scans — extracts PO number, quantity, condition | GPT-4o Vision / LLaVA |
| **Document Parser** | Parses BOL, submittals, procurement docs into structured fields | Unstructured.io + LLM extraction |
| **Schedule Parser** | Ingests Primavera / MS Project exports, maps activities to material dependencies | Python (xml.etree) + custom mapper |
| **Event Stream** | All parsed signals flow into a unified timestamped event log | Apache Kafka / Redis Streams |

---

## 4. Layer 2 — Intelligence Layer

The core of FlowSense. Three AI systems operate in parallel on the unified event stream.

```
┌──────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE LAYER                           │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Unified Event Stream (input)                 │    │
│  └───────────────────────┬──────────────────────────────────┘    │
│                           │                                        │
│         ┌─────────────────┼─────────────────┐                    │
│         ▼                 ▼                  ▼                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │  Material   │  │ Fabrication  │  │    Cascade        │        │
│  │  Tracker    │  │  Forecaster  │  │    Engine         │        │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘        │
│         │                │                    │                   │
│         └────────────────┼────────────────────┘                  │
│                          ▼                                        │
│              ┌──────────────────────┐                            │
│              │   Central State DB   │                            │
│              │  (per-SKU, per-order │                            │
│              │   per-activity)      │                            │
│              └──────────────────────┘                            │
└──────────────────────────────────────────────────────────────────┘
```

---

### 4a. Material Tracker Agent

Maintains a **single source of truth** for every material order across all ingest sources. Reconciles conflicting signals automatically.

```
Signal arrives (email says "shipped", portal says "in fabrication")
            │
            ▼
    Confidence Scoring
    • Recency weight
    • Source reliability score
    • Signal type hierarchy
            │
            ▼
    Reconciled Status per SKU
    ┌─────────────────────────────────┐
    │ Order #482 — Structural Steel   │
    │ Status: IN TRANSIT ✓            │
    │ Last signal: Delivery photo     │
    │ Confidence: 91%                 │
    │ Location: Freight hub, Pune     │
    └─────────────────────────────────┘
```

**Tech:** LangChain ReAct Agent, vector store for signal history (FAISS/Chroma), SQLite/PostgreSQL for state.

---

### 4b. Fabrication-to-Delivery Forecaster

Predicts **when a material will actually arrive** — not just the vendor's promised date. Uses historical lead times, fabrication stage signals, and logistics patterns.

```
Inputs per order:
├── Submittal approval date
├── Fabrication start signal (if available)
├── Vendor historical delivery variance
├── Current logistics leg (factory → freight → site)
└── External signals (port delays, weather flags)

            │
            ▼
    Probabilistic Forecast Model
    (Bayesian updating on each new signal)
            │
            ▼
    ┌──────────────────────────────────────┐
    │ Order #482 — Structural Steel         │
    │ Vendor promised date:  July 15        │
    │ FlowSense forecast:    July 26        │
    │ Confidence interval:   July 22–30     │
    │ Delay probability:     78%            │
    └──────────────────────────────────────┘
```

**Tech:** Prophet / NeuralProphet for time-series, Bayesian updating via PyMC or custom Kalman filter, trained on synthetic + historical PO datasets.

---

### 4c. Cascade Impact Engine

When a delay is detected or forecast, this engine **traverses the project schedule graph** to find every downstream activity at risk.

```
Project Schedule as Directed Graph:
    Activity A (Foundation) ──▶ Activity B (Steel Erection)
                                          │
                               ┌──────────┴──────────┐
                               ▼                     ▼
                    Activity C (Decking)   Activity D (MEP Rough-in)
                               │
                               ▼
                    Activity E (Concrete Pour) ← CRITICAL PATH

Material #482 (Structural Steel) feeds Activity B
    │
    ▼
Delay detected: +11 days
    │
    ▼
Graph traversal (BFS from Activity B):
    • Activity B: delayed 11 days
    • Activity C: delayed 11 days
    • Activity D: delayed 11 days
    • Activity E: delayed 11 days ← CRITICAL PATH IMPACT
    • Project completion: at risk by 11 days
    │
    ▼
Recovery Options Ranked:
    1. Expedite Order #482 — reduces delay to 4 days
    2. Resequence: start Activity D before B (saves 7 days)
    3. Substitute vendor SKU-994 (available in 3 days)
```

**Tech:** NetworkX for schedule graph, BFS/DFS traversal, LLM (GPT-4o) for recovery suggestion generation, constraint-based optimization via OR-Tools for resequencing.

---

## 5. Layer 3 — Action Layer

Surfaces intelligence as decisions and drafts actions for the PM to approve in one click.

```
┌────────────────────────────────────────────────────────────────┐
│                        ACTION LAYER                             │
│                                                                  │
│  ┌──────────────────┐  ┌───────────────────┐  ┌─────────────┐ │
│  │  Live Dashboard  │  │  Proactive Alerts  │  │  Draft      │ │
│  │                  │  │                    │  │  Actions    │ │
│  │ • Order statuses │  │ • Risk threshold   │  │             │ │
│  │ • Forecast ETAs  │  │   crossed          │  │ • Vendor    │ │
│  │ • At-risk items  │  │ • Critical path    │  │   escalation│ │
│  │ • Schedule graph │  │   impact detected  │  │   email     │ │
│  │   visualization  │  │ • Signal conflict  │  │ • RFQ draft │ │
│  │                  │  │   flagged          │  │ • PO amend  │ │
│  └──────────────────┘  └───────────────────┘  └─────────────┘ │
│                                                                  │
│                    ┌───────────────────┐                        │
│                    │   PM Reviews &    │                        │
│                    │   Approves in     │                        │
│                    │   One Click       │                        │
│                    └───────────────────┘                        │
└────────────────────────────────────────────────────────────────┘
```

---

## 6. Full Data Flow (End-to-End)

```
[Vendor Email arrives]
        │
        ▼
[Email Agent extracts: Order #482, status="shipped", date=Jul 14]
        │
        ▼
[Event pushed to Kafka stream]
        │
        ├──▶ [Material Tracker] reconciles with portal status → "IN TRANSIT, confidence 91%"
        │
        ├──▶ [Forecaster] updates ETA distribution → new P50 = Jul 26, delay prob = 78%
        │
        └──▶ [Cascade Engine] traverses schedule graph
                    │
                    ▼
             5 activities flagged at risk
             1 critical path impact detected
                    │
                    ▼
             Alert fired to PM dashboard
             Vendor escalation email drafted
             Recovery options ranked
                    │
                    ▼
             PM approves email → sent
```

---

## 7. Tech Stack

| Layer | Component | Technology |
|---|---|---|
| **Ingest** | Email parsing agent | LangChain + GPT-4o |
| **Ingest** | Vision / OCR | GPT-4o Vision or LLaVA (open-source) |
| **Ingest** | Document intelligence | Unstructured.io |
| **Ingest** | Event streaming | Apache Kafka / Redis Streams |
| **Intelligence** | Material tracker | LangChain ReAct + FAISS |
| **Intelligence** | Forecasting | Prophet / PyMC (Bayesian) |
| **Intelligence** | Schedule graph | NetworkX |
| **Intelligence** | Recovery optimization | Google OR-Tools |
| **Action** | LLM drafting | GPT-4o with structured prompts |
| **Action** | Dashboard | React + Recharts |
| **Storage** | Order state | PostgreSQL |
| **Storage** | Vector store | FAISS / Chroma |
| **Backend** | API layer | FastAPI (Python) |
| **Infra** | Deployment | Docker + Railway / Render |

---

## 8. Demo Script (2-Minute Walkthrough)

| Time | What You Show |
|---|---|
| 0:00–0:20 | Dashboard with 40 open orders, scattered statuses — show the chaos |
| 0:20–0:40 | Vision agent reads a delivery photo → auto-updates Order #482 status |
| 0:40–1:00 | Forecaster shows Order #482 has 78% delay probability, ETA July 26 |
| 1:00–1:30 | Cascade engine fires — 5 activities highlighted, critical path impacted |
| 1:30–1:50 | Recovery options appear: resequence + expedite ranked by impact |
| 1:50–2:00 | PM approves vendor escalation email in one click — done |

---

## 9. Why This Wins

| Judging Criterion | How FlowSense Addresses It |
|---|---|
| Depth beyond API calls | 3 distinct AI systems: agentic, probabilistic forecasting, graph traversal |
| Real construction problem | Delay cascades are the #1 cost driver on construction projects |
| Multiple AI techniques | VLM + time-series + graph modeling + LLM agents |
| Agentic systems | Email agent + vision agent act autonomously, PM only approves |
| Construction-specific AI | RAG over PO/vendor history, schedule-aware context |
| Demo-able in 2 minutes | Linear narrative with a clear before/after |

---

## 10. Team

| Name | Institution | Role |
|---|---|---|
| [Member 1] | IIT [X] | ML / Forecasting |
| [Member 2] | IIT [X] | Agentic Systems / Backend |
| [Member 3] | IIT [X] | Vision / Document Intelligence |
| [Member 4] | IIT [X] | Frontend / Dashboard |

---

*FlowSense — The supply chain brain construction has been waiting for.*

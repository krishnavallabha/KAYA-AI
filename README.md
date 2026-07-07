# FlowSense — Role 2: AI & Predictive Modeling

Working code for the three things Role 2 owns:

1. **Ingest Layer extraction agents** — Email Agent, Vision Agent, Document Parser
2. **Material Tracker Agent** — multi-source reconciliation with confidence scoring
3. **Fabrication-to-Delivery Forecaster** — Bayesian ETA + delay-probability engine

Everything runs standalone against generated synthetic data (no API key needed),
and upgrades to real GPT-4o / GPT-4o Vision calls the instant `OPENAI_API_KEY`
is set in the environment — no code changes required.

## Quick start

```bash
pip install -r requirements.txt
python demo.py
```

To run in LIVE mode against real GPT-4o:

```bash
export OPENAI_API_KEY=sk-...
python demo.py
```

## File map

```
config.py                    # LIVE vs FALLBACK mode switch, OpenAI client
schema.py                    # Event dataclass + EventStream (Kafka stand-in)
synthetic_data.py            # Generates mock emails, label images, BOL/packing
                              #   slip/submittal text, and orders
agents/
  email_agent.py             # Vendor email -> structured Event
  vision_agent.py            # Delivery photo/label -> structured Event (real OCR fallback)
  document_parser.py         # BOL / packing slip / submittal log -> structured Event
intelligence/
  material_tracker.py        # Reconciles Events per order into one verified record
  forecaster.py               # Sequential Bayesian ETA + delay probability
demo.py                      # Wires all of the above end to end
data/                        # Generated fixtures + dashboard_payload.json output
```

## How each piece maps to the problem statements

**Problem 1 (fragmented tracking):** Email/Vision/Document agents each normalize
their source into the same `Event` schema (`schema.py`) and push it to a shared
`EventStream`. The `MaterialTrackerAgent` then pools events per order, weighting
each by `source_reliability x recency x extraction_confidence`, and picks the
status with the most accumulated weight as the verified answer. When two
statuses are close in weight, it explicitly flags `signal_conflict=True` —
this is the "email says shipped, portal shows fabrication" case surfaced for
PM review rather than silently guessed at.

**Problem 2 (inaccurate ETAs):** `DeliveryForecaster` treats the true delivery
date as a latent Normal variable and does closed-form Bayesian (Normal-Normal
conjugate) updating: start from a vendor-reliability-based prior, then fold in
the fabrication-stage signal, the Material Tracker's reconciled ETA, and any
disruption flags — each as a noisy observation weighted by how much to trust
it. Output is a forecast date, a 90% confidence interval, and an explicit
delay probability against the originally promised date.

**Problem 3 (cascades):** Out of scope for Role 2 — this is Role 1's Cascade
Impact Engine. The forecaster's output (`forecast_date`, `delay_probability`,
`days_at_risk`) is exactly the payload Role 1's graph traversal consumes to
decide which downstream activities are at risk. See `dashboard_payload.json`
for the exact shape produced.

## Design notes / what's simplified for the demo vs. production

- **LangChain**: the agents follow the LangChain ReAct extraction pattern
  (structured-output prompt, deterministic fallback) implemented directly
  rather than pulled in as a runtime dependency, to keep the demo fast and
  dependency-light. Wrapping `EmailAgent.extract` / etc. as LangChain `Tool`s
  under an `AgentExecutor` is a thin, non-breaking upgrade — the JSON contract
  each agent returns doesn't change.
- **Vision fallback**: uses real Tesseract OCR (not a scripted/ground-truth
  shortcut) over synthetically rendered label images, so extraction accuracy
  and `extraction_confidence` reflect genuine OCR behavior.
- **Vector store**: `material_tracker.SimpleVectorIndex` wraps FAISS when
  available and falls back to a deterministic hashed-vector cosine search
  when no embeddings API key is present, so historical-pattern lookups work
  offline too.
- **Prophet/PyMC**: the forecaster uses closed-form Bayesian updating
  (precision-weighted Normal-Normal), which is mathematically the same
  updating principle Prophet/PyMC would apply, without requiring a real
  multi-shipment historical time series per vendor to fit against. Swapping
  in Prophet per-vendor once that history exists is additive, not a rewrite
  — `forecast()`'s return shape stays the same.
- **Synthetic data determinism**: `synthetic_data.py` seeds `random.seed(7)`
  so demo runs are reproducible; delete the seed line for varied fixtures.

## Handoff to Role 1 (backend/graph) and Role 3 (frontend/streaming)

- Role 3's Kafka/Redis producer should call the same agents and push
  `Event.to_dict()` payloads — the `EventStream` class here has the same
  `publish()`/`all()` shape as a real producer/consumer would, so swapping
  the transport is a drop-in change.
- Role 1's Cascade Impact Engine should consume `dashboard_payload.json`'s
  shape (`forecast_date`, `delay_probability`, `days_at_risk` per order_id) to
  decide which schedule nodes are now at risk.

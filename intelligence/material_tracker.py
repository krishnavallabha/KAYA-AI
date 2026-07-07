"""
FlowSense Role 2 - Material Tracker Agent

Single source of truth per order/SKU. Reconciles conflicting signals
from email, vision, and document sources using confidence scoring based
on:
  1. Source reliability (schema.SOURCE_RELIABILITY - documents > vision > email)
  2. Recency (exponential decay - a signal from 3 days ago matters less
     than one from this morning)
  3. The extracting agent's own extraction_confidence (how sure was the
     Email/Vision/Doc agent about what it read)

These three multiply into a per-event "vote weight". Votes are pooled by
status value; the status with the most accumulated weight wins, and its
share of total weight becomes the tracker's reported confidence. When the
top two statuses are close, that's a genuine signal conflict, exactly
the "email claims shipped vs portal shows fabrication" case, and gets
flagged for the dashboard's proactive alerting.

Reasoning trace: each reconciliation records an explicit
observe -> weigh -> act trace, the same Thought/Action/Observation shape
a LangChain ReAct agent produces. It's implemented directly here (no
LangChain runtime) so it stays deterministic and dependency-light for
the demo; wrapping this in an actual AgentExecutor with tools (e.g. "look
up vendor's historical reliability") is a drop-in upgrade since the
scoring logic doesn't change.

A lightweight FAISS vector index over raw_excerpt text lets the tracker
retrieve similar historical signals (e.g. "have we seen this vendor's
delay language before") without needing an embeddings API key - it uses
a deterministic hashed bag-of-characters vectorizer in fallback mode and
swaps to real OpenAI embeddings automatically when a key is present.
"""

import math
import sys
import os
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import SOURCE_RELIABILITY, Event
from config import get_openai_client, LIVE_MODE

RECENCY_HALF_LIFE_HOURS = 24.0  # a signal loses half its recency weight per day


def _recency_weight(observed_at_iso: str, now: datetime = None) -> float:
    now = now or datetime.utcnow()
    try:
        observed = datetime.fromisoformat(observed_at_iso)
    except ValueError:
        return 0.5
    hours_ago = max((now - observed).total_seconds() / 3600.0, 0.0)
    decay = math.log(2) / RECENCY_HALF_LIFE_HOURS
    return math.exp(-decay * hours_ago)


def _vote_weight(event: Event, now: datetime = None) -> float:
    source_w = SOURCE_RELIABILITY.get(event.source, 0.5)
    recency_w = _recency_weight(event.observed_at, now)
    return source_w * recency_w * event.extraction_confidence


class SimpleVectorIndex:
    """Hashed bag-of-characters vector index, used as a FAISS/Chroma
    stand-in when no embeddings API key is configured. Swaps to real
    OpenAI embeddings automatically in LIVE mode."""

    def __init__(self, dim: int = 256):
        self.dim = dim
        self._vecs = []
        self._payloads = []
        self._faiss = None
        try:
            import faiss
            import numpy as np
            self._faiss = faiss.IndexFlatL2(dim)
            self._np = np
        except Exception:
            self._faiss = None

    def _hash_embed(self, text: str):
        vec = [0.0] * self.dim
        for i, ch in enumerate(text.lower()):
            vec[hash((ch, i % 5)) % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _embed(self, text: str):
        if LIVE_MODE:
            try:
                client = get_openai_client()
                resp = client.embeddings.create(model="text-embedding-3-small", input=text)
                vec = resp.data[0].embedding[: self.dim]
                vec = vec + [0.0] * (self.dim - len(vec))
                return vec
            except Exception:
                pass
        return self._hash_embed(text)

    def add(self, text: str, payload: dict):
        vec = self._embed(text)
        if self._faiss is not None:
            self._faiss.add(self._np.array([vec], dtype="float32"))
        self._vecs.append(vec)
        self._payloads.append(payload)

    def search(self, text: str, k: int = 3):
        if not self._vecs:
            return []
        query = self._embed(text)
        if self._faiss is not None:
            import numpy as np
            D, I = self._faiss.search(np.array([query], dtype="float32"), min(k, len(self._vecs)))
            return [self._payloads[i] for i in I[0] if i != -1]
        # brute-force cosine similarity fallback
        def cos(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            return dot  # vectors are already normalized in _hash_embed
        scored = sorted(
            range(len(self._vecs)), key=lambda i: cos(query, self._vecs[i]), reverse=True
        )
        return [self._payloads[i] for i in scored[:k]]


class MaterialTrackerAgent:
    def __init__(self):
        self.state = {}          # order_id -> verified record
        self.history = defaultdict(list)  # order_id -> reasoning traces
        self.index = SimpleVectorIndex()

    def ingest(self, events: list, now: datetime = None) -> dict:
        """Reconcile a batch of events (any mix of sources) into verified
        per-order records. Returns {order_id: verified_record}."""
        by_order = defaultdict(list)
        for e in events:
            by_order[e.order_id].append(e)
            self.index.add(e.raw_excerpt or e.signal_type, {
                "order_id": e.order_id, "source": e.source,
                "signal_type": e.signal_type, "observed_at": e.observed_at,
            })

        for order_id, order_events in by_order.items():
            self._reconcile_order(order_id, order_events, now)

        return self.state

    def _reconcile_order(self, order_id: str, events: list, now: datetime = None):
        trace = [f"Observed {len(events)} new signal(s) for {order_id}: "
                 + ", ".join(f"{e.source}:{e.status}" for e in events)]

        status_weight = defaultdict(float)
        eta_candidates = []
        latest_condition = None
        latest_quantity = None
        best_event_per_status = {}

        for e in events:
            w = _vote_weight(e, now)
            if e.status:
                status_weight[e.status] += w
                if e.status not in best_event_per_status or w > best_event_per_status[e.status][1]:
                    best_event_per_status[e.status] = (e, w)
            if e.eta_estimate:
                eta_candidates.append((e.eta_estimate, w))
            if e.condition:
                latest_condition = e.condition
            if e.quantity:
                latest_quantity = e.quantity

        trace.append("Vote weights (source_reliability x recency x extraction_confidence): "
                     + ", ".join(f"{s}={w:.2f}" for s, w in status_weight.items()))

        if status_weight:
            total = sum(status_weight.values())
            ranked = sorted(status_weight.items(), key=lambda kv: kv[1], reverse=True)
            top_status, top_weight = ranked[0]
            confidence = round(top_weight / total, 3) if total else 0.0

            conflict = len(ranked) > 1 and (ranked[0][1] - ranked[1][1]) / total < 0.25
        else:
            top_status, confidence, conflict, ranked = None, 0.0, False, []

        best_eta = max(eta_candidates, key=lambda x: x[1])[0] if eta_candidates else None

        prior = self.state.get(order_id, {})
        record = {
            "order_id": order_id,
            "verified_status": top_status or prior.get("verified_status"),
            "confidence": confidence if status_weight else prior.get("confidence", 0.0),
            "eta_estimate": best_eta or prior.get("eta_estimate"),
            "condition": latest_condition or prior.get("condition"),
            "quantity": latest_quantity or prior.get("quantity"),
            "signal_conflict": conflict,
            "conflicting_sources": [e.source for e in events] if conflict else [],
            "last_updated": (now or datetime.utcnow()).isoformat(),
            "contributing_signals": [e.event_id for e in events],
        }

        if conflict:
            trace.append(
                f"CONFLICT DETECTED: top two statuses within 25% of each other "
                f"({ranked[0][0]}={ranked[0][1]:.2f} vs {ranked[1][0]}={ranked[1][1]:.2f}) "
                f"-> flagging for PM review."
            )
        else:
            trace.append(f"Resolved verified_status={top_status} with confidence={confidence}")

        self.state[order_id] = record
        self.history[order_id].append(trace)

    def get_record(self, order_id: str) -> dict:
        return self.state.get(order_id, {})

    def get_reasoning_trace(self, order_id: str) -> list:
        return self.history.get(order_id, [])

    def all_records(self) -> list:
        return list(self.state.values())

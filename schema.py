"""
FlowSense Role 2 - Shared Event Schema

Every Ingest Layer agent (Email, Vision, Document) normalizes its output
into this single Event shape before pushing to the Unified Event Stream.
The Material Tracker and Forecaster only ever consume Events, never raw
text/images, which is what lets three very different extraction agents
feed one reconciliation pipeline.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import itertools

_counter = itertools.count(1)

# Base reliability weight per source type. This is the "how much do we
# trust this channel in general" prior the Material Tracker starts from
# before layering on recency and extraction-confidence.
SOURCE_RELIABILITY = {
    "email": 0.60,       # informal, prone to stale/optimistic vendor language
    "vision": 0.75,      # photographic evidence of physical state, decent trust
    "document": 0.90,    # formal paperwork (BOL, packing slip), high trust
    "schedule": 1.00,    # internal ground truth for planned dates
}

VALID_STATUSES = {
    "not_started", "in_fabrication", "fabrication_complete",
    "shipped", "in_transit", "delivered", "delayed", "damaged",
}


@dataclass
class Event:
    order_id: str
    source: str                     # "email" | "vision" | "document" | "schedule"
    signal_type: str                # e.g. delay_notice, shipment_confirmation
    status: Optional[str] = None    # normalized status, see VALID_STATUSES
    eta_estimate: Optional[str] = None   # ISO date string, agent's best guess
    quantity: Optional[int] = None
    condition: Optional[str] = None
    extraction_confidence: float = 0.5   # agent's own confidence in its parse
    observed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    raw_excerpt: str = ""
    event_id: str = field(default_factory=lambda: f"EVT-{next(_counter):05d}")

    def to_dict(self):
        return asdict(self)


class EventStream:
    """Minimal in-memory stand-in for the Kafka / Redis Streams unified
    event stream Role 3 owns in production. Same publish/consume contract
    so swapping in a real Kafka producer later is a drop-in change."""

    def __init__(self):
        self._events = []

    def publish(self, event: Event):
        self._events.append(event)
        return event

    def all(self):
        return list(self._events)

    def for_order(self, order_id: str):
        return [e for e in self._events if e.order_id == order_id]

"""
FlowSense Role 2 - Email Agent

Continuously "monitors" a vendor inbox (here: a list of email dicts from
synthetic_data) and extracts structured status updates from unstructured
text. In LIVE mode this calls GPT-4o with a JSON-schema-constrained
prompt. In FALLBACK mode it uses a regex/keyword extractor so the whole
pipeline is runnable and demoable with zero API cost/setup.

Production note: this class is intentionally a thin, swappable wrapper.
To upgrade to a full LangChain ReAct agent with tool-calling (e.g. a
"look up order in DB" tool), wrap `extract()` as a LangChain Tool and
drive it from an AgentExecutor - the JSON contract below doesn't change.
"""

import json
import re
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_openai_client, EMAIL_MODEL, LIVE_MODE
from schema import Event

SYSTEM_PROMPT = """You are the FlowSense Email Agent. You extract structured
supply-chain status updates from raw vendor emails. Always respond with
strict JSON matching this schema, and nothing else:

{
  "order_id": string,            // PO number mentioned, e.g. "PO-1002"
  "signal_type": string,         // one of: delay_notice, shipment_confirmation,
                                  //   fabrication_update, condition_issue, other
  "status": string,              // one of: not_started, in_fabrication,
                                  //   fabrication_complete, shipped, in_transit,
                                  //   delivered, delayed, damaged
  "eta_estimate": string|null,   // ISO date YYYY-MM-DD if mentioned, else null
  "quantity": number|null,       // units mentioned, else null
  "extraction_confidence": number // 0-1, your confidence in this extraction
}
"""

_STATUS_KEYWORDS = [
    (r"\bdamag", "damaged"),
    (r"\bdeliver", "delivered"),
    (r"\bin transit|left our facility|shipped\b", "in_transit"),
    (r"\bfabrication.*(complete|finished)", "fabrication_complete"),
    (r"\bfabrication|production", "in_fabrication"),
    (r"\bdelay|behind schedule|running behind", "delayed"),
]

_SIGNAL_KEYWORDS = [
    (r"delay notice|running behind|won't complete", "delay_notice"),
    (r"shipment confirmed|has left our facility|tracking shows", "shipment_confirmation"),
    (r"production update|% complete|currently in fabrication", "fabrication_update"),
    (r"damage|qa\b", "condition_issue"),
]

_PO_RE = re.compile(r"\bPO-\d{3,6}\b")
_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
_QTY_RE = re.compile(r"\b(\d{1,5})\s*units\b", re.IGNORECASE)


def _fallback_extract(body: str) -> dict:
    """Regex/keyword extractor used when no OPENAI_API_KEY is configured."""
    lower = body.lower()

    order_match = _PO_RE.search(body)
    order_id = order_match.group(0) if order_match else "UNKNOWN"

    status = "in_fabrication"
    for pattern, label in _STATUS_KEYWORDS:
        if re.search(pattern, lower):
            status = label
            break

    signal_type = "other"
    for pattern, label in _SIGNAL_KEYWORDS:
        if re.search(pattern, lower):
            signal_type = label
            break

    date_match = _DATE_RE.search(body)
    eta_estimate = date_match.group(1) if date_match else None

    qty_match = _QTY_RE.search(body)
    quantity = int(qty_match.group(1)) if qty_match else None

    # Confidence heuristic: more matched fields -> higher confidence.
    fields_found = sum(x is not None for x in [order_match, date_match, qty_match]) 
    extraction_confidence = round(0.55 + 0.12 * fields_found, 2)

    return {
        "order_id": order_id,
        "signal_type": signal_type,
        "status": status,
        "eta_estimate": eta_estimate,
        "quantity": quantity,
        "extraction_confidence": min(extraction_confidence, 0.95),
    }


def _live_extract(body: str) -> dict:
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=EMAIL_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": body},
        ],
    )
    return json.loads(resp.choices[0].message.content)


class EmailAgent:
    """Extracts structured events from raw vendor email text."""

    def __init__(self):
        self.live = LIVE_MODE

    def extract(self, email: dict) -> Event:
        body = email["body"]
        try:
            parsed = _live_extract(body) if self.live else _fallback_extract(body)
        except Exception:
            # Any live-call failure (rate limit, bad JSON, network) degrades
            # gracefully to the deterministic fallback rather than dropping
            # the signal on the floor.
            parsed = _fallback_extract(body)

        return Event(
            order_id=parsed.get("order_id", "UNKNOWN"),
            source="email",
            signal_type=parsed.get("signal_type", "other"),
            status=parsed.get("status"),
            eta_estimate=parsed.get("eta_estimate"),
            quantity=parsed.get("quantity"),
            extraction_confidence=float(parsed.get("extraction_confidence", 0.5)),
            observed_at=email.get("received_at", datetime.utcnow().isoformat()),
            raw_excerpt=body[:180],
        )

    def process_inbox(self, emails: list) -> list:
        return [self.extract(e) for e in emails]

"""
FlowSense Role 2 - Document Parser Agent

Extracts structured fields from procurement documents: Bills of Lading,
packing slips, and submittal log entries.

In production, Unstructured.io handles the upstream step of turning a
raw PDF/scan into clean partitioned text; this agent picks up from there
and does the field-level extraction. That upstream partitioning step
isn't reproducible without real PDFs, so synthetic_data.py hands this
agent already-partitioned text, exactly matching what Unstructured.io's
`partition()` output looks like.

LIVE mode: GPT-4o structured extraction. FALLBACK mode: regex extraction
tuned to each document type's field layout.
"""

import json
import re
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_openai_client, DOC_MODEL, LIVE_MODE
from schema import Event

SYSTEM_PROMPT = """You are the FlowSense Document Parser. You extract
structured fields from procurement documents (Bills of Lading, packing
slips, submittal logs). Respond with strict JSON only:

{
  "doc_type": string,        // "bill_of_lading" | "packing_slip" | "submittal_log"
  "order_id": string,        // PO reference
  "quantity": number|null,
  "status": string,          // one of: shipped, in_transit, delivered,
                              //   fabrication_complete, not_started
  "eta_estimate": string|null,  // ISO date if a ship/approval date implies one
  "extraction_confidence": number
}
"""

_PO_RE = re.compile(r"\bPO[-\s]?(\d{3,6})\b", re.IGNORECASE)
_QTY_RE = re.compile(r"(?:Quantity|Units Packed)\s*:\s*(\d+)", re.IGNORECASE)
_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

_DOC_TYPE_HINTS = [
    (r"BILL OF LADING", "bill_of_lading", "shipped"),
    (r"PACKING SLIP", "packing_slip", "shipped"),
    (r"SUBMITTAL LOG", "submittal_log", "fabrication_complete"),
]


def _fallback_extract(text: str) -> dict:
    doc_type, status = "unknown", "in_fabrication"
    for pattern, dtype, default_status in _DOC_TYPE_HINTS:
        if re.search(pattern, text, re.IGNORECASE):
            doc_type, status = dtype, default_status
            break

    po_match = _PO_RE.search(text)
    order_id = f"PO-{po_match.group(1)}" if po_match else "UNKNOWN"

    qty_match = _QTY_RE.search(text)
    quantity = int(qty_match.group(1)) if qty_match else None

    date_match = _DATE_RE.search(text)
    eta_estimate = date_match.group(1) if date_match else None

    fields_found = sum(x is not None for x in [po_match, qty_match, date_match])
    extraction_confidence = round(0.65 + 0.1 * fields_found, 2)

    return {
        "doc_type": doc_type,
        "order_id": order_id,
        "quantity": quantity,
        "status": status,
        "eta_estimate": eta_estimate,
        "extraction_confidence": min(extraction_confidence, 0.97),
    }


def _live_extract(text: str) -> dict:
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=DOC_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return json.loads(resp.choices[0].message.content)


class DocumentParserAgent:
    """Extracts structured events from procurement document text."""

    def __init__(self):
        self.live = LIVE_MODE

    def extract(self, doc: dict) -> Event:
        text = doc["raw_text"]
        try:
            parsed = _live_extract(text) if self.live else _fallback_extract(text)
        except Exception:
            parsed = _fallback_extract(text)

        return Event(
            order_id=parsed.get("order_id", "UNKNOWN"),
            source="document",
            signal_type=parsed.get("doc_type", "unknown"),
            status=parsed.get("status"),
            eta_estimate=parsed.get("eta_estimate"),
            quantity=parsed.get("quantity"),
            extraction_confidence=float(parsed.get("extraction_confidence", 0.7)),
            observed_at=datetime.utcnow().isoformat(),
            raw_excerpt=text[:180],
        )

    def process_documents(self, docs: list) -> list:
        return [self.extract(d) for d in docs]

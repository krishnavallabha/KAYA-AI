import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timezone, timedelta
from backend.models import Signal, Material
from backend.intelligence.material_tracker import reconcile_material_status
from intelligence.material_tracker import MaterialTrackerAgent
from schema import Event

def test_reconcile_material_status_empty():
    mat = Material(status="ORDERED", current_location="Site")
    res = reconcile_material_status(mat, [])
    assert res["status"] == "ORDERED"
    assert res["current_location"] == "Site"
    assert res["confidence_score"] == 1.0

def test_reconcile_material_status_signals():
    mat = Material(status="ORDERED", current_location="Site")
    sig1 = Signal(source="EMAIL", parsed_status="IN_TRANSIT", timestamp=datetime.now(timezone.utc) - timedelta(hours=2), raw_content='{"current_location": "Port"}')
    sig2 = Signal(source="VISION", parsed_status="DELIVERED", timestamp=datetime.now(timezone.utc), raw_content='{"current_location": "Site"}')
    
    # VISION signal is more recent and has higher base credibility, so it should win
    res = reconcile_material_status(mat, [sig1, sig2])
    assert res["status"] == "DELIVERED"
    assert res["current_location"] == "Site"

def test_material_tracker_agent():
    tracker = MaterialTrackerAgent()
    events = [
        Event(
            order_id="PO-1",
            source="email",
            signal_type="status_update",
            status="in_transit",
            extraction_confidence=0.8,
            observed_at=(datetime.utcnow() - timedelta(hours=1)).isoformat()
        ),
        Event(
            order_id="PO-1",
            source="vision",
            signal_type="delivery_photo",
            status="delivered",
            extraction_confidence=0.95,
            observed_at=datetime.utcnow().isoformat()
        )
    ]
    tracker.ingest(events)
    reconciled = tracker.get_record("PO-1")
    assert reconciled["verified_status"] == "delivered"
    assert reconciled["confidence"] > 0.5
    assert reconciled["signal_conflict"] is True

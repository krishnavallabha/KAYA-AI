import math
from datetime import datetime, timezone
from typing import List, cast
from backend.models import Signal, Material


SOURCE_CREDIBILITY = {
    "VISION": 0.95,
    "PORTAL": 0.90,
    "EMAIL": 0.80,
    "MANUAL": 1.00
}


STATUS_WEIGHT = {
    "ORDERED": 1,
    "FABRICATING": 2,
    "SHIPPED": 3,
    "IN_TRANSIT": 4,
    "DELIVERED": 5
}


def reconcile_material_status(material: Material, signals: List[Signal]) -> dict:
    if not signals:
        return {
            "status": cast(str, material.status),
            "current_location": cast(str, material.current_location) if material.current_location is not None else None,
            "confidence_score": 1.0
        }
    now = datetime.now(timezone.utc)
    best_signal = None
    max_score = -1.0
    for sig in signals:
        base_cred = SOURCE_CREDIBILITY.get(cast(str, sig.source), 0.5)
        sig_time = cast(datetime, sig.timestamp)
        if sig_time.tzinfo is None:
            sig_time = sig_time.replace(tzinfo=timezone.utc)
        time_elapsed_hours = (now - sig_time).total_seconds() / 3600.0
        lambda_decay = 0.05 
        recency_weight = math.exp(-lambda_decay * time_elapsed_hours)
        signal_score = base_cred * recency_weight
        status_stage = STATUS_WEIGHT.get(cast(str, sig.parsed_status or "ORDERED"), 1)
        composite_score = signal_score + (status_stage * 0.01)
        if composite_score > max_score:
            max_score = composite_score
            best_signal = sig
    if best_signal:
        reconciled_status = cast(str, best_signal.parsed_status or material.status)
        location = cast(str, material.current_location) if material.current_location is not None else None
        if best_signal.source == "EMAIL" or best_signal.source == "VISION":
            try:
                import json
                parsed_data = json.loads(cast(str, best_signal.raw_content))
                location = parsed_data.get("current_location", location)
            except Exception:
                pass
        final_confidence = min(max(max_score - (STATUS_WEIGHT.get(reconciled_status, 1) * 0.01), 0.0), 1.0)
        return {
            "status": reconciled_status,
            "current_location": location,
            "confidence_score": round(final_confidence, 2)
        }
    return {
        "status": cast(str, material.status),
        "current_location": cast(str, material.current_location) if material.current_location is not None else None,
        "confidence_score": 1.0
    }

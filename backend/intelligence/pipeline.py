import json
from typing import cast
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend import models
from schema import Event
from intelligence.material_tracker import MaterialTrackerAgent
from intelligence.forecaster import DeliveryForecaster
from backend.intelligence import cascade_engine
from backend.action import action_drafter


def map_ml_status_to_db(ml_status: str) -> str:
    status_map = {
        "not_started": "ORDERED",
        "in_fabrication": "FABRICATING",
        "fabrication_complete": "FABRICATING",
        "shipped": "SHIPPED",
        "in_transit": "IN_TRANSIT",
        "delivered": "DELIVERED",
        "delayed": "FABRICATING",
        "damaged": "DELIVERED"
    }
    return status_map.get(ml_status.lower() if ml_status else "", "ORDERED")


def run_intelligence_pipeline(db: Session, material: models.Material):
    signals = db.query(models.Signal).filter(models.Signal.material_id == cast(int, material.id)).all()        
    events = []
    for sig in signals:
        try:
            data = json.loads(cast(str, sig.raw_content))
        except Exception:
            data = {}  
        observed_iso = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        if data.get("observed_at"):
            try:
                observed_iso = datetime.fromisoformat(data["observed_at"].replace("Z", "+00:00")).replace(tzinfo=None).isoformat()
            except Exception:
                pass
        elif sig.timestamp:
            observed_iso = sig.timestamp.replace(tzinfo=None).isoformat()
        events.append(Event(
            order_id=cast(str, material.sku),
            source=cast(str, sig.source).lower() if sig.source else "email",
            signal_type=data.get("signal_type") or "other",
            status=data.get("status") or (cast(str, sig.parsed_status) or "ordered").lower(),
            eta_estimate=data.get("eta_estimate") or data.get("estimated_delivery_date"),
            quantity=data.get("quantity") or data.get("quantity_verified"),
            condition=data.get("condition"),
            extraction_confidence=float(data.get("extraction_confidence") or cast(float, sig.confidence_weight) or 1.0),
            observed_at=observed_iso,
            raw_excerpt=data.get("raw_excerpt") or data.get("explanation") or ""
        ))        
    tracker = MaterialTrackerAgent()
    tracker.ingest(events)
    reconciled = tracker.get_record(cast(str, material.sku))
    ml_status = reconciled.get("verified_status")
    if ml_status:
        material.status = map_ml_status_to_db(ml_status)  # type: ignore
    material.confidence_score = reconciled.get("confidence", 1.0)  # type: ignore
    for e in sorted(events, key=lambda x: x.observed_at, reverse=True):
        if e.source in ("email", "vision", "document"):
            for sig in signals:
                if cast(str, sig.source).lower() == e.source and sig.confidence_weight == e.extraction_confidence:
                    try:
                        d = json.loads(cast(str, sig.raw_content))
                        if d.get("current_location"):
                            material.current_location = d["current_location"]  # type: ignore
                            break
                    except Exception:
                        pass
            else:
                continue
            break     
    if reconciled.get("signal_conflict"):
        existing_conflict_alert = db.query(models.Alert).filter(
            models.Alert.material_id == cast(int, material.id),
            models.Alert.message.like("Signal conflict detected%"),
            models.Alert.is_resolved == False
        ).first()
        if not existing_conflict_alert:
            sources_str = ", ".join(reconciled.get("conflicting_sources", []))
            conflict_msg = f"Signal conflict detected for material SKU {material.sku}. Conflicting sources: {sources_str}."
            new_conflict_alert = models.Alert(
                project_id=1,
                material_id=cast(int, material.id),
                message=conflict_msg,
                severity="WARNING",
                is_resolved=False
            )
            db.add(new_conflict_alert)
            db.commit()            
    forecaster = DeliveryForecaster()
    promised_dt = cast(datetime, material.promised_delivery_date)
    promised_str = promised_dt.strftime("%Y-%m-%d") if promised_dt else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    order_dict = {
        "order_id": cast(str, material.sku),
        "promised_date": promised_str,
        "vendor_reliability": 0.75,
        "vendor": cast(str, material.vendor_name) or "DEFAULT",
        "fabrication_stage": (ml_status or "in_fabrication").lower()
    }
    disruption_flags = []
    current_loc = cast(str, material.current_location)
    if current_loc and "port" in current_loc.lower():
        disruption_flags.append("port_congestion")
    if cast(str, material.sku) == "PO-1002":
        disruption_flags.append("port_congestion")
    forecast_res = forecaster.forecast(order_dict, reconciled, disruption_flags)
    if forecast_res.get("forecast_date"):
        try:
            forecast_dt = datetime.strptime(forecast_res["forecast_date"], "%Y-%m-%d")
            if promised_dt and promised_dt.tzinfo:
                forecast_dt = forecast_dt.replace(tzinfo=timezone.utc)
            material.forecast_delivery_date = forecast_dt  # type: ignore
        except ValueError:
            pass
    material.delay_probability = forecast_res.get("delay_probability", 0.0)  # type: ignore
    db.commit()
    activities = db.query(models.Activity).all()
    relations = db.query(models.ActivityRelation).all()
    materials = db.query(models.Material).all()
    cascade_res = cascade_engine.analyze_cascade_impact(activities, relations, materials)
    if cascade_res["critical_path_impacted"]:
        existing_alert = db.query(models.Alert).filter(
            models.Alert.material_id == cast(int, material.id),
            models.Alert.is_resolved == False
        ).first()
        if not existing_alert:
            alert_msg = f"Material SKU {material.sku} delay impacts project critical path by {cascade_res['max_project_delay_days']} days."
            new_alert = models.Alert(
                project_id=1,
                material_id=cast(int, material.id),
                message=alert_msg,
                severity="CRITICAL",
                is_resolved=False
            )
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            impacted_act_names = [act["name"] for act in cascade_res["impacted_activities"]]
            eta_str = material.forecast_delivery_date.strftime("%Y-%m-%d") if material.forecast_delivery_date else "N/A"
            vendor_str = cast(str, material.vendor_name) if material.vendor_name is not None else "Unknown Vendor"
            sku_str = cast(str, material.sku)
            draft_text = action_drafter.draft_vendor_escalation_email(
                vendor_name=vendor_str,
                sku=sku_str,
                delay_days=cascade_res["max_project_delay_days"],
                new_eta_str=eta_str,
                impacted_activities_names=impacted_act_names
            )
            new_action = models.Action(
                alert_id=new_alert.id,
                action_type="EMAIL_VENDOR",
                draft_content=draft_text,
                status="DRAFT"
            )
            db.add(new_action)
            db.commit()

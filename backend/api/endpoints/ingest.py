import json
from typing import cast
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.ingest import email_parser, vision_parser, schedule_parser
from backend.intelligence import material_tracker, forecaster, cascade_engine
from backend.action import action_drafter


router = APIRouter()


def run_intelligence_pipeline(db:Session,material:models.Material):
    signals = db.query(models.Signal).filter(models.Signal.material_id == material.id).all()
    tracker_res = material_tracker.reconcile_material_status(material, signals)
    material.status = tracker_res["status"]
    material.current_location = tracker_res["current_location"]
    material.confidence_score = tracker_res["confidence_score"]
    forecast = forecaster.calculate_delivery_forecast(material)
    material.forecast_delivery_date = forecast["forecast_delivery_date"]
    material.delay_probability = forecast["delay_probability"]
    db.commit()
    activities = db.query(models.Activity).all()
    relations = db.query(models.ActivityRelation).all()
    materials = db.query(models.Material).all()
    cascade_res = cascade_engine.analyze_cascade_impact(activities, relations, materials)
    if cascade_res["critical_path_impacted"]:
        existing_alert = db.query(models.Alert).filter(
            models.Alert.material_id == material.id,
            models.Alert.is_resolved == False
        ).first()
        if not existing_alert:
            alert_msg = f"Material SKU {material.sku} delay impacts project critical path by {cascade_res['max_project_delay_days']} days."
            new_alert = models.Alert(
                project_id=1,
                material_id=material.id,
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


@router.post("/email")
def ingest_email(email_text:str=Form(...),material_sku:str=Form(...), db:Session=Depends(get_db)):
    material = db.query(models.Material).filter(models.Material.sku == material_sku).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material SKU not found")
    parse_res = email_parser.parse_vendor_email(email_text)
    new_signal = models.Signal(
        material_id=material.id,
        source="EMAIL",
        raw_content=json.dumps(parse_res),
        parsed_status=parse_res.get("status", "ORDERED"),
        confidence_weight=parse_res.get("confidence_weight", 0.8)
    )
    db.add(new_signal)
    db.commit()
    run_intelligence_pipeline(db, material)
    return {
        "message":"Email ingested successfully", 
        "parsed_data":parse_res}


@router.post("/vision")
async def ingest_vision(material_sku:str=Form(...),file:UploadFile=File(...),db:Session=Depends(get_db)):
    material = db.query(models.Material).filter(models.Material.sku == material_sku).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material SKU not found")
    file_bytes = await file.read()
    parse_res = vision_parser.parse_delivery_image(file_bytes)
    new_signal = models.Signal(
        material_id=material.id,
        source="VISION",
        raw_content=json.dumps(parse_res),
        parsed_status=parse_res.get("status", "DELIVERED"),
        confidence_weight=0.95
    )
    db.add(new_signal)
    db.commit()
    run_intelligence_pipeline(db, material)
    return {"message": "Vision photo ingested successfully", "parsed_data": parse_res}


@router.post("/schedule")
async def ingest_schedule(file:UploadFile=File(...),db:Session=Depends(get_db)):
    file_bytes = await file.read()
    xml_content = file_bytes.decode("utf-8")
    activities, relationships = schedule_parser.parse_primavera_xml(xml_content)
    db.query(models.ActivityRelation).delete()
    db.query(models.Activity).delete()
    db.commit()
    for act in activities:
        db_act = models.Activity(
            id=act["id"],
            project_id=1,
            name=act["name"],
            scheduled_start=act["scheduled_start"],
            scheduled_end=act["scheduled_end"],
            is_critical_path=act["is_critical_path"],
            status=act["status"]
        )
        db.add(db_act)
    for rel in relationships:
        db_rel = models.ActivityRelation(
            project_id=1,
            predecessor_id=rel["predecessor_id"],
            successor_id=rel["successor_id"],
            relation_type=rel["relation_type"]
        )
        db.add(db_rel)
    db.commit()
    return {"message": "Schedule ingested successfully", "activities_count": len(activities)}
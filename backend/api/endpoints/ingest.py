import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.ingest import email_parser, vision_parser, schedule_parser
from backend.intelligence.pipeline import run_intelligence_pipeline


router = APIRouter()


@router.post("/email")
def ingest_email(email_text: str = Form(...), material_sku: str = Form(...), db: Session = Depends(get_db)):
    material = db.query(models.Material).filter(models.Material.sku == material_sku).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material SKU not found")
    parse_res = email_parser.parse_vendor_email(email_text)
    new_signal = models.Signal(
        material_id=material.id,
        source="EMAIL",
        raw_content=json.dumps(parse_res),
        parsed_status=parse_res.get("status", "ORDERED").upper(),
        confidence_weight=parse_res.get("extraction_confidence", 0.8)
    )
    db.add(new_signal)
    db.commit()
    run_intelligence_pipeline(db, material)
    return {"message": "Email ingested successfully", "parsed_data": parse_res}


@router.post("/vision")
async def ingest_vision(material_sku: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    material = db.query(models.Material).filter(models.Material.sku == material_sku).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material SKU not found")
        
    file_bytes = await file.read()
    parse_res = vision_parser.parse_delivery_image(file_bytes)
    new_signal = models.Signal(
        material_id=material.id,
        source="VISION",
        raw_content=json.dumps(parse_res),
        parsed_status=parse_res.get("status", "DELIVERED").upper(),
        confidence_weight=parse_res.get("extraction_confidence", 0.95)
    )
    db.add(new_signal)
    db.commit()
    run_intelligence_pipeline(db, material)    
    return {"message": "Vision photo ingested successfully", "parsed_data": parse_res}


@router.post("/schedule")
async def ingest_schedule(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
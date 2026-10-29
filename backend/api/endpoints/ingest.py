import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.ingest import email_parser, vision_parser, schedule_parser
from backend.intelligence.pipeline import run_intelligence_pipeline
from backend.rag.service import ingest_text


def _index_rag_safely(source: str, text: str, source_type: str) -> dict:
    """Keep operational ingestion successful even if optional RAG indexing is unavailable."""
    try:
        return ingest_text(source, text, source_type)
    except Exception as exc:
        # The primary signal/schedule is already committed; surface status for observability.
        return {"indexed": False, "reason": str(exc)}


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
    rag_status = _index_rag_safely(
        f"db:signal:{new_signal.id}",
        f"Vendor email update for material SKU {material.sku}. Vendor: {material.vendor_name or 'Unknown'}. "
        f"Original email: {email_text}\nParsed result: {json.dumps(parse_res, ensure_ascii=False)}",
        "email_signal",
    )
    return {"message": "Email ingested successfully", "parsed_data": parse_res, "rag_indexing": rag_status}


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
    rag_status = _index_rag_safely(
        f"db:signal:{new_signal.id}",
        f"Delivery image analysis for material SKU {material.sku}. Vendor: {material.vendor_name or 'Unknown'}. "
        f"Parsed image result: {json.dumps(parse_res, ensure_ascii=False)}",
        "vision_signal",
    )
    return {"message": "Vision photo ingested successfully", "parsed_data": parse_res, "rag_indexing": rag_status}


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
    rag_results = []
    for act in activities:
        try:
            rag_results.append(ingest_text(
                f"db:activity:{act['id']}",
                f"Schedule activity ID: {act['id']}. Name: {act['name']}. "
                f"Scheduled start: {act['scheduled_start'] or 'Unknown'}. "
                f"Scheduled end: {act['scheduled_end'] or 'Unknown'}. "
                f"Critical path: {act['is_critical_path']}. Status: {act['status']}.",
                "schedule_activity",
            ))
        except Exception as exc:
            rag_results.append({"indexed": False, "activity_id": act["id"], "reason": str(exc)})
    return {"message": "Schedule ingested successfully", "activities_count": len(activities),
            "rag_indexing": {"activities_attempted": len(rag_results),
                             "activities_indexed": sum(1 for r in rag_results if r.get("chunks_added", 0) > 0),
                             "results": rag_results}}
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, cast
from backend.database import get_db
from backend import models, schemas


router = APIRouter()


@router.get("/activities", response_model=List[schemas.ActivityOut])
def get_activities(db: Session = Depends(get_db)):
    return db.query(models.Activity).all()


@router.get("/graph")
def get_schedule_graph_data(db: Session = Depends(get_db)):
    activities = db.query(models.Activity).all()
    relations = db.query(models.ActivityRelation).all()
    nodes = []
    for act in activities:
        nodes.append({
            "id": str(act.id),
            "label": cast(str, act.name),
            "start": act.scheduled_start.isoformat(),
            "end": act.scheduled_end.isoformat(),
            "is_critical": cast(bool, act.is_critical_path),
            "status": cast(str, act.status)
        })
    links = []
    for rel in relations:
        links.append({
            "source": str(rel.predecessor_id),
            "target": str(rel.successor_id),
            "type": cast(str, rel.relation_type)
        })
    return {
        "nodes": nodes, 
        "links": links
    }

from typing import List, cast
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas


router = APIRouter()


@router.get("/", response_model=List[schemas.AlertOut])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).filter(models.Alert.is_resolved == False).all()


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = True  # type: ignore
    db.commit()
    return {
        "message":"Alert marked as resolved"
    }

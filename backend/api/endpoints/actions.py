from typing import List, cast
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas


router = APIRouter()


@router.get("/drafts", response_model=List[schemas.ActionOut])
def get_drafts(db: Session = Depends(get_db)):
    return db.query(models.Action).filter(models.Action.status == "DRAFT").all()


@router.post("/{action_id}/execute")
def execute_action(action_id: int, db: Session = Depends(get_db)):
    action = db.query(models.Action).filter(models.Action.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action draft not found")
    action.status = "SENT"  # type: ignore
    db.commit()
    return {
        "message":f"Action of type '{action.action_type}' was successfully executed (Simulated)"
    }

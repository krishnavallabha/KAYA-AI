import logging
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

# pyrefly: ignore[missing-module-attribute]
from backend.rag.schemas import ScheduleDraftRequest
from backend.intelligence.schedule_planner import generate_schedule_draft

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/schedule", tags=["Schedule Planner"])


@router.post("/generate")
def generate_schedule(payload: ScheduleDraftRequest):
    try:
        target_start = None
        if payload.target_start:
            target_start = date.fromisoformat(payload.target_start).isoformat()

        return generate_schedule_draft(
            brief=payload.brief,
            target_start=target_start,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Schedule draft generation failed")
        raise HTTPException(
            status_code=500,
            detail="Schedule draft generation failed. Check backend logs.",
        ) from exc

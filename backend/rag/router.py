import os
import secrets
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.rag.schemas import RAGQueryRequest, RAGIngestResponse
from backend.rag.service import (
    ingest_document, ingest_text, answer_question, list_sources,
    delete_source, index_project_files,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])


def require_rag_token(authorization: str | None = Header(default=None)):
    """Optional shared bearer token for local demos; configure RAG_API_TOKEN in deployed environments."""
    expected = os.getenv("RAG_API_TOKEN", "").strip()
    if not expected:
        return  # local development only; set RAG_API_TOKEN before deployment
    supplied = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Valid bearer token required.")


@router.post("/ingest", response_model=RAGIngestResponse, dependencies=[Depends(require_rag_token)])
async def ingest(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = ingest_document(file.filename or "uploaded.txt", content)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document ingestion failed. Check backend logs.") from exc


@router.post("/query", dependencies=[Depends(require_rag_token)])
def query(payload: RAGQueryRequest):
    try:
        return answer_question(payload.question, payload.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("RAG query failed")
        raise HTTPException(
            status_code=500,
            detail="RAG query failed. Check backend logs."
        ) from exc


@router.get("/sources", dependencies=[Depends(require_rag_token)])
def sources():
    return {"sources": list_sources()}


@router.delete("/sources/{filename}", dependencies=[Depends(require_rag_token)])
def remove_source(filename: str):
    try:
        return delete_source(filename)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/index-project", dependencies=[Depends(require_rag_token)])
def index_project(db: Session = Depends(get_db)):
    """Index supported files and a snapshot of the current FlowSense database."""
    try:
        file_result = index_project_files()
        # Stable keys ensure each record refreshes rather than duplicating on every run.
        record_results = []
        for material in db.query(models.Material).all():
            text = (
                f"Material SKU: {material.sku}. Description: {material.description or 'Unknown'}. "
                f"Quantity: {material.quantity}. Status: {material.status}. Vendor: {material.vendor_name or 'Unknown'}. "
                f"Current location: {material.current_location or 'Unknown'}. "
                f"Promised delivery: {material.promised_delivery_date or 'Unknown'}. "
                f"Forecast delivery: {material.forecast_delivery_date or 'Unknown'}. "
                f"Delay probability: {material.delay_probability}."
            )
            record_results.append(ingest_text(f"db:material:{material.id}", text, "database_material"))
            for signal in material.signals:
                record_results.append(ingest_text(
                    f"db:signal:{signal.id}",
                    f"Material SKU: {material.sku}. Signal source: {signal.source}. Timestamp: {signal.timestamp}. "
                    f"Parsed status: {signal.parsed_status or 'Unknown'}. Signal content: {signal.raw_content or ''}",
                    "database_signal",
                ))
        for activity in db.query(models.Activity).all():
            text = (
                f"Schedule activity ID: {activity.id}. Name: {activity.name}. Status: {activity.status}. "
                f"Scheduled start: {activity.scheduled_start or 'Unknown'}. Scheduled end: {activity.scheduled_end or 'Unknown'}. "
                f"Critical path: {activity.is_critical_path}."
            )
            record_results.append(ingest_text(f"db:activity:{activity.id}", text, "database_activity"))
        return {"files": file_result, "database_records_indexed": len(record_results),
                "database_results": record_results}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Project indexing failed: {type(exc).__name__}: {exc}") from exc

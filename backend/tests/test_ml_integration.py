import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from datetime import datetime, timezone, timedelta
from backend.database import SessionLocal, Base, engine
from backend import models
from backend.api.endpoints.ingest import ingest_email

def test_ml_integration():
    # Setup clean db schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create Project
        project = models.Project(id=1, name="Test Project", description="Verify ML Integration")
        db.add(project)
        
        # Create Activity
        activity = models.Activity(
            id=101,
            project_id=1,
            name="Foundations",
            scheduled_start=datetime.now(timezone.utc),
            scheduled_end=datetime.now(timezone.utc) + timedelta(days=10),
            is_critical_path=True,
            status="NOT_STARTED"
        )
        db.add(activity)
        
        # Create Material
        material = models.Material(
            id=1,
            sku="SKU-482",
            description="Steel Rebar",
            quantity=50.0,
            status="ORDERED",
            current_location="Factory",
            vendor_name="SteelCorp Ltd",
            promised_delivery_date=datetime.now(timezone.utc) + timedelta(days=5),
            activity_id=101
        )
        db.add(material)
        db.commit()
        
        # Ingest Email
        email_body = (
            "Hi team, this is SteelCorp. Regarding order PO-1002 (SKU-482), "
            "production is complete and we have shipped the 50 units. "
            "They should arrive around 2026-07-15."
        )
        response = ingest_email(email_text=email_body, material_sku="SKU-482", db=db)
        assert response["message"] == "Email ingested successfully"
        
        # Refresh material from DB
        db.refresh(material)
        assert material.status == "IN_TRANSIT"
        assert material.confidence_score == 1.0
        
        # Verify Alerts
        alerts = db.query(models.Alert).all()
        assert len(alerts) == 1
        assert alerts[0].severity == "CRITICAL"
        
        # Ingest Conflicting Email (e.g. damaged) to trigger a conflict
        email_body_conflict = (
            "URGENT: Regarding PO-1002 (SKU-482), we encountered severe fabrication delays. "
            "We are still in fabrication, won't complete until 2026-07-28."
        )
        response_conflict = ingest_email(email_text=email_body_conflict, material_sku="SKU-482", db=db)
        assert response_conflict["message"] == "Email ingested successfully"
        
        db.refresh(material)
        
        # Verify if conflict alert was generated
        alerts = db.query(models.Alert).all()
        assert len(alerts) == 2
        assert alerts[1].severity == "WARNING"
        assert "conflict" in alerts[1].message.lower()
        
    finally:
        db.close()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend import models

client = TestClient(app)

def test_user_flow():
    # Setup clean db schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create Project
        project = models.Project(id=1, name="Test Project", description="User Flow Verification")
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
    finally:
        db.close()

    # 1. User posts email ingestion via HTTP Form data
    email_body = (
        "Hi team, this is SteelCorp. Regarding order PO-1002 (SKU-482), "
        "production is complete and we have shipped the 50 units. "
        "They should arrive around 2026-07-15."
    )
    print("\n--- [INGEST] Sending Email Ingestion Payload ---")
    print(f"Email Text: {email_body}")
    
    response = client.post(
        "/api/v1/ingest/email",
        data={"email_text": email_body, "material_sku": "SKU-482"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["message"] == "Email ingested successfully"
    print(f"Server Response: {json.dumps(res_data, indent=2)}")
    
    # 2. User checks materials list to see updated status & forecasting
    response = client.get("/api/v1/materials/")
    assert response.status_code == 200
    materials_list = response.json()
    assert len(materials_list) == 1
    mat = materials_list[0]
    assert mat["sku"] == "SKU-482"
    assert mat["status"] in ("IN_TRANSIT", "SHIPPED")
    assert mat["confidence_score"] == 1.0
    assert mat["forecast_delivery_date"] is not None
    assert mat["delay_probability"] is not None
    print("\n--- [MATERIALS] Updated Material State ---")
    print(f"SKU: {mat['sku']}")
    print(f"Status: {mat['status']}")
    print(f"Confidence Score: {mat['confidence_score']}")
    print(f"Forecast delivery Date: {mat['forecast_delivery_date']}")
    print(f"Delay Probability: {mat['delay_probability']}")

    # 3. User checks if any alerts were generated
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "CRITICAL"
    assert "SKU-482" in alerts[0]["message"]
    print("\n--- [ALERTS] Generated Alerts ---")
    for alert in alerts:
        print(f"Alert [{alert['severity']}]: {alert['message']}")

    # 4. User posts a conflicting email (claims delay) to test warning alerting
    email_body_conflict = (
        "URGENT: Regarding PO-1002 (SKU-482), we encountered severe fabrication delays. "
        "We are still in fabrication, won't complete until 2026-07-28."
    )
    print("\n--- [INGEST] Sending Conflicting Email Ingestion Payload ---")
    print(f"Email Text: {email_body_conflict}")
    
    response = client.post(
        "/api/v1/ingest/email",
        data={"email_text": email_body_conflict, "material_sku": "SKU-482"}
    )
    assert response.status_code == 200
    
    # 5. User checks if conflict alert is visible in the alert system
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) == 2
    assert alerts[1]["severity"] == "WARNING"
    assert "conflict" in alerts[1]["message"].lower()
    print("\n--- [ALERTS] Alerts after conflict ---")
    for alert in alerts:
        print(f"Alert [{alert['severity']}]: {alert['message']}")

import os
import sys
from datetime import datetime

# Add project root to python path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.models import Project, Activity, ActivityRelation, Material, Alert, Action

def seed():
    # Start with a fresh database
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Inserting demo project...")
        project = Project(
            id=1,
            name="Skyline Tower — Phase 2",
            description="Mixed-use high-rise, structural + envelope package",
            created_at=datetime.fromisoformat("2026-06-01T00:00:00")
        )
        db.add(project)
        db.commit()

        print("Inserting activities...")
        activities = [
            Activity(
                id=1,
                project_id=1,
                name="Foundation Pour",
                scheduled_start=datetime.fromisoformat("2026-07-01T00:00:00"),
                scheduled_end=datetime.fromisoformat("2026-07-06T00:00:00"),
                actual_start=datetime.fromisoformat("2026-07-01T00:00:00"),
                actual_end=datetime.fromisoformat("2026-07-06T00:00:00"),
                is_critical_path=True,
                status="COMPLETED"
            ),
            Activity(
                id=2,
                project_id=1,
                name="Steel Erection",
                scheduled_start=datetime.fromisoformat("2026-07-12T00:00:00"),
                scheduled_end=datetime.fromisoformat("2026-07-21T00:00:00"),
                actual_start=None,
                actual_end=None,
                is_critical_path=True,
                status="NOT_STARTED"
            ),
            Activity(
                id=3,
                project_id=1,
                name="Metal Decking",
                scheduled_start=datetime.fromisoformat("2026-07-22T00:00:00"),
                scheduled_end=datetime.fromisoformat("2026-07-28T00:00:00"),
                actual_start=None,
                actual_end=None,
                is_critical_path=True,
                status="NOT_STARTED"
            ),
            Activity(
                id=4,
                project_id=1,
                name="MEP Rough-in",
                scheduled_start=datetime.fromisoformat("2026-07-22T00:00:00"),
                scheduled_end=datetime.fromisoformat("2026-08-02T00:00:00"),
                actual_start=None,
                actual_end=None,
                is_critical_path=False,
                status="NOT_STARTED"
            ),
            Activity(
                id=5,
                project_id=1,
                name="Concrete Pour (Slab)",
                scheduled_start=datetime.fromisoformat("2026-07-29T00:00:00"),
                scheduled_end=datetime.fromisoformat("2026-08-05T00:00:00"),
                actual_start=None,
                actual_end=None,
                is_critical_path=True,
                status="NOT_STARTED"
            ),
            Activity(
                id=6,
                project_id=1,
                name="Curtain Wall Install",
                scheduled_start=datetime.fromisoformat("2026-08-06T00:00:00"),
                scheduled_end=datetime.fromisoformat("2026-08-18T00:00:00"),
                actual_start=None,
                actual_end=None,
                is_critical_path=False,
                status="NOT_STARTED"
            )
        ]
        
        for activity in activities:
            db.add(activity)
        db.commit()

        print("Inserting activity relations...")
        relations = [
            ActivityRelation(id=1, project_id=1, predecessor_id=1, successor_id=2, relation_type="FS"),
            ActivityRelation(id=2, project_id=1, predecessor_id=2, successor_id=3, relation_type="FS"),
            ActivityRelation(id=3, project_id=1, predecessor_id=2, successor_id=4, relation_type="FS"),
            ActivityRelation(id=4, project_id=1, predecessor_id=3, successor_id=5, relation_type="FS"),
            ActivityRelation(id=5, project_id=1, predecessor_id=4, successor_id=5, relation_type="FS"),
            ActivityRelation(id=6, project_id=1, predecessor_id=5, successor_id=6, relation_type="FS")
        ]
        for relation in relations:
            db.add(relation)
        db.commit()

        print("Inserting materials...")
        materials = [
            Material(
                id=1,
                sku="SKU-482",
                description="Structural steel beams (W12x40)",
                quantity=24.0,
                status="IN_TRANSIT",
                current_location="Freight hub, Pune",
                vendor_name="SteelCorp Ltd",
                promised_delivery_date=datetime.fromisoformat("2026-07-15T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-26T00:00:00"),
                delay_probability=0.78,
                confidence_score=0.91,
                activity_id=2
            ),
            Material(
                id=2,
                sku="SKU-994",
                description="Rebar panels #6 grade 60",
                quantity=50.0,
                status="FABRICATING",
                current_location="SteelCorp fab yard, Nashik",
                vendor_name="ConcreteSupply Co",
                promised_delivery_date=datetime.fromisoformat("2026-07-22T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-24T00:00:00"),
                delay_probability=0.34,
                confidence_score=0.88,
                activity_id=5
            ),
            Material(
                id=3,
                sku="SKU-233",
                description="Galvanized metal decking sheets",
                quantity=120.0,
                status="ORDERED",
                current_location=None,
                vendor_name="DeckPro Industries",
                promised_delivery_date=datetime.fromisoformat("2026-07-28T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-31T00:00:00"),
                delay_probability=0.41,
                confidence_score=0.72,
                activity_id=3
            ),
            Material(
                id=4,
                sku="SKU-660",
                description="HVAC ducting, spiral 12\"",
                quantity=40.0,
                status="SHIPPED",
                current_location="Regional DC, Mumbai",
                vendor_name="AirFlow Systems",
                promised_delivery_date=datetime.fromisoformat("2026-07-19T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-20T00:00:00"),
                delay_probability=0.18,
                confidence_score=0.90,
                activity_id=4
            ),
            Material(
                id=5,
                sku="SKU-118",
                description="Anchor bolts, M24 galvanized",
                quantity=500.0,
                status="DELIVERED",
                current_location="Site warehouse",
                vendor_name="FastenRight",
                promised_delivery_date=datetime.fromisoformat("2026-07-05T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-04T00:00:00"),
                delay_probability=0.02,
                confidence_score=0.98,
                activity_id=2
            ),
            Material(
                id=6,
                sku="SKU-905",
                description="Curtain wall glass panels",
                quantity=60.0,
                status="FABRICATING",
                current_location="GlassWorks plant, Chennai",
                vendor_name="GlassWorks Co",
                promised_delivery_date=datetime.fromisoformat("2026-08-05T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-08-12T00:00:00"),
                delay_probability=0.63,
                confidence_score=0.80,
                activity_id=6
            ),
            Material(
                id=7,
                sku="SKU-347",
                description="Concrete mix additive (retarder)",
                quantity=200.0,
                status="IN_TRANSIT",
                current_location="En route, NH48",
                vendor_name="ConcreteSupply Co",
                promised_delivery_date=datetime.fromisoformat("2026-07-16T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-17T00:00:00"),
                delay_probability=0.22,
                confidence_score=0.86,
                activity_id=5
            ),
            Material(
                id=8,
                sku="SKU-512",
                description="Electrical conduit, EMT 2\"",
                quantity=300.0,
                status="ORDERED",
                current_location=None,
                vendor_name="VoltLine Supplies",
                promised_delivery_date=datetime.fromisoformat("2026-07-30T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-08-01T00:00:00"),
                delay_probability=0.29,
                confidence_score=0.70,
                activity_id=4
            ),
            Material(
                id=9,
                sku="SKU-088",
                description="Steel connection plates & gussets",
                quantity=180.0,
                status="SHIPPED",
                current_location="Freight hub, Pune",
                vendor_name="SteelCorp Ltd",
                promised_delivery_date=datetime.fromisoformat("2026-07-14T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-21T00:00:00"),
                delay_probability=0.66,
                confidence_score=0.89,
                activity_id=2
            ),
            Material(
                id=10,
                sku="SKU-701",
                description="Waterproof membrane rolls",
                quantity=90.0,
                status="DELIVERED",
                current_location="Site warehouse",
                vendor_name="SealTech",
                promised_delivery_date=datetime.fromisoformat("2026-07-03T00:00:00"),
                forecast_delivery_date=datetime.fromisoformat("2026-07-03T00:00:00"),
                delay_probability=0.00,
                confidence_score=0.97,
                activity_id=1
            )
        ]
        
        for material in materials:
            db.add(material)
        db.commit()

        print("Inserting alerts...")
        alerts = [
            Alert(
                id=1,
                project_id=1,
                material_id=1,
                message="Material SKU SKU-482 delay impacts project critical path by 11 days.",
                severity="CRITICAL",
                is_resolved=False,
                created_at=datetime.fromisoformat("2026-07-07T09:12:00")
            ),
            Alert(
                id=2,
                project_id=1,
                material_id=9,
                message="Material SKU SKU-088 forecast slip of 7 days may delay Steel Erection.",
                severity="WARNING",
                is_resolved=False,
                created_at=datetime.fromisoformat("2026-07-07T08:40:00")
            ),
            Alert(
                id=3,
                project_id=1,
                material_id=6,
                message="Signal conflict on SKU-905: vendor portal status differs from latest email.",
                severity="WARNING",
                is_resolved=False,
                created_at=datetime.fromisoformat("2026-07-06T17:20:00")
            )
        ]
        
        for alert in alerts:
            db.add(alert)
        db.commit()

        print("Inserting actions...")
        actions = [
            Action(
                id=1,
                alert_id=1,
                action_type="EMAIL_VENDOR",
                draft_content=(
                    "Subject: URGENT: Delivery Delay Escalation - SKU: SKU-482\n\n"
                    "Dear SteelCorp Ltd Team,\n\n"
                    "We are writing regarding order SKU-482 (Structural steel beams), currently forecast to arrive on 2026-07-26 against a promised date of 2026-07-15 — an 11-day slip.\n\n"
                    "This delay directly impacts the following critical-path activities on our schedule:\n"
                    "  - Steel Erection\n"
                    "  - Metal Decking\n"
                    "  - Concrete Pour (Slab)\n\n"
                    "As a result, projected project completion is now at risk by 11 days. We require the following within 24 hours:\n"
                    "  1. Current transit logs and precise location for this shipment.\n"
                    "  2. Available expediting options and associated lead-time reductions.\n"
                    "  3. A firm, revised delivery commitment.\n\n"
                    "Given the critical-path exposure, we ask that you treat this as a priority escalation.\n\n"
                    "Regards,\n"
                    "Project Controls\n"
                    "FlowSense — on behalf of the Project Management Office"
                ),
                status="DRAFT",
                created_at=datetime.fromisoformat("2026-07-07T09:12:05")
            ),
            Action(
                id=2,
                alert_id=2,
                action_type="EMAIL_VENDOR",
                draft_content=(
                    "Subject: Delivery Risk Notice - SKU: SKU-088\n\n"
                    "Dear SteelCorp Ltd Team,\n\n"
                    "Order SKU-088 (Steel connection plates & gussets) shows a forecast slip of 7 days versus the promised date of 2026-07-14. These components are required to begin Steel Erection.\n\n"
                    "Please confirm the current shipping status and whether partial early delivery of the erection-critical plates is possible.\n\n"
                    "Regards,\n"
                    "Project Controls\n"
                    "FlowSense — on behalf of the Project Management Office"
                ),
                status="DRAFT",
                created_at=datetime.fromisoformat("2026-07-07T08:40:10")
            )
        ]
        
        for action in actions:
            db.add(action)
        db.commit()

        print("Database seeded successfully with all demo data! ✅")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed()

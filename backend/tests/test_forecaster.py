import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timezone, timedelta
from backend.models import Material
from backend.intelligence.forecaster import calculate_delivery_forecast
from intelligence.forecaster import DeliveryForecaster

def test_calculate_delivery_forecast():
    promised = datetime.now(timezone.utc) + timedelta(days=10)
    mat = Material(
        vendor_name="SteelCorp Ltd",
        status="ORDERED",
        promised_delivery_date=promised
    )
    res = calculate_delivery_forecast(mat)
    assert res["forecast_delivery_date"] > promised
    assert res["delay_probability"] > 0.0

def test_calculate_delivery_forecast_delivered():
    promised = datetime.now(timezone.utc)
    mat = Material(
        vendor_name="SteelCorp Ltd",
        status="DELIVERED",
        promised_delivery_date=promised
    )
    res = calculate_delivery_forecast(mat)
    assert res["forecast_delivery_date"] == promised
    assert res["delay_probability"] == 0.0

def test_ml_delivery_forecaster():
    forecaster = DeliveryForecaster()
    order = {
        "order_id": "PO-123",
        "promised_date": "2026-07-20",
        "vendor_reliability": 0.88,
        "vendor": "SteelWorks Fabrication",
        "fabrication_stage": "in_fabrication"
    }
    tracker_record = {
        "verified_status": "in_fabrication",
        "confidence": 0.90,
        "last_observed_date": "2026-07-07"
    }
    res = forecaster.forecast(order, tracker_record, ["port_congestion"])
    assert res["forecast_date"] is not None
    assert res["delay_probability"] >= 0.0

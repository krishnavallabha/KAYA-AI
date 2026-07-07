# calc the expected time of arrival eta and probab of delay using probablisitic methosds


import math
from datetime import datetime, timedelta, timezone
from typing import cast
from scipy.stats import norm
from backend.models import Material


VENDOR_PROFILES = {
    "SteelCorp Ltd": {"mean_delay": 5, "std_dev": 3.5},
    "ConcreteSupply Co": {"mean_delay": 2, "std_dev": 1.2},
    "FastenersInc": {"mean_delay": 0, "std_dev": 0.5},
    "DEFAULT": {"mean_delay": 3, "std_dev": 2.5}
}


STAGE_MODIFIERS = {
    "ORDERED": {"delay_multiplier": 1.0, "uncertainty_multiplier": 1.2},
    "FABRICATING": {"delay_multiplier": 0.8, "uncertainty_multiplier": 1.0},
    "SHIPPED": {"delay_multiplier": 0.5, "uncertainty_multiplier": 0.8},
    "IN_TRANSIT": {"delay_multiplier": 0.3, "uncertainty_multiplier": 0.5},
    "DELIVERED": {"delay_multiplier": 0.0, "uncertainty_multiplier": 0.0}
}


def calculate_delivery_forecast(material: Material) -> dict:
    vendor = cast(str, material.vendor_name) if material.vendor_name is not None else "DEFAULT"
    profile = VENDOR_PROFILES.get(vendor, VENDOR_PROFILES["DEFAULT"])
    mat_status = cast(str, material.status) if material.status is not None else "ORDERED"
    modifier = STAGE_MODIFIERS.get(mat_status, STAGE_MODIFIERS["ORDERED"])
    promised_date = cast(datetime, material.promised_delivery_date)
    if promised_date.tzinfo is None:
        promised_date = promised_date.replace(tzinfo=timezone.utc)
    expected_delay_days = profile["mean_delay"] * modifier["delay_multiplier"]
    std_dev_days = profile["std_dev"] * modifier["uncertainty_multiplier"]
    forecast_date = promised_date + timedelta(days=expected_delay_days)
    if mat_status == "DELIVERED":
        return {
            "forecast_delivery_date": promised_date,
            "delay_probability": 0.0,
            "confidence_interval_start": promised_date,
            "confidence_interval_end": promised_date
        }
    margin_days = 1.645 * std_dev_days
    ci_start = forecast_date - timedelta(days=margin_days)
    ci_end = forecast_date + timedelta(days=margin_days)
    if std_dev_days > 0:
        z_score = (promised_date - forecast_date).days / std_dev_days
        prob_on_time = norm.cdf(z_score)
        delay_prob = 1.0 - prob_on_time
    else:
        delay_prob = 1.0 if forecast_date > promised_date else 0.0
    return {
        "forecast_delivery_date": forecast_date,
        "delay_probability": round(float(delay_prob), 2),
        "confidence_interval_start": ci_start,
        "confidence_interval_end": ci_end
    }
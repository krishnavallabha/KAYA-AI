"""
FlowSense Role 2 - End-to-End Demo

Wires together everything Role 2 owns:
  synthetic emails/images/documents
      -> Email Agent / Vision Agent / Document Parser  (Ingest Layer)
      -> Unified Event Stream                          (schema.EventStream)
      -> Material Tracker Agent                        (reconciliation)
      -> Fabrication-to-Delivery Forecaster             (Bayesian ETA)

Run:
    python demo.py
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from synthetic_data import generate_all
from schema import EventStream
from agents.email_agent import EmailAgent
from agents.vision_agent import VisionAgent
from agents.document_parser import DocumentParserAgent
from intelligence.material_tracker import MaterialTrackerAgent
from intelligence.forecaster import DeliveryForecaster
from config import mode_banner


def run():
    print(mode_banner())
    print("=" * 78)

    bundle = generate_all()
    orders = {o["order_id"]: o for o in bundle["orders"]}

    stream = EventStream()
    email_agent = EmailAgent()
    vision_agent = VisionAgent()
    doc_agent = DocumentParserAgent()
    tracker = MaterialTrackerAgent()
    forecaster = DeliveryForecaster()

    # --- Phase 1: Ingest ---------------------------------------------------
    print("\nPHASE 1: INGEST LAYER")
    for e in email_agent.process_inbox(bundle["emails"]):
        stream.publish(e)
    for e in vision_agent.process_images(bundle["images"]):
        stream.publish(e)
    for e in doc_agent.process_documents(bundle["documents"]):
        stream.publish(e)
    print(f"  Published {len(stream.all())} events to the Unified Event Stream "
          f"from {len(bundle['emails'])} emails, {len(bundle['images'])} images, "
          f"{len(bundle['documents'])} documents.")

    # --- Phase 2: Reconciliation + Forecasting ------------------------------
    print("\nPHASE 2: MATERIAL TRACKER + FORECASTER")
    tracker.ingest(stream.all())

    results = []
    for order_id, order in orders.items():
        record = tracker.get_record(order_id)
        disruption_flags = ["port_congestion"] if order_id == "PO-1002" else []
        forecast = forecaster.forecast(order, record, disruption_flags)
        results.append({"order": order, "tracker_record": record, "forecast": forecast})

    for r in results:
        o, rec, fc = r["order"], r["tracker_record"], r["forecast"]
        print(f"\n--- {o['order_id']} | {o['description']} | vendor={o['vendor']} ---")
        print(f"  Promised date:        {o['promised_date']}")
        print(f"  Verified status:      {rec.get('verified_status')} "
              f"(tracker confidence={rec.get('confidence', 0):.2f})"
              + ("  [CONFLICT FLAGGED]" if rec.get("signal_conflict") else ""))
        print(f"  Forecast delivery:    {fc['forecast_date']}  "
              f"(90% CI: {fc['confidence_interval_90'][0]} to {fc['confidence_interval_90'][1]})")
        print(f"  Delay probability:    {fc['delay_probability'] * 100:.1f}%")
        print(f"  Days at risk:         {fc['days_at_risk']}")
        if rec.get("signal_conflict"):
            print(f"  Conflicting sources:  {rec['conflicting_sources']}")

    # --- Dashboard-ready JSON payload (what Role 3 would consume) ---------
    dashboard_payload = [
        {
            "order_id": r["order"]["order_id"],
            "description": r["order"]["description"],
            "vendor": r["order"]["vendor"],
            "verified_status": r["tracker_record"].get("verified_status"),
            "tracker_confidence": r["tracker_record"].get("confidence"),
            "signal_conflict": r["tracker_record"].get("signal_conflict"),
            "forecast_date": r["forecast"]["forecast_date"],
            "confidence_interval_90": r["forecast"]["confidence_interval_90"],
            "delay_probability": r["forecast"]["delay_probability"],
            "days_at_risk": r["forecast"]["days_at_risk"],
        }
        for r in results
    ]
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dashboard_payload.json")
    with open(out_path, "w") as f:
        json.dump(dashboard_payload, f, indent=2)
    print(f"\nDashboard-ready payload written to {out_path}")

    # Example reasoning trace for one at-risk order, showing the Bayesian
    # update steps and tracker reconciliation logic Role 1's dashboard
    # could surface as an "explain this forecast" panel.
    sample = results[0]
    print(f"\nSAMPLE REASONING TRACE for {sample['order']['order_id']}:")
    for line in tracker.get_reasoning_trace(sample["order"]["order_id"])[0]:
        print(f"  [Tracker] {line}")
    for line in sample["forecast"]["reasoning_trace"]:
        print(f"  [Forecaster] {line}")


if __name__ == "__main__":
    run()

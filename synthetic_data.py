"""
FlowSense Role 2 - Synthetic Data Generator

Produces mock supply-chain signals so the Email, Vision, and Document
agents plus the Material Tracker and Forecaster can be exercised end to
end without real vendor data. Run standalone to (re)generate fixtures:

    python synthetic_data.py
"""

import json
import os
import random
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont

random.seed(7)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
IMG_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

VENDORS = [
    {"name": "SteelWorks Fabrication", "reliability": 0.88},
    {"name": "MetroDuct Supply Co.", "reliability": 0.71},
    {"name": "Precision Rebar LLC", "reliability": 0.93},
    {"name": "Coastal Glazing Systems", "reliability": 0.60},
]

MATERIALS = [
    ("SKU-2201", "Structural Steel Beams - W12x26"),
    ("SKU-3305", "HVAC Ductwork - 24in Galvanized"),
    ("SKU-4110", "Rebar - #5 Grade 60, 20ft"),
    ("SKU-5027", "Curtain Wall Glazing Panels"),
]


def _gen_orders(n=6):
    orders = []
    base = datetime(2026, 7, 1)
    for i in range(n):
        vendor = random.choice(VENDORS)
        sku, desc = random.choice(MATERIALS)
        promised = base + timedelta(days=random.randint(10, 35))
        orders.append({
            "order_id": f"PO-{1000 + i}",
            "po_number": f"PO-{1000 + i}",
            "sku": sku,
            "description": desc,
            "vendor": vendor["name"],
            "vendor_reliability": vendor["reliability"],
            "quantity": random.choice([50, 100, 150, 200]),
            "promised_date": promised.strftime("%Y-%m-%d"),
            "fabrication_stage": random.choice(
                ["not_started", "in_fabrication", "fabrication_complete", "shipped"]
            ),
            "submittal_approved_date": (base - timedelta(days=random.randint(5, 20))).strftime("%Y-%m-%d"),
        })
    return orders


EMAIL_TEMPLATES = [
    ("delay_notice",
     "Subject: Delay Notice - {po}\n\nHi team,\n\nUnfortunately our shop is running "
     "behind on {desc} ({po}). Fabrication won't complete until {new_date}, roughly "
     "{days} days later than the original commitment. We'll expedite freight once it "
     "ships.\n\nRegards,\n{vendor} Logistics"),
    ("shipment_confirmation",
     "Subject: Shipment Confirmed - {po}\n\nThis confirms {po} ({desc}) has left our "
     "facility today via freight carrier. Tracking shows arrival at your site around "
     "{new_date}. Quantity shipped: {qty} units.\n\nThanks,\n{vendor}"),
    ("fabrication_update",
     "Subject: Production Update - {po}\n\n{po} is currently in fabrication, roughly "
     "70% complete. We still expect to hand off to freight by {new_date} as "
     "planned.\n\n{vendor} Production Team"),
    ("condition_issue",
     "Subject: Partial Damage Reported - {po}\n\nSite inspection flagged minor "
     "surface damage on {qty} units of {po} ({desc}) upon arrival. Replacement units "
     "for the damaged portion are being expedited, new ETA {new_date}.\n\n{vendor} QA"),
]


def _gen_emails(orders):
    emails = []
    now = datetime(2026, 7, 7, 9, 0)
    for idx, o in enumerate(orders):
        kind, template = random.choice(EMAIL_TEMPLATES)
        promised = datetime.strptime(o["promised_date"], "%Y-%m-%d")
        drift = random.choice([-2, 0, 3, 6, 10])
        new_date = promised + timedelta(days=drift)
        body = template.format(
            po=o["po_number"], desc=o["description"], vendor=o["vendor"],
            new_date=new_date.strftime("%Y-%m-%d"), days=abs(drift),
            qty=o["quantity"],
        )
        emails.append({
            "email_id": f"EML-{idx:03d}",
            "received_at": (now - timedelta(hours=random.randint(0, 72))).isoformat(),
            "sender": f"logistics@{o['vendor'].split()[0].lower()}.com",
            "body": body,
            "kind_ground_truth": kind,  # only used to score extraction accuracy in demo
            "order_id_ground_truth": o["order_id"],
        })
    return emails


DOC_TEMPLATES = {
    "bill_of_lading": (
        "BILL OF LADING\nBOL Number: BOL-{n}\nPO Reference: {po}\nShipper: {vendor}\n"
        "Consignee: Riverside Tower Project Site\nDescription of Goods: {desc}\n"
        "Quantity: {qty} units\nDate Shipped: {ship_date}\nCarrier: Freightline "
        "Logistics\nFreight Terms: Prepaid"
    ),
    "packing_slip": (
        "PACKING SLIP\nOrder Reference: {po}\nVendor: {vendor}\nItem: {desc}\n"
        "Units Packed: {qty}\nInspection Status: PASSED\nPacked Date: {ship_date}"
    ),
    "submittal_log": (
        "SUBMITTAL LOG ENTRY\nSubmittal ID: SUB-{n}\nRelated PO: {po}\nMaterial: {desc}\n"
        "Approval Status: APPROVED\nApproval Date: {approve_date}\nNotes: Approved for "
        "fabrication release."
    ),
}


def _gen_documents(orders):
    docs = []
    for idx, o in enumerate(orders):
        doc_type = random.choice(list(DOC_TEMPLATES.keys()))
        template = DOC_TEMPLATES[doc_type]
        ship_date = datetime.strptime(o["promised_date"], "%Y-%m-%d") - timedelta(days=random.randint(3, 10))
        text = template.format(
            n=2000 + idx, po=o["po_number"], vendor=o["vendor"], desc=o["description"],
            qty=o["quantity"], ship_date=ship_date.strftime("%Y-%m-%d"),
            approve_date=o["submittal_approved_date"],
        )
        docs.append({
            "doc_id": f"DOC-{idx:03d}",
            "doc_type_ground_truth": doc_type,
            "order_id_ground_truth": o["order_id"],
            "raw_text": text,
        })
    return docs


def _font():
    try:
        return ImageFont.truetype("DejaVuSans.ttf", 22)
    except Exception:
        return ImageFont.load_default()


def _gen_vision_images(orders):
    """Render synthetic 'label / delivery photo' images containing PO number,
    quantity, and a condition note as burned-in text, simulating a jobsite
    photo of a packing label. Ground truth is stored alongside for the
    fallback (non-GPT-4o-Vision) extraction path."""
    records = []
    font = _font()
    for idx, o in enumerate(orders):
        condition = random.choice(["GOOD CONDITION", "MINOR DAMAGE", "GOOD CONDITION"])
        img = Image.new("RGB", (500, 260), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)
        lines = [
            "DELIVERY LABEL",
            f"PO NUMBER: {o['po_number']}",
            f"SKU: {o['sku']}",
            f"QTY: {o['quantity']} UNITS",
            f"CONDITION: {condition}",
            f"VENDOR: {o['vendor']}",
        ]
        y = 15
        for line in lines:
            draw.text((20, y), line, fill=(20, 20, 20), font=font)
            y += 38
        path = os.path.join(IMG_DIR, f"label_{idx:03d}.png")
        img.save(path)
        records.append({
            "image_id": f"IMG-{idx:03d}",
            "path": path,
            "order_id_ground_truth": o["order_id"],
            "condition_ground_truth": condition,
        })
    return records


def generate_all(n_orders=6):
    orders = _gen_orders(n_orders)
    bundle = {
        "orders": orders,
        "emails": _gen_emails(orders),
        "documents": _gen_documents(orders),
        "images": _gen_vision_images(orders),
    }
    with open(os.path.join(DATA_DIR, "synthetic_bundle.json"), "w") as f:
        json.dump(bundle, f, indent=2)
    return bundle


if __name__ == "__main__":
    b = generate_all()
    print(f"Generated {len(b['orders'])} orders, {len(b['emails'])} emails, "
          f"{len(b['documents'])} documents, {len(b['images'])} label images.")
    print(f"Fixtures written to {DATA_DIR}")

# ingest std xml schedue and parse them into activites and relationship edges 


import xml.etree.ElementTree as ET
from datetime import datetime,timezone,timedelta
from typing import List,Dict,Tuple



def parse_primavera_xml(xml_content: str) -> Tuple[List[Dict], List[Dict]]:
    activities = []
    relationships = []

    try:
        root = ET.fromstring(xml_content)

        def get_text(node, *tag_names):
            for tag in tag_names:
                element = node.find(tag)
                if element is not None and element.text:
                    return element.text.strip()
            return None

        for act_node in root.findall(".//Activity"):
            act_id = get_text(act_node, "Id", "ActivityId", "ObjectId")
            act_name = get_text(act_node, "Name", "ActivityName")

            if not act_id or not act_name:
                continue

            try:
                activity_id = int(act_id)
            except ValueError:
                continue

            now = datetime.now(timezone.utc)

            try:
                start_date = datetime.fromisoformat(
                    # pyrefly: ignore[bad-argument-type]
                    get_text(act_node, "StartDate", "PlannedStartDate")
                ) if get_text(act_node, "StartDate", "PlannedStartDate") else now
            except ValueError:
                start_date = now

            try:
                end_date = datetime.fromisoformat(
                    # pyrefly: ignore[bad-argument-type]
                    get_text(act_node, "EndDate", "PlannedFinishDate")
                ) if get_text(act_node, "EndDate", "PlannedFinishDate") else now
            except ValueError:
                end_date = now

            critical = get_text(
                act_node, "IsCritical", "IsCriticalPath", "Critical"
            )

            activities.append({
                "id": activity_id,
                "name": act_name,
                "scheduled_start": start_date,
                "scheduled_end": end_date,
                "is_critical_path": (critical or "").lower() in {
                    "true", "1", "yes"
                },
                "status": "NOT_STARTED",
            })

        for rel_node in root.findall(".//ActivityRelation"):
            pred_id = get_text(
                rel_node, "PredecessorActivityId", "PredecessorId"
            )
            succ_id = get_text(
                rel_node, "SuccessorActivityId", "SuccessorId"
            )
            rel_type = get_text(
                rel_node, "RelationType", "Type"
            ) or "FS"

            if not pred_id or not succ_id:
                continue

            try:
                predecessor_id = int(pred_id)
                successor_id = int(succ_id)
            except ValueError:
                continue

            relationships.append({
                "predecessor_id": predecessor_id,
                "successor_id": successor_id,
                "relation_type": rel_type,
            })

        # Do not silently substitute demo data for a valid but empty schedule.
        if not activities:
            raise ValueError("No valid activities found in XML.")

        activity_ids = {a["id"] for a in activities}
        relationships = [
            r for r in relationships
            if r["predecessor_id"] in activity_ids
            and r["successor_id"] in activity_ids
        ]

        return activities, relationships

    except ET.ParseError as exc:
        raise ValueError(f"Invalid schedule XML: {exc}") from exc


def create_demo_schedule() -> Tuple[List[Dict], List[Dict]]:
    now = datetime.now()
    activities = [
        {
            "id": 1,
            "name": "Activity A - Foundation Pour",
            "scheduled_start": now,
            "scheduled_end": now + timedelta(days=5),
            "is_critical_path": True,
            "status": "COMPLETED"
        },
        {
            "id": 2,
            "name": "Activity B - Structural Steel Erection",
            "scheduled_start": now + timedelta(days=6),
            "scheduled_end": now + timedelta(days=15),
            "is_critical_path": True,
            "status": "NOT_STARTED"
        },
        {
            "id": 3,
            "name": "Activity C - Decking Installation",
            "scheduled_start": now + timedelta(days=16),
            "scheduled_end": now + timedelta(days=20),
            "is_critical_path": True,
            "status": "NOT_STARTED"
        },
        {
            "id": 4,
            "name": "Activity D - Concrete Slab Pour",
            "scheduled_start": now + timedelta(days=21),
            "scheduled_end": now + timedelta(days=24),
            "is_critical_path": True,
            "status": "NOT_STARTED"
        }
    ]
    relationships = [
        {"predecessor_id": 1, "successor_id": 2, "relation_type": "FS"},
        {"predecessor_id": 2, "successor_id": 3, "relation_type": "FS"},
        {"predecessor_id": 3, "successor_id": 4, "relation_type": "FS"}
    ]
    return activities, relationships
# ingest std xml schedue and parse them into activites and relationship edges 


import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from typing import List,Dict,Tuple


def parse_primavera_xml(xml_content: str) -> Tuple[List[Dict], List[Dict]]:
    activities = []
    relationships = []
    try:
        root = ET.fromstring(xml_content)
        for act_node in root.findall(".//Activity"):
            act_id = act_node.find("Id")
            act_name = act_node.find("Name")
            start_date_str = act_node.find("StartDate")
            end_date_str = act_node.find("EndDate")
            critical_node = act_node.find("IsCritical")
            if act_id is not None and act_id.text is not None and act_name is not None and act_name.text is not None:
                try:
                    start_date = datetime.fromisoformat(start_date_str.text) if start_date_str is not None and start_date_str.text else datetime.now(timezone.utc)
                    end_date = datetime.fromisoformat(end_date_str.text) if end_date_str is not None and end_date_str.text else datetime.now(timezone.utc)
                except ValueError:
                    start_date = datetime.now(timezone.utc)
                    end_date = datetime.now(timezone.utc)
                activities.append({
                    "id": int(act_id.text),
                    "name": act_name.text,
                    "scheduled_start": start_date,
                    "scheduled_end": end_date,
                    "is_critical_path": critical_node.text.lower() == "true" if (critical_node is not None and critical_node.text is not None) else False,
                    "status": "NOT_STARTED"
                })                
        for rel_node in root.findall(".//ActivityRelation"):
            pred_id = rel_node.find("PredecessorActivityId")
            succ_id = rel_node.find("SuccessorActivityId")
            rel_type = rel_node.find("RelationType") # default FS (Finish-to-Start)
            if pred_id is not None and pred_id.text is not None and succ_id is not None and succ_id.text is not None:
                relationships.append({
                    "predecessor_id": int(pred_id.text),
                    "successor_id": int(succ_id.text),
                    "relation_type": rel_type.text if (rel_type is not None and rel_type.text is not None) else "FS"
                })
    except Exception as e:
        activities, relationships = create_demo_schedule()
    return activities, relationships


def create_demo_schedule() -> Tuple[List[Dict], List[Dict]]:
    now = datetime.now()
    activities = [
        {
            "id": 1,
            "name": "Activity A - Foundation Pour",
            "scheduled_start": now,
            "scheduled_end": datetime(now.year, now.month, now.day + 5),
            "is_critical_path": True,
            "status": "COMPLETED"
        },
        {
            "id": 2,
            "name": "Activity B - Structural Steel Erection",
            "scheduled_start": datetime(now.year, now.month, now.day + 6),
            "scheduled_end": datetime(now.year, now.month, now.day + 15),
            "is_critical_path": True,
            "status": "NOT_STARTED"
        },
        {
            "id": 3,
            "name": "Activity C - Decking Installation",
            "scheduled_start": datetime(now.year, now.month, now.day + 16),
            "scheduled_end": datetime(now.year, now.month, now.day + 20),
            "is_critical_path": True,
            "status": "NOT_STARTED"
        },
        {
            "id": 4,
            "name": "Activity D - Concrete Slab Pour",
            "scheduled_start": datetime(now.year, now.month, now.day + 21),
            "scheduled_end": datetime(now.year, now.month, now.day + 24),
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
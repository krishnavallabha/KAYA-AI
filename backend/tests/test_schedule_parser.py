import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.ingest.schedule_parser import parse_primavera_xml

def test_parse_valid_xml():
    xml_content = """<Project>
        <Activity>
            <Id>501</Id>
            <Name>Demolition</Name>
            <StartDate>2026-07-01T08:00:00</StartDate>
            <EndDate>2026-07-05T17:00:00</EndDate>
            <IsCritical>true</IsCritical>
        </Activity>
        <ActivityRelation>
            <PredecessorActivityId>501</PredecessorActivityId>
            <SuccessorActivityId>502</SuccessorActivityId>
            <RelationType>FS</RelationType>
        </ActivityRelation>
    </Project>"""
    activities, relationships = parse_primavera_xml(xml_content)
    assert len(activities) == 1
    assert activities[0]["id"] == 501
    assert activities[0]["name"] == "Demolition"
    assert activities[0]["is_critical_path"] is True
    
    assert len(relationships) == 1
    assert relationships[0]["predecessor_id"] == 501
    assert relationships[0]["successor_id"] == 502
    assert relationships[0]["relation_type"] == "FS"

def test_parse_invalid_xml_fallback():
    activities, relationships = parse_primavera_xml("<Invalid XML")
    assert len(activities) == 4
    assert len(relationships) == 3
    assert activities[0]["name"] == "Activity A - Foundation Pour"

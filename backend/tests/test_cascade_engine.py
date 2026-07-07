import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timezone, timedelta
from backend.models import Activity, ActivityRelation, Material
from backend.intelligence.cascade_engine import analyze_cascade_impact

def test_analyze_cascade_impact_no_delay():
    now = datetime.now(timezone.utc)
    act1 = Activity(id=1, name="Act 1", scheduled_start=now, scheduled_end=now + timedelta(days=5), is_critical_path=True)
    mat = Material(id=1, activity_id=1, forecast_delivery_date=now - timedelta(days=2))
    
    res = analyze_cascade_impact([act1], [], [mat])
    assert res["max_project_delay_days"] == 0
    assert res["critical_path_impacted"] is False
    assert len(res["impacted_activities"]) == 0

def test_analyze_cascade_impact_with_delay_cascade():
    now = datetime.now(timezone.utc)
    # act1 predecessors act2
    act1 = Activity(id=1, name="Act 1", scheduled_start=now, scheduled_end=now + timedelta(days=5), is_critical_path=True)
    act2 = Activity(id=2, name="Act 2", scheduled_start=now + timedelta(days=6), scheduled_end=now + timedelta(days=10), is_critical_path=True)
    rel = ActivityRelation(predecessor_id=1, successor_id=2, relation_type="FS")
    
    # Material for act1 is delayed by 4 days (forecast ETA is now + 4 days, but start is now)
    mat = Material(id=1, activity_id=1, forecast_delivery_date=now + timedelta(days=4))
    
    res = analyze_cascade_impact([act1, act2], [rel], [mat])
    assert res["max_project_delay_days"] == 4
    assert res["critical_path_impacted"] is True
    assert len(res["impacted_activities"]) == 2
    assert res["impacted_activities"][0]["calculated_delay_days"] == 4
    assert len(res["recovery_options"]) == 3

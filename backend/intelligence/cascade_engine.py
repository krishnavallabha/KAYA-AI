# analyze schedule impacts when delays occur 


import networkx as nx #type: ignore
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from backend.models import Activity, ActivityRelation, Material


def build_schedule_graph(activities: List[Activity], relations: List[ActivityRelation]) -> nx.DiGraph:
    G = nx.DiGraph()
    for act in activities:
        G.add_node(
            act.id,
            name=act.name,
            start=act.scheduled_start.replace(tzinfo=timezone.utc) if act.scheduled_start.tzinfo is None else act.scheduled_start,
            end=act.scheduled_end.replace(tzinfo=timezone.utc) if act.scheduled_end.tzinfo is None else act.scheduled_end,
            is_critical=act.is_critical_path,
            duration=(act.scheduled_end - act.scheduled_start).days,
            delay_days=0
        )
    for rel in relations:
        G.add_edge(rel.predecessor_id, rel.successor_id, relation_type=rel.relation_type)
    return G


def analyze_cascade_impact(
    activities: List[Activity], 
    relations: List[ActivityRelation], 
    materials: List[Material]
) -> dict:
    G = build_schedule_graph(activities, relations)
    now = datetime.now(timezone.utc)
    impacted_activities = {}
    critical_path_breached = False
    max_project_delay = 0
    for mat in materials:
        if not mat.activity_id or not mat.forecast_delivery_date:
            continue
        forecast_eta = mat.forecast_delivery_date.replace(tzinfo=timezone.utc) if mat.forecast_delivery_date.tzinfo is None else mat.forecast_delivery_date
        target_act = G.nodes.get(mat.activity_id)
        if target_act:
            if forecast_eta > target_act["start"]:
                delay_days = (forecast_eta - target_act["start"]).days
                target_act["delay_days"] = max(target_act["delay_days"], delay_days)
    try:
        nodes_processing_order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        nodes_processing_order = list(G.nodes)
    for node_id in nodes_processing_order:
        node = G.nodes[node_id]
        current_delay = node["delay_days"]
        if current_delay > 0:
            impacted_activities[node_id] = {
                "name": node["name"],
                "original_start": node["start"],
                "original_end": node["end"],
                "calculated_delay_days": current_delay,
                "is_critical": node["is_critical"]
            }
            if node["is_critical"]:
                critical_path_breached = True
                max_project_delay = max(max_project_delay, current_delay)
            for successor in G.successors(node_id):
                G.nodes[successor]["delay_days"] = max(
                    G.nodes[successor]["delay_days"], 
                    current_delay
                )
    recovery_options = []
    if max_project_delay > 0:
        recovery_options = [
            {
                "option_index": 1,
                "strategy": "Expedite Purchase Order",
                "impact": f"Reduces delay on critical path activities by {max(1, max_project_delay - 2)} days.",
                "cost_indicator": "HIGH (Rush shipping fee)"
            },
            {
                "option_index": 2,
                "strategy": "Resequence Downstream Activities",
                "impact": "Decouple affected Finish-to-Start relationships; overlapping tasks saves up to 5 schedule days.",
                "cost_indicator": "MEDIUM (Additional labor overlap)"
            },
            {
                "option_index": 3,
                "strategy": "Source Alternative Vendor Material",
                "impact": "Substitute current SKU with locally stocked equivalent. Eliminates logistics transit lag completely.",
                "cost_indicator": "LOW/MEDIUM (Depends on SKU unit price difference)"
            }
        ]
    return {
        "max_project_delay_days": max_project_delay,
        "critical_path_impacted": critical_path_breached,
        "impacted_activities": list(impacted_activities.values()),
        "recovery_options": recovery_options
    }
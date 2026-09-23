from __future__ import annotations
from typing import Any, Mapping, Sequence

def xi_availability(players: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    expected=available=0.0; variance=0.0; missing_roles=[]
    for p in players:
        role=max(0.0,float(p.get("role_weight",1.0))); prob=max(0.0,min(1.0,float(p.get("availability_probability",1.0))))
        expected+=role; available+=role*prob; variance+=(role**2)*prob*(1-prob)
        if prob<.5 and role>=1.0: missing_roles.append(str(p.get("player_id") or p.get("name") or "unknown"))
    ratio=available/expected if expected>0 else None
    return {"expected_role_mass":expected,"available_role_mass":available,"availability_ratio":ratio,"availability_variance":variance,"high_role_doubts":missing_roles,"t1_source_required":True}

def positional_availability(players: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    buckets={}
    for p in players:
        pos=str(p.get("position_group","unknown")); prob=max(0.0,min(1.0,float(p.get("availability_probability",1.0)))); role=max(0.0,float(p.get("role_weight",1.0)))
        b=buckets.setdefault(pos,{"expected":0.0,"available":0.0}); b["expected"]+=role; b["available"]+=role*prob
    for b in buckets.values(): b["ratio"]=b["available"]/b["expected"] if b["expected"] else None
    return buckets

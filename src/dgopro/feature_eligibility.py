from __future__ import annotations
from typing import Any, Mapping, Sequence

FORBIDDEN_SOURCE_TYPES={"vmd_simulation","vmd_prediction","synthetic_prediction","postmatch_derived_prematch"}
MODULE_REQUIREMENTS={
    "result":["home_goals","away_goals"],
    "goals":["home_goals","away_goals"],
    "corners":["home_corners","away_corners"],
    "cards":["home_cards","away_cards"],
    "shots":["home_shots","away_shots"],
    "sot":["home_sot","away_sot"],
    "xg":["home_xg","away_xg"],
    "lineup":["home_lineup","away_lineup"],
    "events":["events"],
    "tracking":["tracking_frames"],
}

def observational_firewall(record: Mapping[str,Any]) -> dict[str,Any]:
    source_type=str(record.get("source_type","unknown")).lower()
    observed=bool(record.get("observed_real",False))
    pre_match_safe=bool(record.get("prematch_features_t1_safe",False))
    forbidden=source_type in FORBIDDEN_SOURCE_TYPES
    return {"allowed_as_observation":observed and not forbidden,"allowed_as_prematch_feature":observed and pre_match_safe and not forbidden,"source_type":source_type,"forbidden":forbidden}

def module_eligibility(record: Mapping[str,Any]) -> dict[str,Any]:
    firewall=observational_firewall(record); modules={}
    for module,fields in MODULE_REQUIREMENTS.items():
        complete=all(record.get(f) is not None for f in fields)
        modules[module]={"eligible_target":firewall["allowed_as_observation"] and complete,"eligible_prematch_feature":firewall["allowed_as_prematch_feature"] and complete,"missing":[f for f in fields if record.get(f) is None]}
    return {"match_id":record.get("match_id"),"firewall":firewall,"modules":modules}

def coverage_summary(records: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    total=len(records); summary={m:{"target":0,"prematch":0} for m in MODULE_REQUIREMENTS}; blocked=0
    for r in records:
        e=module_eligibility(r)
        if not e["firewall"]["allowed_as_observation"]: blocked+=1
        for m,v in e["modules"].items():
            summary[m]["target"]+=int(v["eligible_target"]); summary[m]["prematch"]+=int(v["eligible_prematch_feature"])
    for m,v in summary.items():
        v["target_pct"]=v["target"]/total if total else 0.0; v["prematch_pct"]=v["prematch"]/total if total else 0.0
    return {"n_records":total,"blocked_records":blocked,"modules":summary}

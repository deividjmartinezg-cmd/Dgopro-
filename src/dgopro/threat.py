from __future__ import annotations
from typing import Any, Mapping, Sequence

def threat_value(action: Mapping[str,Any]) -> dict[str,float]:
    before_score=float(action.get("p_score_before",0)); after_score=float(action.get("p_score_after",0))
    before_concede=float(action.get("p_concede_before",0)); after_concede=float(action.get("p_concede_after",0))
    offensive=after_score-before_score; defensive_risk=after_concede-before_concede
    return {"offensive_value":offensive,"concession_risk":defensive_risk,"dtv":offensive-defensive_risk}

def possession_threat(actions: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    vals=[threat_value(a) for a in actions]
    return {"n_actions":len(vals),"dtv":sum(v["dtv"] for v in vals),"offensive_value":sum(v["offensive_value"] for v in vals),"concession_risk":sum(v["concession_risk"] for v in vals),"trained_model_required_for_input_probabilities":True}

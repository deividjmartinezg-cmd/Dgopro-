from __future__ import annotations
from typing import Any, Mapping, Sequence

def opponent_adjusted_metric(matches: Sequence[Mapping[str,Any]], metric: str, *, baseline_opponent_strength: float=1500.0, sensitivity: float=0.25) -> dict[str,Any]:
    adjusted=[]; raw=[]
    for m in matches:
        if m.get(metric) is None or m.get("opponent_strength") is None: continue
        value=float(m[metric]); opp=float(m["opponent_strength"])
        # Positive metrics such as xG/shots are rewarded when produced vs stronger opposition.
        factor=max(0.65,min(1.35,1.0+sensitivity*(opp-baseline_opponent_strength)/400.0))
        raw.append(value); adjusted.append(value*factor)
    return {"metric":metric,"n":len(adjusted),"raw_mean":sum(raw)/len(raw) if raw else None,"adjusted_mean":sum(adjusted)/len(adjusted) if adjusted else None,"baseline_opponent_strength":baseline_opponent_strength,"sensitivity":sensitivity,"sensitivity_calibrated":False}

def schedule_strength(matches: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    vals=[float(m["opponent_strength"]) for m in matches if m.get("opponent_strength") is not None]
    if not vals: return {"status":"unknown","n":0}
    return {"status":"ok","n":len(vals),"mean":sum(vals)/len(vals),"min":min(vals),"max":max(vals)}

def attack_defense_cross(attack: float, opponent_defense: float, league_baseline: float=1.0) -> float:
    if league_baseline<=0: raise ValueError("league_baseline must be positive")
    return max(0.0,float(attack)*float(opponent_defense)/league_baseline)

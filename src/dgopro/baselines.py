from __future__ import annotations
from typing import Any, Mapping, Sequence
from .team_strength import expected_score

def empirical_binary_baseline(train: Sequence[Mapping[str,Any]], outcome_key: str) -> dict[str,Any]:
    vals=[int(bool(r[outcome_key])) for r in train if r.get(outcome_key) is not None]
    if not vals: return {"probability":None,"n":0,"fitted":False}
    return {"probability":sum(vals)/len(vals),"n":len(vals),"fitted":True,"method":"train_base_rate"}

def elo_home_probability(home_elo: float, away_elo: float, *, home_advantage: float=60.0) -> float:
    return expected_score(float(home_elo),float(away_elo),home_advantage=home_advantage)

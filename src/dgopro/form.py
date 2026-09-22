from __future__ import annotations
from math import exp
from typing import Any, Mapping, Sequence

HORIZONS=(5,10,20)

def _weighted_mean(rows: Sequence[Mapping[str,Any]], metric: str, half_life_matches: float) -> float|None:
    vals=[]; weights=[]
    for i,row in enumerate(rows):
        value=row.get(metric)
        if value is None: continue
        w=exp(-0.6931471805599453*i/max(1e-9,half_life_matches)); vals.append(float(value)); weights.append(w)
    return sum(v*w for v,w in zip(vals,weights))/sum(weights) if weights else None

def multi_horizon_form(matches: Sequence[Mapping[str,Any]], metrics: Sequence[str], *, venue: str|None=None, half_life_matches: float=6.0) -> dict[str,Any]:
    ordered=list(matches)
    if venue is not None: ordered=[m for m in ordered if m.get("venue")==venue]
    result={"venue":venue or "all","half_life_matches":half_life_matches,"horizons":{}}
    for h in HORIZONS:
        sample=ordered[:h]; result["horizons"][f"L{h}"]={"n":len(sample),**{metric:_weighted_mean(sample,metric,half_life_matches) for metric in metrics}}
    result["structural"]={metric:_weighted_mean(ordered,metric,max(half_life_matches,12.0)) for metric in metrics}
    return result

def blend_horizons(profile: Mapping[str,Any], metric: str, weights: Mapping[str,float]|None=None) -> float|None:
    weights=dict(weights or {"L5":0.45,"L10":0.35,"L20":0.20}); pairs=[]
    for h,w in weights.items():
        value=(profile.get("horizons",{}).get(h,{}) or {}).get(metric)
        if value is not None: pairs.append((float(value),float(w)))
    return sum(v*w for v,w in pairs)/sum(w for _,w in pairs) if pairs else None

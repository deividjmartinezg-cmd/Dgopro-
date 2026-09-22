from __future__ import annotations
from statistics import mean, pstdev
from typing import Any, Mapping, Sequence

def scenario_stability(scenarios: Sequence[Mapping[str,Any]], *, threshold: float=.5) -> dict[str,Any]:
    probs=[float(s["probability"]) for s in scenarios if "probability" in s]
    weights=[max(0.0,float(s.get("weight",1.0))) for s in scenarios if "probability" in s]
    if not probs or sum(weights)<=0: return {"status":"unknown","stability":0.0}
    wmean=sum(p*w for p,w in zip(probs,weights))/sum(weights)
    spread=pstdev(probs) if len(probs)>1 else 0.0
    same_side=sum(w for p,w in zip(probs,weights) if (p>=threshold)==(wmean>=threshold))/sum(weights)
    stability=max(0.0,min(1.0,.6*same_side+.4*(1-min(1,spread/.25))))
    return {"status":"ok","weighted_probability":wmean,"scenario_sd":spread,"same_side_rate":same_side,"stability":stability,"n":len(probs)}

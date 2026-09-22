from __future__ import annotations
from typing import Any, Mapping

DEFAULT_WEIGHTS={"data_quality":.20,"calibration":.20,"oos_stability":.15,"model_agreement":.15,"scenario_stability":.10,"sample_reliability":.10,"drift_health":.10}

def prediction_quality_score(signals: Mapping[str,float], weights: Mapping[str,float]=DEFAULT_WEIGHTS) -> dict[str,Any]:
    available=[(k,max(0.0,min(1.0,float(signals[k]))),float(w)) for k,w in weights.items() if k in signals]
    if not available: return {"status":"unknown","score":None}
    denom=sum(w for _,_,w in available); score=sum(v*w for _,v,w in available)/denom
    uncertainty=max(0.0,min(1.0,float(signals.get("uncertainty",0.0))))
    score=max(0.0,score-.15*uncertainty)
    if score>=.80: grade="A"
    elif score>=.68: grade="B"
    elif score>=.55: grade="C"
    else: grade="D"
    return {"status":"ok","score":round(score*100,2),"grade":grade,"probability_independent":True,"components":{k:v for k,v,_ in available}}

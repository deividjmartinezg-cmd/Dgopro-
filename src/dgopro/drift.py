from __future__ import annotations
from typing import Any, Mapping

def relative_drift(reference: float, recent: float, *, lower_is_better: bool=True) -> float:
    if reference==0: return 0.0
    raw=(recent-reference)/abs(reference)
    return raw if lower_is_better else -raw

def drift_monitor(reference: Mapping[str,float], recent: Mapping[str,float], *, warning: float=.08, critical: float=.15) -> dict[str,Any]:
    metrics={}; worst=0.0
    for key in ("brier","log_loss","rps","ece"):
        if key not in reference or key not in recent: continue
        d=relative_drift(float(reference[key]),float(recent[key])); metrics[key]=d; worst=max(worst,d)
    status="CRITICAL" if worst>=critical else ("WARNING" if worst>=warning else "STABLE")
    return {"status":status,"metrics":metrics,"worst_degradation":worst,"weight_multiplier":0.5 if status=="CRITICAL" else (0.8 if status=="WARNING" else 1.0)}

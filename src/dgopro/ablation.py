from __future__ import annotations
from typing import Any, Mapping

def ablation_gate(baseline: Mapping[str,float], challenger: Mapping[str,float], *, min_relative_improvement: float=0.002) -> dict[str,Any]:
    lower=("brier","log_loss","rps","ece")
    deltas={}; improved=[]; worsened=[]
    for metric in lower:
        if metric not in baseline or metric not in challenger: continue
        b=float(baseline[metric]); c=float(challenger[metric]); delta=c-b
        rel=(b-c)/abs(b) if b else 0.0
        deltas[metric]={"delta":delta,"relative_improvement":rel}
        if rel>=min_relative_improvement: improved.append(metric)
        elif rel<=-min_relative_improvement: worsened.append(metric)
    promotable=bool(improved) and not worsened and bool(challenger.get("oos",False)) and bool(challenger.get("frozen_before_outcome",False))
    return {"status":"candidate" if promotable else "blocked","deltas":deltas,"improved":improved,"worsened":worsened,"requires_significance_test":True,"promotable":promotable}

from __future__ import annotations
from typing import Any, Mapping, Sequence
from .evaluation import brier, log_loss, ece
from .walkforward import frozen_prediction_gate

def evaluate_binary_predictions(rows: Sequence[Mapping[str,Any]], *, bins: int=10) -> dict[str,Any]:
    valid=[]; rejected=[]
    for r in rows:
        if not frozen_prediction_gate(r,r):
            rejected.append(r.get("prediction_id")); continue
        p=float(r["probability"]); y=int(r["outcome"])
        if not 0<=p<=1 or y not in (0,1): rejected.append(r.get("prediction_id")); continue
        valid.append((y,p))
    if not valid: return {"status":"blocked","reason":"no_valid_frozen_predictions","rejected":rejected}
    y=[x[0] for x in valid]; p=[x[1] for x in valid]
    hits=sum((pi>=.5)==bool(yi) for yi,pi in valid)/len(valid)
    return {"status":"ok","n":len(valid),"accuracy_at_0_5":hits,"brier":brier(y,p),"log_loss":log_loss(y,p),"ece":ece(y,p,bins),"rejected":rejected,"oos_required":True}

def compare_models(champion: Mapping[str,float], challenger: Mapping[str,float]) -> dict[str,Any]:
    metrics=("brier","log_loss","ece"); deltas={m:float(challenger[m])-float(champion[m]) for m in metrics if m in champion and m in challenger}
    wins=[m for m,d in deltas.items() if d<0]; losses=[m for m,d in deltas.items() if d>0]
    return {"deltas_challenger_minus_champion":deltas,"wins":wins,"losses":losses,"dominates":bool(wins) and not losses}

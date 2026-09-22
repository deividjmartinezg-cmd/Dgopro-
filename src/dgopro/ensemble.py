from __future__ import annotations
from typing import Any, Mapping, Sequence

def weighted_ensemble(predictions: Sequence[Mapping[str,Any]], *, require_oos: bool=True) -> dict[str,Any]:
    usable=[]
    for row in predictions:
        if require_oos and not row.get("oos_validated",False): continue
        p=float(row["probability"]); w=max(0.0,float(row.get("weight",1.0)))
        if 0<=p<=1 and w>0: usable.append((p,w,str(row.get("model","unknown"))))
    if not usable: return {"status":"blocked","reason":"no_validated_models"}
    total=sum(w for _,w,_ in usable); p=sum(p*w for p,w,_ in usable)/total
    variance=sum(w*(x-p)**2 for x,w,_ in usable)/total
    return {"status":"ok","probability":p,"model_disagreement_sd":variance**0.5,"models":[m for _,_,m in usable],"oos_only":require_oos}

def disagreement_penalty(probability: float, disagreement_sd: float, *, strength: float=.75) -> float:
    p=min(1,max(0,float(probability))); sd=max(0,float(disagreement_sd))
    # Shrink toward maximum uncertainty rather than pretending disagreement changes the event itself.
    shrink=min(1.0,strength*sd*2.0)
    return 0.5+(p-0.5)*(1.0-shrink)

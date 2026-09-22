from __future__ import annotations
import math
from typing import Sequence

def brier(y: Sequence[int], p: Sequence[float]) -> float:
    if len(y)!=len(p) or not y: raise ValueError("aligned non-empty inputs required")
    return sum((float(pi)-int(yi))**2 for yi,pi in zip(y,p))/len(y)

def log_loss(y: Sequence[int], p: Sequence[float], eps: float=1e-15) -> float:
    if len(y)!=len(p) or not y: raise ValueError("aligned non-empty inputs required")
    total=0.0
    for yi,pi in zip(y,p):
        q=min(1-eps,max(eps,float(pi)))
        total += -(int(yi)*math.log(q)+(1-int(yi))*math.log(1-q))
    return total/len(y)

def calibration_bins(y: Sequence[int], p: Sequence[float], bins: int=10) -> list[dict]:
    if len(y)!=len(p): raise ValueError("aligned inputs required")
    out=[]
    for i in range(bins):
        lo=i/bins; hi=(i+1)/bins
        idx=[j for j,x in enumerate(p) if lo<=x<(hi if i<bins-1 else hi+1e-12)]
        if not idx: continue
        mean_p=sum(float(p[j]) for j in idx)/len(idx); obs=sum(int(y[j]) for j in idx)/len(idx)
        out.append({"lo":lo,"hi":hi,"n":len(idx),"mean_probability":mean_p,"observed_frequency":obs,"gap":obs-mean_p})
    return out

def ece(y: Sequence[int], p: Sequence[float], bins: int=10) -> float:
    table=calibration_bins(y,p,bins); n=len(y)
    return sum(row["n"]/n*abs(row["gap"]) for row in table) if n else float("nan")

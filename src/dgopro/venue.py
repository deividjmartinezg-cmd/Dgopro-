from __future__ import annotations
from typing import Any, Mapping, Sequence

def venue_profile(matches: Sequence[Mapping[str,Any]], metric: str, *, prior_mean: float, prior_weight: float=5.0) -> dict[str,Any]:
    out={}
    for venue in ("home","away"):
        vals=[float(m[metric]) for m in matches if m.get("venue")==venue and m.get(metric) is not None]
        n=len(vals); raw=sum(vals)/n if n else None
        shrunk=(sum(vals)+prior_weight*prior_mean)/(n+prior_weight) if n or prior_weight else prior_mean
        out[venue]={"n":n,"raw_mean":raw,"shrunk_mean":shrunk}
    return {"metric":metric,"prior_mean":prior_mean,"prior_weight":prior_weight,"venues":out}

def venue_reliability(profile: Mapping[str,Any], venue: str, target_n: int=10) -> float:
    n=int((profile.get("venues",{}).get(venue,{}) or {}).get("n",0)); return min(1.0,n/max(1,target_n))

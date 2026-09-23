from __future__ import annotations
from datetime import datetime
from typing import Any, Mapping, Sequence

METRICS=("goals","xg","shots","sot","corners","cards")
DEFAULT_WEIGHTS=(.30,.25,.20,.15,.10)

def _dt(r: Mapping[str,Any]) -> datetime:
    return datetime.fromisoformat(str(r.get("kickoff") or r.get("date")).replace("Z","+00:00"))

def _side(row: Mapping[str,Any], team: str) -> tuple[str,str]|None:
    if row.get("home_team")==team: return "home","away"
    if row.get("away_team")==team: return "away","home"
    return None

def _value(row: Mapping[str,Any], prefix: str, metric: str) -> float|None:
    key=f"{prefix}_{metric}"
    try: return None if row.get(key) is None else float(row[key])
    except (TypeError,ValueError): return None

def weighted_recent(records: Sequence[Mapping[str,Any]], team: str, cutoff: datetime, *, venue: str|None=None, n: int=5, weights: Sequence[float]=DEFAULT_WEIGHTS) -> dict[str,Any]:
    history=[]
    for row in records:
        try:
            if _dt(row)>=cutoff: continue
        except Exception: continue
        side=_side(row,team)
        if side is None: continue
        own,opp=side
        if venue and own!=venue: continue
        history.append(row)
    history=sorted(history,key=_dt,reverse=True)[:n]
    out={"n":len(history),"cutoff":cutoff.isoformat(),"venue":venue,"leakage_safe":True}
    for metric in METRICS:
        pairs=[]
        for i,row in enumerate(history):
            own,opp=_side(row,team) or ("","")
            a=_value(row,own,metric); c=_value(row,opp,metric)
            if a is not None: pairs.append(("for",a,weights[i] if i<len(weights) else 1.0))
            if c is not None: pairs.append(("against",c,weights[i] if i<len(weights) else 1.0))
        for direction in ("for","against"):
            vals=[(v,w) for d,v,w in pairs if d==direction]
            out[f"{metric}_{direction}"]=sum(v*w for v,w in vals)/sum(w for _,w in vals) if vals and sum(w for _,w in vals)>0 else None
            out[f"{metric}_{direction}_n"]=len(vals)
    return out

def build_match_temporal_features(records: Sequence[Mapping[str,Any]], fixture: Mapping[str,Any]) -> dict[str,Any]:
    cutoff=_dt(fixture); home=str(fixture["home_team"]); away=str(fixture["away_team"])
    return {"match_id":fixture.get("match_id"),"cutoff":cutoff.isoformat(),"home":{"l5":weighted_recent(records,home,cutoff,n=5),"l5_venue":weighted_recent(records,home,cutoff,venue="home",n=5),"l10":weighted_recent(records,home,cutoff,n=10,weights=(.18,.16,.14,.12,.10,.08,.07,.06,.05,.04))},"away":{"l5":weighted_recent(records,away,cutoff,n=5),"l5_venue":weighted_recent(records,away,cutoff,venue="away",n=5),"l10":weighted_recent(records,away,cutoff,n=10,weights=(.18,.16,.14,.12,.10,.08,.07,.06,.05,.04))},"t1_safe":True}

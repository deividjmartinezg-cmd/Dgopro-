from __future__ import annotations
from collections import defaultdict
from typing import Any, Mapping, Sequence

FIELDS={"result":("home_goals","away_goals"),"shots":("home_shots","away_shots"),"sot":("home_sot","away_sot"),"corners":("home_corners","away_corners"),"cards":("home_cards","away_cards"),"xg":("home_xg","away_xg"),"lineup":("home_lineup","away_lineup"),"events":("events",),"tracking":("tracking_frames",)}

def coverage_audit(records: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    by=defaultdict(lambda:{m:0 for m in FIELDS}|{"n":0})
    totals={m:0 for m in FIELDS}; totals["n"]=len(records)
    for r in records:
        key=(str(r.get("competition_id") or "unknown"),str(r.get("season_id") or r.get("season") or "unknown")); by[key]["n"]+=1
        for m,fields in FIELDS.items():
            ok=all(r.get(f) is not None for f in fields)
            if ok: totals[m]+=1; by[key][m]+=1
    rows=[]
    for (competition,season),v in sorted(by.items()):
        row={"competition":competition,"season":season,**v}
        for m in FIELDS: row[f"{m}_pct"]=v[m]/v["n"] if v["n"] else 0.0
        rows.append(row)
    return {"totals":totals,"by_competition_season":rows,"observed_only":True}

def training_readiness(audit: Mapping[str,Any], thresholds: Mapping[str,int]|None=None) -> dict[str,Any]:
    thresholds=dict(thresholds or {"result":500,"shots":5000,"sot":5000,"corners":5000,"cards":5000,"xg":1000,"lineup":1000,"events":100000,"tracking":10000})
    totals=audit.get("totals",{}); out={}
    for m,t in thresholds.items():
        n=int(totals.get(m,0)); out[m]={"n":n,"threshold":t,"ready":n>=t,"shortfall":max(0,t-n)}
    return out

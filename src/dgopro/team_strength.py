from __future__ import annotations
from math import pow
from typing import Any, Mapping, Sequence

def expected_score(rating_a: float, rating_b: float, *, home_advantage: float=0.0) -> float:
    return 1.0/(1.0+pow(10.0,((rating_b-(rating_a+home_advantage))/400.0)))

def temporal_elo(records: Sequence[Mapping[str,Any]], *, initial: float=1500.0, k: float=20.0, home_advantage: float=60.0) -> dict[str,Any]:
    ratings: dict[str,float]={}; snapshots=[]
    ordered=sorted(records,key=lambda r:str(r.get("kickoff") or r.get("date") or ""))
    for row in ordered:
        h=str(row.get("home_team") or ""); a=str(row.get("away_team") or "")
        if not h or not a: continue
        try: hg=float(row["home_goals"]); ag=float(row["away_goals"])
        except (KeyError,TypeError,ValueError): continue
        rh=ratings.get(h,initial); ra=ratings.get(a,initial)
        snapshots.append({"match_id":row.get("match_id"),"kickoff":row.get("kickoff") or row.get("date"),"home_team":h,"away_team":a,"home_elo_pre":rh,"away_elo_pre":ra,"leakage_safe":True})
        eh=expected_score(rh,ra,home_advantage=home_advantage); sh=1.0 if hg>ag else (.5 if hg==ag else 0.0)
        delta=k*(sh-eh); ratings[h]=rh+delta; ratings[a]=ra-delta
    return {"ratings":ratings,"snapshots":snapshots,"initial":initial,"k":k,"home_advantage":home_advantage,"parameters_calibrated":False}

def pre_match_strength(snapshots: Sequence[Mapping[str,Any]], match_id: Any) -> dict[str,Any]|None:
    for s in snapshots:
        if s.get("match_id")==match_id: return dict(s)
    return None

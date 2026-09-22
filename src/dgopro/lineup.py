from __future__ import annotations
from typing import Any, Mapping, Sequence

def lineup_strength(players: Sequence[Mapping[str,Any]], *, expected_players: int=11) -> dict[str,Any]:
    used=[]; uncertainty=0.0
    for p in players:
        rating=float(p.get("rating",0)); minutes=max(0,min(90,float(p.get("expected_minutes",90))))/90.0
        availability=max(0,min(1,float(p.get("availability_probability",1))))
        role_weight=max(.5,min(1.5,float(p.get("role_weight",1))))
        used.append(rating*minutes*availability*role_weight)
        uncertainty += availability*(1-availability)
    n=len(players); completeness=min(1.0,n/max(1,expected_players))
    return {"strength":sum(used),"n_players":n,"completeness":completeness,"availability_uncertainty":uncertainty/max(1,n),"confirmed":all(float(p.get("availability_probability",1))==1 for p in players) and n>=expected_players}

def lineup_delta(team: Mapping[str,Any], opponent: Mapping[str,Any]) -> float:
    return float(team.get("strength",0))-float(opponent.get("strength",0))

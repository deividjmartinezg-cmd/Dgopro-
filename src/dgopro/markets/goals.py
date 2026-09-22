from __future__ import annotations
from math import exp
from typing import Any
from .counts import count_distribution, summarize

def goals_engine(home_xg: float, away_xg: float) -> dict[str,Any]:
    if home_xg<0 or away_xg<0: raise ValueError("xG must be non-negative")
    total=home_xg+away_xg
    h0=exp(-home_xg); a0=exp(-away_xg)
    btts_yes=(1-h0)*(1-a0)
    return {"home_xg":home_xg,"away_xg":away_xg,"total":summarize(total,(1.5,2.5,3.5),12),"btts":{"yes":btts_yes,"no":1-btts_yes},"model":"independent_poisson_baseline","dixon_coles_adjusted":False,"calibrated":False}

def score_matrix(home_xg: float, away_xg: float, max_goals: int=8) -> dict[str,float]:
    h=count_distribution(home_xg,max_goals); a=count_distribution(away_xg,max_goals)
    return {f"{i}-{j}":hp*ap for i,hp in h.items() for j,ap in a.items()}

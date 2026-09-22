from __future__ import annotations
from typing import Any
from .goals import score_matrix

def result_engine(home_xg: float, away_xg: float, max_goals: int=10) -> dict[str,Any]:
    matrix=score_matrix(home_xg,away_xg,max_goals); home=draw=away=0.0
    for score,p in matrix.items():
        h,a=map(int,score.split("-"))
        if h>a: home+=p
        elif h==a: draw+=p
        else: away+=p
    total=home+draw+away
    home,draw,away=(home/total,draw/total,away/total)
    return {"1":home,"X":draw,"2":away,"1X":home+draw,"X2":draw+away,"12":home+away,"model":"score_distribution_baseline","calibrated":False}

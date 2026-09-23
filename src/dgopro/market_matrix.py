from __future__ import annotations
from typing import Any, Mapping, Sequence
from .rc1_gate import market_rc1_gate
from .error_analysis import diagnose


def market_evidence(market: str, predictions: Sequence[Mapping[str,Any]], *, baseline_brier: float|None, seasons: int, competitions: int) -> dict[str,Any]:
    rows=[r for r in predictions if r.get("probability") is not None and r.get("outcome") is not None]
    n=len(rows)
    if not rows:
        return {"market":market,"oos_n":0,"seasons":seasons,"competitions":competitions,"ece":None,"brier":None,"baseline_brier":baseline_brier,"strict_walk_forward":True,"frozen_before_outcome":True,"leakage_detected":False}
    brier=sum((float(r["probability"])-int(r["outcome"]))**2 for r in rows)/n
    # weighted absolute calibration gap over deciles
    bins=[]
    for b in range(10):
        subset=[r for r in rows if b/10<=float(r["probability"])<((b+1)/10) or (b==9 and float(r["probability"])==1)]
        if subset:
            mp=sum(float(r["probability"]) for r in subset)/len(subset); obs=sum(int(r["outcome"]) for r in subset)/len(subset)
            bins.append((len(subset),abs(obs-mp)))
    ece=sum(k*g for k,g in bins)/n if bins else None
    return {"market":market,"oos_n":n,"seasons":seasons,"competitions":competitions,"ece":ece,"brier":brier,"baseline_brier":baseline_brier,"strict_walk_forward":all(bool(r.get("strict_oos",True)) for r in rows),"frozen_before_outcome":all(bool(r.get("frozen_before_outcome",False)) for r in rows),"leakage_detected":any(bool(r.get("leakage_detected",False)) for r in rows),"error_analysis":diagnose(rows)}


def build_market_matrix(items: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    evidence=[]; gates=[]
    for item in items:
        e=market_evidence(str(item["market"]),item.get("predictions",[]),baseline_brier=item.get("baseline_brier"),seasons=int(item.get("seasons",0)),competitions=int(item.get("competitions",0)))
        evidence.append(e); gates.append(market_rc1_gate(e,thresholds=item.get("thresholds")))
    return {"evidence":evidence,"gates":gates,"rc1":[g["market"] for g in gates if g["rc1"]],"challenger":[g["market"] for g in gates if not g["rc1"]]}

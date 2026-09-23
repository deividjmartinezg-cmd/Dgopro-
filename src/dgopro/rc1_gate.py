from __future__ import annotations
from typing import Any, Mapping, Sequence

DEFAULTS={"min_oos_n":1000,"max_ece":0.05,"max_brier_binary":0.25,"min_seasons":3,"min_competitions":1}

def market_rc1_gate(evidence: Mapping[str,Any], *, thresholds: Mapping[str,float]|None=None) -> dict[str,Any]:
    t=dict(DEFAULTS); t.update(dict(thresholds or {})); failures=[]
    n=int(evidence.get("oos_n",0)); seasons=int(evidence.get("seasons",0)); competitions=int(evidence.get("competitions",0))
    ece=evidence.get("ece"); brier=evidence.get("brier"); baseline_brier=evidence.get("baseline_brier")
    if n<int(t["min_oos_n"]): failures.append("insufficient_oos_n")
    if seasons<int(t["min_seasons"]): failures.append("insufficient_temporal_coverage")
    if competitions<int(t["min_competitions"]): failures.append("insufficient_competition_coverage")
    if ece is None or float(ece)>float(t["max_ece"]): failures.append("calibration_failed")
    if brier is None or float(brier)>float(t["max_brier_binary"]): failures.append("brier_failed")
    if baseline_brier is None or brier is None or float(brier)>=float(baseline_brier): failures.append("does_not_beat_baseline")
    if not bool(evidence.get("strict_walk_forward",False)): failures.append("not_strict_walk_forward")
    if not bool(evidence.get("frozen_before_outcome",False)): failures.append("predictions_not_frozen")
    if bool(evidence.get("leakage_detected",False)): failures.append("leakage_detected")
    passed=not failures
    return {"market":evidence.get("market"),"rc1":passed,"status":"RC1" if passed else "CHALLENGER","failures":failures,"thresholds":t,"evidence":dict(evidence)}

def rc1_matrix(markets: Sequence[Mapping[str,Any]], *, thresholds: Mapping[str,float]|None=None) -> dict[str,Any]:
    rows=[market_rc1_gate(m,thresholds=thresholds) for m in markets]
    return {"rows":rows,"rc1_markets":[r["market"] for r in rows if r["rc1"]],"blocked_markets":[r["market"] for r in rows if not r["rc1"]],"partial_release_allowed":True,"all_markets_required":False}

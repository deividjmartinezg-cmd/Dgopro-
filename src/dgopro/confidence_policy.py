from __future__ import annotations
from typing import Any, Mapping

DEFAULTS={"min_probability":0.55,"min_bin_n":100,"max_bin_gap":0.05,"max_uncertainty_width":0.20}

def decision(probability: float, evidence: Mapping[str,Any], *, thresholds: Mapping[str,float]|None=None) -> dict[str,Any]:
    t=dict(DEFAULTS); t.update(dict(thresholds or {})); p=max(0.0,min(1.0,float(probability))); failures=[]
    if not bool(evidence.get("market_rc1",False)): failures.append("market_not_rc1")
    if not bool(evidence.get("calibrated",False)): failures.append("uncalibrated")
    if int(evidence.get("calibration_bin_n",0))<int(t["min_bin_n"]): failures.append("thin_calibration_bin")
    if abs(float(evidence.get("calibration_gap",1.0)))>float(t["max_bin_gap"]): failures.append("calibration_gap")
    lo=evidence.get("probability_lo"); hi=evidence.get("probability_hi")
    if lo is None or hi is None: failures.append("uncertainty_missing")
    elif float(hi)-float(lo)>float(t["max_uncertainty_width"]): failures.append("uncertainty_too_wide")
    if p<float(t["min_probability"]): failures.append("weak_probability")
    if failures:
        severe={"market_not_rc1","uncalibrated","uncertainty_missing"}
        status="ABSTAIN" if severe.intersection(failures) else "LOW_CONFIDENCE"
    else: status="PREDICT"
    return {"status":status,"probability":p,"failures":failures,"thresholds":t,"evidence":dict(evidence)}

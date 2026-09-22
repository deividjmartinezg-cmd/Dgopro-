from __future__ import annotations
from typing import Any, Mapping

def promotion_decision(report: Mapping[str,Any], *, min_samples: int=500, max_ece: float=.05) -> dict[str,Any]:
    reasons=[]
    if int(report.get("n",0))<min_samples: reasons.append("insufficient_sample")
    if not bool(report.get("strict_oos",False)): reasons.append("not_strict_oos")
    if not bool(report.get("predictions_frozen",False)): reasons.append("predictions_not_frozen")
    if float(report.get("ece",1.0))>max_ece: reasons.append("calibration_too_weak")
    if not bool(report.get("beats_baseline",False)): reasons.append("does_not_beat_baseline")
    if not bool(report.get("ablation_passed",False)): reasons.append("ablation_failed")
    if report.get("drift_status") not in ("STABLE",None): reasons.append("active_drift")
    if not bool(report.get("arb_review_passed",False)): reasons.append("arb_review_missing_or_failed")
    return {"promote":not reasons,"decision":"PROMOTE" if not reasons else "KEEP_CHALLENGER","reasons":reasons,"automatic_promotion":False}

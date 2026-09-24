from __future__ import annotations

from math import log
from typing import Any, Mapping, Sequence

DEFAULTS = {
    "min_n": 100,
    "min_days": 5,
    "max_abs_calibration_gap": 0.08,
    "max_brier_worsening_vs_baseline": 0.02,
    "max_penalty": 15.0,
}


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def summarize_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    valid=[r for r in rows if r.get("probability") is not None and r.get("outcome") is not None]
    n=len(valid)
    if not valid:
        return {"n":0,"mean_probability":None,"observed_rate":None,"calibration_gap":None,"brier":None,"log_loss":None,"days":0}
    ps=[_clip01(float(r["probability"])) for r in valid]
    ys=[1 if int(r["outcome"]) else 0 for r in valid]
    eps=1e-12
    mean_p=sum(ps)/n; obs=sum(ys)/n
    brier=sum((p-y)**2 for p,y in zip(ps,ys))/n
    log_loss=-sum(y*log(max(eps,p))+(1-y)*log(max(eps,1-p)) for p,y in zip(ps,ys))/n
    days=len({str(r.get("date") or r.get("kickoff_date") or "") for r in valid if r.get("date") or r.get("kickoff_date")})
    return {"n":n,"mean_probability":mean_p,"observed_rate":obs,"calibration_gap":obs-mean_p,"brier":brier,"log_loss":log_loss,"days":days}


def reliability_decision(rows: Sequence[Mapping[str, Any]], *, baseline_brier: float | None = None, thresholds: Mapping[str,float] | None = None) -> dict[str, Any]:
    t=dict(DEFAULTS); t.update(dict(thresholds or {}))
    s=summarize_family(rows)
    if s["n"] < int(t["min_n"]) or s["days"] < int(t["min_days"]):
        return {**s,"status":"OBSERVE","penalty":0.0,"reasons":["insufficient_prospective_evidence"],"thresholds":t}

    reasons=[]; severity=0.0
    gap=abs(float(s["calibration_gap"]))
    if gap > float(t["max_abs_calibration_gap"]):
        reasons.append("persistent_miscalibration")
        severity += min(1.0, gap/0.20)
    if baseline_brier is not None:
        worsening=float(s["brier"])-float(baseline_brier)
        if worsening > float(t["max_brier_worsening_vs_baseline"]):
            reasons.append("brier_worse_than_baseline")
            severity += min(1.0, worsening/0.10)
    penalty=min(float(t["max_penalty"]), float(t["max_penalty"])*severity/2.0) if reasons else 0.0
    return {**s,"status":"PENALIZE" if reasons else "STABLE","penalty":round(penalty,2),"reasons":reasons,"thresholds":t}


def family_reliability_matrix(rows: Sequence[Mapping[str, Any]], *, baseline_brier_by_family: Mapping[str,float] | None=None, thresholds: Mapping[str,float] | None=None) -> list[dict[str,Any]]:
    grouped: dict[str,list[Mapping[str,Any]]]={}
    for row in rows:
        family=str(row.get("market_family") or "unknown").lower()
        grouped.setdefault(family,[]).append(row)
    baselines=dict(baseline_brier_by_family or {})
    out=[]
    for family, items in sorted(grouped.items()):
        d=reliability_decision(items,baseline_brier=baselines.get(family),thresholds=thresholds)
        out.append({"market_family":family,**d})
    return out

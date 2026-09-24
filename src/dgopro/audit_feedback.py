from __future__ import annotations

from math import log
from typing import Any, Mapping, Sequence

from .market_reliability import family_reliability_matrix
from .prospective_ledger import prediction_digest_valid


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def audit_eligible(row: Mapping[str, Any]) -> tuple[bool, str]:
    """Return whether a ledger row can enter prospective performance metrics."""
    if str(row.get("audit_status", "")).upper() != "SETTLED":
        return False, "not_settled"
    if bool(row.get("excluded_from_metrics", False)):
        return False, "explicitly_excluded"
    if not bool(row.get("frozen_before_outcome", False)):
        return False, "not_frozen_before_outcome"
    if not bool(row.get("settled_after_freeze", False)):
        return False, "settlement_not_after_freeze"
    if row.get("outcome") is None or row.get("probability") is None:
        return False, "missing_probability_or_outcome"
    if not prediction_digest_valid(row):
        return False, "digest_mismatch"

    meta=dict(row.get("metadata") or {})
    if not bool(meta.get("prospective", False)):
        return False, "not_prospective"
    if not bool(meta.get("publication_integrity_passed", False)):
        return False, "publication_integrity_not_passed"
    return True, "eligible"


def metric_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out=[]
    for row in rows:
        ok,_=audit_eligible(row)
        if not ok:
            continue
        meta=dict(row.get("metadata") or {})
        kickoff=str(row.get("kickoff") or "")
        out.append({
            "match_id":row.get("match_id"),
            "market":row.get("market"),
            "market_family":meta.get("market_family", row.get("market_family", "unknown")),
            "probability":_clip01(float(row["probability"])),
            "outcome":1 if int(row["outcome"]) else 0,
            "date":meta.get("date") or kickoff[:10],
            "kickoff_date":kickoff[:10],
            "model_version":row.get("model_version"),
        })
    return out


def _binary_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n":0,"hits":0,"misses":0,"hit_rate":None,"brier":None,"log_loss":None,"mean_probability":None,"observed_rate":None}
    ps=[_clip01(float(r["probability"])) for r in rows]
    ys=[1 if int(r["outcome"]) else 0 for r in rows]
    n=len(rows); eps=1e-12
    hits=sum(ys)
    brier=sum((p-y)**2 for p,y in zip(ps,ys))/n
    ll=-sum(y*log(max(eps,p))+(1-y)*log(max(eps,1-p)) for p,y in zip(ps,ys))/n
    return {
        "n":n,
        "hits":hits,
        "misses":n-hits,
        "hit_rate":hits/n,
        "brier":brier,
        "log_loss":ll,
        "mean_probability":sum(ps)/n,
        "observed_rate":hits/n,
    }


def prospective_audit_report(
    rows: Sequence[Mapping[str, Any]],
    *,
    baseline_brier_by_family: Mapping[str,float] | None=None,
    reliability_thresholds: Mapping[str,float] | None=None,
) -> dict[str, Any]:
    """Build a contamination-safe audit report and reliability feedback payload."""
    valid=metric_rows(rows)
    exclusions: dict[str,int]={}
    invalidated=0
    for row in rows:
        if str(row.get("audit_status", "")).upper()=="INVALIDATED":
            invalidated+=1
        ok,reason=audit_eligible(row)
        if not ok:
            exclusions[reason]=exclusions.get(reason,0)+1

    families=family_reliability_matrix(
        valid,
        baseline_brier_by_family=baseline_brier_by_family,
        thresholds=reliability_thresholds,
    )
    penalties={r["market_family"]:float(r.get("penalty",0.0)) for r in families}
    return {
        "total_rows":len(rows),
        "eligible_rows":len(valid),
        "invalidated_rows":invalidated,
        "excluded_rows":len(rows)-len(valid),
        "exclusions":dict(sorted(exclusions.items())),
        "metrics":_binary_metrics(valid),
        "family_reliability":families,
        "reliability_penalty_by_family":penalties,
        "metric_rows":valid,
    }

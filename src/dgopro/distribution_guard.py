from __future__ import annotations
from typing import Any, Mapping

DEFAULTS = {
    "max_adjusted_p4plus_for_under35": 0.12,
    "max_runaway_risk": 0.55,
    "risk_uplift_weight": 0.08,
}


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def under35_tail_guard(evidence: Mapping[str, Any], *, thresholds: Mapping[str, float] | None = None) -> dict[str, Any]:
    """Audit the 4+ goal tail before allowing Under 3.5 into a TOP.

    Inputs are pre-match probabilities/normalized risk signals. The guard is
    intentionally conservative and its defaults are provisional until enough OOS
    evidence is accumulated.
    """
    t=dict(DEFAULTS); t.update(dict(thresholds or {}))
    p4=evidence.get("p_4plus")
    if p4 is None:
        return {"status":"ABSTAIN","eligible":False,"reason":"p4plus_missing","thresholds":t}

    risks=[
        _clip01(evidence.get("attack_mismatch",0.0)),
        _clip01(evidence.get("defensive_fragility",0.0)),
        _clip01(evidence.get("early_lead_runaway",0.0)),
        _clip01(evidence.get("transition_exposure",0.0)),
    ]
    runaway=max(risks)
    mean_risk=sum(risks)/len(risks)
    adjusted=_clip01(float(p4) + float(t["risk_uplift_weight"])*mean_risk)

    failures=[]
    if adjusted > float(t["max_adjusted_p4plus_for_under35"]):
        failures.append("tail_4plus_too_large")
    if runaway > float(t["max_runaway_risk"]):
        failures.append("runaway_game_state_risk")

    if failures:
        status="LOW_CONFIDENCE"
        eligible=False
    else:
        status="PREDICT"
        eligible=True
    return {
        "status":status,
        "eligible":eligible,
        "p_4plus":_clip01(float(p4)),
        "adjusted_p_4plus":adjusted,
        "runaway_risk":runaway,
        "failures":failures,
        "thresholds":t,
    }

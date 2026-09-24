from __future__ import annotations

from math import log10
from typing import Any, Mapping, Sequence

WEIGHTS = {
    "calibrated_probability": 0.30,
    "calibration_quality": 0.20,
    "igc": 0.15,
    "coverage": 0.10,
    "stability": 0.10,
    "convergence": 0.05,
    "uncertainty_quality": 0.05,
    "sample_quality": 0.05,
}

RISK_PENALTY = {"green": 0.0, "yellow": 4.0, "red": 10.0}
STATUS_PENALTY = {"PREDICT": 0.0, "LOW_CONFIDENCE": 6.0, "ABSTAIN": 100.0}


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def sample_quality(n: int, target_n: int = 1000) -> float:
    """Smoothly penalize thin evidence while saturating at target_n."""
    if n <= 0:
        return 0.0
    return _clip01(log10(n + 1) / log10(target_n + 1))


def calibration_quality(ece: float | None, max_ece: float = 0.10) -> float:
    """1.0 is perfect empirical calibration; 0.0 at or beyond max_ece."""
    if ece is None:
        return 0.0
    return _clip01(1.0 - float(ece) / max_ece)


def uncertainty_quality(width: float | None, max_width: float = 0.30) -> float:
    """Rewards narrow uncertainty intervals; missing uncertainty gets no credit."""
    if width is None:
        return 0.0
    return _clip01(1.0 - float(width) / max_width)


def ranking_score(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return a reproducible 0-100 TOP score plus eligibility metadata.

    reliability_penalty is optional and must be produced by the evidence-gated
    market_reliability monitor. Thin samples therefore add no penalty by default.
    """
    prospective = bool(row.get("prospective", False))
    frozen = bool(row.get("frozen_before_outcome", False))
    status = str(row.get("status", "ABSTAIN")).upper()
    risk = str(row.get("risk", "red")).lower()

    components = {
        "calibrated_probability": _clip01(row.get("calibrated_probability", 0.0)),
        "calibration_quality": calibration_quality(row.get("ece")),
        "igc": _clip01(float(row.get("igc", 0.0)) / 100.0),
        "coverage": _clip01(row.get("coverage", 0.0)),
        "stability": _clip01(row.get("stability", 0.0)),
        "convergence": _clip01(row.get("convergence", 0.0)),
        "uncertainty_quality": uncertainty_quality(row.get("uncertainty_width")),
        "sample_quality": sample_quality(int(row.get("oos_n", 0))),
    }

    raw = 100.0 * sum(WEIGHTS[k] * components[k] for k in WEIGHTS)
    reliability_penalty=max(0.0, min(15.0, float(row.get("reliability_penalty", 0.0))))
    penalty = RISK_PENALTY.get(risk, 10.0) + STATUS_PENALTY.get(status, 100.0) + reliability_penalty
    if not prospective:
        penalty += 100.0
    if not frozen:
        penalty += 100.0

    score = max(0.0, raw - penalty)
    eligible = prospective and frozen and status != "ABSTAIN" and score > 0.0
    return {
        "ranking_score": round(score, 2),
        "raw_score": round(raw, 2),
        "penalty": round(penalty, 2),
        "reliability_penalty": round(reliability_penalty, 2),
        "eligible": eligible,
        "components": components,
    }


def rank_markets(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for row in rows:
        scored = ranking_score(row)
        if not scored["eligible"]:
            continue
        ranked.append({**dict(row), **scored})
    ranked.sort(
        key=lambda r: (
            r["ranking_score"],
            float(r.get("calibrated_probability", 0.0)),
            float(r.get("igc", 0.0)),
        ),
        reverse=True,
    )
    for i, row in enumerate(ranked, start=1):
        row["rank"] = i
    return ranked


def official_tops(rows: Sequence[Mapping[str, Any]], sizes: Sequence[int] = (30, 20, 10, 5)) -> dict[str, list[dict[str, Any]]]:
    ranked = rank_markets(rows)
    return {f"top_{size}": ranked[:size] for size in sizes}

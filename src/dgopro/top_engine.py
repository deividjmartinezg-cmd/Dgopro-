from __future__ import annotations

from typing import Any, Mapping, Sequence

from .confidence_policy import decision as confidence_decision
from .ranking_score import rank_markets


def _uncertainty_width(row: Mapping[str, Any]) -> float | None:
    if row.get("uncertainty_width") is not None:
        return float(row["uncertainty_width"])
    lo = row.get("probability_lo")
    hi = row.get("probability_hi")
    if lo is None or hi is None:
        return None
    return max(0.0, float(hi) - float(lo))


def _base_rank_row(row: Mapping[str, Any], probability: float, status: str) -> dict[str, Any]:
    return {
        **dict(row),
        "calibrated_probability": max(0.0, min(1.0, float(probability))),
        "status": status,
        "uncertainty_width": _uncertainty_width(row),
        "prospective": bool(row.get("prospective", False)),
        "frozen_before_outcome": bool(row.get("frozen_before_outcome", False)),
    }


def build_rc1_top(rows: Sequence[Mapping[str, Any]], *, confidence_thresholds: Mapping[str, float] | None = None) -> list[dict[str, Any]]:
    """Build the certified RC1 TOP.

    RC1 candidates must be calibrated, pass the confidence policy as PREDICT,
    be prospective, and have been frozen before the outcome. LOW_CONFIDENCE and
    ABSTAIN rows are excluded from the official RC1 TOP rather than merely
    penalized.
    """
    candidates: list[dict[str, Any]] = []
    for row in rows:
        p = row.get("calibrated_probability")
        if p is None:
            continue
        evidence = {
            "market_rc1": bool(row.get("market_rc1", False)),
            "calibrated": bool(row.get("calibrated", False)),
            "calibration_bin_n": int(row.get("calibration_bin_n", 0)),
            "calibration_gap": float(row.get("calibration_gap", 1.0)),
            "probability_lo": row.get("probability_lo"),
            "probability_hi": row.get("probability_hi"),
        }
        d = confidence_decision(float(p), evidence, thresholds=confidence_thresholds)
        if d["status"] != "PREDICT":
            continue
        candidate = _base_rank_row(row, float(p), "PREDICT")
        candidate.update({
            "top_tier": "RC1",
            "probability_basis": "CALIBRATED",
            "probability_certified": True,
            "confidence_failures": [],
        })
        candidates.append(candidate)
    return rank_markets(candidates)


def build_challenger_top(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build a clearly labeled research/Challenger TOP without faking RC1 status.

    The model estimate can be ranked, but it is explicitly marked as
    non-certified. Missing ECE/OOS evidence earns zero credit in ranking_score,
    which naturally pushes thin-evidence signals below better-supported ones.
    """
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if bool(row.get("market_rc1", False)):
            continue
        p = row.get("model_probability", row.get("probability"))
        if p is None:
            continue
        status = str(row.get("status", "LOW_CONFIDENCE")).upper()
        if status == "ABSTAIN":
            continue
        candidate = _base_rank_row(row, float(p), status)
        candidate.update({
            "top_tier": "CHALLENGER",
            "probability_basis": "MODEL_ESTIMATE",
            "probability_certified": False,
            "calibration_status": "UNVERIFIED",
        })
        # Do not grant calibration credit to an uncertified probability.
        candidate["ece"] = row.get("ece") if bool(row.get("calibrated", False)) else None
        candidates.append(candidate)
    return rank_markets(candidates)


def official_top_views(rows: Sequence[Mapping[str, Any]], *, tier: str = "challenger", sizes: Sequence[int] = (30, 20, 10, 5), confidence_thresholds: Mapping[str, float] | None = None) -> dict[str, Any]:
    tier_normalized = str(tier).strip().lower()
    if tier_normalized == "rc1":
        ranked = build_rc1_top(rows, confidence_thresholds=confidence_thresholds)
        label = "RC1"
    elif tier_normalized == "challenger":
        ranked = build_challenger_top(rows)
        label = "CHALLENGER"
    else:
        raise ValueError("tier must be 'rc1' or 'challenger'")

    return {
        "tier": label,
        "ranked": ranked,
        "tops": {f"top_{int(size)}": ranked[: int(size)] for size in sizes},
        "ranking_consistent": True,
        "probability_certified": label == "RC1",
    }

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .confidence_policy import decision as confidence_decision
from .data_integrity import publication_integrity_gate
from .distribution_guard import under35_tail_guard
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


def _publication_integrity_ok(row: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    record=row.get("integrity_record")
    if isinstance(record, Mapping):
        result=publication_integrity_gate(record)
        return result.passed, {
            "integrity_score":result.score,
            "integrity_failures":list(result.failures),
            "integrity_warnings":list(result.warnings),
        }
    passed=bool(row.get("publication_integrity_passed", False))
    return passed, {"integrity_score":1.0 if passed else 0.0,"integrity_failures":[] if passed else ["publication_integrity_not_verified"],"integrity_warnings":[]}


def _distribution_ok(row: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    market=str(row.get("market", "")).lower().replace(" ", "")
    family=str(row.get("market_family", "")).lower()
    under35 = market in {"u3.5","under3.5","under_3_5","-3.5"} or (family=="goals" and str(row.get("line", "")) in {"3.5","-3.5"} and str(row.get("side","")).lower()=="under")
    if not under35:
        return True, {"distribution_guard":"not_required"}
    result=under35_tail_guard(row.get("distribution_evidence", {}), thresholds=row.get("distribution_thresholds"))
    return bool(result.get("eligible",False)), {"distribution_guard":result}


def _top_market_allowed(row: Mapping[str, Any]) -> bool:
    family=str(row.get("market_family", "")).strip().lower()
    market=str(row.get("market", "")).strip().lower()
    # Exact score is descriptive distribution output, never a primary TOP market.
    return family not in {"exact_score","correct_score"} and market not in {"exact_score","correct_score"}


def _pre_top_gate(row: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    if not _top_market_allowed(row):
        return False, {"pre_top_failure":"market_not_top_eligible"}
    integrity_ok, integrity_meta=_publication_integrity_ok(row)
    if not integrity_ok:
        return False, integrity_meta
    distribution_ok, distribution_meta=_distribution_ok(row)
    if not distribution_ok:
        return False, {**integrity_meta, **distribution_meta}
    return True, {**integrity_meta, **distribution_meta}


def build_rc1_top(rows: Sequence[Mapping[str, Any]], *, confidence_thresholds: Mapping[str, float] | None = None) -> list[dict[str, Any]]:
    """Build the certified RC1 TOP after integrity, distribution and confidence gates."""
    candidates: list[dict[str, Any]] = []
    for row in rows:
        gate_ok, gate_meta=_pre_top_gate(row)
        if not gate_ok:
            continue
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
        candidate.update(gate_meta)
        candidate.update({
            "top_tier": "RC1",
            "probability_basis": "CALIBRATED",
            "probability_certified": True,
            "confidence_failures": [],
        })
        candidates.append(candidate)
    return rank_markets(candidates)


def build_challenger_top(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build a non-certified Challenger TOP after strict pre-publication gates."""
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if bool(row.get("market_rc1", False)):
            continue
        gate_ok, gate_meta=_pre_top_gate(row)
        if not gate_ok:
            continue
        p = row.get("model_probability", row.get("probability"))
        if p is None:
            continue
        status = str(row.get("status", "LOW_CONFIDENCE")).upper()
        if status == "ABSTAIN":
            continue
        candidate = _base_rank_row(row, float(p), status)
        candidate.update(gate_meta)
        candidate.update({
            "top_tier": "CHALLENGER",
            "probability_basis": "MODEL_ESTIMATE",
            "probability_certified": False,
            "calibration_status": "UNVERIFIED",
        })
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

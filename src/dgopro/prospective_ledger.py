from __future__ import annotations
from hashlib import sha256
import json
from typing import Any, Mapping


def _freeze_core(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "match_id": row["match_id"],
        "kickoff": row["kickoff"],
        "market": row["market"],
        "probability": max(0.0, min(1.0, float(row["probability"]))),
        "model_version": row["model_version"],
        "feature_cutoff": row["feature_cutoff"],
        "metadata": dict(row.get("metadata") or {}),
        "outcome": None,
        "frozen_before_outcome": True,
    }


def _digest(core: Mapping[str, Any]) -> str:
    return sha256(json.dumps(dict(core), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def freeze_prediction(*, match_id: str, kickoff: str, market: str, probability: float, model_version: str, feature_cutoff: str, metadata: Mapping[str,Any]|None=None) -> dict[str,Any]:
    core={
        "match_id":match_id,
        "kickoff":kickoff,
        "market":market,
        "probability":max(0.0,min(1.0,float(probability))),
        "model_version":model_version,
        "feature_cutoff":feature_cutoff,
        "metadata":dict(metadata or {}),
        "outcome":None,
        "frozen_before_outcome":True,
    }
    return {
        **core,
        "prediction_sha256":_digest(core),
        "audit_status":"FROZEN",
        "excluded_from_metrics":False,
    }


def prediction_digest_valid(row: Mapping[str, Any]) -> bool:
    try:
        expected=str(row.get("prediction_sha256") or "")
        return bool(expected) and _digest(_freeze_core(row)) == expected
    except Exception:
        return False


def settle_prediction(frozen: Mapping[str,Any], outcome: int) -> dict[str,Any]:
    if frozen.get("outcome") is not None:
        raise ValueError("prediction already settled")
    if str(frozen.get("audit_status", "FROZEN")).upper() == "INVALIDATED":
        raise ValueError("invalidated prediction cannot be settled")
    if not prediction_digest_valid(frozen):
        raise ValueError("prediction digest mismatch or unfrozen prediction")
    row=dict(frozen)
    row["outcome"]=int(bool(outcome))
    row["settled_after_freeze"]=True
    row["audit_status"]="SETTLED"
    row["excluded_from_metrics"]=False
    return row


def invalidate_prediction(frozen: Mapping[str, Any], reason: str) -> dict[str, Any]:
    """Invalidate a frozen row without turning it into a HIT/MISS observation."""
    if frozen.get("outcome") is not None:
        raise ValueError("settled prediction cannot be invalidated")
    if not prediction_digest_valid(frozen):
        raise ValueError("prediction digest mismatch or unfrozen prediction")
    row=dict(frozen)
    row["audit_status"]="INVALIDATED"
    row["invalidation_reason"]=str(reason)
    row["excluded_from_metrics"]=True
    row["settled_after_freeze"]=False
    return row

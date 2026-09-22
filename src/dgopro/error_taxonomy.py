from __future__ import annotations
from typing import Any, Mapping

ERROR_TYPES=("DATA_ERROR","LINEUP_ERROR","TACTICAL_ERROR","MODEL_ERROR","CALIBRATION_ERROR","TAIL_EVENT","NORMAL_VARIANCE","CONCEPT_DRIFT","UNKNOWN")

def classify_error(evidence: Mapping[str,Any]) -> dict[str,Any]:
    if evidence.get("data_invalid"): label="DATA_ERROR"
    elif evidence.get("unexpected_lineup_material"): label="LINEUP_ERROR"
    elif evidence.get("tactical_regime_miss"): label="TACTICAL_ERROR"
    elif evidence.get("drift_detected"): label="CONCEPT_DRIFT"
    elif evidence.get("calibration_bucket_failed"): label="CALIBRATION_ERROR"
    elif evidence.get("rare_red_card") or evidence.get("rare_penalty") or evidence.get("major_injury_event"): label="TAIL_EVENT"
    elif evidence.get("distribution_miss_systematic"): label="MODEL_ERROR"
    elif evidence.get("outcome_within_predicted_tail"): label="NORMAL_VARIANCE"
    else: label="UNKNOWN"
    return {"label":label,"valid":label in ERROR_TYPES,"automatic_model_change":False,"requires_repeated_evidence":label not in ("DATA_ERROR","LINEUP_ERROR")}

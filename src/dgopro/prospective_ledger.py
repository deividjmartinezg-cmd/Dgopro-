from __future__ import annotations
from hashlib import sha256
import json
from typing import Any, Mapping

def freeze_prediction(*, match_id: str, kickoff: str, market: str, probability: float, model_version: str, feature_cutoff: str, metadata: Mapping[str,Any]|None=None) -> dict[str,Any]:
    core={"match_id":match_id,"kickoff":kickoff,"market":market,"probability":max(0.0,min(1.0,float(probability))),"model_version":model_version,"feature_cutoff":feature_cutoff,"metadata":dict(metadata or {}),"outcome":None,"frozen_before_outcome":True}
    digest=sha256(json.dumps(core,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
    return {**core,"prediction_sha256":digest}

def settle_prediction(frozen: Mapping[str,Any], outcome: int) -> dict[str,Any]:
    if frozen.get("outcome") is not None: raise ValueError("prediction already settled")
    if not frozen.get("prediction_sha256"): raise ValueError("unfrozen prediction")
    row=dict(frozen); row["outcome"]=int(bool(outcome)); row["settled_after_freeze"]=True
    return row

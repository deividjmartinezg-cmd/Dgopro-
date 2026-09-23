from __future__ import annotations
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence
from .rc1_gate import rc1_matrix


def evidence_digest(payload: Mapping[str,Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode("utf-8")
    return sha256(raw).hexdigest()


def build_rc1_manifest(markets: Sequence[Mapping[str,Any]], *, dataset_id: str, feature_store_version: str, code_ref: str, thresholds: Mapping[str,float]|None=None) -> dict[str,Any]:
    matrix=rc1_matrix(markets,thresholds=thresholds)
    core={"dataset_id":dataset_id,"feature_store_version":feature_store_version,"code_ref":code_ref,"matrix":matrix,"partial_release_allowed":True,"scientific_status":"EVIDENCE_REQUIRED" if not matrix["rc1_markets"] else "PARTIAL_RC1"}
    return {**core,"evidence_sha256":evidence_digest(core),"reproducible_inputs_required":True,"actions_required":False}

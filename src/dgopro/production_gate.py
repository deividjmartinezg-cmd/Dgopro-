from __future__ import annotations
from typing import Any, Mapping

def release_gate(validation: Mapping[str,Any], *, models_frozen: bool, calibrators_frozen: bool, provenance_complete: bool, monitoring_enabled: bool) -> dict[str,Any]:
    failures=[]
    promotion=validation.get("promotion",{})
    if not bool(promotion.get("promote",False)): failures.append("challenger_not_promoted")
    if not models_frozen: failures.append("models_not_frozen")
    if not calibrators_frozen: failures.append("calibrators_not_frozen")
    if not provenance_complete: failures.append("provenance_incomplete")
    if not monitoring_enabled: failures.append("drift_monitoring_disabled")
    return {"release":not failures,"status":"DGOPRO_3_CHAMPION" if not failures else "DGOPRO_3_CHALLENGER","failures":failures,"manual_release_required":True,"probability_claims_require_oos_evidence":True}

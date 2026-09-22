from __future__ import annotations
from typing import Any, Mapping, Sequence
from .feature_eligibility import module_eligibility
from .observational_index import canonical_match_key

ALLOWED_INDEX_STATUSES={"CANONICAL_MATCH","STAGING_UNIQUE"}

def build_market_dataset(records: Sequence[Mapping[str,Any]], index_rows: Sequence[Mapping[str,Any]], module: str, *, require_t1_features: bool=True) -> dict[str,Any]:
    index={r.get("match_key"):r for r in index_rows if r.get("match_key")}
    accepted=[]; rejected={}
    for record in records:
        key=canonical_match_key(record); idx=index.get(key)
        reason=None
        if idx is None: reason="not_indexed"
        elif idx.get("status") not in ALLOWED_INDEX_STATUSES: reason=f"index:{idx.get('status')}"
        else:
            eligibility=module_eligibility(record); info=eligibility.get("modules",{}).get(module)
            if info is None: reason="unknown_module"
            elif not info.get("eligible_target"): reason="target_ineligible"
            elif require_t1_features and not bool(record.get("prematch_features_t1_safe",False)): reason="prematch_not_t1_safe"
        if reason:
            rejected[reason]=rejected.get(reason,0)+1; continue
        accepted.append(record)
    return {"module":module,"n":len(accepted),"records":accepted,"rejected":rejected,"require_t1_features":require_t1_features,"canonical_counter_delta":0}

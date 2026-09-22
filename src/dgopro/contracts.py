from __future__ import annotations
from typing import Any, Mapping

EXPECTED_KEYS=("home_xg","away_xg","home_corners","away_corners","home_cards","away_cards","home_shots","away_shots","home_sot","away_sot","home_keeper_saves","away_keeper_saves")

def validate_match_contract(payload: Mapping[str,Any]) -> dict[str,Any]:
    errors=[]; warnings=[]
    for key in ("match_id","kickoff","snapshot_at","home_team","away_team"):
        if payload.get(key) in (None,""): errors.append(f"missing:{key}")
    expected=payload.get("expected")
    if not isinstance(expected,Mapping): errors.append("missing:expected")
    else:
        for key in EXPECTED_KEYS:
            if key not in expected: warnings.append(f"missing_expected:{key}")
            elif float(expected[key])<0: errors.append(f"negative_expected:{key}")
    if payload.get("headline_probability") is not None and not 0<=float(payload["headline_probability"])<=1:
        errors.append("invalid:headline_probability")
    return {"valid":not errors,"errors":errors,"warnings":warnings,"contract_version":"3.0-challenger"}

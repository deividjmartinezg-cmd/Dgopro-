from __future__ import annotations
from typing import Any, Mapping, Sequence
from .temporal_features import build_match_temporal_features


def build_feature_row(history: Sequence[Mapping[str,Any]], fixture: Mapping[str,Any], *, strength: Mapping[str,Any]|None=None, home_context: Mapping[str,Any]|None=None, away_context: Mapping[str,Any]|None=None, home_xi: Mapping[str,Any]|None=None, away_xi: Mapping[str,Any]|None=None) -> dict[str,Any]:
    temporal=build_match_temporal_features(history,fixture)
    row={"match_id":fixture.get("match_id"),"kickoff":fixture.get("kickoff") or fixture.get("date"),"competition_id":fixture.get("competition_id"),"home_team":fixture.get("home_team"),"away_team":fixture.get("away_team"),"temporal":temporal,"strength":dict(strength or {}),"home_context":dict(home_context or {}),"away_context":dict(away_context or {}),"home_xi":dict(home_xi or {}),"away_xi":dict(away_xi or {}),"t1_safe":bool(temporal.get("t1_safe")),"feature_store_version":"3.0-t1-v1"}
    return row

def build_feature_store(history: Sequence[Mapping[str,Any]], fixtures: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    rows=[build_feature_row(history,f) for f in fixtures]
    return {"version":"3.0-t1-v1","n":len(rows),"rows":rows,"all_t1_safe":all(r["t1_safe"] for r in rows)}

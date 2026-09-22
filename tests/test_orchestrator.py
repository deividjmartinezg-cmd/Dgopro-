from dgopro.orchestrator import analyze_match
from dgopro.contracts import validate_match_contract

BASE={"match_id":"m1","kickoff":"2026-09-23T20:00:00+00:00","snapshot_at":"2026-09-22T18:00:00+00:00","home_team":"A","away_team":"B","source_provenance":"fixture","expected":{"home_xg":1.6,"away_xg":1.0,"home_corners":5.4,"away_corners":4.0,"home_cards":2.1,"away_cards":2.4,"home_shots":14,"away_shots":10,"home_sot":5,"away_sot":3.5,"home_keeper_saves":2.5,"away_keeper_saves":4.0},"headline_probability":.72,"calibration_reliability":.85,"oos_stability":.8,"model_agreement":.82,"sample_reliability":.8,"drift_health":.9,"uncertainty":.12,"scenarios":[{"probability":.72},{"probability":.69},{"probability":.74}]}

def test_contract_accepts_complete_payload():
    assert validate_match_contract(BASE)["valid"] is True

def test_orchestrator_runs_end_to_end():
    r=analyze_match(BASE); assert r["status"]=="OK" and r["engine"]=="DGOPRO-3-CHALLENGER" and "goals" in r["markets"] and r["validated_champion"] is False

def test_orchestrator_blocks_temporal_leakage():
    bad=dict(BASE); bad["snapshot_at"]="2026-09-24T18:00:00+00:00"
    r=analyze_match(bad); assert r["status"]=="BLOCKED" and r["stage"]=="t1_integrity"

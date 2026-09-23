from dgopro.rc1_manifest import build_rc1_manifest
from dgopro.prospective_ledger import freeze_prediction, settle_prediction

def test_manifest_is_deterministic_and_does_not_require_actions():
    markets=[{"market":"o25","oos_n":10,"seasons":1,"competitions":1,"ece":.1,"brier":.3,"baseline_brier":.25,"strict_walk_forward":True,"frozen_before_outcome":True,"leakage_detected":False}]
    a=build_rc1_manifest(markets,dataset_id="d1",feature_store_version="v1",code_ref="abc")
    b=build_rc1_manifest(markets,dataset_id="d1",feature_store_version="v1",code_ref="abc")
    assert a["evidence_sha256"]==b["evidence_sha256"] and a["actions_required"] is False
    assert a["matrix"]["blocked_markets"]==["o25"]

def test_prediction_is_frozen_before_settlement():
    p=freeze_prediction(match_id="m1",kickoff="2026-01-01T20:00:00",market="o25",probability=.71,model_version="rc1",feature_cutoff="2026-01-01T18:00:00")
    assert p["outcome"] is None and p["frozen_before_outcome"]
    s=settle_prediction(p,1); assert s["outcome"]==1 and s["prediction_sha256"]==p["prediction_sha256"]

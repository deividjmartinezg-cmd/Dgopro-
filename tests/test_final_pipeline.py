from dgopro.feature_store import build_feature_store
from dgopro.training_pipeline import chronological_folds
from dgopro.calibration import reliability_bins, empirical_calibrate
from dgopro.production_gate import release_gate

def test_feature_store_is_t1_safe():
    hist=[{"date":"2026-01-01","home_team":"A","away_team":"B","home_goals":1,"away_goals":0}]
    fixtures=[{"match_id":"m","date":"2026-01-02","home_team":"A","away_team":"B"}]
    assert build_feature_store(hist,fixtures)["all_t1_safe"] is True

def test_walkforward_never_shuffles():
    rows=[{"date":f"2026-01-{i:02d}"} for i in range(1,21)]
    f=chronological_folds(rows,min_train=10,test_size=5)
    assert len(f)==2 and f[0]["strict_oos"] is True

def test_reliability_calibration_requires_sample():
    y=[1]*60; p=[.8]*60; table=reliability_bins(y,p)
    r=empirical_calibrate(.8,table,min_bin_n=50)
    assert r["calibrated"] is True and r["probability"]==1.0

def test_release_gate_blocks_unvalidated_challenger():
    r=release_gate({"promotion":{"promote":False}},models_frozen=True,calibrators_frozen=True,provenance_complete=True,monitoring_enabled=True)
    assert r["release"] is False and r["status"]=="DGOPRO_3_CHALLENGER"

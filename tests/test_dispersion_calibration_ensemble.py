from dgopro.markets.dispersion import dixon_coles_matrix, negative_binomial_distribution, variance_from_nb
from dgopro.calibration import CalibrationKey, BetaCalibration, CalibrationRegistry
from dgopro.ensemble import weighted_ensemble, disagreement_penalty
from dgopro.walkforward import walk_forward_splits, frozen_prediction_gate

def test_dixon_coles_matrix_normalizes():
    d=dixon_coles_matrix(1.5,1.0); assert abs(sum(d.values())-1)<1e-9

def test_negative_binomial_is_overdispersed():
    d=negative_binomial_distribution(10,5); assert abs(sum(d.values())-1)<1e-9 and variance_from_nb(10,5)>10

def test_calibration_requires_provenance_and_transforms():
    reg=CalibrationRegistry(); key=CalibrationKey("EPL","goals","2.5")
    reg.register(key,BetaCalibration(1,-1,0,500,"2025_train__2026_valid")); r=reg.calibrate(key,.7); assert r["calibrated"] is True and 0<r["probability"]<1

def test_ensemble_excludes_unvalidated_models():
    r=weighted_ensemble([{"model":"a","probability":.8,"oos_validated":True},{"model":"b","probability":.2,"oos_validated":False}]); assert r["probability"]==.8
    assert disagreement_penalty(.9,.3)<.9

def test_walk_forward_is_temporal_and_freeze_gate_works():
    rows=[{"kickoff":f"2026-01-{d:02d}T12:00:00+00:00"} for d in range(1,11)]
    s=walk_forward_splits(rows,min_train=5,test_size=2); assert len(s)>0 and s[0]["train_end"]<s[0]["test_start"]
    assert frozen_prediction_gate({"frozen_at":"2026-01-01T10:00:00+00:00"},{"known_at":"2026-01-01T12:00:00+00:00"})

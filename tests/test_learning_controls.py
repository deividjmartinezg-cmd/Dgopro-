from dgopro.ablation import ablation_gate
from dgopro.drift import drift_monitor
from dgopro.error_taxonomy import classify_error
from dgopro.market_benchmark import no_vig_probabilities, market_disagreement, clv_decimal
from dgopro.pqs import prediction_quality_score

def test_ablation_blocks_metric_regression():
    b={"brier":.20,"log_loss":.50}; c={"brier":.19,"log_loss":.55,"oos":True,"frozen_before_outcome":True}
    assert ablation_gate(b,c)["status"]=="blocked"

def test_drift_detects_degradation():
    assert drift_monitor({"brier":.20},{"brier":.25})["status"]=="CRITICAL"

def test_normal_variance_does_not_trigger_auto_change():
    r=classify_error({"outcome_within_predicted_tail":True}); assert r["label"]=="NORMAL_VARIANCE" and r["automatic_model_change"] is False

def test_no_vig_and_clv():
    p=no_vig_probabilities({"1":2.0,"X":4.0,"2":4.0}); assert abs(sum(p.values())-1)<1e-9
    assert market_disagreement(.70,.55)["audit_required"] is True
    assert clv_decimal(2.2,2.0)["price_clv"]>0

def test_pqs_is_probability_independent():
    r=prediction_quality_score({"data_quality":.9,"calibration":.9,"oos_stability":.9,"model_agreement":.9,"scenario_stability":.8,"sample_reliability":.8,"drift_health":.9,"uncertainty":.1}); assert r["score"]>80 and r["probability_independent"] is True

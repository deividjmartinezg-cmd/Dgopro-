from dgopro.backtest import evaluate_binary_predictions, compare_models
from dgopro.promotion import promotion_decision

def test_backtest_rejects_leaked_prediction():
    rows=[{"prediction_id":"a","probability":.8,"outcome":1,"frozen_at":"2026-01-01T10:00:00+00:00","known_at":"2026-01-01T12:00:00+00:00"},{"prediction_id":"b","probability":.9,"outcome":1,"frozen_at":"2026-01-01T13:00:00+00:00","known_at":"2026-01-01T12:00:00+00:00"}]
    r=evaluate_binary_predictions(rows); assert r["n"]==1 and "b" in r["rejected"]

def test_model_comparison_prefers_lower_losses():
    r=compare_models({"brier":.20,"log_loss":.50,"ece":.04},{"brier":.18,"log_loss":.47,"ece":.03}); assert r["dominates"] is True

def test_promotion_is_conservative():
    good={"n":1000,"strict_oos":True,"predictions_frozen":True,"ece":.03,"beats_baseline":True,"ablation_passed":True,"drift_status":"STABLE","arb_review_passed":True}
    assert promotion_decision(good)["promote"] is True
    bad=dict(good); bad["n"]=50
    assert promotion_decision(bad)["promote"] is False

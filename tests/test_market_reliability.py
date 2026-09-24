from dgopro.market_reliability import reliability_decision, summarize_family
from dgopro.ranking_score import ranking_score


def make_rows(n, p=.8, y=1, days=10):
    return [{"probability":p,"outcome":y,"date":f"2026-09-{1 + (i % days):02d}"} for i in range(n)]


def test_thin_sample_only_observes_and_never_penalizes():
    d=reliability_decision(make_rows(14,p=.8,y=1))
    assert d["status"]=="OBSERVE"
    assert d["penalty"]==0.0


def test_large_persistent_miscalibration_can_penalize():
    d=reliability_decision(make_rows(120,p=.9,y=0),baseline_brier=.25)
    assert d["status"]=="PENALIZE"
    assert d["penalty"]>0


def test_ranking_accepts_only_explicit_reliability_penalty():
    base={"calibrated_probability":.8,"igc":80,"coverage":.8,"stability":.8,"convergence":.8,"uncertainty_width":.1,"oos_n":1000,"ece":.02,"risk":"green","status":"PREDICT","prospective":True,"frozen_before_outcome":True}
    a=ranking_score(base)
    b=ranking_score({**base,"reliability_penalty":10})
    assert a["ranking_score"]-b["ranking_score"]==10

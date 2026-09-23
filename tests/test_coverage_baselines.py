from dgopro.coverage_audit import coverage_audit, training_readiness
from dgopro.baselines import empirical_binary_baseline, elo_home_probability
from dgopro.model_card import model_card

def test_coverage_does_not_invent_missing_fields():
    rows=[{"competition_id":"x","season":"1","home_goals":1,"away_goals":0},{"competition_id":"x","season":"1","home_goals":2,"away_goals":2,"home_shots":10,"away_shots":8}]
    a=coverage_audit(rows); assert a["totals"]["result"]==2 and a["totals"]["shots"]==1 and a["totals"]["xg"]==0
    r=training_readiness(a,{"result":2,"shots":2}); assert r["result"]["ready"] and not r["shots"]["ready"]

def test_empirical_baseline_uses_training_only():
    b=empirical_binary_baseline([{"y":1},{"y":0},{"y":1}],"y"); assert b["probability"]==2/3 and b["n"]==3
    assert 0<elo_home_probability(1500,1500)<1

def test_model_card_refuses_unreleased_probability_claim():
    c=model_card(name="x",market="goals",dataset={"n":100},validation={"backtest":{"status":"ok","oos_required":True,"brier":.2}},release={"release":False,"status":"DGOPRO_3_CHALLENGER","failures":["not_promoted"]})
    assert c["probability_claims_verified"] is False and c["release"] is False

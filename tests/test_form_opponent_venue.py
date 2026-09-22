from dgopro.form import multi_horizon_form, blend_horizons
from dgopro.opponent_adjustment import opponent_adjusted_metric, schedule_strength, attack_defense_cross
from dgopro.venue import venue_profile, venue_reliability

def test_multi_horizon_respects_venue():
    rows=[{"venue":"home","xg":2.0},{"venue":"away","xg":1.0},{"venue":"home","xg":1.5}]
    p=multi_horizon_form(rows,["xg"],venue="home"); assert p["horizons"]["L5"]["n"]==2 and blend_horizons(p,"xg") is not None

def test_stronger_schedule_rewards_positive_production():
    r=opponent_adjusted_metric([{"xg":1.0,"opponent_strength":1800}],"xg"); assert r["adjusted_mean"]>r["raw_mean"]

def test_schedule_strength_reports_range():
    r=schedule_strength([{"opponent_strength":1400},{"opponent_strength":1600}]); assert r["mean"]==1500

def test_attack_defense_cross_is_positive():
    assert attack_defense_cross(1.2,0.9)>0

def test_venue_shrinkage_and_reliability():
    p=venue_profile([{"venue":"home","xg":2.0}],"xg",prior_mean=1.2,prior_weight=4); assert 1.2<p["venues"]["home"]["shrunk_mean"]<2.0 and venue_reliability(p,"home")==0.1

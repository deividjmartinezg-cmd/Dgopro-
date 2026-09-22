from dgopro.xg2 import contextual_xg, post_shot_xg
from dgopro.threat import threat_value
from dgopro.lineup import lineup_strength
from dgopro.tactical import tactical_matchup, game_state_adjustment
from dgopro.scenarios import scenario_stability

def test_xg_context_is_bounded():
    r=contextual_xg({"distance_m":12,"angle_rad":.8,"under_pressure":False,"defenders_goal_side":1}); assert 0<r["xg"]<1 and r["coefficients_fitted"] is False
    assert 0<post_shot_xg(r["xg"],placement_quality=.8)["psxg"]<1

def test_threat_value_rewards_attack_without_risk():
    assert threat_value({"p_score_before":.1,"p_score_after":.2,"p_concede_before":.1,"p_concede_after":.1})["dtv"]>0

def test_lineup_uncertainty_detects_expected_players():
    r=lineup_strength([{"rating":70,"availability_probability":.5}]); assert r["availability_uncertainty"]>0 and not r["confirmed"]

def test_tactical_and_game_state_layers_are_explicit_challengers():
    t=tactical_matchup({"pressing":.8},{"press_resistance":.4}); assert t["mapping_fitted"] is False
    g=game_state_adjustment(1.0,score_diff=-1,minute=70); assert g["adjusted_rate"]>1 and g["coefficients_fitted"] is False

def test_scenario_stability_penalizes_disagreement():
    stable=scenario_stability([{"probability":.8},{"probability":.82},{"probability":.79}])
    unstable=scenario_stability([{"probability":.2},{"probability":.8},{"probability":.5}])
    assert stable["stability"]>unstable["stability"]

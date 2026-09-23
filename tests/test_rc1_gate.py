from dgopro.rc1_gate import market_rc1_gate, rc1_matrix

def good(market="goals_over_25"):
    return {"market":market,"oos_n":3000,"seasons":6,"competitions":5,"ece":.025,"brier":.205,"baseline_brier":.225,"strict_walk_forward":True,"frozen_before_outcome":True,"leakage_detected":False}

def test_good_market_can_enter_rc1():
    r=market_rc1_gate(good()); assert r["rc1"] and r["status"]=="RC1"

def test_high_accuracy_is_not_enough_without_calibration_and_baseline_gain():
    x=good(); x.update({"accuracy":.94,"ece":.12,"brier":.24,"baseline_brier":.22})
    r=market_rc1_gate(x); assert not r["rc1"] and "calibration_failed" in r["failures"] and "does_not_beat_baseline" in r["failures"]

def test_small_sample_is_blocked():
    x=good(); x["oos_n"]=80
    assert "insufficient_oos_n" in market_rc1_gate(x)["failures"]

def test_partial_release_is_market_specific():
    bad=good("corners_over_95"); bad["ece"]=.2
    r=rc1_matrix([good(),bad]); assert r["rc1_markets"]==["goals_over_25"] and r["blocked_markets"]==["corners_over_95"] and r["partial_release_allowed"]

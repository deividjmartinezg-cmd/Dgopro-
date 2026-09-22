from dgopro.markets.goals import goals_engine, score_matrix
from dgopro.markets.result import result_engine
from dgopro.markets.specialists import corners_engine, cards_engine, shots_engine, sot_engine, saves_engine

def test_goals_probabilities_are_coherent():
    r=goals_engine(1.6,1.1); assert 0<=r["btts"]["yes"]<=1 and abs(r["btts"]["yes"]+r["btts"]["no"]-1)<1e-9

def test_score_matrix_is_nearly_normalized():
    assert abs(sum(score_matrix(1.2,.9,10).values())-1)<1e-8

def test_result_engine_normalizes_1x2():
    r=result_engine(1.5,1.0); assert abs(r["1"]+r["X"]+r["2"]-1)<1e-9 and abs(r["1X"]-(r["1"]+r["X"]))<1e-9

def test_specialist_count_engines_expose_distributions():
    engines=[corners_engine(5.2,4.1),cards_engine(2.1,2.3),shots_engine(13,10),sot_engine(4.8,3.2),saves_engine(2.7,3.4)]
    assert all(e["calibrated"] is False for e in engines)

def test_higher_mean_increases_over_probability():
    low=corners_engine(3,3)["total"]["lines"]["8.5"]["over"]
    high=corners_engine(6,6)["total"]["lines"]["8.5"]["over"]
    assert high>low

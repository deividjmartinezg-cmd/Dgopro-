from dgopro.team_strength import temporal_elo
from dgopro.context_features import haversine_km, context_features
from dgopro.xi_availability import xi_availability, positional_availability

def test_elo_snapshot_is_pre_match():
    rows=[{"match_id":"m1","date":"2026-01-01","home_team":"A","away_team":"B","home_goals":2,"away_goals":0},{"match_id":"m2","date":"2026-01-02","home_team":"A","away_team":"B","home_goals":0,"away_goals":1}]
    r=temporal_elo(rows); s=r["snapshots"]
    assert s[0]["home_elo_pre"]==1500 and s[0]["away_elo_pre"]==1500
    assert s[1]["home_elo_pre"]>s[1]["away_elo_pre"] and r["parameters_calibrated"] is False

def test_context_burden_increases_with_harder_schedule():
    easy=context_features(rest_days=7,travel_km=50,matches_last_14d=1)["context_burden"]
    hard=context_features(rest_days=2,travel_km=4000,timezone_shift_hours=5,matches_last_14d=5)["context_burden"]
    assert hard>easy and haversine_km(0,0,0,1)>100

def test_xi_availability_weights_important_absence():
    p=[{"name":"star","role_weight":1.5,"availability_probability":0.0,"position_group":"attack"},{"name":"other","role_weight":1.0,"availability_probability":1.0,"position_group":"midfield"}]
    r=xi_availability(p); pos=positional_availability(p)
    assert r["availability_ratio"]<.5 and "star" in r["high_role_doubts"] and pos["attack"]["ratio"]==0

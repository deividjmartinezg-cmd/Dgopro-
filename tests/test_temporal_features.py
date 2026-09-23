from datetime import datetime, timezone
from dgopro.temporal_features import weighted_recent, build_match_temporal_features
from dgopro.opponent_adjustment import geometric_attack_defense_cross

def r(date,h,a,hg,ag,hx=None,ax=None):
    return {"date":date,"home_team":h,"away_team":a,"home_goals":hg,"away_goals":ag,"home_xg":hx,"away_xg":ax}

def test_future_match_never_enters_features():
    rows=[r("2026-01-01","A","B",2,0,1.8,.5),r("2026-01-10","A","C",9,0,6,.1)]
    f=weighted_recent(rows,"A",datetime(2026,1,5,tzinfo=timezone.utc),n=5)
    assert f["n"]==1 and f["goals_for"]==2 and f["xg_for"]==1.8

def test_venue_filter_uses_only_home_or_away_history():
    rows=[r("2026-01-01","A","B",2,0),r("2026-01-02","C","A",1,4)]
    f=weighted_recent(rows,"A",datetime(2026,1,5,tzinfo=timezone.utc),venue="home")
    assert f["n"]==1 and f["goals_for"]==2

def test_match_builder_produces_5l5v_views():
    rows=[r("2026-01-01","A","X",1,0),r("2026-01-02","Y","B",0,2)]
    out=build_match_temporal_features(rows,{"match_id":"m","date":"2026-01-05","home_team":"A","away_team":"B"})
    assert out["home"]["l5_venue"]["n"]==1 and out["away"]["l5_venue"]["n"]==1 and out["t1_safe"]

def test_geometric_cross_balances_attack_and_concession():
    x=geometric_attack_defense_cross(2.0,1.5,league_rate=1.5)
    assert x["expected_rate"]>1.5 and x["expected_rate"]<2.0

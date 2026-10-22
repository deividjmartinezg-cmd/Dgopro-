import copy

from dgopro.independent_prematch import forecast_from_observed_history

def row(date,home,away,hg,ag,**kwargs):
    return {"date":date,"competition_id":"E0","home_team":home,"away_team":away,
            "home_goals":hg,"away_goals":ag,**kwargs}

def history_with_real_metrics():
    records=[]
    for i in range(1,6):
        date=f"2026-10-{i:02d}"
        records.append(row(date,"A",f"X{i}",2,1,
                           home_shots=14,away_shots=9,home_sot=5,away_sot=3,
                           home_corners=6,away_corners=4,home_cards=2,away_cards=3))
        records.append(row(date,f"Y{i}","B",0,3,
                           home_shots=7,away_shots=16,home_sot=2,away_sot=7,
                           home_corners=3,away_corners=7,home_cards=3,away_cards=2))
    return records

FIXTURE={"competition_id":"E0","home_team":"A","away_team":"B","date":"2026-10-10"}

def test_independent_prematch_uses_history_for_all_available_markets():
    result=forecast_from_observed_history(history_with_real_metrics(),FIXTURE)
    assert result["status"]=="EXPERIMENTAL_UNCALIBRATED"
    assert result["recommendation"]=="ABSTAIN"
    assert result["vmd_used"] is False and result["odds_used"] is False
    assert result["history_n"]=={"home":5,"away":5}
    assert result["projected_means"]["home_goals"]==1.0
    assert result["projected_means"]["away_goals"]==2.0
    assert result["projected_means"]["home_corners"]==4.5
    assert set(result["available_market_families"])=={"goals","result","corners","cards","shots","sot"}
    assert result["markets"]["goals"]["goal_rate_basis"]=="PREVIOUS_OBSERVED_GOALS_NOT_XG"
    assert result["probabilities_certified"] is False
    assert "saves" not in result["markets"]

def test_same_day_and_future_result_never_leak_into_prematch_projection():
    past=history_with_real_metrics()
    expected=forecast_from_observed_history(past,FIXTURE)
    extra=[
        row("2026-10-10","A","B",19,0,home_shots=90,away_shots=2),
        row("2026-10-11","A","B",100,0,home_shots=100,away_shots=2),
    ]
    actual=forecast_from_observed_history(past+extra,FIXTURE)
    assert actual["projected_means"]==expected["projected_means"]
    assert actual["markets"]["result"]["1"]==expected["markets"]["result"]["1"]

def test_missing_metrics_do_not_become_fake_zero():
    stripped=[]
    for item in history_with_real_metrics():
        stripped.append({k:v for k,v in item.items() if not any(p in k for p in ("corners","shots","sot","cards"))})
    result=forecast_from_observed_history(stripped,FIXTURE)
    assert "goals" in result["markets"]
    for market in ("corners","cards","shots","sot"):
        assert market not in result["markets"]

def test_insufficient_team_history_abstains_and_blocks():
    result=forecast_from_observed_history(history_with_real_metrics()[:3],FIXTURE)
    assert result["status"]=="BLOCKED"
    assert result["reason"]=="insufficient_prematch_team_history"
    assert result["recommendation"]=="ABSTAIN"

"""First independent DGOPRO prematch statistical baseline.

Inputs are observed earlier match results. No VMD, betting odds, bookmaker models
or externally supplied predicted probabilities. This is NOT calibrated or
authorized to publish bets. Day-only archives exclude all same-date matches.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import exp
from typing import Any, Mapping, Sequence

from .temporal_features import weighted_recent
from .markets.result import result_engine
from .markets.counts import summarize


def _cutoff_day(fixture: Mapping[str,Any]) -> datetime:
    value=str(fixture.get("date") or fixture.get("kickoff") or "")
    if not value or len(value)<10:
        raise ValueError("Fixture must contain a date (local day for day-only archives)")
    day=datetime.fromisoformat(value[:10])
    return datetime(day.year,day.month,day.day,tzinfo=timezone.utc)


def _mean(a: float|None,b: float|None) -> float|None:
    return (a+b)/2 if a is not None and b is not None else None


def _team_metric(form: Mapping[str,Any], metric: str, direction: str,
                 *, min_observations: int) -> float|None:
    key=f"{metric}_{direction}"
    if int(form.get(key+"_n",0))<min_observations:
        return None
    value=form.get(key)
    return float(value) if value is not None else None


def forecast_from_observed_history(
    history: Sequence[Mapping[str,Any]],
    fixture: Mapping[str,Any],
    *,
    min_team_matches: int=5,
    min_metric_observations: int=3
) -> dict[str,Any]:
    league=str(fixture.get("competition_id") or "")
    home=str(fixture.get("home_team") or "")
    away=str(fixture.get("away_team") or "")
    if not league or not home or not away or home==away:
        return {"status":"BLOCKED","reason":"invalid_fixture_identity"}
    cutoff=_cutoff_day(fixture)
    league_history=[r for r in history if str(r.get("competition_id"))==league]
    hf=weighted_recent(league_history,home,cutoff,n=5)
    af=weighted_recent(league_history,away,cutoff,n=5)
    foundation={
        "engine":"DGOPRO-INDEPENDENT-OBSERVED-BASELINE",
        "status":"EXPERIMENTAL_UNCALIBRATED",
        "recommendation":"ABSTAIN",
        "probabilities_certified":False,
        "historical_prospective_frozen":False,
        "fixture":{"competition_id":league,"home_team":home,"away_team":away,
                   "cutoff_day_utc":cutoff.date().isoformat()},
        "history_n":{"home":hf["n"],"away":af["n"]},
        "history_scope":"same competition, strictly BEFORE match calendar date",
        "odds_used":False,"vmd_used":False,
        "missing":["xG-calibrated goal rates","referee adjustment",
                   "confirmed XI and player props","goalkeeper saves",
                   "out-of-sample calibration","official fixture independent verification"],
    }
    if hf["n"]<min_team_matches or af["n"]<min_team_matches:
        return {**foundation,"status":"BLOCKED","reason":"insufficient_prematch_team_history",
                "markets":{}}

    projected={}
    for metric in ("goals","shots","sot","corners","cards"):
        for side,own,opp in (("home",hf,af),("away",af,hf)):
            attack=_team_metric(own,metric,"for",min_observations=min_metric_observations)
            opponent_defense=_team_metric(opp,metric,"against",
                                          min_observations=min_metric_observations)
            projected[f"{side}_{metric}"]=_mean(attack,opponent_defense)

    markets={}
    hg=projected["home_goals"]; ag=projected["away_goals"]
    if hg is not None and ag is not None:
        markets["result"]=result_engine(hg,ag)
        markets["goals"]={
            "total":summarize(hg+ag,(1.5,2.5,3.5),max_count=14),
            "btts":{"yes":(1-exp(-hg))*(1-exp(-ag))},
            "goal_rate_basis":"PREVIOUS_OBSERVED_GOALS_NOT_XG",
        }
    for metric,lines,maximum in (
        ("corners",(7.5,8.5,9.5,10.5,11.5),30),
        ("cards",(4.5,5.5),22),
        ("shots",(23.5,24.5,25.5,26.5,27.5,28.5,29.5),65),
        ("sot",(7.5,9.5),40),
    ):
        hm=projected[f"home_{metric}"]; am=projected[f"away_{metric}"]
        if hm is not None and am is not None:
            markets[metric]={"total":summarize(hm+am,lines,max_count=maximum),
                             "statistic_source":"OBSERVED_MATCH_HISTORY"}
    return {**foundation,"projected_means":projected,"markets":markets,
            "available_market_families":list(markets),
            "unavailable_market_families":[m for m in ("result","goals","corners","cards","shots","sot") if m not in markets]}

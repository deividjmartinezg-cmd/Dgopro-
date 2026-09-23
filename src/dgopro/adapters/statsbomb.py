from __future__ import annotations
from collections import defaultdict
from typing import Any, Mapping, Sequence


def detect_statsbomb_capabilities(*, events: Sequence[Mapping[str,Any]]|None=None, lineups: Sequence[Mapping[str,Any]]|None=None, three_sixty: Sequence[Mapping[str,Any]]|None=None) -> dict[str,bool]:
    events=list(events or []); lineups=list(lineups or []); three_sixty=list(three_sixty or [])
    shot_events=[e for e in events if (e.get("type") or {}).get("name")=="Shot"]
    return {
        "events":bool(events),"shots":bool(shot_events),
        "xg":any((e.get("shot") or {}).get("statsbomb_xg") is not None for e in shot_events),
        "lineups":bool(lineups),"three_sixty":bool(three_sixty),
        "continuous_tracking":False,
    }


def _team_name(event: Mapping[str,Any]) -> str|None:
    team=event.get("team") or {}; return team.get("name") if isinstance(team,Mapping) else None


def summarize_events(events: Sequence[Mapping[str,Any]], home_team: str, away_team: str) -> dict[str,Any]:
    stats=defaultdict(lambda: defaultdict(float))
    for e in events:
        team=_team_name(e)
        if team not in (home_team,away_team): continue
        typ=(e.get("type") or {}).get("name")
        if typ=="Shot":
            stats[team]["shots"]+=1
            shot=e.get("shot") or {}; xg=shot.get("statsbomb_xg")
            if xg is not None: stats[team]["xg"]+=float(xg)
            outcome=(shot.get("outcome") or {}).get("name")
            if outcome in {"Goal","Saved","Saved to Post"}: stats[team]["sot"]+=1
        elif typ=="Corner": stats[team]["corners"]+=1
        elif typ=="Foul Committed": stats[team]["fouls"]+=1
        card=((e.get("foul_committed") or {}).get("card") or {}).get("name")
        if card in {"Yellow Card","Second Yellow","Red Card"}: stats[team]["cards"]+=1
    return {"home_shots":int(stats[home_team]["shots"]),"away_shots":int(stats[away_team]["shots"]),"home_sot":int(stats[home_team]["sot"]),"away_sot":int(stats[away_team]["sot"]),"home_xg":stats[home_team]["xg"],"away_xg":stats[away_team]["xg"],"home_fouls":int(stats[home_team]["fouls"]),"away_fouls":int(stats[away_team]["fouls"]),"home_cards":int(stats[home_team]["cards"]),"away_cards":int(stats[away_team]["cards"])}


def build_observational_record(match: Mapping[str,Any], *, events: Sequence[Mapping[str,Any]]|None=None, lineups: Sequence[Mapping[str,Any]]|None=None, three_sixty: Sequence[Mapping[str,Any]]|None=None, source_sha_verified: bool=False, materialized: bool=False) -> dict[str,Any]:
    home=(match.get("home_team") or {}).get("home_team_name") or match.get("home_team")
    away=(match.get("away_team") or {}).get("away_team_name") or match.get("away_team")
    record={"match_id":match.get("match_id"),"date":match.get("match_date"),"competition_id":(match.get("competition") or {}).get("competition_id") or match.get("competition_id"),"home_team":home,"away_team":away,"source":"statsbomb_open","source_type":"statsbomb_open","observed_real":True,"prematch_features_t1_safe":False,"source_sha_verified":bool(source_sha_verified),"materialized":bool(materialized)}
    if events: record.update(summarize_events(events,str(home),str(away)))
    record["capabilities"]=detect_statsbomb_capabilities(events=events,lineups=lineups,three_sixty=three_sixty)
    record["lineups"]=list(lineups or []) if lineups else None
    record["three_sixty_frames"]=len(three_sixty or [])
    return record

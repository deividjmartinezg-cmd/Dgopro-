import json
from pathlib import Path

import pytest

from dgopro.adapters.footballcsv import parse_footballcsv
from dgopro.temporal_features import weighted_recent
from datetime import datetime, timezone
from scripts.ingest_football_data import ingest, source_url

CSV = """Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,HS,AS,HST,AST,HC,AC,HY,AY,HR,AR,Referee,B365H
E0,18/10/2026,Arsenal,Everton,2,1,18,8,6,2,7,2,2,3,0,1,Ref A,1.4
E0,19/10/2026,Everton,Arsenal,0,3,9,15,3,7,4,9,3,1,0,0,Ref B,4.5
"""

def test_full_csv_fields_are_actually_materialized_not_merely_detected():
    result=parse_footballcsv(CSV,competition_id="E0",source_path="source.csv")
    assert result["n"]==2 and result["capabilities"]["corners"] is True
    row=result["records"][0]
    assert row["home_goals"]==2 and row["away_goals"]==1
    assert row["home_shots"]==18 and row["away_sot"]==2
    assert row["home_corners"]==7 and row["away_corners"]==2
    assert row["home_cards"]==2 and row["away_cards"]==3
    assert row["away_red_cards"]==1 and row["referee"]=="Ref A"
    assert row["home_xg"] is None and row["prematch_features_t1_safe"] is False
    assert "B365H" not in row and row["odds_imported"] is False

def test_optional_missing_metrics_remain_missing_not_silent_zero():
    minimal="Date,HomeTeam,AwayTeam,FTHG,FTAG\n19/10/2026,Arsenal,Everton,2,1\n"
    row=parse_footballcsv(minimal,competition_id="E0")["records"][0]
    for key in ("home_shots","away_sot","home_cards","away_corners","home_xg"):
        assert row[key] is None

def test_partial_columns_are_not_reported_as_complete():
    text="Date,HomeTeam,AwayTeam,FTHG,FTAG,HC\n19/10/2026,A,B,2,1,3\n"
    parsed=parse_footballcsv(text,competition_id="E0")
    assert parsed["capabilities"]["corners"] is False
    assert parsed["records"][0]["away_corners"] is None

def test_source_url_rejects_bad_seasons_and_unsupported_leagues():
    assert source_url("2627","E0")=="https://www.football-data.co.uk/mmz4281/2627/E0.csv"
    with pytest.raises(ValueError): source_url("2628","E0")
    with pytest.raises(ValueError): source_url("../../etc","E0")
    with pytest.raises(ValueError): source_url("2627","E1")

def test_ingestion_offline_creates_real_csv_and_provenance_manifest(tmp_path):
    seen=[]
    def fake_fetch(url):
        seen.append(url)
        return CSV.encode("utf-8")
    manifest=ingest(output_root=tmp_path,seasons=["2627"],divisions=["E0"],
                    fetcher=fake_fetch,min_matches=2)
    assert manifest["status"]=="COMPLETE"
    assert manifest["n_completed_matches"]==2 and len(manifest["datasets"])==1
    assert manifest["coverage"]["corners"]==2
    assert manifest["coverage"]["shots"]==2
    assert manifest["coverage"]["xg"]==0
    assert (tmp_path/"data/raw/footballcsv/2627/E0.csv").read_text()==CSV
    assert json.loads((tmp_path/"artifacts/ingestion_manifest.json").read_text())["provider"]=="football-data.co.uk"
    assert seen==["https://www.football-data.co.uk/mmz4281/2627/E0.csv"]

def test_insufficient_data_fails_closed_not_marked_complete(tmp_path):
    manifest=ingest(output_root=tmp_path,seasons=["2627"],divisions=["E0"],
                    fetcher=lambda url:CSV.encode("utf-8"),min_matches=10)
    assert manifest["status"]=="INCOMPLETE"
    assert manifest["datasets"]==[]
    assert manifest["failures"] and manifest["n_completed_matches"]==0

def test_no_future_game_enters_form_on_match_day():
    rows=parse_footballcsv(CSV,competition_id="E0")["records"]
    features=weighted_recent(rows,"Arsenal",datetime(2026,10,19,tzinfo=timezone.utc))
    assert features["n"]==1
    assert features["goals_for"]==2
    assert features["corners_for"]==7
    assert features["shots_for"]==18

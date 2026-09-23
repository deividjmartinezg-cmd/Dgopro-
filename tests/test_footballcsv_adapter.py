from dgopro.adapters.footballcsv import parse_footballcsv

def test_minimal_schema_is_result_only():
    text="Date,Team 1,FT,HT,Team 2\nFri Aug 13 2021,Brentford,2-0,1-0,Arsenal\n"
    r=parse_footballcsv(text,competition_id="eng.1",source_path="eng.1.csv")
    assert r["n"]==1 and r["records"][0]["home_goals"]==2
    assert r["capabilities"]["result"] is True
    assert r["capabilities"]["shots"] is False and r["capabilities"]["corners"] is False
    assert r["records"][0]["prematch_features_t1_safe"] is False

def test_invalid_result_is_rejected():
    text="Date,Team 1,FT,HT,Team 2\nFri Aug 13 2021,A,postponed,,B\n"
    r=parse_footballcsv(text,competition_id="x")
    assert r["n"]==0 and len(r["rejected"])==1

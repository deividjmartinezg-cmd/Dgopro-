from dgopro.observational_index import canonical_match_key, build_observational_index
from dgopro.training_dataset import build_market_dataset

def row(**kw):
    base={"date":"2026-09-01","competition_id":"ESP_1","home_team":"Real Madrid","away_team":"Villarreal","home_goals":2,"away_goals":1,"source_type":"real","observed_real":True,"prematch_features_t1_safe":True,"source":"test"}
    base.update(kw); return base

def test_key_normalizes_accents_and_case():
    a=row(home_team="Atlético Madrid"); b=row(home_team="atletico-madrid")
    assert canonical_match_key(a)==canonical_match_key(b)

def test_unique_canonical_match_does_not_increment_counter():
    canonical=[row()]; result=build_observational_index([row(source_id="new")],canonical)
    assert result["counts"]["CANONICAL_MATCH"]==1 and result["canonical_counter_delta"]==0

def test_score_conflict_goes_to_quarantine():
    result=build_observational_index([row(home_goals=4)],[row(home_goals=2)])
    assert result["counts"]["AMBIGUOUS_QUARANTINE"]==1

def test_internal_duplicate_is_detected():
    result=build_observational_index([row(source_id="a"),row(source_id="b")],[])
    assert result["counts"]["STAGING_UNIQUE"]==1 and result["counts"]["DUPLICATE_INTERNAL"]==1

def test_market_dataset_respects_t1_gate():
    records=[row(),row(date="2026-09-02",prematch_features_t1_safe=False)]
    idx=build_observational_index(records,[])
    ds=build_market_dataset(records,idx["rows"],"goals",require_t1_features=True)
    assert ds["n"]==1 and ds["rejected"]["prematch_not_t1_safe"]==1 and ds["canonical_counter_delta"]==0

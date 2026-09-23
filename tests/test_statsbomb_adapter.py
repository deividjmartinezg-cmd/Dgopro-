from dgopro.adapters.statsbomb import detect_statsbomb_capabilities, summarize_events, build_observational_record

def events():
    return [
        {"type":{"name":"Shot"},"team":{"name":"A"},"shot":{"statsbomb_xg":.30,"outcome":{"name":"Goal"}}},
        {"type":{"name":"Shot"},"team":{"name":"A"},"shot":{"statsbomb_xg":.10,"outcome":{"name":"Off T"}}},
        {"type":{"name":"Shot"},"team":{"name":"B"},"shot":{"statsbomb_xg":.20,"outcome":{"name":"Saved"}}},
        {"type":{"name":"Foul Committed"},"team":{"name":"B"},"foul_committed":{"card":{"name":"Yellow Card"}}},
    ]

def test_capabilities_do_not_claim_tracking():
    c=detect_statsbomb_capabilities(events=events(),lineups=[{"team_id":1}],three_sixty=[{"event_uuid":"x"}])
    assert c["events"] and c["shots"] and c["xg"] and c["lineups"] and c["three_sixty"]
    assert c["continuous_tracking"] is False

def test_event_summary_aggregates_shots_sot_xg_cards():
    s=summarize_events(events(),"A","B")
    assert s["home_shots"]==2 and s["home_sot"]==1 and abs(s["home_xg"]-.4)<1e-9
    assert s["away_shots"]==1 and s["away_sot"]==1 and s["away_cards"]==1

def test_record_is_observational_not_t1_feature():
    m={"match_id":1,"match_date":"2023-08-01","home_team":{"home_team_name":"A"},"away_team":{"away_team_name":"B"},"competition":{"competition_id":9}}
    r=build_observational_record(m,events=events(),source_sha_verified=True,materialized=True)
    assert r["observed_real"] is True and r["prematch_features_t1_safe"] is False
    assert r["source_sha_verified"] is True and r["materialized"] is True

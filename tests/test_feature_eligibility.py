from dgopro.feature_eligibility import observational_firewall, module_eligibility, coverage_summary

def test_vmd_simulation_is_forbidden():
    r=observational_firewall({"source_type":"vmd_simulation","observed_real":True,"prematch_features_t1_safe":True})
    assert r["forbidden"] is True and r["allowed_as_observation"] is False

def test_real_observation_can_train_available_targets():
    r=module_eligibility({"match_id":"m1","source_type":"statsbomb_open","observed_real":True,"prematch_features_t1_safe":True,"home_goals":2,"away_goals":1,"home_xg":1.7,"away_xg":.9})
    assert r["modules"]["goals"]["eligible_target"] is True
    assert r["modules"]["xg"]["eligible_prematch_feature"] is True
    assert r["modules"]["corners"]["eligible_target"] is False

def test_postmatch_observation_is_target_but_not_prematch_feature():
    r=module_eligibility({"source_type":"footballcsv","observed_real":True,"prematch_features_t1_safe":False,"home_goals":1,"away_goals":0})
    assert r["modules"]["goals"]["eligible_target"] is True
    assert r["modules"]["goals"]["eligible_prematch_feature"] is False

def test_coverage_summary_counts_modules():
    rows=[{"source_type":"real","observed_real":True,"prematch_features_t1_safe":True,"home_goals":1,"away_goals":0},{"source_type":"vmd_prediction","observed_real":False,"prematch_features_t1_safe":False,"home_goals":2,"away_goals":2}]
    r=coverage_summary(rows); assert r["n_records"]==2 and r["blocked_records"]==1 and r["modules"]["goals"]["target"]==1

from dgopro.top_engine import build_challenger_top, build_rc1_top, official_top_views


def base(**kw):
    row = {
        "market": "o15",
        "market_family": "goals",
        "match_id": "m1",
        "prospective": True,
        "frozen_before_outcome": True,
        "publication_integrity_passed": True,
        "risk": "green",
        "status": "PREDICT",
        "igc": 85,
        "coverage": .9,
        "stability": .9,
        "convergence": .9,
        "probability_lo": .80,
        "probability_hi": .90,
        "oos_n": 1000,
    }
    row.update(kw)
    return row


def test_challenger_probability_is_explicitly_uncertified():
    ranked = build_challenger_top([base(model_probability=.91, market_rc1=False, calibrated=False)])
    assert len(ranked) == 1
    assert ranked[0]["top_tier"] == "CHALLENGER"
    assert ranked[0]["probability_basis"] == "MODEL_ESTIMATE"
    assert ranked[0]["probability_certified"] is False


def test_rc1_requires_full_confidence_policy_pass():
    good = base(
        calibrated_probability=.82,
        market_rc1=True,
        calibrated=True,
        calibration_bin_n=500,
        calibration_gap=.02,
        ece=.02,
    )
    bad = base(
        match_id="m2",
        calibrated_probability=.94,
        market_rc1=True,
        calibrated=True,
        calibration_bin_n=20,
        calibration_gap=.01,
        ece=.01,
    )
    ranked = build_rc1_top([good, bad])
    assert [r["match_id"] for r in ranked] == ["m1"]
    assert ranked[0]["probability_certified"] is True


def test_all_top_views_are_prefixes_of_same_ranking():
    rows = [base(match_id=f"m{i}", model_probability=.70 + i*.01, market_rc1=False, calibrated=False) for i in range(8)]
    out = official_top_views(rows, tier="challenger", sizes=(5, 3, 1))
    ids = [r["match_id"] for r in out["ranked"]]
    assert [r["match_id"] for r in out["tops"]["top_5"]] == ids[:5]
    assert [r["match_id"] for r in out["tops"]["top_3"]] == ids[:3]
    assert [r["match_id"] for r in out["tops"]["top_1"]] == ids[:1]


def test_unverified_fixture_cannot_enter_top():
    ranked=build_challenger_top([base(model_probability=.97, publication_integrity_passed=False)])
    assert ranked == []


def test_under35_requires_safe_four_plus_tail():
    unsafe=base(
        market="under_3_5",
        model_probability=.90,
        distribution_evidence={"p_4plus":.14,"attack_mismatch":.8,"defensive_fragility":.8,"early_lead_runaway":.8,"transition_exposure":.7},
    )
    safe=base(
        match_id="m2",
        market="under_3_5",
        model_probability=.86,
        distribution_evidence={"p_4plus":.06,"attack_mismatch":.2,"defensive_fragility":.2,"early_lead_runaway":.2,"transition_exposure":.2},
    )
    ranked=build_challenger_top([unsafe,safe])
    assert [r["match_id"] for r in ranked] == ["m2"]


def test_exact_score_is_never_primary_top_market():
    ranked=build_challenger_top([base(market="exact_score",market_family="exact_score",model_probability=.99)])
    assert ranked == []


def test_reliability_penalty_can_reorder_market_families():
    goals=base(match_id="g",market_family="goals",model_probability=.84)
    btts=base(match_id="b",market="btts_yes",market_family="btts",model_probability=.88)
    out=official_top_views(
        [goals,btts],
        tier="challenger",
        reliability_penalty_by_family={"goals":0.0,"btts":10.0},
    )
    assert [r["match_id"] for r in out["ranked"]] == ["g","b"]
    assert out["ranked"][1]["reliability_penalty"] == 10.0


def test_zero_reliability_penalty_does_not_change_order():
    a=base(match_id="a",market_family="goals",model_probability=.84)
    b=base(match_id="b",market="btts_yes",market_family="btts",model_probability=.88)
    out=official_top_views(
        [a,b],
        tier="challenger",
        reliability_penalty_by_family={"goals":0.0,"btts":0.0},
    )
    assert [r["match_id"] for r in out["ranked"]] == ["b","a"]

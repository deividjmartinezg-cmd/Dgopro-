from dgopro.top_engine import build_challenger_top, build_rc1_top, official_top_views


def base(**kw):
    row = {
        "market": "o15",
        "match_id": "m1",
        "prospective": True,
        "frozen_before_outcome": True,
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

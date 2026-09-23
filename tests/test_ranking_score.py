from dgopro.ranking_score import official_tops, rank_markets, ranking_score


def base(**overrides):
    row = {
        "match": "A-B",
        "market": "under_3_5",
        "calibrated_probability": 0.85,
        "ece": 0.02,
        "igc": 85,
        "coverage": 0.90,
        "stability": 0.90,
        "convergence": 0.85,
        "uncertainty_width": 0.10,
        "oos_n": 1500,
        "risk": "green",
        "status": "PREDICT",
        "prospective": True,
        "frozen_before_outcome": True,
    }
    row.update(overrides)
    return row


def test_high_probability_can_rank_below_better_supported_market():
    thin = base(match="HighP", calibrated_probability=0.95, ece=0.08, coverage=0.55, stability=0.55, uncertainty_width=0.24, oos_n=40, igc=78)
    robust = base(match="Robust", calibrated_probability=0.88, ece=0.015, coverage=0.95, stability=0.95, uncertainty_width=0.07, oos_n=3000, igc=91)
    ranked = rank_markets([thin, robust])
    assert ranked[0]["match"] == "Robust"
    assert ranked[0]["ranking_score"] > ranked[1]["ranking_score"]


def test_nonprospective_and_abstain_are_ineligible():
    assert ranking_score(base(prospective=False))["eligible"] is False
    assert ranking_score(base(status="ABSTAIN"))["eligible"] is False


def test_low_confidence_is_penalized_but_can_remain_eligible():
    pred = ranking_score(base(status="PREDICT"))
    low = ranking_score(base(status="LOW_CONFIDENCE"))
    assert low["eligible"] is True
    assert pred["ranking_score"] - low["ranking_score"] == 6.0


def test_official_tops_share_one_ordering():
    rows = [base(match=f"M{i}", calibrated_probability=0.60 + i / 100) for i in range(35)]
    tops = official_tops(rows)
    assert len(tops["top_30"]) == 30
    assert tops["top_20"] == tops["top_30"][:20]
    assert tops["top_10"] == tops["top_30"][:10]
    assert tops["top_5"] == tops["top_30"][:5]

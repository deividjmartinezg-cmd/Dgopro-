from dgopro.audit_feedback import audit_eligible, prospective_audit_report
from dgopro.prospective_ledger import freeze_prediction, settle_prediction, invalidate_prediction


def frozen(match_id="m1", market="u35", p=.85, family="goals"):
    return freeze_prediction(
        match_id=match_id,
        kickoff="2026-09-23T20:00:00-03:00",
        market=market,
        probability=p,
        model_version="dgopro-3-challenger",
        feature_cutoff="2026-09-23T19:00:00-03:00",
        metadata={
            "prospective": True,
            "publication_integrity_passed": True,
            "market_family": family,
            "date": "2026-09-23",
        },
    )


def test_valid_settled_prediction_enters_metrics():
    row=settle_prediction(frozen(), 1)
    ok,reason=audit_eligible(row)
    assert ok is True
    assert reason == "eligible"
    report=prospective_audit_report([row])
    assert report["eligible_rows"] == 1
    assert report["metrics"]["hits"] == 1


def test_invalidated_fixture_never_enters_metrics():
    row=invalidate_prediction(frozen(), "fixture_mismatch")
    report=prospective_audit_report([row])
    assert report["eligible_rows"] == 0
    assert report["invalidated_rows"] == 1
    assert report["metrics"]["n"] == 0


def test_non_prospective_metadata_is_excluded_even_if_settled():
    row=freeze_prediction(
        match_id="m2",
        kickoff="2026-09-23T20:00:00-03:00",
        market="btts_yes",
        probability=.62,
        model_version="dgopro-3-challenger",
        feature_cutoff="2026-09-23T19:00:00-03:00",
        metadata={"prospective":False,"publication_integrity_passed":True,"market_family":"btts","date":"2026-09-23"},
    )
    row=settle_prediction(row, 0)
    report=prospective_audit_report([row])
    assert report["eligible_rows"] == 0
    assert report["exclusions"]["not_prospective"] == 1


def test_tampering_breaks_digest_and_excludes_row():
    row=settle_prediction(frozen(), 1)
    row=dict(row)
    row["probability"] = .99
    ok,reason=audit_eligible(row)
    assert ok is False
    assert reason == "digest_mismatch"


def test_small_family_sample_remains_observe_without_penalty():
    rows=[]
    for i in range(14):
        r=settle_prediction(frozen(match_id=f"m{i}", market="btts_yes", p=.60, family="btts"), i % 2)
        rows.append(r)
    report=prospective_audit_report(rows)
    family=report["family_reliability"][0]
    assert family["market_family"] == "btts"
    assert family["status"] == "OBSERVE"
    assert family["penalty"] == 0.0


def test_mixed_rows_only_valid_settled_feed_reliability():
    good=settle_prediction(frozen(match_id="good"), 1)
    bad=invalidate_prediction(frozen(match_id="bad"), "wrong_fixture")
    report=prospective_audit_report([good,bad])
    assert report["total_rows"] == 2
    assert report["eligible_rows"] == 1
    assert report["excluded_rows"] == 1
    assert len(report["metric_rows"]) == 1
    assert report["metric_rows"][0]["match_id"] == "good"

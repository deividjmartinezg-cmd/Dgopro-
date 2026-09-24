from dgopro.data_integrity import fixture_integrity_gate, publication_integrity_gate
from dgopro.distribution_guard import under35_tail_guard


def fixture(**kw):
    row={
        "match_id":"m1",
        "kickoff":"2026-09-24T20:00:00+00:00",
        "snapshot_at":"2026-09-24T18:00:00+00:00",
        "home_team":"Team A",
        "away_team":"Team B",
        "competition":"Cup",
        "source_provenance":"official",
        "fixture_verified":True,
        "fixture_source":"federation",
        "fixture_source_is_official":True,
        "fixture_confirmation_count":1,
        "official_home_team":"Team A",
        "official_away_team":"Team B",
        "official_competition":"Cup",
        "official_kickoff":"2026-09-24T20:00:00+00:00",
    }
    row.update(kw)
    return row


def test_fixture_gate_rejects_swapped_opponents():
    r=fixture(official_home_team="Team B",official_away_team="Team A")
    out=fixture_integrity_gate(r)
    assert not out.passed
    assert "fixture_mismatch:home_team" in out.failures


def test_publication_gate_requires_pre_match_snapshot_and_fixture_match():
    assert publication_integrity_gate(fixture()).passed
    assert not publication_integrity_gate(fixture(snapshot_at="2026-09-24T20:01:00+00:00")).passed


def test_under35_guard_abstains_without_tail_probability():
    out=under35_tail_guard({})
    assert out["status"]=="ABSTAIN" and not out["eligible"]


def test_under35_guard_penalizes_runaway_tail():
    out=under35_tail_guard({"p_4plus":.10,"attack_mismatch":.8,"defensive_fragility":.8,"early_lead_runaway":.9,"transition_exposure":.7})
    assert not out["eligible"]
    assert "runaway_game_state_risk" in out["failures"]


def test_under35_guard_allows_small_stable_tail():
    out=under35_tail_guard({"p_4plus":.05,"attack_mismatch":.1,"defensive_fragility":.1,"early_lead_runaway":.1,"transition_exposure":.1})
    assert out["eligible"] and out["status"]=="PREDICT"

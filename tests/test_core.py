from dgopro.data_integrity import t1_integrity_gate
from dgopro.evaluation import brier, log_loss, ece
from dgopro.strength import StrengthInputs, expected_score_probability
from dgopro.confidence import ConfidenceEvidence, publication_gate

def test_t1_gate_rejects_post_match_snapshot():
    r=t1_integrity_gate({"match_id":"1","kickoff":"2026-09-22T20:00:00+00:00","snapshot_at":"2026-09-22T21:00:00+00:00","home_team":"A","away_team":"B","source_provenance":"test"})
    assert not r.passed

def test_metrics_are_finite():
    y=[1,0,1,1]; p=[.8,.2,.7,.6]
    assert brier(y,p)>=0 and log_loss(y,p)>=0 and ece(y,p)>=0

def test_strength_probability_direction():
    strong=StrengthInputs(1700,1700); weak=StrengthInputs(1400,1400)
    assert expected_score_probability(strong,weak)>.5

def test_confidence_can_abstain():
    e=ConfidenceEvidence(.9,.2,.8,.8,.8,.8,.1)
    assert publication_gate(e)["status"]=="ABSTAIN"

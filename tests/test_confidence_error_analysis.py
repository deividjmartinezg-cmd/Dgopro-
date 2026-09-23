from dgopro.confidence_policy import decision
from dgopro.error_analysis import error_slices, diagnose

def test_unvalidated_market_abstains():
    r=decision(.91,{"market_rc1":False,"calibrated":True,"calibration_bin_n":500,"calibration_gap":.01,"probability_lo":.87,"probability_hi":.94})
    assert r["status"]=="ABSTAIN" and "market_not_rc1" in r["failures"]

def test_good_evidence_can_predict():
    r=decision(.82,{"market_rc1":True,"calibrated":True,"calibration_bin_n":500,"calibration_gap":.01,"probability_lo":.77,"probability_hi":.86})
    assert r["status"]=="PREDICT"

def test_error_analysis_finds_large_calibration_gap():
    rows=[{"probability":.8,"outcome":1,"competition":"x","season":"1"} for _ in range(100)]
    s=error_slices(rows); assert s["n"]==100 and s["slices"]["competition"][0]["brier"]<.05
    d=diagnose(rows); assert d["requires_recalibration"] is True

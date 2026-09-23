from dgopro.market_matrix import market_evidence, build_market_matrix

def rows(n=100,p=.8,y=1):
    return [{"probability":p,"outcome":y,"strict_oos":True,"frozen_before_outcome":True,"leakage_detected":False} for _ in range(n)]

def test_market_evidence_computes_brier_and_ece():
    e=market_evidence("o25",rows(),baseline_brier=.10,seasons=3,competitions=1)
    assert e["oos_n"]==100 and abs(e["brier"]-.04)<1e-9 and abs(e["ece"]-.2)<1e-9

def test_matrix_keeps_small_sample_as_challenger():
    m=build_market_matrix([{"market":"o25","predictions":rows(),"baseline_brier":.10,"seasons":3,"competitions":1}])
    assert m["rc1"]==[] and m["challenger"]==["o25"]

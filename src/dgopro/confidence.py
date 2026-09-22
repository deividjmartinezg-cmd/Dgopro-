from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfidenceEvidence:
    calibrated_probability: float
    data_quality: float
    calibration_reliability: float
    model_agreement: float
    scenario_stability: float
    drift_health: float
    uncertainty_width: float


def prediction_quality(e: ConfidenceEvidence) -> float:
    components=(e.data_quality,e.calibration_reliability,e.model_agreement,e.scenario_stability,e.drift_health)
    base=sum(max(0,min(1,float(x))) for x in components)/len(components)
    penalty=max(0,min(1,e.uncertainty_width))*0.35
    return round(max(0,min(1,base-penalty)),4)

def publication_gate(e: ConfidenceEvidence, min_quality: float=0.65) -> dict:
    p=max(0,min(1,e.calibrated_probability)); q=prediction_quality(e)
    if e.data_quality < 0.45 or q < 0.45:
        status="ABSTAIN"
    elif q < min_quality:
        status="LOW_CONFIDENCE"
    else:
        status="PREDICT"
    return {"status":status,"probability":round(p,4),"residual_risk":round(1-p,4),"prediction_quality":q,"uncertainty_width":e.uncertainty_width}

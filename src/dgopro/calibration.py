from __future__ import annotations
from dataclasses import dataclass
from math import exp, log
from typing import Any, Mapping

@dataclass(frozen=True)
class CalibrationKey:
    competition: str
    market: str
    line: str = "none"

@dataclass(frozen=True)
class BetaCalibration:
    a: float
    b: float
    c: float
    fitted_samples: int
    validation_split: str

    def transform(self, p: float) -> float:
        q=min(1-1e-12,max(1e-12,float(p)))
        z=self.a*log(q)+self.b*log(1-q)+self.c
        return 1.0/(1.0+exp(-z))

class CalibrationRegistry:
    def __init__(self) -> None: self._models: dict[CalibrationKey,BetaCalibration]={}
    def register(self, key: CalibrationKey, model: BetaCalibration) -> None:
        if model.fitted_samples<=0 or not model.validation_split: raise ValueError("calibration provenance required")
        self._models[key]=model
    def calibrate(self, key: CalibrationKey, raw_probability: float) -> dict[str,Any]:
        model=self._models.get(key)
        if model is None:
            return {"probability":float(raw_probability),"calibrated":False,"reason":"no_market_calibrator"}
        return {"probability":model.transform(raw_probability),"calibrated":True,"samples":model.fitted_samples,"validation_split":model.validation_split}

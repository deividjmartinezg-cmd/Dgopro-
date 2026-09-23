from __future__ import annotations
from dataclasses import dataclass
from math import exp, log
from typing import Any, Mapping, Sequence

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
        if model is None: return {"probability":float(raw_probability),"calibrated":False,"reason":"no_market_calibrator"}
        return {"probability":model.transform(raw_probability),"calibrated":True,"samples":model.fitted_samples,"validation_split":model.validation_split}

def reliability_bins(y: Sequence[int], p: Sequence[float], bins: int=10) -> list[dict[str,Any]]:
    out=[]
    for b in range(bins):
        lo=b/bins; hi=(b+1)/bins; idx=[i for i,x in enumerate(p) if lo<=float(x)<hi or (b==bins-1 and float(x)==1)]
        if not idx: continue
        mp=sum(float(p[i]) for i in idx)/len(idx); rate=sum(int(y[i]) for i in idx)/len(idx)
        out.append({"lo":lo,"hi":hi,"n":len(idx),"mean_probability":mp,"observed_rate":rate,"gap":rate-mp})
    return out

def empirical_calibrate(probability: float, table: Sequence[Mapping[str,Any]], *, min_bin_n: int=50) -> dict[str,Any]:
    p=max(0,min(1,float(probability)))
    for r in table:
        if r["lo"]<=p<r["hi"] or (p==1 and r["hi"]==1):
            if int(r["n"])<min_bin_n: return {"probability":p,"calibrated":False,"reason":"insufficient_bin_sample"}
            return {"probability":max(0,min(1,float(r["observed_rate"]))),"raw_probability":p,"calibrated":True,"method":"oos_reliability"}
    return {"probability":p,"calibrated":False,"reason":"no_bin"}

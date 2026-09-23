from __future__ import annotations
from collections import defaultdict
from typing import Any, Mapping, Sequence

def _brier(rows):
    return sum((float(r["probability"])-int(r["outcome"]))**2 for r in rows)/len(rows) if rows else None

def error_slices(predictions: Sequence[Mapping[str,Any]], keys=("competition","season","probability_band")) -> dict[str,Any]:
    valid=[r for r in predictions if r.get("probability") is not None and r.get("outcome") is not None]
    result={"n":len(valid),"slices":{}}
    for key in keys:
        groups=defaultdict(list)
        for r in valid:
            if key=="probability_band":
                p=float(r["probability"]); label=f"{int(p*10)*10:02d}-{min(100,(int(p*10)+1)*10):02d}%"
            else: label=str(r.get(key,"unknown"))
            groups[label].append(r)
        result["slices"][key]=[]
        for label,rows in sorted(groups.items()):
            mean_p=sum(float(r["probability"]) for r in rows)/len(rows); hit=sum(int(r["outcome"]) for r in rows)/len(rows)
            result["slices"][key].append({"label":label,"n":len(rows),"mean_probability":mean_p,"observed_rate":hit,"calibration_gap":hit-mean_p,"brier":_brier(rows)})
    return result

def diagnose(predictions: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    slices=error_slices(predictions); flags=[]
    for dimension,rows in slices["slices"].items():
        for r in rows:
            if r["n"]>=100 and abs(r["calibration_gap"])>.05: flags.append({"dimension":dimension,"label":r["label"],"issue":"miscalibration","gap":r["calibration_gap"],"n":r["n"]})
    return {"summary":slices,"flags":flags,"requires_recalibration":bool(flags)}

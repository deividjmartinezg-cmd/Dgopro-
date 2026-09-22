from __future__ import annotations
from datetime import datetime
from typing import Any, Mapping, Sequence

def _dt(value: Any) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z","+00:00"))

def walk_forward_splits(records: Sequence[Mapping[str,Any]], *, min_train: int=200, test_size: int=50, step: int|None=None) -> list[dict[str,Any]]:
    ordered=sorted(records,key=lambda r:_dt(r["kickoff"])); step=step or test_size; splits=[]
    start=min_train
    while start < len(ordered):
        end=min(len(ordered),start+test_size); train=ordered[:start]; test=ordered[start:end]
        if not test: break
        train_max=_dt(train[-1]["kickoff"]); test_min=_dt(test[0]["kickoff"])
        if train_max>=test_min: raise ValueError("temporal ordering violation")
        splits.append({"train":train,"test":test,"train_end":train[-1]["kickoff"],"test_start":test[0]["kickoff"]})
        start+=step
    return splits

def frozen_prediction_gate(prediction: Mapping[str,Any], outcome: Mapping[str,Any]) -> bool:
    try: return _dt(prediction["frozen_at"]) < _dt(outcome["known_at"])
    except Exception: return False

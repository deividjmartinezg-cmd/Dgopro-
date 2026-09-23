from __future__ import annotations
from typing import Any, Mapping, Sequence

def chronological_folds(rows: Sequence[Mapping[str,Any]], *, min_train: int=500, test_size: int=100, step: int|None=None) -> list[dict[str,Any]]:
    ordered=sorted(rows,key=lambda r:str(r.get("kickoff") or r.get("date") or "")); step=step or test_size; folds=[]
    end=min_train
    while end+test_size<=len(ordered):
        folds.append({"train":ordered[:end],"test":ordered[end:end+test_size],"train_end":ordered[end-1].get("kickoff") or ordered[end-1].get("date"),"test_start":ordered[end].get("kickoff") or ordered[end].get("date"),"strict_oos":True})
        end+=step
    return folds

def training_plan(rows: Sequence[Mapping[str,Any]], module: str, *, min_train: int=500, test_size: int=100) -> dict[str,Any]:
    folds=chronological_folds(rows,min_train=min_train,test_size=test_size)
    return {"module":module,"n_rows":len(rows),"n_folds":len(folds),"folds":folds,"random_shuffle":False,"predictions_must_be_frozen":True,"fit_status":"READY" if folds else "INSUFFICIENT_DATA"}

from __future__ import annotations
from typing import Any, Mapping

def model_card(*, name: str, market: str, dataset: Mapping[str,Any], validation: Mapping[str,Any], release: Mapping[str,Any]) -> dict[str,Any]:
    backtest=validation.get("backtest",{})
    return {"name":name,"market":market,"status":release.get("status","UNKNOWN"),"release":bool(release.get("release",False)),"dataset_n":dataset.get("n") or dataset.get("n_rows"),"strict_oos":bool(backtest.get("oos_required",False)),"brier":backtest.get("brier"),"log_loss":backtest.get("log_loss"),"ece":backtest.get("ece"),"accuracy_at_0_5":backtest.get("accuracy_at_0_5"),"probability_claims_verified":bool(release.get("release",False)) and backtest.get("status")=="ok","limitations":list(release.get("failures",[])),"generated_from_frozen_evidence":True}

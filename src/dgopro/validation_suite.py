from __future__ import annotations
from typing import Any, Mapping, Sequence
from .backtest import evaluate_binary_predictions, compare_models
from .ablation import ablation_gate
from .drift import drift_monitor
from .promotion import promotion_decision

def validate_challenger(*, predictions: Sequence[Mapping[str,Any]], champion_metrics: Mapping[str,float], ablation_baseline: Mapping[str,float], reference_metrics: Mapping[str,float], arb_review_passed: bool=False) -> dict[str,Any]:
    challenger=evaluate_binary_predictions(predictions)
    if challenger.get("status")!="ok": return {"status":"BLOCKED","backtest":challenger}
    comparison=compare_models(champion_metrics,challenger)
    ablation_input=dict(challenger); ablation_input.update({"oos":True,"frozen_before_outcome":True})
    ablation=ablation_gate(ablation_baseline,ablation_input)
    drift=drift_monitor(reference_metrics,challenger)
    report={"n":challenger["n"],"strict_oos":True,"predictions_frozen":not challenger.get("rejected"),"ece":challenger["ece"],"beats_baseline":comparison["dominates"],"ablation_passed":ablation["promotable"],"drift_status":drift["status"],"arb_review_passed":arb_review_passed}
    promotion=promotion_decision(report)
    return {"status":"OK","backtest":challenger,"comparison":comparison,"ablation":ablation,"drift":drift,"promotion":promotion,"champion_remains_active":not promotion["promote"]}

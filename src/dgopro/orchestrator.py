from __future__ import annotations
from typing import Any, Mapping
from .data_integrity import t1_integrity_gate
from .markets.goals import goals_engine
from .markets.result import result_engine
from .markets.specialists import corners_engine, cards_engine, shots_engine, sot_engine, saves_engine
from .confidence import ConfidenceEvidence, publication_gate
from .pqs import prediction_quality_score
from .scenarios import scenario_stability


def _quality_signals(payload: Mapping[str,Any], integrity_score: float, scenario: Mapping[str,Any]) -> dict[str,float]:
    return {
        "data_quality": integrity_score,
        "calibration": float(payload.get("calibration_reliability",0.0)),
        "oos_stability": float(payload.get("oos_stability",0.0)),
        "model_agreement": float(payload.get("model_agreement",0.0)),
        "scenario_stability": float(scenario.get("stability",0.0)),
        "sample_reliability": float(payload.get("sample_reliability",0.0)),
        "drift_health": float(payload.get("drift_health",0.0)),
        "uncertainty": float(payload.get("uncertainty",1.0)),
    }


def analyze_match(payload: Mapping[str,Any]) -> dict[str,Any]:
    integrity=t1_integrity_gate(payload)
    if not integrity.passed:
        return {"status":"BLOCKED","stage":"t1_integrity","failures":list(integrity.failures),"warnings":list(integrity.warnings),"data_quality":integrity.score}
    expected=payload.get("expected",{})
    hx=float(expected.get("home_xg",0)); ax=float(expected.get("away_xg",0))
    outputs={
        "goals":goals_engine(hx,ax),
        "result":result_engine(hx,ax),
        "corners":corners_engine(float(expected.get("home_corners",0)),float(expected.get("away_corners",0))),
        "cards":cards_engine(float(expected.get("home_cards",0)),float(expected.get("away_cards",0)),float(expected.get("referee_factor",1))),
        "shots":shots_engine(float(expected.get("home_shots",0)),float(expected.get("away_shots",0))),
        "sot":sot_engine(float(expected.get("home_sot",0)),float(expected.get("away_sot",0))),
        "saves":saves_engine(float(expected.get("home_keeper_saves",0)),float(expected.get("away_keeper_saves",0))),
    }
    scenarios=scenario_stability(payload.get("scenarios",[]))
    signals=_quality_signals(payload,integrity.score,scenarios)
    pqs=prediction_quality_score(signals)
    headline=float(payload.get("headline_probability",0.5))
    evidence=ConfidenceEvidence(headline,signals["data_quality"],signals["calibration"],signals["model_agreement"],signals["scenario_stability"],signals["drift_health"],signals["uncertainty"])
    gate=publication_gate(evidence)
    return {"status":"OK","engine":"DGOPRO-3-CHALLENGER","integrity":{"score":integrity.score,"warnings":list(integrity.warnings)},"markets":outputs,"scenario_stability":scenarios,"prediction_quality":pqs,"publication":gate,"validated_champion":False}

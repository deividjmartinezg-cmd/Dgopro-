"""Execute a reproducible UNCALIBRATED DGOPRO preview on independently researched inputs.

No odds, VMD, third-party predicted probabilities, or fabricated model calibration.
This is not a certified T-1 forecasting production run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgopro.data_integrity import publication_integrity_gate
from dgopro.markets.goals import score_matrix
from dgopro.orchestrator import analyze_match


def run(input_file: Path, output_file: Path) -> dict:
    payload = json.loads(input_file.read_text(encoding="utf-8"))
    fixture_check = publication_integrity_gate(payload)
    if not fixture_check.passed:
        raise ValueError("Publication fixture/T-1 integrity failed: " + ",".join(fixture_check.failures))

    result = analyze_match(payload)
    if result["status"] != "OK":
        raise ValueError("DGOPRO engine blocked preview: " + json.dumps(result, ensure_ascii=False))

    expected = payload["expected"]
    scores = score_matrix(float(expected["home_xg"]), float(expected["away_xg"]), max_goals=10)
    likely_score, score_probability = max(scores.items(), key=lambda item: item[1])
    markets = result["markets"]
    overview = {
        "match_id": payload["match_id"],
        "fixture": payload["home_team"] + " vs " + payload["away_team"],
        "kickoff_utc": payload["kickoff"],
        "engine": result["engine"],
        "status": "EXPERIMENTAL_UNCALIBRATED",
        "official_publication_authorized": False,
        "probability_certified": False,
        "pre_match_integrity": "PASS",
        "official_fixture_integrity": "PASS",
        "source_urls": [item["url"] for item in payload["source_provenance"]],
        "input_means": expected,
        "probabilities": {
            "result_1x2": {key:markets["result"][key] for key in ("1", "X", "2")},
            "double_chance": {key:markets["result"][key] for key in ("1X", "X2", "12")},
            "goals": markets["goals"]["total"]["lines"],
            "btts": markets["goals"]["btts"],
            "corners": markets["corners"]["total"]["lines"],
            "cards": markets["cards"]["total"]["lines"],
            "shots": markets["shots"]["total"]["lines"],
            "shots_on_target": markets["sot"]["total"]["lines"],
        },
        "likely_exact_score": likely_score,
        "likely_exact_score_probability": score_probability,
        "publication_gate": result["publication"],
        "prediction_quality": result["prediction_quality"],
        "missing_validation": [
            "calibration from verified historical dataset",
            "out-of-sample backtesting",
            "fixture-specific calibrated expected metrics",
            "confirmed XI and player props",
            "referee-specific cards baseline",
            "ARB independent assessment",
        ],
        "methodology": payload["metadata"],
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(overview, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(overview, indent=2, ensure_ascii=False))
    return overview


if __name__ == "__main__":
    fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "examples/randers-brondby-2026-10-23.preview.json"
    report = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "artifacts/randers-brondby-2026-10-23.experimental.json"
    run(fixture, report)

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class IntegrityResult:
    passed: bool
    score: float
    failures: tuple[str, ...]
    warnings: tuple[str, ...]

REQUIRED = ("match_id", "kickoff", "snapshot_at", "home_team", "away_team")

def t1_integrity_gate(record: Mapping[str, Any]) -> IntegrityResult:
    failures=[]; warnings=[]
    for key in REQUIRED:
        if record.get(key) in (None, ""):
            failures.append(f"missing:{key}")
    try:
        kickoff=datetime.fromisoformat(str(record["kickoff"]).replace("Z", "+00:00"))
        snap=datetime.fromisoformat(str(record["snapshot_at"]).replace("Z", "+00:00"))
        if snap >= kickoff:
            failures.append("temporal_leakage:snapshot_not_pre_match")
    except Exception:
        failures.append("invalid_datetime")
    if not record.get("source_provenance"):
        warnings.append("missing_source_provenance")
    if record.get("lineup_status") not in ("confirmed", "expected", None):
        warnings.append("unknown_lineup_status")
    completeness=sum(record.get(k) not in (None, "") for k in REQUIRED)/len(REQUIRED)
    provenance=1.0 if record.get("source_provenance") else 0.5
    score=max(0.0, min(1.0, completeness*0.8+provenance*0.2-(0.5 if failures else 0.0)))
    return IntegrityResult(not failures, round(score,4), tuple(failures), tuple(warnings))

def deduplicate(records: Sequence[Mapping[str,Any]]) -> list[Mapping[str,Any]]:
    seen=set(); out=[]
    for r in records:
        key=(r.get("match_id"), r.get("snapshot_at"))
        if key in seen: continue
        seen.add(key); out.append(r)
    return out

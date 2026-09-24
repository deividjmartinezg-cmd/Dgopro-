from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence
import re
import unicodedata

@dataclass(frozen=True)
class IntegrityResult:
    passed: bool
    score: float
    failures: tuple[str, ...]
    warnings: tuple[str, ...]

REQUIRED = ("match_id", "kickoff", "snapshot_at", "home_team", "away_team")
FIXTURE_REQUIRED = (
    "fixture_verified",
    "fixture_source",
    "official_home_team",
    "official_away_team",
    "official_competition",
    "official_kickoff",
)


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _parse_dt(value: Any) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def t1_integrity_gate(record: Mapping[str, Any]) -> IntegrityResult:
    failures=[]; warnings=[]
    for key in REQUIRED:
        if record.get(key) in (None, ""):
            failures.append(f"missing:{key}")
    try:
        kickoff=_parse_dt(record["kickoff"])
        snap=_parse_dt(record["snapshot_at"])
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


def fixture_integrity_gate(record: Mapping[str, Any], *, kickoff_tolerance_minutes: int = 15) -> IntegrityResult:
    """Fail closed unless a canonical fixture has been verified against a source.

    This gate prevents swapped opponents, wrong competitions, wrong dates and stale
    aggregator fixtures from reaching DGOPRO publication. It compares the working
    record with a separately stored canonical/official fixture snapshot.
    """
    failures=[]; warnings=[]
    for key in FIXTURE_REQUIRED:
        if record.get(key) in (None, "", False):
            failures.append(f"fixture_missing:{key}")
    if failures:
        return IntegrityResult(False, 0.0, tuple(failures), tuple(warnings))

    if _norm(record.get("home_team")) != _norm(record.get("official_home_team")):
        failures.append("fixture_mismatch:home_team")
    if _norm(record.get("away_team")) != _norm(record.get("official_away_team")):
        failures.append("fixture_mismatch:away_team")
    if record.get("competition") and _norm(record.get("competition")) != _norm(record.get("official_competition")):
        failures.append("fixture_mismatch:competition")

    try:
        kickoff=_parse_dt(record.get("kickoff"))
        official=_parse_dt(record.get("official_kickoff"))
        delta=abs((kickoff-official).total_seconds())/60.0
        if delta > float(kickoff_tolerance_minutes):
            failures.append("fixture_mismatch:kickoff")
    except Exception:
        failures.append("fixture_invalid_datetime")

    if not record.get("fixture_source_is_official", False):
        warnings.append("fixture_source_not_marked_official")
    if int(record.get("fixture_confirmation_count", 1)) < 1:
        failures.append("fixture_unconfirmed")

    score=1.0
    if warnings:
        score-=0.1
    if failures:
        score=0.0
    return IntegrityResult(not failures, round(max(0.0, score),4), tuple(failures), tuple(warnings))


def publication_integrity_gate(record: Mapping[str, Any]) -> IntegrityResult:
    """Combined T-1 + canonical fixture gate used before any public prediction."""
    t1=t1_integrity_gate(record)
    fixture=fixture_integrity_gate(record)
    failures=tuple(t1.failures)+tuple(fixture.failures)
    warnings=tuple(t1.warnings)+tuple(fixture.warnings)
    score=min(t1.score, fixture.score)
    return IntegrityResult(not failures, round(score,4), failures, warnings)


def deduplicate(records: Sequence[Mapping[str,Any]]) -> list[Mapping[str,Any]]:
    seen=set(); out=[]
    for r in records:
        key=(r.get("match_id"), r.get("snapshot_at"))
        if key in seen: continue
        seen.add(key); out.append(r)
    return out

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence


def _ascii(value: Any) -> str:
    text=unicodedata.normalize("NFKD",str(value or "")).encode("ascii","ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+"," ",text.lower()).strip()


def _date(value: Any) -> str:
    text=str(value or "").strip()
    if not text: return ""
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%d/%m/%y","%d-%m-%Y","%Y/%m/%d"):
        try: return datetime.strptime(text[:10],fmt).date().isoformat()
        except ValueError: pass
    try: return datetime.fromisoformat(text.replace("Z","+00:00")).date().isoformat()
    except ValueError: return ""


def canonical_match_key(record: Mapping[str,Any]) -> str:
    parts=(_date(record.get("date") or record.get("kickoff")),_ascii(record.get("competition_id") or record.get("competition")),_ascii(record.get("home_team")),_ascii(record.get("away_team")))
    if not all(parts): return ""
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def score_signature(record: Mapping[str,Any]) -> tuple[int,int]|None:
    try:
        h=int(float(record["home_goals"])); a=int(float(record["away_goals"]))
        return (h,a) if h>=0 and a>=0 else None
    except (KeyError,TypeError,ValueError): return None

@dataclass(frozen=True)
class IndexDecision:
    status: str
    match_key: str
    reason: str
    canonical_counter_delta: int=0


def classify_record(record: Mapping[str,Any], *, canonical_by_key: Mapping[str,Sequence[Mapping[str,Any]]], staging_seen: set[str]) -> IndexDecision:
    key=canonical_match_key(record)
    if not key: return IndexDecision("AMBIGUOUS_QUARANTINE","","insufficient_identity")
    if key in staging_seen: return IndexDecision("DUPLICATE_INTERNAL",key,"repeated_staging_identity")
    candidates=list(canonical_by_key.get(key,()))
    if len(candidates)==1:
        incoming=score_signature(record); existing=score_signature(candidates[0])
        if incoming is not None and existing is not None and incoming!=existing:
            return IndexDecision("AMBIGUOUS_QUARANTINE",key,"identity_matches_but_score_conflicts")
        return IndexDecision("CANONICAL_MATCH",key,"unique_identity_match")
    if len(candidates)>1: return IndexDecision("AMBIGUOUS_QUARANTINE",key,"multiple_canonical_candidates")
    return IndexDecision("STAGING_UNIQUE",key,"not_found_in_recoverable_canonical_index")


def build_observational_index(records: Iterable[Mapping[str,Any]], canonical_records: Iterable[Mapping[str,Any]]=()) -> dict[str,Any]:
    canonical_by_key: dict[str,list[Mapping[str,Any]]]={}
    for row in canonical_records:
        key=canonical_match_key(row)
        if key: canonical_by_key.setdefault(key,[]).append(row)
    seen:set[str]=set(); rows=[]; counts={}
    for record in records:
        decision=classify_record(record,canonical_by_key=canonical_by_key,staging_seen=seen)
        if decision.match_key and decision.status!="DUPLICATE_INTERNAL": seen.add(decision.match_key)
        counts[decision.status]=counts.get(decision.status,0)+1
        rows.append({"match_key":decision.match_key,"status":decision.status,"reason":decision.reason,"canonical_counter_delta":0,"source":record.get("source"),"source_id":record.get("source_id")})
    return {"version":"observational-index-v1","rows":rows,"counts":counts,"canonical_counter_delta":0,"policy":{"auto_admit_new_canonical":False,"ambiguous_to_quarantine":True,"score_is_secondary_check":True}}

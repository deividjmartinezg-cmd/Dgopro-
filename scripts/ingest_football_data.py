"""Acquire historical match statistics independently of VMD.

Approved provider: football-data.co.uk. Downloads *observed results only*.
The snapshots are observational/post-match, NOT prematch predictions.
No bookmaker odds are imported or used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgopro.adapters.footballcsv import parse_footballcsv
from dgopro.coverage_audit import coverage_audit

BASE = "https://www.football-data.co.uk/mmz4281"
APPROVED_DIVISIONS = {"E0", "SP1", "I1", "D1", "F1"}
MAX_CSV_BYTES = 3_000_000

def source_url(season: str, division: str) -> str:
    if not re.fullmatch(r"\d{4}",season):
        raise ValueError("Season must be a four-digit code (e.g. 2526)")
    if division not in APPROVED_DIVISIONS:
        raise ValueError("Division not in approved first-division list")
    if int(season[2:]) != (int(season[:2]) + 1) % 100:
        raise ValueError("Invalid season interval")
    return f"{BASE}/{season}/{division}.csv"

def fetch_csv(url: str, *, attempts: int=2) -> bytes:
    if not url.startswith(BASE + "/"):
        raise ValueError("Unapproved data origin")
    last_error = None
    for i in range(attempts):
        try:
            request=Request(url, headers={"User-Agent": "DGOPRO research data-ingestion/1.0"})
            with urlopen(request, timeout=30) as response:
                final_url=urlsplit(response.geturl())
                original_url=urlsplit(url)
                # Some CSV links canonicalize www vs non-www. Permit only HTTPS,
                # identical dataset path and one of the two official hostnames.
                if (final_url.scheme!="https" or
                    final_url.hostname not in {"football-data.co.uk","www.football-data.co.uk"} or
                    final_url.path!=original_url.path or final_url.query):
                    raise RuntimeError(f"Unapproved provider redirect: {response.geturl()}")
                raw=response.read(MAX_CSV_BYTES+1)
            if len(raw)>MAX_CSV_BYTES or not raw.strip():
                raise ValueError("Oversize or empty CSV")
            if b"<html" in raw[:1024].lower() or b"<!doctype" in raw[:1024].lower():
                raise ValueError("Provider returned HTML, not CSV")
            return raw
        except (URLError, HTTPError, TimeoutError) as error:
            last_error = error
            if i+1<attempts:
                time.sleep(2)
    raise RuntimeError(f"CSV download failed for {url}: {last_error}")

def ingest(*, output_root: Path, seasons: list[str], divisions: list[str],
           fetcher=fetch_csv, min_matches: int=10) -> dict:
    root=Path(output_root)
    # Validate all parameters before doing any network or filesystem writes.
    for season in seasons:
        for division in divisions:
            source_url(season, division)
    if not seasons or not divisions:
        raise ValueError("At least one season and division are required")
    now=datetime.now(timezone.utc).isoformat()
    manifest={"schema":"dgopro_independent_ingestion_v1","fetched_at_utc":now,
              "provider":"football-data.co.uk","vmd_dependency":False,
              "odds_imported":False,"prematch_features_certified":False,
              "datasets":[],"failures":[]}
    all_records=[]
    for season in seasons:
        for division in divisions:
            url=source_url(season,division)
            try:
                raw=fetcher(url)
                csv_text=raw.decode("utf-8-sig")
                parsed=parse_footballcsv(csv_text,competition_id=division,source_path=url)
                if parsed["n"] < min_matches:
                    raise ValueError(f"Only {parsed['n']} completed matches parsed; required {min_matches}")
                relative=Path(season)/f"{division}.csv"
                target=root/"data/raw/footballcsv"/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(raw)
                for match in parsed["records"]:
                    match["season"]=season
                all_records.extend(parsed["records"])
                manifest["datasets"].append({
                    "division":division,"season":season,"url":url,
                    "path":str(target.relative_to(root)),
                    "sha256":sha256(raw).hexdigest(),
                    "completed_matches":parsed["n"],
                    "rejected_rows":len(parsed["rejected"]),
                    "capabilities":parsed["capabilities"],
                })
            except (ValueError, UnicodeError, RuntimeError, OSError) as error:
                manifest["failures"].append({"division":division,"season":season,
                                             "url":url,"error":str(error)})
    manifest["coverage"]=coverage_audit(all_records)["totals"]
    manifest["n_completed_matches"]=len(all_records)
    manifest["status"]="COMPLETE" if manifest["datasets"] and not manifest["failures"] else "INCOMPLETE"
    dest=root/"artifacts/ingestion_manifest.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return manifest

def main() -> int:
    p=argparse.ArgumentParser(description="DGOPRO independent historical data ingestion")
    p.add_argument("--output-root",type=Path,default=Path("."))
    p.add_argument("--seasons",nargs="+",default=["2425","2526","2627"])
    p.add_argument("--divisions",nargs="+",default=["E0","SP1","I1","D1","F1"])
    p.add_argument("--min-matches",type=int,default=10)
    args=p.parse_args()
    result=ingest(output_root=args.output_root,seasons=args.seasons,divisions=args.divisions,
                  min_matches=args.min_matches)
    print(json.dumps({"status":result["status"],"datasets":len(result["datasets"]),
                      "completed_matches":result["n_completed_matches"],
                      "coverage":result["coverage"],"failures":result["failures"]},
                     indent=2,ensure_ascii=False))
    return 0 if result["status"]=="COMPLETE" else 1

if __name__=="__main__":
    raise SystemExit(main())

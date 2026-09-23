from __future__ import annotations
import csv
import io
import re
from datetime import datetime
from typing import Any

DATE_FORMATS=("%a %b %d %Y","%d/%m/%Y","%d/%m/%y","%Y-%m-%d")

def _date(value: str) -> str:
    value=value.strip()
    for fmt in DATE_FORMATS:
        try: return datetime.strptime(value,fmt).date().isoformat()
        except ValueError: pass
    return ""

def _score(value: str) -> tuple[int,int]|None:
    m=re.fullmatch(r"\s*(\d+)\s*[-:]\s*(\d+)\s*",value or "")
    return (int(m.group(1)),int(m.group(2))) if m else None

def detect_capabilities(fieldnames: list[str]|None) -> dict[str,bool]:
    fields={str(x).strip().lower() for x in (fieldnames or [])}
    aliases={
        "result":{"ft","fthg","ftag"},
        "shots":{"hs","as","home_shots","away_shots"},
        "sot":{"hst","ast","home_sot","away_sot"},
        "corners":{"hc","ac","home_corners","away_corners"},
        "cards":{"hy","ay","hr","ar","home_cards","away_cards"},
        "xg":{"home_xg","away_xg","hxg","axg"},
    }
    return {k:bool(fields & v) for k,v in aliases.items()}

def parse_footballcsv(text: str, *, competition_id: str, source_path: str="") -> dict[str,Any]:
    reader=csv.DictReader(io.StringIO(text)); capabilities=detect_capabilities(reader.fieldnames); records=[]; rejected=[]
    for i,row in enumerate(reader,start=2):
        date=_date(row.get("Date","") or row.get("date","")); home=row.get("Team 1") or row.get("HomeTeam") or row.get("home_team"); away=row.get("Team 2") or row.get("AwayTeam") or row.get("away_team")
        score=_score(row.get("FT","") or (f"{row.get('FTHG','')}-{row.get('FTAG','')}" if row.get("FTHG") not in (None,"") else ""))
        if not date or not home or not away or score is None:
            rejected.append({"line":i,"reason":"identity_or_result_missing"}); continue
        record={"date":date,"competition_id":competition_id,"home_team":home.strip(),"away_team":away.strip(),"home_goals":score[0],"away_goals":score[1],"source":"footballcsv","source_type":"footballcsv","source_id":f"{source_path}:{i}","observed_real":True,"prematch_features_t1_safe":False}
        records.append(record)
    return {"records":records,"rejected":rejected,"capabilities":capabilities,"n":len(records),"source_path":source_path}

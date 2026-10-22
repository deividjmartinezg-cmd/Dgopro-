from __future__ import annotations
import csv
import io
import math
import re
from datetime import datetime
from typing import Any

DATE_FORMATS=("%a %b %d %Y","%d/%m/%Y","%d/%m/%y","%Y-%m-%d")
PAIRS={
    "shots":(("HS","home_shots"),("AS","away_shots")),
    "sot":(("HST","home_sot"),("AST","away_sot")),
    "corners":(("HC","home_corners"),("AC","away_corners")),
    "cards":(("HY","home_cards"),("AY","away_cards")),
    "red_cards":(("HR","home_red_cards"),("AR","away_red_cards")),
    "xg":(("HxG","home_xg"),("AxG","away_xg")),
}

def _date(value: str) -> str:
    value=str(value or "").strip()
    for fmt in DATE_FORMATS:
        try: return datetime.strptime(value,fmt).date().isoformat()
        except ValueError: pass
    return ""

def _score(value: str) -> tuple[int,int]|None:
    m=re.fullmatch(r"\s*(\d+)\s*[-:]\s*(\d+)\s*",value or "")
    return (int(m.group(1)),int(m.group(2))) if m else None

def _number(row: dict[str,str], names: tuple[str,...], *, integer: bool=True) -> int|float|None:
    lookup={str(k).strip().lower():v for k,v in row.items() if k is not None}
    raw=next((lookup[name.lower()] for name in names if lookup.get(name.lower()) not in (None,"")),None)
    if raw is None: return None
    try:
        value=float(str(raw).strip())
        if not math.isfinite(value) or value<0 or (integer and not value.is_integer()):
            return None
        return int(value) if integer else value
    except (TypeError,ValueError,OverflowError):
        return None

def detect_capabilities(fieldnames: list[str]|None) -> dict[str,bool]:
    fields={str(x).strip().lower() for x in (fieldnames or [])}
    pair_aliases={
        "shots":({"hs","home_shots"},{"as","away_shots"}),
        "sot":({"hst","home_sot"},{"ast","away_sot"}),
        "corners":({"hc","home_corners"},{"ac","away_corners"}),
        "cards":({"hy","home_cards"},{"ay","away_cards"}),
        "red_cards":({"hr","home_red_cards"},{"ar","away_red_cards"}),
        "xg":({"hxg","home_xg"},{"axg","away_xg"}),
    }
    result=("ft" in fields) or ({"fthg","ftag"} <= fields) or ({"home_goals","away_goals"} <= fields)
    return {"result":result,**{market:bool(fields & home and fields & away) for market,(home,away) in pair_aliases.items()}}

def parse_footballcsv(text: str, *, competition_id: str, source_path: str="") -> dict[str,Any]:
    reader=csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    capabilities=detect_capabilities(reader.fieldnames)
    records=[]; rejected=[]
    for i,row in enumerate(reader,start=2):
        date=_date(row.get("Date","") or row.get("date",""))
        home=row.get("Team 1") or row.get("HomeTeam") or row.get("home_team")
        away=row.get("Team 2") or row.get("AwayTeam") or row.get("away_team")
        hg=_number(row,("FTHG","home_goals"))
        ag=_number(row,("FTAG","away_goals"))
        score=(hg,ag) if hg is not None and ag is not None else _score(row.get("FT",""))
        if not date or not home or not away or score is None:
            rejected.append({"line":i,"reason":"identity_or_result_missing"}); continue
        record={"date":date,"competition_id":competition_id,"home_team":str(home).strip(),"away_team":str(away).strip(),
                "home_goals":score[0],"away_goals":score[1],
                "source":"footballcsv","source_type":"footballcsv","source_id":f"{source_path}:{i}",
                "observed_real":True,"prematch_features_t1_safe":False,
                "date_precision":"day_only","odds_imported":False}
        for metric,((raw_h,key_h),(raw_a,key_a)) in PAIRS.items():
            record[key_h]=_number(row,(raw_h,key_h),integer=(metric!="xg"))
            record[key_a]=_number(row,(raw_a,key_a),integer=(metric!="xg"))
        referee=row.get("Referee") or row.get("referee")
        if referee: record["referee"]=str(referee).strip()
        # Cards are yellow cards from HY/AY. Red cards HR/AR are tracked separately.
        # No bookmaker odds or post-match data may become pre-kickoff features.
        records.append(record)
    return {"records":records,"rejected":rejected,"capabilities":capabilities,"n":len(records),"source_path":source_path}

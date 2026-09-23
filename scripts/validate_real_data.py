from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dgopro.adapters.footballcsv import parse_footballcsv
from dgopro.coverage_audit import coverage_audit, training_readiness
from dgopro.observational_index import build_observational_index
from dgopro.evaluation import brier, log_loss, ece

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path("../VMD-World")
BASE=ROOT/"data/raw/footballcsv"
records=[]; files=[]; rejected=0
for path in sorted(BASE.glob("*/*.csv")):
    season=path.parent.name; comp=path.stem
    parsed=parse_footballcsv(path.read_text(encoding="utf-8-sig"),competition_id=comp,source_path=str(path))
    for r in parsed["records"]: r["season"]=season
    records.extend(parsed["records"]); rejected+=len(parsed["rejected"])
    files.append({"season":season,"competition":comp,"n":parsed["n"],"rejected":len(parsed["rejected"]),"capabilities":parsed["capabilities"]})
index=build_observational_index(records,[])
audit=coverage_audit(records); readiness=training_readiness(audit)

def expanding_goal_baseline(line: float, min_train: int=100):
    ordered=sorted(records,key=lambda r:(r["date"],r["competition_id"],r["home_team"],r["away_team"]))
    by_comp={}; pred=[]; y=[]
    # Date-group update: no match on a date can train another match on the same date.
    dates=sorted({r["date"] for r in ordered})
    for date in dates:
        today=[r for r in ordered if r["date"]==date]
        for r in today:
            hist=by_comp.get(r["competition_id"],[])
            if len(hist)>=min_train:
                p=sum(hist)/len(hist); outcome=int(r["home_goals"]+r["away_goals"]>line)
                pred.append(p); y.append(outcome)
        for r in today:
            by_comp.setdefault(r["competition_id"],[]).append(int(r["home_goals"]+r["away_goals"]>line))
    if not y: return {"line":line,"n":0}
    acc=sum((p>=.5)==bool(v) for p,v in zip(pred,y))/len(y)
    return {"line":line,"n":len(y),"accuracy_at_0_5":acc,"brier":brier(y,pred),"log_loss":log_loss(y,pred),"ece":ece(y,pred),"mean_probability":sum(pred)/len(pred),"observed_rate":sum(y)/len(y),"strict_date_oos":True}

report={"source":"VMD-World/data/raw/footballcsv","n_files":len(files),"n_records":len(records),"rejected":rejected,"index_counts":index["counts"],"canonical_counter_delta":index["canonical_counter_delta"],"coverage":audit,"readiness":readiness,"goal_baselines":[expanding_goal_baseline(1.5),expanding_goal_baseline(2.5),expanding_goal_baseline(3.5)],"files":files}
out=Path("artifacts"); out.mkdir(exist_ok=True); (out/"real_data_validation.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({k:report[k] for k in ("n_files","n_records","rejected","index_counts","canonical_counter_delta","readiness","goal_baselines")},indent=2))

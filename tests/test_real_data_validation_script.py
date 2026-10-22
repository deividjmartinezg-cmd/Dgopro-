from pathlib import Path
import subprocess
import sys

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/validate_real_data.py"

def test_validator_fails_closed_when_dataset_directory_is_missing(tmp_path):
    result=subprocess.run([sys.executable,str(SCRIPT),str(tmp_path)],capture_output=True,text=True)
    assert result.returncode!=0
    assert "Historical validation NOT EXECUTED" in result.stderr

def test_validator_fails_closed_when_no_csv_files_exist(tmp_path):
    (tmp_path/"data/raw/footballcsv").mkdir(parents=True)
    result=subprocess.run([sys.executable,str(SCRIPT),str(tmp_path)],capture_output=True,text=True)
    assert result.returncode!=0
    assert "no CSV files" in result.stderr

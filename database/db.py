import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
DB=DATA/"modelvault.sqlite3"

def connect():
    DATA.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS model_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, model_name TEXT NOT NULL, version TEXT NOT NULL,
        description TEXT, task_type TEXT NOT NULL, filename TEXT NOT NULL, artifact_path TEXT NOT NULL,
        metrics_json TEXT NOT NULL, dataset_columns_json TEXT NOT NULL, target_column TEXT NOT NULL,
        rows_evaluated INTEGER NOT NULL, created_at TEXT NOT NULL, is_production INTEGER NOT NULL DEFAULT 0,
        UNIQUE(model_name,version))''')

def register_version(model_name,version,description,task_type,filename,path,metrics,columns,target,rows):
    with connect() as c:
        c.execute('''INSERT INTO model_versions
        (model_name,version,description,task_type,filename,artifact_path,metrics_json,dataset_columns_json,target_column,rows_evaluated,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',(model_name,version,description,task_type,filename,path,json.dumps(metrics),json.dumps(columns),target,rows,datetime.now(timezone.utc).isoformat(timespec="seconds")))

def list_versions():
    with connect() as c: rows=c.execute("SELECT * FROM model_versions ORDER BY id DESC").fetchall()
    result=[]
    for r in rows:
        d=dict(r); d["is_production"]=bool(d["is_production"]); result.append(d)
    return result

def list_models():
    with connect() as c: return [r[0] for r in c.execute("SELECT DISTINCT model_name FROM model_versions").fetchall()]

def get_metrics(version_id):
    with connect() as c: r=c.execute("SELECT metrics_json FROM model_versions WHERE id=?",(version_id,)).fetchone()
    return json.loads(r[0]) if r else {}

def set_production(name,version):
    with connect() as c:
        c.execute("UPDATE model_versions SET is_production=0 WHERE model_name=?",(name,))
        c.execute("UPDATE model_versions SET is_production=1 WHERE model_name=? AND version=?",(name,version))

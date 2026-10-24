from pathlib import Path
import re,uuid,joblib
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/"data"/"incoming"
ARTIFACTS=ROOT/"artifacts"

def safe_name(name):
    return re.sub(r"[^A-Za-z0-9._-]+","_",name.strip())[:80] or "model"

def save_upload(uploaded_file,model_name):
    INCOMING.mkdir(parents=True,exist_ok=True)
    suffix=Path(uploaded_file.name).suffix.lower()
    if suffix not in {".pkl",".joblib"}: raise ValueError("Only .pkl and .joblib are supported.")
    p=INCOMING/f"{safe_name(model_name)}_{uuid.uuid4().hex}{suffix}"
    p.write_bytes(uploaded_file.getvalue())
    return p

def load_trusted_model(path):
    # Pickle/joblib loading can execute code: only load trusted artifacts.
    return joblib.load(path)

def artifact_path(name,version,filename):
    suffix=Path(filename).suffix.lower()
    return ARTIFACTS/safe_name(name)/version/f"model{suffix}"

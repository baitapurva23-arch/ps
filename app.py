import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import shutil
from database.db import init_db, list_versions, list_models, get_metrics, register_version, set_production
from services.model_evaluator import evaluate_model
from services.model_registry import save_upload, load_trusted_model, artifact_path
from services.version_manager import next_version

st.set_page_config(page_title="ModelVault", page_icon="🗂️", layout="wide")
init_db()
st.title("🗂️ ModelVault")
st.caption("Machine Learning Model Versioning & Management System")
page = st.sidebar.radio("Navigation", ["Dashboard", "Upload & Evaluate", "Model Registry", "Version Comparison", "About"])

versions = list_versions()
if page == "Dashboard":
    a,b,c = st.columns(3)
    a.metric("Registered models", len(list_models()))
    b.metric("Saved versions", len(versions))
    c.metric("Production versions", sum(v["is_production"] for v in versions))
    if versions:
        st.subheader("Recent versions")
        st.dataframe(pd.DataFrame(versions)[["model_name","version","task_type","created_at","is_production"]], use_container_width=True, hide_index=True)
        rows=[]
        for v in versions:
            for metric,value in get_metrics(v["id"]).items():
                if isinstance(value,(int,float)):
                    rows.append({"Version":f'{v["model_name"]} {v["version"]}',"Metric":metric,"Value":value})
        if rows:
            d=pd.DataFrame(rows)
            metric=st.selectbox("Metric",sorted(d.Metric.unique()))
            st.plotly_chart(px.bar(d[d.Metric==metric],x="Version",y="Value",title=f"{metric} by version"),use_container_width=True)
    else:
        st.info("No models yet. Upload a trained model and labelled test CSV to begin.")
elif page == "Upload & Evaluate":
    st.subheader("Upload and evaluate a trusted model")
    st.warning("Only upload model files you trained or fully trust. Pickle/joblib deserialization can execute arbitrary code.")
    with st.form("upload"):
        name=st.text_input("Model name",placeholder="Iris Classifier")
        desc=st.text_input("Description (optional)")
        task=st.selectbox("Task type",["classification","regression"])
        model_file=st.file_uploader("Model file (.pkl or .joblib)",type=["pkl","joblib"])
        csv_file=st.file_uploader("Labelled test dataset (.csv)",type=["csv"])
        target=st.text_input("Target column",value="target")
        go=st.form_submit_button("Evaluate and save version",type="primary")
    if go:
        if not name.strip() or not model_file or not csv_file:
            st.error("Enter a model name and upload both files.")
        elif model_file.size>50*1024*1024 or csv_file.size>50*1024*1024:
            st.error("Files must be 50 MB or smaller.")
        else:
            temp=None
            try:
                df=pd.read_csv(csv_file)
                if target not in df.columns: raise ValueError(f"Target column '{target}' not found.")
                if df.empty: raise ValueError("CSV has no rows.")
                X=df.drop(columns=[target]); y=df[target]
                temp=save_upload(model_file,name)
                model=load_trusted_model(temp)
                metrics,details=evaluate_model(model,X,y,task)
                version=next_version(name.strip())
                dest=artifact_path(name,version,model_file.name)
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.move(str(temp),str(dest))
                register_version(name.strip(),version,desc,task,model_file.name,str(dest),metrics,list(X.columns),target,len(df))
                st.success(f"Evaluation complete. Saved as {version}.")
                st.json(metrics)
                if "confusion_matrix" in details:
                    st.write("Confusion matrix")
                    st.dataframe(pd.DataFrame(details["confusion_matrix"]),hide_index=True)
            except Exception as e:
                st.error(f"Could not evaluate or save model: {e}")
                st.caption("Check feature names/order and preprocessing compatibility.")
            finally:
                if temp and Path(temp).exists(): Path(temp).unlink()
elif page == "Model Registry":
    if not versions: st.info("No model versions saved yet.")
    else:
        st.dataframe(pd.DataFrame(versions)[["model_name","version","description","task_type","created_at","is_production"]],use_container_width=True,hide_index=True)
        labels=[f'{v["model_name"]} — {v["version"]}' for v in versions]
        selected=st.selectbox("Select version",labels)
        v=next(v for v,l in zip(versions,labels) if l==selected)
        st.json(get_metrics(v["id"]))
        p=Path(v["artifact_path"])
        if p.exists(): st.download_button("Download model",p.read_bytes(),file_name=v["filename"],mime="application/octet-stream")
        if st.button("Mark as production",type="primary"):
            set_production(v["model_name"],v["version"]); st.success("Production version updated."); st.rerun()
elif page == "Version Comparison":
    if len(versions)<2: st.info("Save at least two versions to compare them.")
    else:
        labels=[f'{v["model_name"]} — {v["version"]}' for v in versions]
        selected=st.multiselect("Choose versions",labels,default=labels[:2])
        rows=[]
        for v,l in zip(versions,labels):
            if l in selected:
                row={"Version":l,"Task":v["task_type"],"Dataset rows":v["rows_evaluated"]}
                row.update(get_metrics(v["id"])); rows.append(row)
        if len(rows)>=2:
            d=pd.DataFrame(rows); st.dataframe(d,use_container_width=True,hide_index=True)
            st.caption("For a fair comparison, evaluate versions on the same held-out dataset and settings.")
            numeric=[c for c in d.columns if c not in ["Version","Task","Dataset rows"] and pd.api.types.is_numeric_dtype(d[c])]
            if numeric:
                m=st.selectbox("Chart metric",numeric)
                st.plotly_chart(px.bar(d,x="Version",y=m,title=f"Comparison: {m}"),use_container_width=True)
else:
    st.subheader("About ModelVault")
    st.write("An educational MLOps mini-project for model evaluation, version history, metric comparison, Jenkins CI, and Docker.")
    st.markdown("**Workflow:** upload a trusted model and labelled CSV → evaluate → save a version → compare versions → mark a production version. Jenkins tests the code and builds the image; Docker runs the app.")
    st.warning("This is a local prototype. Model files must be trusted, features must match the trained model, and metrics are only comparable on equivalent test data.")

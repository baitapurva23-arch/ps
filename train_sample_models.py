from pathlib import Path
import joblib
import pandas as pd
from sklearn.datasets import load_iris,load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression,LinearRegression

ROOT=Path(__file__).resolve().parent
(ROOT/"sample_data").mkdir(exist_ok=True); (ROOT/"sample_models").mkdir(exist_ok=True)
iris=load_iris(as_frame=True); X,y=iris.data,iris.target
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
clf=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000)).fit(Xtr,ytr)
out=Xte.copy(); out["target"]=yte; out.to_csv(ROOT/"sample_data"/"iris_test.csv",index=False)
joblib.dump(clf,ROOT/"sample_models"/"iris_classifier.joblib")
diabetes=load_diabetes(as_frame=True); X,y=diabetes.data,diabetes.target
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42)
reg=make_pipeline(StandardScaler(),LinearRegression()).fit(Xtr,ytr)
out=Xte.copy(); out["target"]=yte; out.to_csv(ROOT/"sample_data"/"diabetes_test.csv",index=False)
joblib.dump(reg,ROOT/"sample_models"/"diabetes_regressor.joblib")
print("Generated demo models and CSVs.")

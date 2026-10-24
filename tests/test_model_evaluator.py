import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier,DummyRegressor
from services.model_evaluator import evaluate_model

def test_classification_metrics():
    X=pd.DataFrame({"x":[0,1,2,3]}); y=np.array([0,0,1,1])
    model=DummyClassifier(strategy="most_frequent").fit(X,y)
    metrics,details=evaluate_model(model,X,y,"classification")
    assert 0 <= metrics["accuracy"] <= 1
    assert "f1_macro" in metrics and "confusion_matrix" in details

def test_regression_metrics():
    X=pd.DataFrame({"x":[0,1,2,3]}); y=np.array([0.,1.,2.,3.])
    model=DummyRegressor(strategy="mean").fit(X,y)
    metrics,_=evaluate_model(model,X,y,"regression")
    assert metrics["mae"]>=0 and metrics["rmse"]>=0 and "r2" in metrics

import numpy as np
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score

def evaluate_model(model,X,y,task_type):
    if len(X)==0 or len(X)!=len(y): raise ValueError("Features and target must have the same non-zero row count.")
    pred=model.predict(X)
    if len(pred)!=len(y): raise ValueError("Prediction count does not match test rows.")
    if task_type=="classification":
        labels=list(dict.fromkeys(list(y)+list(pred)))
        metrics={"accuracy":float(accuracy_score(y,pred)),
                 "precision_macro":float(precision_score(y,pred,average="macro",zero_division=0)),
                 "recall_macro":float(recall_score(y,pred,average="macro",zero_division=0)),
                 "f1_macro":float(f1_score(y,pred,average="macro",zero_division=0))}
        return metrics,{"confusion_matrix":confusion_matrix(y,pred,labels=labels).tolist(),"labels":[str(x) for x in labels]}
    if task_type=="regression":
        mse=mean_squared_error(y,pred)
        return {"mae":float(mean_absolute_error(y,pred)),"rmse":float(np.sqrt(mse)),"r2":float(r2_score(y,pred)) if len(y)>1 else float("nan")},{}
    raise ValueError("Task type must be classification or regression.")

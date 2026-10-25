
import sys
from pathlib import Path

import joblib
import pandas as pd

from services.model_evaluator import evaluate_model


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: python jenkins_evaluate.py "
            "MODEL_PATH CSV_PATH TARGET_COLUMN TASK"
        )
        return 1

    model_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])
    target = sys.argv[3]
    task = sys.argv[4].lower()

    if not model_path.is_file():
        print(f"ERROR: Model file not found: {model_path}")
        return 1

    if not csv_path.is_file():
        print(f"ERROR: Test CSV not found: {csv_path}")
        return 1

    if task not in ("classification", "regression"):
        print("ERROR: Task must be classification or regression.")
        return 1

    print(f"Model: {model_path}")
    print(f"Dataset: {csv_path}")
    print(f"Task: {task}")

    model = joblib.load(model_path)
    df = pd.read_csv(csv_path)

    if target not in df.columns:
        print(f"ERROR: Target column '{target}' not found.")
        return 1

    X = df.drop(columns=[target])
    y = df[target]

    metrics, details = evaluate_model(model, X, y, task)

    print("\n========== MODEL EVALUATION RESULTS ==========")
    print(f"Test rows: {len(df)}")

    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")

    if "confusion_matrix" in details:
        print("\nConfusion Matrix:")
        for row in details["confusion_matrix"]:
            print(row)

    print("\nMODEL EVALUATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

from dataclasses import dataclass
from typing import Dict, Any
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from joblib import dump, load

@dataclass
class TrainResult:
    model_path: str
    metrics: Dict[str, Any]

def make_model(name: str="gbt") -> Pipeline:
    if name == "gbt":
        model = GradientBoostingClassifier(random_state=42)
    elif name == "rf":
        model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    elif name == "logreg":
        model = LogisticRegression(max_iter=500)
    else:
        raise ValueError(f"Unknown model: {name}")
    return Pipeline([("scaler", StandardScaler(with_mean=False)), ("clf", model)])

def train(X, y, model_name: str="gbt"):
    pipe = make_model(model_name)
    pipe.fit(X, y)
    return pipe

def evaluate(pipe: Pipeline, X, y):
    pred = pipe.predict(X)
    acc = accuracy_score(y, pred)
    return {"accuracy": float(acc), "report": classification_report(y, pred, output_dict=True)}

def save_model(pipe: Pipeline, path: str) -> str:
    dump(pipe, path)
    return path

def load_model(path: str) -> Pipeline:
    return load(path)

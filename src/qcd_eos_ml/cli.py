import argparse, json
from pathlib import Path
from . import data as D, labels as L, features as F, models as M, plotting as P

def train_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gbt", choices=["gbt","rf","logreg"])
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    df = D.add_muhat(D.load_eos(args.data))
    df = L.add_phase_label(df)
    tr, te = D.train_eval_split(df, test_frac=0.2, seed=42)
    Xtr, ytr = F.build_features(tr)
    Xte, yte = F.build_features(te)
    pipe = M.train(Xtr, ytr, model_name=args.model)
    metrics_tr = M.evaluate(pipe, Xtr, ytr)
    metrics_te = M.evaluate(pipe, Xte, yte)
    M.save_model(pipe, str(out / "model.joblib"))
    (out / "metrics.json").write_text(json.dumps({"train":metrics_tr,"test":metrics_te}, indent=2))
    print(f"Saved -> {out}/model.joblib")
    print(f"Test accuracy: {metrics_te['accuracy']:.4f}")

def eval_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True)
    args = ap.parse_args()
    df = D.add_muhat(D.load_eos(args.data))
    df = L.add_phase_label(df)
    X, y = F.build_features(df)
    pipe = M.load_model(args.model)
    print(json.dumps(M.evaluate(pipe, X, y), indent=2))

def predict_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--yq", type=float, required=True)
    ap.add_argument("--T", type=float, required=True)
    ap.add_argument("--muB_H", type=float, required=True)
    ap.add_argument("--muB_Q", type=float, required=True)
    ap.add_argument("--muQ_H", type=float, required=True)
    ap.add_argument("--muQ_Q", type=float, required=True)
    args = ap.parse_args()
    import pandas as pd
    row = pd.DataFrame([vars(args)]).rename(columns={"yq":"YQ"})
    from .features import build_features
    X,_ = build_features(row.assign(phase=0))
    pipe = M.load_model(args.model)
    print({"phase_pred": int(pipe.predict(X)[0]), "0=hadron,1=quark": True})

def figures_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    df = D.load_eos(args.data)
    P.fig_3d_from_eos(df, outdir=out)
    print(f"Figures written to {out}")

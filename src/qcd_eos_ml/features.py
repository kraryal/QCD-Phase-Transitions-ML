import pandas as pd
FEAT_COLS = ["YQ","T","muB_H","muB_Q","muQ_H","muQ_Q"]
def build_features(df: pd.DataFrame):
    X = df[FEAT_COLS].copy()
    Xn = (X - X.mean())/X.std(ddof=0)
    Xn["YQ_T"] = Xn["YQ"]*Xn["T"]
    Xn["delta_muB"] = Xn["muB_Q"] - Xn["muB_H"]
    Xn["delta_muQ"] = Xn["muQ_Q"] - Xn["muQ_H"]
    y = df["phase"].astype(int)
    return Xn, y

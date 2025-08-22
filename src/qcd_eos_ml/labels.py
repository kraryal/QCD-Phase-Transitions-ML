import pandas as pd
def add_phase_label(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["phase"] = (df["F_quark"] < df["F_hadron"]).astype(int)
    return df

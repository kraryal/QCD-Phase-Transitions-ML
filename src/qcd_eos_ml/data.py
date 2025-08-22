import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple

COLS = {
    "YQ": 0, "T": 1, "F_quark": 2, "F_hadron": 3,
    "muB_Q": 6, "muB_H": 7, "muQ_Q": 8, "muQ_H": 9
}

def load_eos(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, delim_whitespace=True, header=None)
    ren = {v:k for k,v in COLS.items()}
    df = df.rename(columns=ren)
    for c in ren.values(): df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    return df

def add_muhat(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["muhat_H"] = df["muB_H"] + df["YQ"]*df["muQ_H"]
    df["muhat_Q"] = df["muB_Q"] + df["YQ"]*df["muQ_Q"]
    return df

def train_eval_split(df: pd.DataFrame, test_frac: float=0.2, seed: int=42):
    df = df.copy()
    bins = np.linspace(df["T"].min(), df["T"].max(), 9)
    df["T_bin"] = np.digitize(df["T"], bins, right=False)
    from sklearn.model_selection import StratifiedShuffleSplit
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_frac, random_state=seed)
    train_idx, test_idx = next(sss.split(df, df["T_bin"]))
    return df.iloc[train_idx].drop(columns=["T_bin"]), df.iloc[test_idx].drop(columns=["T_bin"])

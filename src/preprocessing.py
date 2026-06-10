import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def remove_duplicates(df):
    return df.drop_duplicates()

def remove_infinite(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    return df.dropna()

def remove_constant_features(df):
    constant_cols = [
        col for col in df.columns
        if df[col].nunique() == 1
    ]
    return df.drop(columns=constant_cols)

def split_data(X, y):

    return train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
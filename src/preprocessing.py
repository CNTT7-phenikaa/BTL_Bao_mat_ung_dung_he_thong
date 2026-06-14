import pandas as pd
import numpy as np
from src.config import SELECTED_FEATURES

def clean_network_data(df, selected_features=SELECTED_FEATURES):
    df_clean = df.copy()
    
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    
  
    df_clean = df_clean.dropna(subset=selected_features)
    
    return df_clean


def select_features(df):
    return df[SELECTED_FEATURES]
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
import joblib

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

# chọn đặc trưng
def select_features(df):
    selected_features = [
        'Flow Duration',
        'Flow Bytes/s',
        'Flow Packets/s',
        'Total Fwd Packets',
        'Total Backward Packets',
        'Packet Length Mean',
        'Packet Length Std',
        'Average Packet Size',
        'Flow IAT Mean',
        'Flow IAT Std',
        'SYN Flag Count',
        'ACK Flag Count',
        'Label'
    ]

    return df[selected_features]
#mã nhãn
def encode_labels(df):
    le = LabelEncoder()

    df = df.copy()
    df['Label'] = le.fit_transform(df['Label'])

    return df, le
# chuẩn hóa dữ liệu
def scale_data(X_train, X_test):
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, scaler
# lưu scaler
def save_scaler(scaler, path):
    joblib.dump(scaler, path)

# lưu tập train và test
def save_processed_data(
    X_train,
    X_test,
    y_train,
    y_test,
    output_dir
):
    X_train.to_csv(
        f"{output_dir}/X_train.csv",
        index=False
    )

    X_test.to_csv(
        f"{output_dir}/X_test.csv",
        index=False
    )

    y_train.to_csv(
        f"{output_dir}/y_train.csv",
        index=False
    )

    y_test.to_csv(
        f"{output_dir}/y_test.csv",
        index=False
    )
# kiểm tra missing values
def check_missing_values(df):
    return df.isnull().sum()
# hàm tách x, y
def split_features_labels(df):
    X = df.drop(columns=['Label'])
    y = df['Label']
    return X, y
#tiền xử lí dữ liệu 
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    print(
        f"[load_data] "
        f"{df.shape[0]:,} hàng × "
        f"{df.shape[1]} cột"
    )

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    original_len = len(df)

    df = df.drop_duplicates()

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns

    df[numeric_cols] = df[numeric_cols].replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.dropna()

    print(
        f"[clean_data] "
        f"Còn {len(df):,} hàng "
        f"(mất {original_len - len(df):,} hàng)"
    )

    return df.reset_index(drop=True)


def remove_constant_columns(
    df: pd.DataFrame
) -> pd.DataFrame:

    constant_cols = [
        col
        for col in df.columns
        if df[col].nunique() == 1
    ]

    if constant_cols:

        print(
            f"[remove_constant_columns] "
            f"Xóa {len(constant_cols)} cột"
        )

        df = df.drop(
            columns=constant_cols
        )

    return df


def encode_labels(
    df: pd.DataFrame,
    label_col: str = "Label"
):

    df = df.copy()

    le = LabelEncoder()

    df[label_col] = le.fit_transform(
        df[label_col]
    )

    print(
        "[encode_labels] Classes:"
    )

    print(
        list(le.classes_)
    )

    return df, le


def split_features_labels(
    df: pd.DataFrame,
    label_col: str = "Label"
):

    X = df.drop(
        columns=[label_col]
    )

    y = df[label_col]

    return X, y


def split_train_test(
    X,
    y,
    test_size: float = 0.2,
    random_state: int = 42
):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    print(
        f"[split_train_test] "
        f"Train: {len(X_train):,} | "
        f"Test: {len(X_test):,}"
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


def scale_features(
    X_train,
    X_test
):

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    return (
        X_train_scaled,
        X_test_scaled,
        scaler
    )
# if __name__ == "__main__":

#     df = load_data("data/raw/cicids2017_100k.csv")

#     df = clean_data(df)

#     df = remove_constant_columns(df)

#     df, le = encode_labels(df)

#     X, y = split_features_labels(df)

#     X_train, X_test, y_train, y_test = split_train_test(X, y)

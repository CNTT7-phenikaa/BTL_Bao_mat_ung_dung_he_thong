
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
def load_data():
    X_train = pd.read_csv("data/processed/X_train.csv")
    y_train = pd.read_csv("data/processed/y_train.csv")
    x_test = pd.read_csv("data/processed/X_test.csv")
    y_test = pd.read_csv("data/processed/y_test.csv")

    return X_train, y_train.squeeze(), x_test, y_test.squeeze()


def get_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=1,
            solver="lbfgs",
            random_state=42
        ),

        "Random Forest": RandomForestClassifier(
            random_state=42, 
            n_estimators=100, 
            max_depth=None, 
            oob_score=True, 
            n_jobs=-1
        ),

        "SVM": LinearSVC(
            C=1,
            random_state=42
        )
    }


def evaluate_models_cv(X_train, y_train, cv=skf):

    results = []

    models = get_models()

    for name, model in models.items():

        scores = cross_val_score(
            model,
            X_train,
            y_train,
            cv=skf,
            scoring="f1_weighted",
            n_jobs=-1
        )

        results.append({
            "Model": name,
            "Mean_F1": scores.mean(),
            "Std_F1": scores.std()
        })

    results_df = pd.DataFrame(results)

    return results_df.sort_values(
        by="Mean_F1",
        ascending=False
    )


def train_best_model(model_name, X_train, y_train):

    model = get_models()[model_name]

    model.fit(X_train, y_train)

    return model


if __name__ == "__main__":

    X_train, y_train, x_test, y_test = load_data()

    results = evaluate_models_cv(
        X_train,
        y_train,
        cv=skf
    )

    print("\n===== K-Fold Cross Validation =====")
    print(results)

    best_model_name = results.iloc[0]["Model"]

    print(f"\nBest Model: {best_model_name}")

    best_model = train_best_model(
        best_model_name,
        X_train,
        y_train
    )
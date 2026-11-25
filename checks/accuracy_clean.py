"""Churn-model test accuracy (%) on customer_model_features as built by dbt.

Every column except customer_id and churned is a feature, so a leaked column added to the model shows up here.
"""

import tomllib
from pathlib import Path

import duckdb
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

KEY = "acc_clean"
TOLERANCE = tomllib.loads(Path("demo_numbers.toml").read_text())["acc_tolerance_pts"]  # stop if accuracy moves more than this


def features() -> pd.DataFrame:
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        return con.sql("select * from customer_model_features order by customer_id").df()


def accuracy(df: pd.DataFrame) -> float:
    X, y = df.drop(columns=["customer_id", "churned"]), df["churned"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
    return 100 * model.score(X_test, y_test)


def value() -> int:
    return round(accuracy(features()))

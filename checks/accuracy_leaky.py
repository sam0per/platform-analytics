"""Churn-model test accuracy (%) when the outcome-only column exit_survey_sent is added back."""

import pandas as pd

from checks.accuracy_clean import accuracy, features

KEY = "acc_leaky"


def leaky_features() -> pd.DataFrame:
    survey = pd.read_csv("data/raw/features_v2.csv", usecols=["customer_id", "exit_survey_sent"], dtype={"customer_id": str})
    survey["customer_id"] = survey["customer_id"].str.strip()
    return features().merge(survey, on="customer_id")


def value() -> int:
    return round(accuracy(leaky_features()))

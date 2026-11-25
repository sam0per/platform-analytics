"""Customers left after a naive inner join of accounts to features_v2 on the untrimmed key."""

import pandas as pd

KEY = "customers_out"


def value() -> int:
    accounts = pd.read_csv("data/raw/accounts.csv", dtype={"customer_id": str})
    features = pd.read_csv("data/raw/features_v2.csv", dtype={"customer_id": str})
    return len(accounts.merge(features[["customer_id"]], on="customer_id"))

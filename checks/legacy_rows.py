"""Customers in the old feature table, data/raw/features_legacy.csv. A model still on it reaches only this many."""

import duckdb

KEY = "legacy_rows"


def value() -> int:
    return duckdb.sql("select count(*) from 'data/raw/features_legacy.csv'").fetchall()[0][0]

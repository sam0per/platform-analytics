"""Chapter 7: raw event rows in data/raw/events.csv, re-deliveries included."""

import duckdb

KEY = "events_total"


def value() -> int:
    return duckdb.sql("select count(*) from 'data/raw/events.csv'").fetchall()[0][0]

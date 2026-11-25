"""Smoke test before the warehouse export: raw files present, models built, cloud credentials in place.

uv run python scripts/smoke_test.py
"""

import os
import sys
from pathlib import Path

import duckdb

RAW = ["accounts.csv", "usage.csv", "features_v2.csv", "features_legacy.csv", "events.csv"]  # customers.csv: via stg_customers
MODELS = ["customer_activity", "customer_model_features", "daily_events", "stg_customers"]
CREDENTIALS = "~/.config/gcloud/application_default_credentials.json"  # the export signs in to the warehouse with these


def probe(path: str) -> str:
    # Opens and closes the file without reading a byte: a smoke test must never print a credential.
    try:
        os.close(os.open(os.path.expanduser(path), os.O_RDONLY))
    except FileNotFoundError:
        return "missing"
    except PermissionError:
        return "blocked"
    return "readable"


def main() -> int:
    missing = [f for f in RAW if not os.path.lexists(Path("data/raw") / f)]
    print("raw files:", f"missing {', '.join(missing)}" if missing else "ok")
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        empty = [m for m in MODELS if con.sql(f"select count(*) from {m}").fetchall()[0][0] == 0]
    print("models built:", f"empty {', '.join(empty)}" if empty else "ok")
    print(f"cloud credentials ({CREDENTIALS}):", probe(CREDENTIALS))
    return 1 if missing or empty else 0


if __name__ == "__main__":
    sys.exit(main())

"""customer_activity: planted chapter 6 defects and the fixed models on main.

Needs `uv run generate customer_activity` and `uv run dbt build` first.
"""

import hashlib
from pathlib import Path

import duckdb
import pandas as pd

from checks import accuracy_clean, accuracy_leaky, customers_out
from generate import customer_activity

RAW = Path("data/raw")


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / name, dtype={"customer_id": str})


def mart(sql: str):
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        return con.sql(sql).fetchall()


def test_ten_thousand_accounts():
    assert len(read("accounts.csv")) == 10_000


def test_270_padded_keys():
    ids = read("features_v2.csv")["customer_id"]
    assert len(ids) == 10_000
    assert (ids != ids.str.rstrip()).sum() == 270


def test_naive_join_drops_padded_keys_and_trimmed_join_keeps_all():
    accounts, features = read("accounts.csv"), read("features_v2.csv")
    assert customers_out.value() == 9_730
    features["customer_id"] = features["customer_id"].str.strip()
    assert len(accounts.merge(features, on="customer_id")) == 10_000


def test_customer_model_features_has_every_customer_and_no_leak():
    assert mart("select count(*), count(distinct customer_id) from customer_model_features") == [(10_000, 10_000)]
    columns = [c for (c,) in mart("select column_name from information_schema.columns where table_name = 'customer_model_features'")]
    assert "churned" in columns
    assert "exit_survey_sent" not in columns


def test_customer_activity_one_row_per_customer():
    assert mart("select count(*), count(distinct customer_id) from customer_activity") == [(10_000, 10_000)]


def test_five_roughly_balanced_regions():
    counts = [n for (_, n) in mart("select region, count(*) from customer_activity group by 1")]
    assert len(counts) == 5 and min(counts) > 1_800


def test_no_model_reads_features_legacy():
    assert not [p for p in Path("models").rglob("*") if p.is_file() and "features_legacy" in p.read_text()]


def test_accuracies_are_whole_and_clear_of_rounding_edges():
    clean = accuracy_clean.accuracy(accuracy_clean.features())
    leaky = accuracy_leaky.accuracy(accuracy_leaky.leaky_features())
    assert round(clean) == 71 and abs(clean - 71) <= 0.2
    assert round(leaky) == 97 and abs(leaky - 97) <= 0.2
    churn = read("accounts.csv")["churned"].mean()
    assert max(churn, 1 - churn) < 0.65  # majority baseline well below 71%


def test_generator_is_deterministic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    hashes = []
    for _ in range(2):
        customer_activity.main()
        hashes.append({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path("data/raw").iterdir())})
    assert hashes[0] == hashes[1]
    assert set(hashes[0]) == {"accounts.csv", "usage.csv", "features_v2.csv", "features_legacy.csv"}

import hashlib

import duckdb

from checks import event_drop
from generate import daily_events


def test_raw_has_200k_rows():
    assert duckdb.sql("select count(*) from 'data/raw/events.csv'").fetchall()[0][0] == 200_000


def test_current_rule_removes_redeliveries():
    rows, ids = duckdb.sql("select count(*), count(distinct event_id) from 'data/raw/events.csv'").fetchall()[0]
    assert ids < rows


def test_overall_drop_rounds_to_18():
    assert round(event_drop.drop_pct()) == 18


def test_every_day_drop_rounds_to_18():
    days = event_drop.by_day()
    assert len(days) == daily_events.DAYS
    assert all(round(100 * (c - p) / c) == 18 for _, c, p in days)


def test_generator_is_deterministic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data/raw").mkdir(parents=True)
    out = tmp_path / "data/raw/events.csv"
    hashes = []
    for _ in range(2):
        daily_events.main()
        hashes.append(hashlib.sha256(out.read_bytes()).hexdigest())
    assert hashes[0] == hashes[1]

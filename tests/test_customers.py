import csv
from functools import cache

import duckdb


# Not a fixture: pytest prints fixture values in tracebacks, which would leak names and emails.
@cache
def people() -> list[dict]:
    with open("data/raw/customers.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# Every assert compares plain ints or bools, so a failure never prints names or emails.
def test_exactly_2000_people():
    rows = people()
    n = len(rows)
    assert n == 2000


def test_ids_and_emails_unique():
    rows = people()
    n, ids, emails = len(rows), len({r["person_id"] for r in rows}), len({r["email"] for r in rows})
    assert ids == n
    assert emails == n


def test_emails_on_reserved_domain():
    rows = people()
    assert all(r["email"].endswith("@example.com") for r in rows)


def test_no_empty_names_or_birth_dates():
    rows = people()
    assert all(r["first_name"] and r["last_name"] and r["birth_date"] for r in rows)


def test_names_have_no_synthea_digits():
    rows = people()
    assert not any(c.isdigit() for r in rows for c in r["first_name"] + r["last_name"])


def test_stg_customers_has_no_personal_columns():
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        cols = {c for (c,) in con.execute(
            "select column_name from information_schema.columns where table_name = 'stg_customers'"
        ).fetchall()}
    assert cols == {"person_id", "birth_year", "state"}

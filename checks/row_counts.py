"""Row-count check: customers that reach customer_model_features, as built by dbt.

All 10,000 accounts must come out of the joins. A join that drops customers prints fewer and fails.
"""

import duckdb

KEY = "customers_in"


def value() -> int:
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        return con.sql("select count(*) from customer_model_features").fetchall()[0][0]

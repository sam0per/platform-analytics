"""Living people in the customers table, counted from stg_customers as built by dbt.

The count never opens data/raw/customers.csv, so it works under the deny rules and the sandbox.
"""

import duckdb

KEY = "people"


def value() -> int:
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        return con.sql("select count(*) from stg_customers").fetchall()[0][0]

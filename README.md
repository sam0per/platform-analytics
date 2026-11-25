# platform-analytics

This repo belongs to the data platform team at Halvarik, an invented company. All names and data are synthetic.

- `uv run generate [table]` writes seeded synthetic data to `data/raw/`.
- `uv run dbt build` builds the DuckDB models into `platform.duckdb`.
- `uv run pytest` runs the tests on the generated data.
- `uv run check <name|all>` prints a demo number and exits 2 if it differs from `demo_numbers.toml`.

# platform-analytics

- `uv run generate [table]` writes seeded synthetic data to `data/raw/`.
- `uv run dbt build` builds the DuckDB models into `platform.duckdb`.
- `uv run pytest` runs the tests on the generated data.
- `uv run check <name|all>` prints a demo number and exits 2 if it differs from `demo_numbers.toml`.

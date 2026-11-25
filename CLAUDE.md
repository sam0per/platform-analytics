# CLAUDE.md

Guidance for Claude Code and for humans working in the platform-analytics repo.
Maintained by the data platform team. Last reviewed: 2026-10-02.

## What this repo is

platform-analytics holds the data platform team's analytics models.
It turns raw CSV extracts into DuckDB tables with dbt, then runs checks on the results.
There are three marts: customer_activity (subscriptions), customers (people) and daily_events (alerts).

## Tech stack

- Python 3.12, managed with uv. Never use pip.
- dbt-duckdb for the models. DuckDB is the warehouse file, `platform.duckdb`.
- pandas and numpy for the generators.
- scikit-learn for the churn model check.

## Setup

1. Install uv.
2. Run `uv sync` to create `.venv`.
3. Run `uv run generate` to write the raw files to `data/raw/`.
4. Run `uv run dbt build` to build and test every model.

`make build` runs generate, dbt build and the checks in one go.

## Commands

- `uv run generate` writes every raw table. `uv run generate <table>` writes one.
- `uv run dbt build` builds all models and runs their tests.
- `uv run dbt build --select customer_activity` builds one model.
- `uv run pytest -q` runs the Python tests.
- `uv run check <name>` prints one number and exits 2 if it differs from `demo_numbers.toml`.
- `uv run check all` runs every check.

## Directory layout

- `generate/`: one seeded generator per mart. `cli.py` is the entry point.
- `models/`: dbt models, one folder per mart.
- `checks/`: one module per check, each with a `KEY` and a `value()` function.
- `tests/`: pytest tests on the generated data and the CLIs.
- `data/raw/`: generated CSV files. Gitignored.
- `vendor/`: the Synthea jar. Gitignored.

## How dbt works here

- dbt reads `dbt_project.yml` and `profiles.yml` from the repo root.
- Every model materializes as a table.
- Staging models (`stg_`) read one raw CSV each with `read_csv`.
- Intermediate models (`int_`) join or aggregate staging models.
- Mart models are the final tables other teams read.
- Tests live in each folder's `schema.yml`.
- dbt tests use the `data_tests:` key, not the old `tests:` key.
- `test-paths` points to `tests_dbt` so dbt ignores the pytest folder.

## customer_activity mart

Sources in `data/raw/`:

- `accounts.csv`: one row per customer with signup_date, plan_tier, region and churned.
- `usage.csv`: one row per customer per active day, with sessions and minutes.
- `features_v2.csv`: the current feature table, with monthly_fee, seats and support_tickets_90d.
- `features_legacy.csv` is the old feature table. The ops team's nightly scheduler loads it from outside this repo, so nothing here references it. The billing export still reads it. Do not delete, rename or reshape it.

Models:

- `stg_accounts`, `stg_usage` and `stg_features_v2` read one source each.
- `stg_features_v2` trims customer_id because some keys arrive with trailing spaces.
- `int_customer_usage` sums usage per customer over the 90-day window.
- `customer_activity` has one row per customer, with is_active.
- `customer_model_features` has one row per customer for the churn model.

Columns in `customer_activity`:

- customer_id, signup_date, plan_tier, region
- days_active_90d, days_active_last_30, minutes_90d, last_active_date
- is_active

- "Active customer" means used the product in the last 30 days. Product, Finance and Support agreed this in a meeting on 2026-09-14. The code follows this definition, not the other way round.
- Customer IDs come from the billing system and never change. A customer who cancels and comes back keeps the same ID.
- `customer_model_features` must not hold a column known only after the outcome. exit_survey_sent stays out for that reason.

## customers mart

- `customers.csv` comes from Synthea v4.0.0 and holds 2,000 living people.
- It holds names, emails and birth dates. Treat them as personal data.
- `stg_customers` keeps only patient_id, birth_year and state.
- The generator needs Homebrew openjdk@17. The system java is a stub.

## daily_events mart

- `events.csv` holds 200,000 alert events over 30 days.
- `stg_events` casts event_ts to a timestamp.
- `int_events_deduped` drops exact re-deliveries, rows with the same event_id.
- `daily_events` counts events per day and source.

## Checks

- Each check lives in `checks/<name>.py`.
- `value()` returns a whole number. `KEY` names its entry in `demo_numbers.toml`.
- `row_counts` counts customers in customer_model_features.
- `accuracy_clean` trains a logistic regression on customer_model_features.
- Never edit `demo_numbers.toml` to make a check pass. Those numbers are signed off, so a mismatch means the code is wrong.

## Code style

- SQL keywords in lower case.
- Four-space indentation in SQL and Python.
- Type hints on public Python functions.

## Git

- Branch from main.
- Write commit messages in the imperative mood.

## Before you finish

- A change to a model is done when `uv run dbt build && uv run check all` passes. Paste the output, not a summary.
- Ask the analytics lead before you change a metric that a dashboard shows.

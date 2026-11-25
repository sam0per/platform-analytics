# CLAUDE.md

Only what the code cannot tell you. Read the code and README for the rest.

## Facts from outside the repo

- `features_legacy.csv` is the old feature table. The ops team's nightly scheduler loads it from outside this repo, so nothing here references it. The billing export still reads it. Do not delete, rename or reshape it.
- "Active customer" means used the product in the last 30 days. Product, Finance and Support agreed this in a meeting on 2026-09-14. The code follows this definition, not the other way round.
- Customer IDs come from the billing system and never change. A customer who cancels and comes back keeps the same ID.

## Rules

- Never edit `demo_numbers.toml` to make a check pass. Those numbers are signed off, so a mismatch means the code is wrong.
- A change to a model is done when `uv run dbt build && uv run check all` passes. Paste the output, not a summary.
- Ask the analytics lead before you change a metric that a dashboard shows.

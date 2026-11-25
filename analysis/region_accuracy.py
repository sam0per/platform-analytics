"""Churn-model test accuracy for one customer region, with a bootstrap 95% interval and the sample size.

Usage: uv run python analysis/region_accuracy.py <region> [--quick]

The model and the split are the ones `uv run check accuracy_clean` uses (checks/accuracy_clean.py fit()).
One model trains on the 70% training split across all regions. Each region slices the 30% test set, using customer_activity.region.
The interval resamples that region's test customers 2,000 times with seed 42, so every run prints the same line.
--quick skips the bootstrap and prints the accuracy only, for a fast look.
Run `uv run dbt build` first.
"""

import sys

import duckdb
import numpy as np

from checks.accuracy_clean import features, fit

REGIONS = ["Eastholm", "Midmoor", "Northmere", "Southreach", "Westhollow"]
SEED = 42
RESAMPLES = 2000


def correct(region: str) -> np.ndarray:
    """1 for each test customer in the region the model got right, else 0."""
    df = features()
    model, X_test, y_test = fit(df)
    with duckdb.connect("platform.duckdb", read_only=True) as con:
        regions = dict(con.sql("select customer_id, region from customer_activity").fetchall())
    in_region = df.loc[X_test.index, "customer_id"].map(regions).eq(region).to_numpy()
    return (model.predict(X_test) == y_test.to_numpy())[in_region].astype(int)


def result(region: str, quick: bool = False) -> str:
    hits = correct(region)
    line = f"{region}: accuracy {round(100 * hits.mean())}%"
    if quick:
        return line
    resampled = np.random.default_rng(SEED).choice(hits, (RESAMPLES, len(hits))).mean(axis=1)
    lo, hi = np.percentile(100 * resampled, [2.5, 97.5])
    return f"{line} (95% CI {round(lo)}-{round(hi)}%), n={len(hits)}"


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in REGIONS or args[1:] not in ([], ["--quick"]):
        sys.exit(f"usage: region_accuracy.py [{'|'.join(REGIONS)}] [--quick]")
    print(result(args[0], quick=args[1:] == ["--quick"]))


if __name__ == "__main__":
    main()

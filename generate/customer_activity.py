"""Subscription data for the customer_activity mart: accounts, usage, features_v2, features_legacy.

features_v2 comes from another system's export:
- 270 of its customer_id values carry a trailing space.
- exit_survey_sent is set when the exit survey goes out, after a customer churns.
features_legacy is an older snapshot of the features.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N = 10_000
PADDED = 270
DAYS = 90
START = np.datetime64("2026-08-01")  # usage window: 2026-08-01 .. 2026-10-29
LEGACY_SNAPSHOT = np.datetime64("2026-03-31")
CHURN_RATE = 0.40  # majority-class baseline 60%
NOISE = 3.79  # churn-latent noise; tunes acc_clean
SURVEY_FLIP = 0.029  # exit-survey mislabel rate; tunes acc_leaky
OUT = Path("data/raw")

PLANS = np.array(["basic", "team", "enterprise"])
FEES = np.array([29, 99, 399])
REGIONS = np.array(["Northmere", "Eastholm", "Southreach", "Westhollow", "Midmoor"])


def _z(x: np.ndarray) -> np.ndarray:
    return (x - x.mean()) / x.std()


def _write(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False, lineterminator="\n")


def main() -> None:
    rng = np.random.default_rng(SEED)
    ids = np.array([f"C{i:05d}" for i in range(1, N + 1)])
    signup = START - rng.integers(1, 1200, N)
    tenure = (START - signup).astype(int)
    plan = rng.choice(3, N, p=[0.5, 0.35, 0.15])
    seats = np.select([plan == 0, plan == 1], [rng.integers(1, 4, N), rng.integers(3, 26, N)], rng.integers(20, 201, N))
    engagement = rng.beta(2, 3, N)  # chance of using the product on a given day
    tickets = rng.poisson(0.5 + 3 * (1 - engagement))

    latent = -1.0 * _z(engagement) + 0.5 * _z(tickets) - 0.4 * _z(np.log(tenure)) - 0.3 * plan + NOISE * rng.normal(size=N)
    churned = (latent > np.quantile(latent, 1 - CHURN_RATE)).astype(int)

    # Churners fade over the window; everyone else keeps their usual rate.
    fade = np.where(churned == 1, rng.uniform(0.3, 1.0, N), 1.0)
    rate = engagement[:, None] * (1 - (1 - fade[:, None]) * np.linspace(0, 1, DAYS)[None, :])
    cust, day = np.nonzero(rng.random((N, DAYS)) < rate)
    usage = pd.DataFrame(
        {
            "customer_id": ids[cust],
            "usage_date": (START + day).astype(str),
            "sessions": 1 + rng.poisson(1.5, cust.size),
            "minutes": np.round(rng.gamma(2.0, 15.0, cust.size)).astype(int) + 1,
        }
    )

    survey = churned ^ (rng.random(N) < SURVEY_FLIP)
    padded_ids = ids.astype(object)  # fixed-width <U6 would silently drop the added space
    padded_ids[rng.choice(N, PADDED, replace=False)] += " "

    region = REGIONS[np.random.default_rng([SEED, 8]).integers(0, len(REGIONS), N)]  # own stream: leaves every other value unchanged
    accounts = pd.DataFrame(
        {"customer_id": ids, "signup_date": signup.astype(str), "plan_tier": PLANS[plan], "region": region, "churned": churned}
    )
    features_v2 = pd.DataFrame(
        {
            "customer_id": padded_ids,
            "plan_tier": PLANS[plan],
            "monthly_fee": FEES[plan],
            "seats": seats,
            "support_tickets_90d": tickets,
            "exit_survey_sent": survey.astype(int),
        }
    )
    old = signup < LEGACY_SNAPSHOT
    features_legacy = pd.DataFrame(
        {
            "customer_id": ids[old],
            "plan_tier": PLANS[np.maximum(plan[old] - (rng.random(old.sum()) < 0.2), 0)],
            "seats": np.maximum(seats[old] - rng.integers(0, 5, old.sum()), 1),
            "support_tickets": rng.poisson(2.0, old.sum()),
            "snapshot_date": str(LEGACY_SNAPSHOT),
        }
    )

    OUT.mkdir(parents=True, exist_ok=True)
    _write(accounts, "accounts.csv")
    _write(usage, "usage.csv")
    _write(features_v2, "features_v2.csv")
    _write(features_legacy, "features_legacy.csv")

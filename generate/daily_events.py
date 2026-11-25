"""Event stream: data/raw/events.csv, 200,000 raw events over 30 days (numpy seed 7).

Repeats in the stream:
- re-deliveries: exact copies of a row, same event_id;
- bursts: new event_id, same source, event_type and device in the same minute.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 7
DAYS = 30
START = np.datetime64("2026-10-01T00:00:00")
DISTINCT = 190_000  # distinct event_ids
REDELIVERED = 10_000  # extra rows that repeat an event_id, so 200,000 raw rows
SOURCES = ["web-app", "mobile-app", "payments-api", "partner-feed"]
SEVERITIES = ["low", "medium", "high", "critical"]


def main() -> None:
    rng = np.random.default_rng(SEED)
    weekday = (np.arange(DAYS) + 3) % 7 < 5  # 2026-10-01 is a Thursday
    per_day = rng.multinomial(DISTINCT, np.where(weekday, 1.0, 0.8) / np.where(weekday, 1.0, 0.8).sum())
    burst_share = rng.uniform(0.178, 0.182, DAYS)  # per-day share of bursts among distinct events

    days, seconds, parent = [], [], []
    for d, (n, share) in enumerate(zip(per_day, burst_share)):
        bursts = round(n * share)
        base = n - bursts
        base_sec = rng.integers(0, 86_400, base)
        pick = rng.integers(0, base, bursts)  # each burst repeats one base event in its minute
        offset = sum(len(s) for s in seconds)
        days += [d] * n
        seconds += [base_sec, base_sec[pick] // 60 * 60 + rng.integers(0, 60, bursts)]
        parent += [np.arange(offset, offset + base), offset + pick]
    days, seconds = np.array(days), np.concatenate(seconds)
    parent = np.concatenate(parent)  # row index of the base event each row copies (itself for a base event)

    n = len(seconds)
    source = rng.choice(len(SOURCES), n, p=[0.35, 0.25, 0.3, 0.1])
    event_type = rng.integers(1000, 1040, n)
    device = rng.integers(1, 801, n)
    severity = rng.choice(len(SEVERITIES), n, p=[0.5, 0.3, 0.15, 0.05])
    source, event_type, device, severity = (a[parent] for a in (source, event_type, device, severity))

    ts = START + (days * 86_400 + seconds).astype("timedelta64[s]")
    order = np.lexsort((np.arange(n), ts))
    events = pd.DataFrame({
        "event_id": [f"evt-{i:06d}" for i in range(1, n + 1)],
        "event_ts": pd.Series(ts[order]).dt.strftime("%Y-%m-%d %H:%M:%S"),
        "source": np.array(SOURCES)[source[order]],
        "event_type": [f"type-{s}" for s in event_type[order]],
        "severity": np.array(SEVERITIES)[severity[order]],
        "device": [f"device-{e:04d}" for e in device[order]],
    })
    repeats = events.iloc[np.sort(rng.choice(n, REDELIVERED, replace=False))]
    events = pd.concat([events, repeats]).sort_values(["event_ts", "event_id"], kind="stable")
    events.to_csv(Path("data/raw/events.csv"), index=False, lineterminator="\n")

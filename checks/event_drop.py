"""% fewer event rows when the proposed duplicate rule replaces the current one."""

import duckdb

KEY = "event_drop_pct"

RAW = "select * from read_csv('data/raw/events.csv', types={'event_ts': 'TIMESTAMP'})"

# CURRENT rule (on main, same as models/daily_events/int_events_deduped.sql): drop exact re-deliveries.
CURRENT_RULE = """
select * from raw_events
qualify row_number() over (partition by event_id order by event_ts) = 1
"""

# PROPOSED rule: also collapse events that share
# source, event_type and device within the same minute.
PROPOSED_RULE = """
select * from current_rule
qualify row_number() over (
    partition by source, event_type, device, date_trunc('minute', event_ts)
    order by event_ts, event_id
) = 1
"""

BY_DAY = f"""
with raw_events as ({RAW}),
current_rule as ({CURRENT_RULE}),
proposed_rule as ({PROPOSED_RULE}),
cur as (select cast(event_ts as date) as day, count(*) as n from current_rule group by 1),
prop as (select cast(event_ts as date) as day, count(*) as n from proposed_rule group by 1)
select cur.day, cur.n as current_rows, prop.n as proposed_rows
from cur join prop using (day) order by cur.day
"""


def by_day() -> list[tuple]:
    """(day, current_rows, proposed_rows) per day, computed from the raw file."""
    return duckdb.connect().sql(BY_DAY).fetchall()


def drop_pct() -> float:
    rows = by_day()
    current, proposed = sum(r[1] for r in rows), sum(r[2] for r in rows)
    return 100 * (current - proposed) / current


def value() -> int:
    return round(drop_pct())

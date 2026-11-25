"""Compare daily_events in this tree with daily_events built from a base ref (default main).

Usage: uv run python scripts/compare_daily_events.py [BASE_REF]

Run `uv run dbt build` first. The script builds the base ref's daily_events in a temporary git worktree,
on the same data/raw files, then sums event_count per day over every source on both sides.
It prints the worst day's change as a whole number: % fewer rows than the base (negative means more).
It exits 1 when any day moves more than event_drop_limit_pct in demo_numbers.toml.
"""

import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import duckdb

PER_DAY = "select event_date, sum(event_count) from {db}.daily_events group by 1"


def build_base(ref: str, tmp: Path) -> Path:
    tree = tmp / "base"
    subprocess.run(["git", "worktree", "add", "--quiet", "--detach", str(tree), ref], check=True)
    (tree / "data").symlink_to(Path("data").resolve())
    subprocess.run(["dbt", "run", "--quiet", "--select", "+daily_events"], cwd=tree, check=True)
    return tree


def per_day_change(base_db: Path) -> list[tuple]:
    """(day, base_rows, rows, % fewer rows) per day, over the days either side has."""
    con = duckdb.connect()
    con.execute(f"attach '{base_db}' as base (read_only)")
    con.execute("attach 'platform.duckdb' as here (read_only)")
    rows = con.sql(f"""
        select coalesce(b.event_date, h.event_date), coalesce(b.n, 0), coalesce(h.n, 0)
        from ({PER_DAY.format(db='base')}) as b(event_date, n)
        full join ({PER_DAY.format(db='here')}) as h(event_date, n) using (event_date)
        order by 1
    """).fetchall()
    con.close()
    return [(day, b, h, 100 * (b - h) / b if b else -100.0) for day, b, h in rows]


def main() -> None:
    ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    limit = tomllib.loads(Path("demo_numbers.toml").read_text())["event_drop_limit_pct"]
    with tempfile.TemporaryDirectory() as tmp:
        try:
            tree = build_base(ref, Path(tmp))
            days = per_day_change(tree / "platform.duckdb")
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(Path(tmp) / "base")], capture_output=True)
    day, _, _, pct = max(days, key=lambda d: abs(d[3]))
    print(round(pct))
    if abs(pct) > limit:
        sys.exit(f"daily_events: {round(pct)}% fewer rows on {day} than on {ref}; the limit is {limit}% per day")


if __name__ == "__main__":
    main()

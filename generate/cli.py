"""uv run generate [table]: run generate/<table>.py main(), or all of them in sorted order."""

import importlib
import pkgutil
import sys
from pathlib import Path

import generate


def tables() -> list[str]:
    return sorted(m.name for m in pkgutil.iter_modules(generate.__path__) if m.name != "cli")


def run(table: str) -> None:
    importlib.import_module(f"generate.{table}").main()


def main() -> None:
    args = sys.argv[1:]
    known = tables()
    if len(args) > 1 or (args and args[0] not in known):
        sys.exit(f"usage: generate [{'|'.join(known)}]")
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    for table in args or known:
        run(table)

"""uv run check <name|all>: compare checks/<name>.py value() with demo_numbers.toml[KEY]."""

import importlib
import pkgutil
import sys
import tomllib
from pathlib import Path

import checks

FAIL = 2


def names() -> list[str]:
    return sorted(m.name for m in pkgutil.iter_modules(checks.__path__) if m.name != "cli")


def expected() -> dict:
    return tomllib.loads(Path("demo_numbers.toml").read_text())


def run(name: str, numbers: dict) -> tuple[object, bool]:
    mod = importlib.import_module(f"checks.{name}")
    value = mod.value()
    return value, value == numbers[mod.KEY]


def main() -> None:
    args = sys.argv[1:]
    known = names()
    if len(args) != 1 or args[0] not in [*known, "all"]:
        sys.exit(f"usage: check [{'|'.join([*known, 'all'])}]")
    numbers = expected()
    if args[0] != "all":
        value, ok = run(args[0], numbers)
        print(value)
        sys.exit(0 if ok else FAIL)
    failed = False
    for name in known:
        value, ok = run(name, numbers)
        print(name, value)
        failed |= not ok
    sys.exit(FAIL if failed else 0)

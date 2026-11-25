import tomllib
from pathlib import Path

KEYS = {"customers_in", "customers_out", "acc_clean", "acc_leaky", "event_drop_pct", "people", "events_total"}


def test_demo_numbers_has_the_seven_keys():
    numbers = tomllib.loads(Path("demo_numbers.toml").read_text())
    assert set(numbers) == KEYS
    assert all(isinstance(v, int) for v in numbers.values())


def test_clis_import():
    from checks import cli as check_cli
    from generate import cli as generate_cli

    assert callable(check_cli.main) and callable(generate_cli.main)

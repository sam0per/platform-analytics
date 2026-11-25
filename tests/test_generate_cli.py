import pytest

from generate import cli


def test_missing_synthea_jar_fails_customers_but_writes_events(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no vendor/ jar and no customers.csv here
    monkeypatch.setattr("sys.argv", ["generate"])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code == "generate: failed tables: customers"
    assert (tmp_path / "data/raw/events.csv").exists()
    assert (tmp_path / "data/raw/accounts.csv").exists()

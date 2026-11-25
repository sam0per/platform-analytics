import tomllib
from pathlib import Path

import pytest

from analysis import region_accuracy


@pytest.mark.parametrize("region", region_accuracy.REGIONS)
def test_region_line_matches_demo_numbers(region):
    n = tomllib.loads(Path("demo_numbers.toml").read_text())
    key = region.lower()
    want = f"{region}: accuracy {n[key + '_acc']}% (95% CI {n[key + '_ci_lo']}-{n[key + '_ci_hi']}%), n={n[key + '_n']}"
    assert region_accuracy.result(region) == want
    assert region_accuracy.result(region, quick=True) == f"{region}: accuracy {n[key + '_acc']}%"


def test_regions_cover_every_test_customer():
    assert sum(len(region_accuracy.correct(r)) for r in region_accuracy.REGIONS) == 3000

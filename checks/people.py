import csv

KEY = "people"


def value() -> int:
    with open("data/raw/customers.csv", newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))

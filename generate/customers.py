"""Raw customers table: 2,000 living people from Synthea, written to data/raw/customers.csv.

Personal-records flavour. Names, emails and birth dates are synthetic but look personal.
"""

import csv
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

JAR = Path("vendor/synthea-with-dependencies.jar")
JAR_SHA256 = "ed43c20ad40ba5c3bc724503a5af032715fe3c491620b766148e7c2361e6ecc1"  # Synthea v4.0.0
OUT = Path("data/raw/customers.csv")
PEOPLE = 2000
COLUMNS = ["person_id", "first_name", "last_name", "email", "birth_date", "city", "state"]


def java() -> str:
    try:
        prefix = subprocess.run(["brew", "--prefix", "openjdk@17"], capture_output=True, text=True, check=True).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("customers: needs Homebrew openjdk@17 (brew install openjdk@17); the system java is a stub")
    path = Path(prefix) / "bin" / "java"
    if not path.exists():
        sys.exit(f"customers: {path} not found; run brew install openjdk@17")
    return str(path)


def verify_jar() -> None:
    if not JAR.exists():
        sys.exit(f"customers: {JAR} missing; download Synthea v4.0.0 synthea-with-dependencies.jar there")
    digest = hashlib.sha256(JAR.read_bytes()).hexdigest()
    if digest != JAR_SHA256:
        sys.exit(f"customers: {JAR} sha256 is {digest}, expected {JAR_SHA256}")


def synthea_people(tmp: Path) -> list[dict]:
    cmd = [
        java(), "-jar", str(JAR.resolve()),
        # -e pins the simulation end date; Synthea defaults it to today, so output would drift.
        "-s", "42", "-cs", "42", "-r", "20260101", "-e", "20261127", "-p", str(PEOPLE),
        f"--exporter.baseDirectory={tmp}",
        "--exporter.csv.export=true",
        "--exporter.csv.included_files=patients.csv",
        "--exporter.fhir.export=false",
        "--exporter.hospital.fhir.export=false",
        "--exporter.practitioner.fhir.export=false",
    ]
    subprocess.run(cmd, cwd=tmp, check=True, stdout=subprocess.DEVNULL)
    with open(tmp / "csv" / "patients.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(name: str) -> str:
    return re.sub(r"\d", "", name)  # Synthea appends digits to every name


def email_stem(first: str, last: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", f"{first}.{last}").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z.]", "", ascii_name.lower())


def rows(people: list[dict]) -> list[list[str]]:
    living = sorted((p for p in people if not p["DEATHDATE"]), key=lambda p: p["Id"])  # thread order is not stable
    if len(living) != PEOPLE:
        sys.exit(f"customers: Synthea gave {len(living)} living people, expected {PEOPLE}")
    seen: dict[str, int] = {}
    out = []
    for i, p in enumerate(living, start=1):
        first, last = clean(p["FIRST"]), clean(p["LAST"])
        stem = email_stem(first, last)
        seen[stem] = seen.get(stem, 0) + 1
        suffix = "" if seen[stem] == 1 else str(seen[stem])
        out.append([f"PER-{i:04d}", first, last, f"{stem}{suffix}@example.com", p["BIRTHDATE"], p["CITY"], p["STATE"]])
    return out


def main() -> None:
    # shortcut: reuses an existing customers.csv because Synthea takes ~30 s, delete the file after changing this generator
    if OUT.exists():
        print(f"customers: {OUT} exists, skipping Synthea (delete it to rebuild)")
        return
    verify_jar()
    with tempfile.TemporaryDirectory() as tmp:
        data = rows(synthea_people(Path(tmp)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    partial = OUT.with_suffix(".csv.tmp")
    with open(partial, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(data)
    shutil.move(partial, OUT)  # a crash mid-write must not leave a file the shortcut would trust
    print(f"customers: wrote {len(data)} rows to {OUT}")

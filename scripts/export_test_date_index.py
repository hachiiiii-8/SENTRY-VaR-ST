"""Expand the released compressed test-date index into a local CSV file."""
from __future__ import annotations

import gzip
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "test_date_index.csv.gz"
DESTINATION = ROOT / "data" / "test_date_index.csv"

with gzip.open(SOURCE, "rb") as source, DESTINATION.open("wb") as destination:
    shutil.copyfileobj(source, destination)

print(f"Wrote {DESTINATION.relative_to(ROOT)}")

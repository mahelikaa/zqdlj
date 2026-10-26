"""Load the January 2026 snapshot produced by scripts/fetch_data.py."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# Cached so each CSV is read once per process. Callers must not modify the returned frames.
@lru_cache
def load_actuals() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "actuals.csv", parse_dates=["startTime"])


@lru_cache
def load_forecasts() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "forecasts.csv", parse_dates=["startTime", "publishTime"])

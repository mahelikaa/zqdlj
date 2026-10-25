"""Download January 2026 wind actuals and forecasts from Elexon BMRS into CSV snapshots."""

from pathlib import Path

import httpx
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TARGET_START = pd.Timestamp("2026-01-01T00:00:00Z")
TARGET_END = pd.Timestamp("2026-01-31T23:30:00Z")
MAX_HORIZON = pd.Timedelta(hours=48)


def fetch_actuals(client: httpx.Client) -> pd.DataFrame:
    """Fetch half-hourly actual wind generation for January 2026."""

    response = client.get(
        f"{BASE_URL}/FUELHH/stream",
        params={
            "settlementDateFrom": "2026-01-01",
            "settlementDateTo": "2026-01-31",
            "fuelType": "WIND",
        },
    )
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    df = df[["startTime", "generation"]].copy()
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)

    df = df[df["startTime"].between(TARGET_START, TARGET_END)]

    return df.sort_values("startTime").reset_index(drop=True)


def fetch_forecasts(client: httpx.Client) -> pd.DataFrame:
    """Fetch wind forecasts targeting January 2026."""

    response = client.get(
        f"{BASE_URL}/WINDFOR/stream",
        params={
            "publishDateTimeFrom": (TARGET_START - MAX_HORIZON).isoformat(),
            "publishDateTimeTo": TARGET_END.isoformat(),
        },
    )
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    df = df[["startTime", "publishTime", "generation"]].copy()

    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)

    df = df[df["startTime"].between(TARGET_START, TARGET_END)]

    return df.sort_values(
        ["startTime", "publishTime"]
    ).reset_index(drop=True)


def main() -> None:
    """Download data and save CSV snapshots."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=60) as client:
        actuals = fetch_actuals(client)
        forecasts = fetch_forecasts(client)

    actuals.to_csv(DATA_DIR / "actuals.csv", index=False)
    forecasts.to_csv(DATA_DIR / "forecasts.csv", index=False)

    print(
        f"Saved {len(actuals)} actuals and "
        f"{len(forecasts)} forecasts to {DATA_DIR}"
    )


if __name__ == "__main__":
    main()
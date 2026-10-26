"""HTTP API for the wind forecast monitor."""

from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.analysis import MAX_HORIZON_HOURS, accuracy_by_horizon, compare, compute_metrics
from app.data import load_actuals, load_forecasts

app = FastAPI(title="Wind Forecast Monitor API")

# Read-only public data, so any origin may call it (the frontend is deployed separately).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])


def to_utc(value: datetime) -> pd.Timestamp:
    """Treat timestamps without a timezone as UTC."""
    ts = pd.Timestamp(value)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def window(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return df[df["startTime"].between(start, end)]


def to_records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> JSON-friendly list of dicts, with timestamps as ISO 8601 strings."""
    out = df.copy()
    for col in out.select_dtypes(include="datetime").columns:
        out[col] = out[col].map(lambda t: t.isoformat())
    return out.to_dict(orient="records")


def parse_window(start: datetime, end: datetime) -> tuple[pd.Timestamp, pd.Timestamp]:
    start_ts, end_ts = to_utc(start), to_utc(end)
    if start_ts >= end_ts:
        raise HTTPException(status_code=400, detail="start must be before end")
    return start_ts, end_ts


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/comparison")
def comparison(
    start: datetime,
    end: datetime,
    horizon: float = Query(24, ge=0, le=MAX_HORIZON_HOURS),
) -> dict:
    """Actuals, the forecasts available `horizon` hours ahead, and their error metrics."""
    start_ts, end_ts = parse_window(start, end)
    actuals = window(load_actuals(), start_ts, end_ts)
    compared = compare(actuals, load_forecasts(), horizon)
    return {
        "actuals": to_records(actuals),
        "forecasts": to_records(compared[["startTime", "publishTime", "forecast", "error"]]),
        "metrics": compute_metrics(compared["error"]),
    }


@app.get("/api/accuracy-by-horizon")
def accuracy(start: datetime, end: datetime) -> dict:
    """MAE / RMSE / P90 for every whole-hour horizon from 0 to MAX_HORIZON_HOURS."""
    start_ts, end_ts = parse_window(start, end)
    actuals = window(load_actuals(), start_ts, end_ts)
    horizons = list(range(0, MAX_HORIZON_HOURS + 1))
    return {"horizons": accuracy_by_horizon(actuals, load_forecasts(), horizons)}

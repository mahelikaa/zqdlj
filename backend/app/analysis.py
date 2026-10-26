"""Core analysis: pick the forecast available at decision time and measure its error."""

import numpy as np
import pandas as pd

# Largest horizon the API accepts.
MAX_HORIZON_HOURS = 48


def select_forecasts(forecasts: pd.DataFrame, horizon_hours: float) -> pd.DataFrame:
    """For each target time, select the latest forecast published at least
    `horizon_hours` before it.

    Returns one row per startTime with columns:
    startTime, publishTime, generation.
    """
    if not 0 <= horizon_hours <= MAX_HORIZON_HOURS:
        raise ValueError(f"horizon_hours must be between 0 and {MAX_HORIZON_HOURS}")

    horizon = forecasts["startTime"] - forecasts["publishTime"]

    eligible = forecasts[
        horizon >= pd.Timedelta(hours=horizon_hours)
    ].copy()

    selected = (
        eligible
        .sort_values("publishTime")
        .drop_duplicates(subset="startTime", keep="last")
    )

    return (
        selected[["startTime", "publishTime", "generation"]]
        .sort_values("startTime")
        .reset_index(drop=True)
    )


def compute_metrics(errors: pd.Series) -> dict:
    """Summary statistics for forecast errors (forecast - actual, in MW).

    Returns: count, mae, rmse, bias, p90_abs_error.
    With no errors, count is 0 and every other value is None.
    """
    if errors.empty:
        return {
            "count": 0,
            "mae": None,
            "rmse": None,
            "bias": None,
            "p90_abs_error": None,
        }

    return {
        "count": len(errors),
        "mae": float(errors.abs().mean()),
        "rmse": float(np.sqrt((errors ** 2).mean())),
        "bias": float(errors.mean()),
        "p90_abs_error": float(np.percentile(errors.abs(), 90)),
    }


def compare(
    actuals: pd.DataFrame,
    forecasts: pd.DataFrame,
    horizon_hours: float,
) -> pd.DataFrame:
    """Select forecasts and join them to actuals on target time.

    Returns columns: startTime, publishTime, forecast, actual, error.
    """
    selected = select_forecasts(forecasts, horizon_hours).rename(
        columns={"generation": "forecast"}
    )

    merged = selected.merge(
        actuals.rename(columns={"generation": "actual"}),
        on="startTime",
    )

    merged["error"] = merged["forecast"] - merged["actual"]

    return merged


def accuracy_by_horizon(
    actuals: pd.DataFrame,
    forecasts: pd.DataFrame,
    horizons: list[float],
) -> list[dict]:
    """Calculate error metrics for each forecast horizon, over the same target hours.

    Forecast runs don't always reach the longest horizons, so some hours have no forecast
    there. Only hours with a forecast at every horizon are used, so horizons are compared
    like for like.
    """
    compared = {h: compare(actuals, forecasts, h) for h in horizons}
    common = set.intersection(*(set(c["startTime"]) for c in compared.values()))

    return [
        {
            "horizon": h,
            **compute_metrics(c.loc[c["startTime"].isin(common), "error"]),
        }
        for h, c in compared.items()
    ]
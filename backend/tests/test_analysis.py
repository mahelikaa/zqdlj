import math

import pandas as pd
import pytest

from app.analysis import accuracy_by_horizon, compare, compute_metrics, select_forecasts

T = pd.Timestamp("2026-01-10T12:00:00Z")


def forecasts_for_target(rows: list[tuple[float, int]], target: pd.Timestamp = T) -> pd.DataFrame:
    """Build forecasts for one target time from (hours_ahead, generation) pairs."""
    return pd.DataFrame(
        {
            "startTime": [target] * len(rows),
            "publishTime": [target - pd.Timedelta(hours=h) for h, _ in rows],
            "generation": [g for _, g in rows],
        }
    )


# Real values for target 10 Jan 12:00 (see the Phase 1 table), plus one row published after the fact.
REAL_EXAMPLE = forecasts_for_target([(57.5, 7804), (41.5, 8492), (24.5, 8949), (13.5, 7824), (-2.0, 7777)])


@pytest.mark.parametrize(
    ("horizon", "expected"),
    [(40, 8492), (24, 8949), (13.5, 7824), (0, 7824)],
)
def test_picks_latest_forecast_published_before_cutoff(horizon, expected):
    selected = select_forecasts(REAL_EXAMPLE, horizon)
    assert len(selected) == 1
    assert selected.loc[0, "generation"] == expected


def test_ignores_forecasts_published_after_target_time():
    selected = select_forecasts(forecasts_for_target([(-2.0, 7777)]), 0)
    assert selected.empty


def test_no_forecast_when_none_published_early_enough():
    selected = select_forecasts(forecasts_for_target([(13.5, 7824)]), 24)
    assert selected.empty


def test_returns_one_row_per_target_sorted():
    later = T + pd.Timedelta(hours=1)
    forecasts = pd.concat(
        [forecasts_for_target([(30, 100), (20, 200)], later), forecasts_for_target([(30, 300), (20, 400)])]
    )
    selected = select_forecasts(forecasts, 10)
    assert list(selected["startTime"]) == [T, later]
    assert list(selected["generation"]) == [400, 200]
    assert list(selected.columns) == ["startTime", "publishTime", "generation"]


def test_metrics_known_values():
    metrics = compute_metrics(pd.Series([1000, -1000, 200, -200]))
    assert metrics["count"] == 4
    assert metrics["mae"] == pytest.approx(600)
    assert metrics["bias"] == pytest.approx(0)
    assert metrics["rmse"] == pytest.approx(math.sqrt(520_000))
    assert metrics["p90_abs_error"] == pytest.approx(1000)


def test_metrics_empty():
    metrics = compute_metrics(pd.Series([], dtype=float))
    assert metrics == {"count": 0, "mae": None, "rmse": None, "bias": None, "p90_abs_error": None}


def test_compare_joins_on_hour_and_computes_error():
    actuals = pd.DataFrame(
        {"startTime": [T, T + pd.Timedelta(minutes=30)], "generation": [7777, 7700]}
    )
    compared = compare(actuals, REAL_EXAMPLE, 40)
    assert len(compared) == 1  # the half-hour actual has no forecast
    assert compared.loc[0, "error"] == 8492 - 7777


def test_accuracy_by_horizon_uses_hours_available_at_every_horizon():
    later = T + pd.Timedelta(hours=1)
    forecasts = pd.concat(
        [forecasts_for_target([(30, 1100), (10, 1050)]), forecasts_for_target([(10, 2000)], later)]
    )
    actuals = pd.DataFrame({"startTime": [T, later], "generation": [1000, 1000]})
    rows = accuracy_by_horizon(actuals, forecasts, [0, 20])
    # `later` has no forecast 20h ahead, so it is left out at 0h too.
    assert [row["count"] for row in rows] == [1, 1]
    assert [row["bias"] for row in rows] == [pytest.approx(50), pytest.approx(100)]

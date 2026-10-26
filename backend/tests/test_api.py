from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
JAN_10 = {"start": "2026-01-10T00:00:00Z", "end": "2026-01-10T23:30:00Z"}


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_comparison_returns_series_and_metrics():
    body = client.get("/api/comparison", params={**JAN_10, "horizon": 24}).json()
    assert len(body["actuals"]) == 48  # one day of half-hours
    assert 0 < len(body["forecasts"]) <= 24  # hourly
    assert body["metrics"]["count"] == len(body["forecasts"])


def test_naive_timestamps_are_treated_as_utc():
    naive = {"start": "2026-01-10T00:00:00", "end": "2026-01-10T23:30:00"}
    assert client.get("/api/comparison", params=naive).json() == client.get("/api/comparison", params=JAN_10).json()


def test_rejects_horizon_out_of_range():
    assert client.get("/api/comparison", params={**JAN_10, "horizon": 60}).status_code == 422


def test_rejects_start_after_end():
    params = {"start": JAN_10["end"], "end": JAN_10["start"]}
    assert client.get("/api/comparison", params=params).status_code == 400


def test_accuracy_by_horizon_covers_0_to_48():
    body = client.get("/api/accuracy-by-horizon", params=JAN_10).json()
    assert [row["horizon"] for row in body["horizons"]] == list(range(49))

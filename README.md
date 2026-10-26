# Wind Forecast Monitor

Compares GB national wind generation forecasts with actual generation for January 2026, so a day-ahead power buyer can see the forecast they would have had at decision time and how far off it typically is.

**Live app:** https://wind-forecast-monitor-mu.vercel.app (API: https://wind-forecast-monitor-api.vercel.app/docs) · **Data:** Elexon BMRS [FUELHH](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream) (actuals, `fuelType=WIND`) and [WINDFOR](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream) (forecasts)

## How it works

- **Horizon rule:** for each target hour T and a chosen horizon H (0–48h), use the latest forecast published at or before T − H. Forecasts published after their target hour are never used.
- **Accuracy:** error = forecast − actual, summarised as MAE, RMSE, bias and P90 absolute error, plus MAE/P90 for every horizon from 0 to 48h.
- **Scope:** target times 1 Jan 2026 00:00 – 31 Jan 2026 23:30 UTC (UK time in January). The data is a snapshot fetched once, since it is historical.

## Files and directories

```
backend/                  Python 3.12, FastAPI, pandas
  scripts/fetch_data.py   Downloads the January 2026 snapshot from Elexon
  data/                   actuals.csv, forecasts.csv (the snapshot)
  app/data.py             Loads the CSVs once (cached)
  app/analysis.py         Forecast selection, actual/forecast join, error metrics
  app/main.py             API: /api/comparison, /api/accuracy-by-horizon, /api/health
  tests/                  pytest unit and API tests
  Dockerfile
frontend/                 React, TypeScript, Vite, Recharts
  src/App.tsx             State and data fetching
  src/components/         Controls, metric cards, forecast chart, horizon chart
  src/api.ts              Typed API client
  Dockerfile, nginx.conf  Static build served by nginx, /api proxied to the backend
docker-compose.yml        Runs backend and frontend together
```

## Running it

**Docker** (requires Docker):

```bash
docker compose up --build
```

Open http://localhost:8080.

**Without Docker** (requires [uv](https://docs.astral.sh/uv/) and Node 20+):

```bash
cd backend && uv sync && uv run uvicorn app.main:app --port 8000
cd frontend && npm ci && npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to the backend.

**Tests:** `cd backend && uv run pytest`

**Refresh the data snapshot:** `cd backend && uv run python scripts/fetch_data.py`

**Deployment:** two Vercel projects from this repo, `backend/` (Python function) and `frontend/` (static site, with `VITE_API_URL` set to the backend URL).

## AI tools

Built with the help of Claude Code (Anthropic). I wrote the data fetch script and the core forecast selection and metrics functions, with Claude guiding and reviewing. Claude wrote the frontend, the Docker setup, the API layer and the tests, and helped draft this README. I reviewed and understand all of the code.

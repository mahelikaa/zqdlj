// Types mirror the JSON returned by the FastAPI backend (backend/app/main.py).

export type Metrics = {
  count: number
  mae: number | null
  rmse: number | null
  bias: number | null
  p90_abs_error: number | null
}

export type ActualPoint = { startTime: string; generation: number }

export type ForecastPoint = {
  startTime: string
  publishTime: string
  forecast: number
  error: number
}

export type Comparison = {
  actuals: ActualPoint[]
  forecasts: ForecastPoint[]
  metrics: Metrics
}

export type HorizonMetrics = Metrics & { horizon: number }

// Empty in development (Vite proxies /api); the backend URL when deployed separately.
const API_URL = import.meta.env.VITE_API_URL ?? ''

async function getJson<T>(path: string, params: Record<string, string>, signal: AbortSignal): Promise<T> {
  const response = await fetch(`${API_URL}${path}?${new URLSearchParams(params)}`, { signal })
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`)
  }
  return response.json()
}

export function fetchComparison(start: string, end: string, horizon: number, signal: AbortSignal) {
  return getJson<Comparison>('/api/comparison', { start, end, horizon: String(horizon) }, signal)
}

export async function fetchAccuracyByHorizon(start: string, end: string, signal: AbortSignal) {
  const body = await getJson<{ horizons: HorizonMetrics[] }>('/api/accuracy-by-horizon', { start, end }, signal)
  return body.horizons
}

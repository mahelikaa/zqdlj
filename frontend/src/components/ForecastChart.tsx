import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Comparison } from '../api'
import { formatDateTime, formatDay, formatMW } from '../format'

type Point = {
  time: number
  actual?: number
  forecast?: number
  error?: number
  publishTime?: string
}

// Actuals are half-hourly and forecasts hourly, so merge both into one list keyed by time.
// Half-hour points simply have no forecast.
function toPoints({ actuals, forecasts }: Comparison): Point[] {
  const byTime = new Map<number, Point>()
  for (const a of actuals) {
    const time = Date.parse(a.startTime)
    byTime.set(time, { time, actual: a.generation })
  }
  for (const f of forecasts) {
    const time = Date.parse(f.startTime)
    byTime.set(time, { ...byTime.get(time), time, forecast: f.forecast, error: f.error, publishTime: f.publishTime })
  }
  return [...byTime.values()].sort((a, b) => a.time - b.time)
}

const DAY_MS = 24 * 60 * 60 * 1000
const GW_STEP = 5000

// One x-axis tick per midnight in the range.
function dayTicks(points: Point[]): number[] {
  if (points.length === 0) return []
  const first = Math.ceil(points[0].time / DAY_MS) * DAY_MS
  const last = points[points.length - 1].time
  const ticks = []
  for (let t = first; t <= last; t += DAY_MS) ticks.push(t)
  return ticks
}

export function ForecastChart({ data }: { data: Comparison }) {
  const points = toPoints(data)

  return (
    <ResponsiveContainer width="100%" height={380}>
      <LineChart data={points} margin={{ top: 8, right: 16, bottom: 8, left: 16 }}>
        <CartesianGrid stroke="var(--grid)" vertical={false} />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={['dataMin', 'dataMax']}
          ticks={dayTicks(points)}
          tickFormatter={formatDay}
          minTickGap={24}
        />
        <YAxis
          domain={[0, (max: number) => Math.ceil(max / GW_STEP) * GW_STEP]}
          tickCount={6}
          tickFormatter={(v: number) => `${v / 1000} GW`}
          width={56}
        />
        <Tooltip content={<PointTooltip />} />
        <Legend />
        <Line name="Actual" dataKey="actual" stroke="var(--actual)" dot={false} strokeWidth={2} connectNulls />
        <Line name="Forecast" dataKey="forecast" stroke="var(--forecast)" dot={false} strokeWidth={2} connectNulls />
      </LineChart>
    </ResponsiveContainer>
  )
}

type TooltipProps = { active?: boolean; payload?: { payload: Point }[] }

function PointTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null
  const p = payload[0].payload
  return (
    <div className="tooltip">
      <strong>{formatDateTime(p.time)}</strong>
      <div>Actual: {formatMW(p.actual ?? null)}</div>
      {p.forecast !== undefined && (
        <>
          <div>Forecast: {formatMW(p.forecast)}</div>
          <div>Error: {formatMW(p.error ?? null, true)}</div>
          <div className="muted">Forecast made {formatDateTime(p.publishTime!)}</div>
        </>
      )}
    </div>
  )
}

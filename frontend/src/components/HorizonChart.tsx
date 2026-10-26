import { CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { HorizonMetrics } from '../api'
import { formatMW } from '../format'

type Props = {
  rows: HorizonMetrics[]
  horizon: number
  onSelectHorizon: (horizon: number) => void
}

export function HorizonChart({ rows, horizon, onSelectHorizon }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={rows}
        margin={{ top: 8, right: 16, bottom: 8, left: 16 }}
        // Clicking a point on the chart moves the horizon slider there.
        onClick={(state) => {
          const row = rows[Number(state?.activeIndex)]
          if (row) onSelectHorizon(row.horizon)
        }}
        style={{ cursor: 'pointer', outline: 'none' }}
      >
        <CartesianGrid stroke="var(--grid)" vertical={false} />
        <XAxis dataKey="horizon" tickFormatter={(h: number) => `${h}h`} interval={5} />
        <YAxis tickFormatter={(v: number) => `${(v / 1000).toFixed(1)} GW`} width={64} />
        <Tooltip
          labelFormatter={(h) => `Forecast made ${h}h ahead`}
          formatter={(value) => formatMW(typeof value === 'number' ? value : null)}
        />
        <Legend />
        <ReferenceLine x={horizon} stroke="var(--muted)" strokeDasharray="4 4" />
        <Line name="Average miss (MAE)" dataKey="mae" stroke="var(--actual)" dot={false} strokeWidth={2} />
        <Line name="P90 miss" dataKey="p90_abs_error" stroke="var(--p90)" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}

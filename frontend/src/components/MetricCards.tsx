import type { Metrics } from '../api'
import { formatMW } from '../format'

type Props = { metrics: Metrics; horizon: number }

export function MetricCards({ metrics, horizon }: Props) {
  const { count, mae, rmse, bias, p90_abs_error } = metrics

  if (count === 0) {
    return <p className="notice">No forecasts were published {horizon}h or more ahead for this period.</p>
  }

  const direction = bias !== null && bias > 0 ? 'too high' : 'too low'

  return (
    <section>
      <div className="cards">
        <Card label="Average miss (MAE)" value={formatMW(mae)} hint="Typical size of the error" />
        <Card label="RMSE" value={formatMW(rmse)} hint="Weights large misses more" />
        <Card label="Bias" value={formatMW(bias, true)} hint={`On average the forecast was ${direction}`} />
        <Card label="P90 miss" value={formatMW(p90_abs_error)} hint="9 hours in 10 the miss was smaller" />
        <Card label="Hours compared" value={count.toLocaleString('en-GB')} hint="Hourly forecast vs actual pairs" />
      </div>
      <p className="insight">
        Deciding <strong>{horizon}h</strong> ahead, the wind forecast missed by <strong>{formatMW(mae)}</strong> on
        average and ran <strong>{formatMW(Math.abs(bias ?? 0))} {direction}</strong>. A buffer of{' '}
        <strong>{formatMW(p90_abs_error)}</strong> would have covered the miss in 9 hours out of 10.
      </p>
    </section>
  )
}

function Card({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="card">
      <div className="card-label">{label}</div>
      <div className="card-value">{value}</div>
      <div className="card-hint">{hint}</div>
    </div>
  )
}

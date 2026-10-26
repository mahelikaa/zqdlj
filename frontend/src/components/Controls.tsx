type Props = {
  startDate: string
  endDate: string
  horizon: number
  onStartDateChange: (value: string) => void
  onEndDateChange: (value: string) => void
  onHorizonChange: (value: number) => void
}

// The snapshot covers target times in January 2026 only.
const MIN_DATE = '2026-01-01'
const MAX_DATE = '2026-01-31'

export function Controls({
  startDate,
  endDate,
  horizon,
  onStartDateChange,
  onEndDateChange,
  onHorizonChange,
}: Props) {
  return (
    <section className="controls">
      <label>
        From
        <input
          type="date"
          value={startDate}
          min={MIN_DATE}
          max={endDate}
          onChange={(e) => onStartDateChange(e.target.value)}
        />
      </label>
      <label>
        To
        <input
          type="date"
          value={endDate}
          min={startDate}
          max={MAX_DATE}
          onChange={(e) => onEndDateChange(e.target.value)}
        />
      </label>
      <label className="horizon">
        <span>
          Forecast horizon: <strong>{horizon}h</strong>
          <small> — use the latest forecast made at least {horizon}h before each hour</small>
        </span>
        <input
          type="range"
          min={0}
          max={48}
          step={1}
          value={horizon}
          onChange={(e) => onHorizonChange(Number(e.target.value))}
        />
      </label>
    </section>
  )
}

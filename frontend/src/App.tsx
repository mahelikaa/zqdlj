import { useEffect, useState } from 'react'
import { fetchAccuracyByHorizon, fetchComparison } from './api'
import type { Comparison, HorizonMetrics } from './api'
import { Controls } from './components/Controls'
import { ForecastChart } from './components/ForecastChart'
import { HorizonChart } from './components/HorizonChart'
import { MetricCards } from './components/MetricCards'

export default function App() {
  // What the user picked.
  const [startDate, setStartDate] = useState('2026-01-10')
  const [endDate, setEndDate] = useState('2026-01-16')
  const [horizon, setHorizon] = useState(24)

  // What the API returned.
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [accuracy, setAccuracy] = useState<HorizonMetrics[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Whole days, from the first half-hour of the start date to the last half-hour of the end date.
  const start = `${startDate}T00:00:00Z`
  const end = `${endDate}T23:30:00Z`

  // Re-fetch whenever the window or horizon changes. Dragging the slider fires many changes, so
  // each run aborts the previous request; only the latest response is ever shown.
  useEffect(() => {
    const controller = new AbortController()
    fetchComparison(start, end, horizon, controller.signal)
      .then((data) => {
        setComparison(data)
        setError(null)
      })
      .catch((e: Error) => {
        if (!controller.signal.aborted) setError(e.message)
      })
    return () => controller.abort()
  }, [start, end, horizon])

  // Accuracy across all horizons depends only on the window, not on the slider.
  useEffect(() => {
    const controller = new AbortController()
    fetchAccuracyByHorizon(start, end, controller.signal)
      .then(setAccuracy)
      .catch((e: Error) => {
        if (!controller.signal.aborted) setError(e.message)
      })
    return () => controller.abort()
  }, [start, end])

  return (
    <main>
      <header>
        <h1>Wind Forecast Monitor</h1>
        <p className="muted">
          GB national wind generation, January 2026 · forecasts vs actuals from Elexon BMRS · times in UK time (GMT)
        </p>
      </header>

      <Controls
        startDate={startDate}
        endDate={endDate}
        horizon={horizon}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
        onHorizonChange={setHorizon}
      />

      {error && <p className="notice error">Could not load data: {error}</p>}

      {comparison && (
        <>
          <MetricCards metrics={comparison.metrics} horizon={horizon} />
          <section className="panel">
            <h2>Actual vs forecast generation</h2>
            <p className="muted">
              Each forecast point is the latest one published at least {horizon}h before that hour.
            </p>
            <ForecastChart data={comparison} />
          </section>
        </>
      )}

      {accuracy && (
        <section className="panel">
          <h2>How accuracy changes with horizon</h2>
          <p className="muted">
            Error over the selected dates for every horizon. Click the chart to jump the slider to a horizon.
          </p>
          <HorizonChart rows={accuracy} horizon={horizon} onSelectHorizon={setHorizon} />
        </section>
      )}
    </main>
  )
}

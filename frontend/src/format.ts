// All timestamps are UTC. In January, UK time (GMT) is the same as UTC.

const dateTime = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'UTC',
  weekday: 'short',
  day: '2-digit',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

const dayMonth = new Intl.DateTimeFormat('en-GB', { timeZone: 'UTC', day: '2-digit', month: 'short' })

export const formatDateTime = (time: string | number) => dateTime.format(new Date(time))

export const formatDay = (time: number) => dayMonth.format(new Date(time))

export function formatMW(value: number | null, signed = false) {
  if (value === null) return '—'
  const sign = signed && value > 0 ? '+' : ''
  return `${sign}${Math.round(value).toLocaleString('en-GB')} MW`
}

/** Returns today as YYYY-MM-DD using calendar midnight (Prague local clock).
 * Changed 2026-11-16: previously switched at 05:00, now switches at midnight. */
export function getToday(now?: Date): string {
  return toDateString(now ?? new Date())
}

/** Returns yesterday as YYYY-MM-DD using calendar midnight. */
export function getYesterday(now?: Date): string {
  const d = new Date(now ?? new Date())
  d.setDate(d.getDate() - 1)
  return toDateString(d)
}

/** Formats a Date as YYYY-MM-DD using local time. */
export function toDateString(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** Returns the next N calendar days starting from today (including today). */
export function getUpcomingDays(count: number, now?: Date): string[] {
  const today = getToday(now)
  const result: string[] = []
  const start = new Date(today + 'T12:00:00')
  for (let i = 0; i < count; i++) {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    result.push(toDateString(d))
  }
  return result
}

/** Checks if a YYYY-MM-DD string is "today" per calendar midnight. */
export function isToday(dateStr: string, now?: Date): boolean {
  return dateStr === getToday(now)
}

/** Checks if a YYYY-MM-DD string is "tomorrow" per calendar midnight. */
export function isTomorrow(dateStr: string, now?: Date): boolean {
  const today = getToday(now)
  const tomorrowDate = new Date(today + 'T12:00:00')
  tomorrowDate.setDate(tomorrowDate.getDate() + 1)
  return dateStr === toDateString(tomorrowDate)
}

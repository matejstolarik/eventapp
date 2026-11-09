/** Returns "today" as YYYY-MM-DD, switching at 05:00 Prague local time.
 * Before 05:00 the previous calendar day is still "today". */
export function getToday(now?: Date): string {
  const d = now ?? new Date()
  // Prague time offset: UTC+1 (CET) or UTC+2 (CEST)
  // We approximate using the browser's local time if already in CZ,
  // or use a fixed UTC+1/+2 offset. The simplest approach: use the
  // device clock since the app is used in Prague. Adjust: if hour < 5,
  // step back one day.
  const hour = d.getHours()
  const adjusted = new Date(d)
  if (hour < 5) {
    adjusted.setDate(adjusted.getDate() - 1)
  }
  return toDateString(adjusted)
}

/** Formats a Date as YYYY-MM-DD using local time. */
export function toDateString(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** Returns the next N calendar days starting from today (including today).
 * "Today" follows the 05:00 rule. */
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

/** Checks if a YYYY-MM-DD string is "today" per the 05:00 rule. */
export function isToday(dateStr: string, now?: Date): boolean {
  return dateStr === getToday(now)
}

/** Checks if a YYYY-MM-DD string is "tomorrow" per the 05:00 rule. */
export function isTomorrow(dateStr: string, now?: Date): boolean {
  const today = getToday(now)
  const tomorrowDate = new Date(today + 'T12:00:00')
  tomorrowDate.setDate(tomorrowDate.getDate() + 1)
  return dateStr === toDateString(tomorrowDate)
}

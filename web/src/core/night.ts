import type { Event } from './types'
import { toDateString } from './day'

export const NIGHT_DAY = 'night' as const

/** Returns true if current time is in the night window: 00:00–04:59. */
export function isNightTime(now: Date): boolean {
  return now.getHours() < 5
}

/**
 * In V noci mode, should this event be shown?
 * - Known end_time: show if end > now
 * - No end_time: only party/dj type OR late-night venue, started ≥ 20:00
 */
export function isNightEvent(
  event: Pick<Event, 'start_time' | 'end_time' | 'date' | 'formats'>,
  venueCharacter: string[],
  now: Date
): boolean {
  if (event.end_time) {
    let endDateStr = event.date
    if (event.start_time && event.end_time < event.start_time) {
      const d = new Date(event.date + 'T12:00:00')
      d.setDate(d.getDate() + 1)
      endDateStr = toDateString(d)
    }
    const endDt = new Date(`${endDateStr}T${event.end_time}:00`)
    return endDt > now
  }
  const isPartyOrDj = event.formats.includes('party') || event.formats.includes('dj')
  const isLateNight = venueCharacter.includes('late-night')
  if (!isPartyOrDj && !isLateNight) return false
  return !!event.start_time && event.start_time >= '20:00'
}

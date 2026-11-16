import type { Event, EventsData } from './types'
import { getYesterday, toDateString } from './day'
import { eventEndsAt } from './events'

export const NIGHT_DAY = 'night' as const

/**
 * Returns the correct selected day after the app returns from background.
 * Handles all transitions: midnight cross, end of night window, overnight background.
 */
export function resolveSelectedDay(selectedDay: string, now: Date, data?: EventsData): string {
  const isNight = data ? isNightMode(data, now) : _isNightWindow(now)
  if (isNight) {
    if (selectedDay === NIGHT_DAY) return NIGHT_DAY
    return selectedDay
  }
  if (selectedDay === NIGHT_DAY) return _getCalendarToday(now)
  if (selectedDay < _getCalendarToday(now)) return _getCalendarToday(now)
  return selectedDay
}

function _getCalendarToday(now: Date): string {
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** True if current time is in the potential night window 0:00–6:59. */
function _isNightWindow(now: Date): boolean {
  return now.getHours() < 7
}

/**
 * True when the app should be in "V noci" (night) mode:
 * between 0:00 and 7:00 AND at least one event from yesterday is still running as a night event.
 */
export function isNightMode(data: EventsData, now: Date): boolean {
  if (!_isNightWindow(now)) return false
  const yesterday = getYesterday(now)
  for (const venue of data.venues) {
    for (const e of data.events) {
      if (e.venue_id !== venue.id || e.date !== yesterday) continue
      if (e.status === 'cancelled' || e.status === 'gone') continue
      if (isNightEvent(e, venue.character, venue.closing, now)) return true
    }
  }
  return false
}

/**
 * In V noci mode, should this event be shown?
 * Event must still be running (not finished) AND be a "night" event
 * (party/dj or late-night venue, started ≥ 20:00 or has known end after now).
 */
export function isNightEvent(
  event: Pick<Event, 'start_time' | 'end_time' | 'date' | 'formats'>,
  venueCharacter: string[],
  venueClosing: Record<string, string> | null | undefined,
  now: Date
): boolean {
  const endsAt = eventEndsAt(event as Event, venueClosing, venueCharacter)
  if (endsAt <= now) return false

  if (event.end_time) {
    // Known end: show if still running (already checked above) and started ≥ 20:00 or was explicitly night
    const isPartyOrDj = event.formats.includes('party') || event.formats.includes('dj')
    const isLateNight = venueCharacter.includes('late-night')
    if (isPartyOrDj || isLateNight) return true
    return !!event.start_time && event.start_time >= '20:00'
  }

  const isPartyOrDj = event.formats.includes('party') || event.formats.includes('dj')
  const isLateNight = venueCharacter.includes('late-night')
  if (!isPartyOrDj && !isLateNight) return false
  return !!event.start_time && event.start_time >= '20:00'
}

/** @deprecated Use isNightMode(data, now) instead. Kept for callers that don't have data yet. */
export function isNightTime(now: Date): boolean {
  return _isNightWindow(now)
}

export { toDateString }

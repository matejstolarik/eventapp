import type { Event } from './types'
import { getToday } from './day'

/** An event is "finished" only when end_time is known and has passed.
 * If end_time is unknown, the event stays visible until 05:00 day switch. */
export function isEventFinished(event: Event, now: Date): boolean {
  if (!event.end_time) return false
  const eventDate = event.date
  let endDateStr = eventDate

  // If end_time < start_time the event spans midnight; end is next day
  if (event.start_time && event.end_time < event.start_time) {
    const d = new Date(eventDate + 'T12:00:00')
    d.setDate(d.getDate() + 1)
    endDateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const endDt = new Date(`${endDateStr}T${event.end_time}:00`)
  return now >= endDt
}

/** An event is "live" (ongoing) when start_time is known and has started
 * but is not yet finished. */
export function isEventLive(event: Event, now: Date): boolean {
  if (!event.start_time) return false
  const startDt = new Date(`${event.date}T${event.start_time}:00`)
  if (now < startDt) return false
  return !isEventFinished(event, now)
}

/**
 * Whether an event shows a live/pulse indicator right now.
 * - Known end_time: started and not finished (same as isEventLive).
 * - No end_time + party/dj format or late-night venue: from start until 5:00 next morning.
 * - No end_time, other: at most 3 hours from start.
 * - Event in a different day (by 5:00 rule) never pulses.
 */
export function isEventPulsing(event: Event, venueCharacter: string[], now: Date): boolean {
  if (!event.start_time) return false
  if (event.date !== getToday(now)) return false
  const startDt = new Date(`${event.date}T${event.start_time}:00`)
  if (now < startDt) return false
  if (event.end_time) return !isEventFinished(event, now)

  const isPartyOrDj = event.formats.includes('party') || event.formats.includes('dj')
  const isLateNight = venueCharacter.includes('late-night')
  if (isPartyOrDj || isLateNight) {
    const nextDay = new Date(event.date + 'T12:00:00')
    nextDay.setDate(nextDay.getDate() + 1)
    nextDay.setHours(5, 0, 0, 0)
    return now < nextDay
  }
  const threeHoursAfterStart = new Date(startDt.getTime() + 3 * 60 * 60 * 1000)
  return now < threeHoursAfterStart
}

/** Returns events for a venue on a specific day, filtered and sorted.
 * Cancelled/gone events are excluded. Finished events are excluded.
 * venueCharacter is used to sort pulsing events first. */
export function getVenueEvents(events: Event[], venueId: string, day: string, now: Date, venueCharacter: string[] = []): Event[] {
  return events
    .filter(e =>
      e.venue_id === venueId &&
      e.date === day &&
      e.status !== 'cancelled' &&
      e.status !== 'gone' &&
      !isEventFinished(e, now)
    )
    .sort((a, b) => {
      const aPulse = isEventPulsing(a, venueCharacter, now) ? 0 : 1
      const bPulse = isEventPulsing(b, venueCharacter, now) ? 0 : 1
      if (aPulse !== bPulse) return aPulse - bPulse
      if (!a.start_time && !b.start_time) return 0
      if (!a.start_time) return 1
      if (!b.start_time) return -1
      return a.start_time.localeCompare(b.start_time)
    })
}

/** Returns all venue IDs that have at least one visible event on the given day. */
export function getActiveVenueIds(events: Event[], day: string, now: Date): Set<string> {
  const ids = new Set<string>()
  for (const e of events) {
    if (e.date === day && e.status !== 'cancelled' && e.status !== 'gone' && !isEventFinished(e, now)) {
      ids.add(e.venue_id)
    }
  }
  return ids
}

/** Picks the "primary" event to show in the map panel.
 * Expects events pre-sorted by getVenueEvents (pulsing first). */
export function getPrimaryEvent(events: Event[]): Event | null {
  return events[0] ?? null
}

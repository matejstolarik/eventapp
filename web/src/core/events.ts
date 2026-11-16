import type { Event } from './types'
import { getToday, getYesterday, toDateString } from './day'

type Closing = Record<string, string> | null | undefined

const DAY_NAMES = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'] as const

function defaultClose(eventDate: string): Date {
  const d = new Date(eventDate + 'T12:00:00')
  d.setDate(d.getDate() + 1)
  d.setHours(3, 0, 0, 0)
  return d
}

function closingDatetime(eventDate: string, startTime: string | null, closingTime: string): Date {
  const nextDay = new Date(eventDate + 'T12:00:00')
  nextDay.setDate(nextDay.getDate() + 1)
  const nextDayStr = toDateString(nextDay)
  if (startTime === null) {
    // No start: closing < 12:00 → next day, else same day
    return closingTime < '12:00'
      ? new Date(`${nextDayStr}T${closingTime}:00`)
      : new Date(`${eventDate}T${closingTime}:00`)
  }
  // closing >= startTime → same day; else next day (e.g. 05:00 < 22:00 → next day)
  return closingTime >= startTime
    ? new Date(`${eventDate}T${closingTime}:00`)
    : new Date(`${nextDayStr}T${closingTime}:00`)
}

function getVenueClosingDt(eventDate: string, startTime: string | null, closing: Closing): Date | null {
  if (!closing) return null
  const d = new Date(eventDate + 'T12:00:00')
  const closingTime = closing[DAY_NAMES[d.getDay()]]
  if (!closingTime) return null
  return closingDatetime(eventDate, startTime, closingTime)
}

/**
 * Returns the Date when the event ends (computed from event data and venue closing).
 * - Known end_time → that time (next day if end < start)
 * - No end, party/dj or late-night → venue closing time, else 3:00 next day
 * - No end, other → start + 3 h
 * - No start_time → 3:00 next day (never pulses)
 */
export function eventEndsAt(event: Event, venueClosing: Closing, venueCharacter: string[]): Date {
  const eventDate = event.date

  if (event.end_time) {
    let endDateStr = eventDate
    if (event.start_time && event.end_time < event.start_time) {
      const d = new Date(eventDate + 'T12:00:00')
      d.setDate(d.getDate() + 1)
      endDateStr = toDateString(d)
    }
    return new Date(`${endDateStr}T${event.end_time}:00`)
  }

  const isPartyOrDj = event.formats.includes('party') || event.formats.includes('dj')
  const isLateNight = venueCharacter.includes('late-night')

  if (isPartyOrDj || isLateNight) {
    const closingDt = getVenueClosingDt(eventDate, event.start_time, venueClosing)
    return closingDt ?? defaultClose(eventDate)
  }

  if (event.start_time) {
    const startDt = new Date(`${eventDate}T${event.start_time}:00`)
    return new Date(startDt.getTime() + 3 * 60 * 60 * 1000)
  }

  return defaultClose(eventDate)
}

export function isEventFinished(event: Event, now: Date, venueClosing?: Closing, venueCharacter?: string[]): boolean {
  return now >= eventEndsAt(event, venueClosing ?? null, venueCharacter ?? [])
}

export function isEventLive(event: Event, now: Date, venueClosing?: Closing, venueCharacter?: string[]): boolean {
  if (!event.start_time) return false
  const startDt = new Date(`${event.date}T${event.start_time}:00`)
  if (now < startDt) return false
  return !isEventFinished(event, now, venueClosing, venueCharacter)
}

/**
 * Whether an event shows a live/pulse indicator right now.
 * Also allows yesterday's events to pulse during the 0:00–7:00 night window.
 */
export function isEventPulsing(event: Event, venueCharacter: string[], venueClosing: Closing, now: Date): boolean {
  if (!event.start_time) return false
  const today = getToday(now)
  const yesterday = getYesterday(now)
  const isNightWindow = now.getHours() < 7
  if (event.date !== today && !(isNightWindow && event.date === yesterday)) return false
  const startDt = new Date(`${event.date}T${event.start_time}:00`)
  if (now < startDt) return false
  return !isEventFinished(event, now, venueClosing, venueCharacter)
}

/** Returns events for a venue on a specific day, filtered and sorted.
 * Cancelled/gone events are excluded. Finished events are excluded.
 * venueCharacter and venueClosing are used for finish time and sorting. */
export function getVenueEvents(
  events: Event[],
  venueId: string,
  day: string,
  now: Date,
  venueCharacter: string[] = [],
  venueClosing: Closing = null,
): Event[] {
  return events
    .filter(e =>
      e.venue_id === venueId &&
      e.date === day &&
      e.status !== 'cancelled' &&
      e.status !== 'gone' &&
      !isEventFinished(e, now, venueClosing, venueCharacter)
    )
    .sort((a, b) => {
      const aPulse = isEventPulsing(a, venueCharacter, venueClosing, now) ? 0 : 1
      const bPulse = isEventPulsing(b, venueCharacter, venueClosing, now) ? 0 : 1
      if (aPulse !== bPulse) return aPulse - bPulse
      if (!a.start_time && !b.start_time) return 0
      if (!a.start_time) return 1
      if (!b.start_time) return -1
      return a.start_time.localeCompare(b.start_time)
    })
}

/** Returns all venue IDs that have at least one visible event on the given day. */
export function getActiveVenueIds(
  events: Event[],
  day: string,
  now: Date,
  venueMap?: Map<string, { closing: Record<string, string> | null; character: string[] }>,
): Set<string> {
  const ids = new Set<string>()
  for (const e of events) {
    if (e.date === day && e.status !== 'cancelled' && e.status !== 'gone') {
      const v = venueMap?.get(e.venue_id)
      if (!isEventFinished(e, now, v?.closing, v?.character)) {
        ids.add(e.venue_id)
      }
    }
  }
  return ids
}

/** Picks the "primary" event to show in the map panel.
 * Expects events pre-sorted by getVenueEvents (pulsing first). */
export function getPrimaryEvent(events: Event[]): Event | null {
  return events[0] ?? null
}

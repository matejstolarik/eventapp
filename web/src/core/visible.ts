import type { Event, EventsData, Venue } from './types'
import { getVenueEvents, getActiveVenueIds } from './events'
import { getYesterday } from './day'
import { isNightEvent, NIGHT_DAY } from './night'

export interface VisibleOpts {
  favoritesOnly: boolean
  isFavorite: (id: string) => boolean
  /** Task 075: only events that pass the filter (pin, count and card follow it) */
  eventFilter?: (e: Event, venue: Venue) => boolean
}

/**
 * Single source of truth for which events are visible for each venue.
 * Returns a map venueId → Event[] (already filtered and sorted).
 * Used by buildMarkers, panelEvents, and sortedVenues.
 */
export function visibleEvents(
  data: EventsData,
  day: string,
  now: Date,
  opts: VisibleOpts
): Map<string, Event[]> {
  const result = new Map<string, Event[]>()

  if (day === NIGHT_DAY) {
    const nightDate = getYesterday(now)
    for (const venue of data.venues) {
      if (opts.favoritesOnly && !opts.isFavorite(venue.id)) continue
      const events = getVenueEvents(data.events, venue.id, nightDate, now, venue.character, venue.closing)
      const nightEvents = events.filter(e => isNightEvent(e, venue.character, venue.closing, now)
        && (!opts.eventFilter || opts.eventFilter(e, venue)))
      if (nightEvents.length > 0) result.set(venue.id, nightEvents)
    }
  } else {
    const venueMap = new Map(data.venues.map(v => [v.id, { closing: v.closing, character: v.character }]))
    const activeIds = getActiveVenueIds(data.events, day, now, venueMap)
    for (const venue of data.venues) {
      if (!activeIds.has(venue.id)) continue
      if (opts.favoritesOnly && !opts.isFavorite(venue.id)) continue
      let events = getVenueEvents(data.events, venue.id, day, now, venue.character, venue.closing)
      if (opts.eventFilter) events = events.filter(e => opts.eventFilter!(e, venue))
      if (events.length > 0) result.set(venue.id, events)
    }
  }

  return result
}

/** First day after `afterDate` (within the loaded data) with a visible event —
 * "Najbližšie" in the empty filter card (task 075). */
export function nearestVisibleDay(data: EventsData, afterDate: string, now: Date, opts: VisibleOpts): string | null {
  const dates = [...new Set(data.events.map(e => e.date))].filter(d => d > afterDate).sort()
  for (const d of dates) if (visibleEvents(data, d, now, opts).size > 0) return d
  return null
}

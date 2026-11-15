import type { Event, EventsData } from './types'
import { getVenueEvents, getActiveVenueIds } from './events'
import { getToday } from './day'
import { isNightEvent, NIGHT_DAY } from './night'

/**
 * Single source of truth for which events are visible for each venue.
 * Returns a map venueId → Event[] (already filtered and sorted).
 * Used by buildMarkers, panelEvents, and sortedVenues.
 */
export function visibleEvents(
  data: EventsData,
  day: string,
  now: Date,
  opts: { favoritesOnly: boolean; isFavorite: (id: string) => boolean }
): Map<string, Event[]> {
  const result = new Map<string, Event[]>()

  if (day === NIGHT_DAY) {
    const nightDate = getToday(now)
    for (const venue of data.venues) {
      if (opts.favoritesOnly && !opts.isFavorite(venue.id)) continue
      const events = getVenueEvents(data.events, venue.id, nightDate, now, venue.character)
      const nightEvents = events.filter(e => isNightEvent(e, venue.character, now))
      if (nightEvents.length > 0) result.set(venue.id, nightEvents)
    }
  } else {
    const activeIds = getActiveVenueIds(data.events, day, now)
    for (const venue of data.venues) {
      if (!activeIds.has(venue.id)) continue
      if (opts.favoritesOnly && !opts.isFavorite(venue.id)) continue
      const events = getVenueEvents(data.events, venue.id, day, now, venue.character)
      if (events.length > 0) result.set(venue.id, events)
    }
  }

  return result
}

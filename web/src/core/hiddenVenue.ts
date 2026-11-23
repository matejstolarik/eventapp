import type { Event, Venue } from './types'

/** Task 092: a venue whose source is failing (`source_failing` from the pipeline)
 * is hidden in the app once it has no future event left (kept events drop out as
 * their day passes). A venue that simply has no programme stays visible. */
export function isVenueHidden(venue: Venue, events: Event[], today: string): boolean {
  if (!venue.source_failing) return false
  return !events.some(e => e.venue_id === venue.id && e.date >= today)
}

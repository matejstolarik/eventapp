import type { Event, Venue } from './types'

export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
}

export function matchesSearch(query: string, event: Event, venue: Venue | undefined): boolean {
  const q = normalizeText(query.trim())
  if (!q) return true
  if (normalizeText(event.title).includes(q)) return true
  if (venue && normalizeText(venue.name).includes(q)) return true
  for (const tag of [...event.formats, ...event.genres]) {
    if (normalizeText(tag).includes(q)) return true
  }
  if (venue) {
    for (const tag of venue.character) {
      if (normalizeText(tag).includes(q)) return true
    }
  }
  return false
}

/** Is this event "for you"? = it's in a favorite venue */
export function isForYou(event: Event, favoriteVenueIds: Set<string>): boolean {
  return favoriteVenueIds.has(event.venue_id)
}

/** Is this event "new"? = first_seen within last 7 days (inclusive today) */
export function isNew(event: Event, now: Date): boolean {
  if (!event.first_seen) return false
  const cutoff = new Date(now)
  cutoff.setDate(cutoff.getDate() - 6)
  cutoff.setHours(0, 0, 0, 0)
  const seen = new Date(event.first_seen + 'T00:00:00')
  return seen >= cutoff
}

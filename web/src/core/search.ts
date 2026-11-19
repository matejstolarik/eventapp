import type { Event, Venue } from './types'
import { filterTypeOf, eventUmbrellas, type FilterType } from './filter'
import { cultureSubtype, type CultureSubtype } from './eventType'

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

/** Everything Pre teba is computed from (task 079). */
export interface ForYouPrefs {
  favorites: Set<string>
  types: FilterType[]
  subtypes: CultureSubtype[]
  genres: string[]
}

export function hasAnyPrefs(p: ForYouPrefs): boolean {
  return p.favorites.size > 0 || p.types.length > 0 || p.subtypes.length > 0 || p.genres.length > 0
}

/** Is this event "for you"? (design.md 4, block 2026-11-19, task 079)
 * - selected types exist and the event's type is not among them → no;
 * - music (concert, DJ, party) → favourite venue or an umbrella genre among the liked genres;
 * - culture → its subtype among the selected subtypes; culture without subtypes → culture in a favourite venue;
 * - no types selected → favourite venue or genre match, any type;
 * - no preferences at all → nothing. */
export function isForYou(event: Event, p: ForYouPrefs): boolean {
  const fav = p.favorites.has(event.venue_id)
  const genreMatch = () => p.genres.length > 0 && eventUmbrellas(event).some(u => p.genres.includes(u))
  if (p.types.length === 0) return fav || genreMatch()
  const type = filterTypeOf(event)
  if (!p.types.includes(type)) return false
  if (type === 'culture') {
    if (p.subtypes.length === 0) return fav
    const sub = cultureSubtype(event.formats, event.primary_format)
    return sub !== null && p.subtypes.includes(sub)
  }
  return fav || genreMatch()
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

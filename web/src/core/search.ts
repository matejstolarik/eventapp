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

/** Music genres of an event that the score counts: genres with at least one
 * umbrella offered as a genre chip (culture-only genres like `horror` are left out). */
function scoredGenres(event: Event): string[] {
  return event.genres.filter(g => eventUmbrellas({ genres: [g] }).length > 0)
}

/** Match score 0–100 (task 087, design.md 4 block 2026-11-21; replaces yes/no of 079).
 * - no preferences at all → 0;
 * - selected types and the event's type not among them → 0 (gate);
 * - culture (culture selected): subtype among selected subtypes → 80, not among → 0,
 *   culture selected without subtypes → 40;
 * - genres (model D, order not used): at least one event genre whose umbrella is liked
 *   → 50 + 30 × matched / all event genres; none matched → 0;
 *   event without genres or user without liked genres → neutral 40, but only when the
 *   type matched positively (selected types) or, without selected types, the venue is a favourite;
 * - favourite venue +20; capped at 100. */
export function forYouScore(event: Event, p: ForYouPrefs): number {
  if (!hasAnyPrefs(p)) return 0
  const fav = p.favorites.has(event.venue_id)
  const bonus = fav ? 20 : 0
  let base: number
  if (p.types.length > 0) {
    const type = filterTypeOf(event)
    if (!p.types.includes(type)) return 0
    if (type === 'culture') {
      if (p.subtypes.length === 0) base = 40
      else {
        const sub = cultureSubtype(event.formats, event.primary_format)
        if (sub === null || !p.subtypes.includes(sub)) return 0
        base = 80
      }
      return Math.min(100, base + bonus)
    }
    base = genrePoints(event, p, true)
  } else {
    base = genrePoints(event, p, fav)
  }
  return Math.min(100, base + bonus)
}

function genrePoints(event: Event, p: ForYouPrefs, neutralAllowed: boolean): number {
  const genres = scoredGenres(event)
  if (p.genres.length === 0 || genres.length === 0) return neutralAllowed ? 40 : 0
  const matched = genres.filter(g => eventUmbrellas({ genres: [g] }).some(u => p.genres.includes(u))).length
  if (matched === 0) return 0
  return Math.round(50 + 30 * matched / genres.length)
}

/** Two tiers (task 087): 2 = ✦✦ "Presne pre teba" (≥ 75), 1 = ✦ "Mohlo by ťa baviť" (40–74), 0 = nothing. */
export type ForYouTier = 0 | 1 | 2
export function forYouTier(score: number): ForYouTier {
  return score >= 75 ? 2 : score >= 40 ? 1 : 0
}
/** Internal tier names (not shown in the UI). */
export const FOR_YOU_TIER_NAME: Record<ForYouTier, string> = { 0: '', 1: 'Mohlo by ťa baviť', 2: 'Presne pre teba' }

/** Is this event "for you"? = score ≥ 40 (✦ or ✦✦). */
export function isForYou(event: Event, p: ForYouPrefs): boolean {
  return forYouScore(event, p) >= 40
}

/** Is this event "new"? = first_seen within last 7 days (inclusive today).
 *  Task 086: events of the venue's first load (first_seen <= venue.first_loaded)
 *  are never new — only events that appeared in later pipeline runs. */
export function isNew(event: Event, now: Date, venue?: { first_loaded?: string | null } | null): boolean {
  if (!event.first_seen) return false
  if (venue?.first_loaded && event.first_seen <= venue.first_loaded) return false
  const cutoff = new Date(now)
  cutoff.setDate(cutoff.getDate() - 6)
  cutoff.setHours(0, 0, 0, 0)
  const seen = new Date(event.first_seen + 'T00:00:00')
  return seen >= cutoff
}

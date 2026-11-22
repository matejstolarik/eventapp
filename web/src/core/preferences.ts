import type { Event } from './types'
import { filterTypeOf, eventUmbrellas, toggleIn, type FilterType } from './filter'
import type { CultureSubtype } from './eventType'
import { MAX_PREF_GENRES, type Preferences } from './store'

// Task 079: helpers for the onboarding and My account → Event preferences.

/** Umbrella music genres (concert, DJ, party; no culture subtypes) with at
 * least one event, most events first; ties alphabetically. */
export function preferenceGenres(events: Event[]): string[] {
  const counts = new Map<string, number>()
  for (const e of events) {
    if (filterTypeOf(e) === 'culture') continue
    for (const u of eventUmbrellas(e)) counts.set(u, (counts.get(u) ?? 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([g]) => g)
}

/** Toggle a genre; adding beyond MAX_PREF_GENRES is ignored. */
export function togglePrefGenre(p: Preferences, g: string): Preferences {
  if (!p.genres.includes(g) && p.genres.length >= MAX_PREF_GENRES) return p
  return { ...p, genres: toggleIn(p.genres, g) }
}

/** Toggle a type; turning culture off clears its subtypes (they collapse). */
export function togglePrefType(p: Preferences, t: FilterType): Preferences {
  const on = p.types.includes(t)
  const types = toggleIn(p.types, t)
  return { ...p, types, subtypes: t === 'culture' && on ? [] : p.subtypes }
}

export function togglePrefSubtype(p: Preferences, s: CultureSubtype): Preferences {
  return { ...p, subtypes: toggleIn(p.subtypes, s) }
}

/** Genres step only when a music type is selected. */
export function hasMusicType(p: Preferences): boolean {
  return p.types.some(t => t !== 'culture')
}

/** Task 080: a pick step's Next needs at least one pick (otherwise the button shakes). */
export type PickStep = 'places' | 'types' | 'genres'
export function stepHasPick(step: PickStep, p: Preferences, favorites: Set<string>): boolean {
  if (step === 'places') return favorites.size > 0
  if (step === 'types') return p.types.length > 0
  return p.genres.length > 0
}

/** Task 080: section order on the Event preferences page (places last, the longest). */
export const PREF_SECTION_ORDER = ['types', 'genres', 'places'] as const

/** Task 080: Pre teba is on but there are no preferences → empty list with the set-up message.
 * Task 091: also with only types (no favourite venue, no genre) → 'typesOnly' (its own text). */
export type ForYouSetup = 'none' | 'typesOnly' | null
export function forYouNeedsSetup(forYouActive: boolean, hasPrefs: boolean, onlyTypes = false): ForYouSetup {
  if (!forYouActive) return null
  if (!hasPrefs) return 'none'
  return onlyTypes ? 'typesOnly' : null
}

/** Task 091: once at least one type is selected, the last one cannot be removed (Event preferences). */
export function canToggleTypeOff(p: Preferences, t: FilterType): boolean {
  return !(p.types.length === 1 && p.types[0] === t)
}

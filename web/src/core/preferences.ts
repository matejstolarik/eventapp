import type { Event } from './types'
import { filterTypeOf, eventUmbrellas, toggleIn, type FilterType } from './filter'
import type { CultureSubtype } from './eventType'
import { MAX_PREF_GENRES, type Preferences } from './store'

// Task 079: helpers for the onboarding and My account → Your preferences.

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

import type { Language, EventsData } from './types'
import { isEventFinished } from './events'
import { parseFilter, serializeFilter, FILTER_TYPES, type EventFilter, type FilterType } from './filter'
import { CULTURE_SUBTYPES, type CultureSubtype } from './eventType'
import type { ForYouPrefs } from './search'

function safeGet(key: string): string | null {
  try { return localStorage.getItem(key) } catch { return null }
}
function safeSet(key: string, value: string): void {
  try { localStorage.setItem(key, value) } catch { /* ignore */ }
}

// ── Favorites ──────────────────────────────────────────────────────────────

export function getFavorites(): Set<string> {
  const raw = safeGet('favorites')
  if (!raw) return new Set()
  try { return new Set(JSON.parse(raw) as string[]) } catch { return new Set() }
}

export function isFavorite(venueId: string): boolean {
  return getFavorites().has(venueId)
}

export function toggleFavorite(venueId: string): boolean {
  const favs = getFavorites()
  if (favs.has(venueId)) {
    favs.delete(venueId)
  } else {
    favs.add(venueId)
  }
  safeSet('favorites', JSON.stringify([...favs]))
  notifyPreferencesChanged()
  return favs.has(venueId)
}

// ── Going ──────────────────────────────────────────────────────────────────

export function getGoing(): Set<string> {
  const raw = safeGet('going')
  if (!raw) return new Set()
  try { return new Set(JSON.parse(raw) as string[]) } catch { return new Set() }
}

export function isGoing(eventId: string): boolean {
  return getGoing().has(eventId)
}

export function toggleGoing(eventId: string): boolean {
  const going = getGoing()
  if (going.has(eventId)) {
    going.delete(eventId)
  } else {
    going.add(eventId)
  }
  safeSet('going', JSON.stringify([...going]))
  return going.has(eventId)
}

/** Remove finished events from the stored going list to prevent unbounded growth. */
export function pruneGoing(data: EventsData, now: Date): void {
  const going = getGoing()
  if (going.size === 0) return
  const eventMap = new Map(data.events.map(e => [e.id, e]))
  const venueMap = new Map(data.venues.map(v => [v.id, v]))
  const before = going.size
  for (const id of [...going]) {
    const event = eventMap.get(id)
    if (!event) { going.delete(id); continue }
    const venue = venueMap.get(event.venue_id)
    if (isEventFinished(event, now, venue?.closing ?? null, venue?.character ?? [])) {
      going.delete(id)
    }
  }
  if (going.size !== before) safeSet('going', JSON.stringify([...going]))
}

// ── Language ───────────────────────────────────────────────────────────────

export function getStoredLanguage(): Language | null {
  const v = safeGet('language')
  if (v === 'sk' || v === 'cs' || v === 'en') return v
  return null
}

export function setStoredLanguage(lang: Language): void {
  safeSet('language', lang)
}

/** Task 072: first of cs / sk / en in the device's language list (in order), else en. */
export function pickLanguage(languages: readonly string[]): Language {
  for (const tag of languages) {
    const base = tag.toLowerCase().split(/[-_]/)[0]
    if (base === 'cs' || base === 'sk' || base === 'en') return base
  }
  return 'en'
}

export function detectLanguage(): Language {
  const stored = getStoredLanguage()
  if (stored) return stored
  const langs = navigator.languages?.length ? navigator.languages : [navigator.language ?? '']
  return pickLanguage(langs)
}

// ── Events period ─────────────────────────────────────────────────────────

import type { Period } from './period'

export function getStoredPeriod(): Period | null {
  const raw = safeGet('eventsPeriod')
  if (!raw) return null
  try {
    const p = JSON.parse(raw) as Period
    if (p.type === 'custom') return null
    if (!p.type) return null
    return p
  } catch { return null }
}

export function setStoredPeriod(period: Period): void {
  if (period.type === 'custom') return
  safeSet('eventsPeriod', JSON.stringify(period))
}

// ── Shared user location (map → events) ───────────────────────────────────

let _lastKnownLocation: { lat: number; lng: number } | null = null

export function setLastKnownLocation(loc: { lat: number; lng: number } | null): void {
  _lastKnownLocation = loc
}

export function getLastKnownLocation(): { lat: number; lng: number } | null {
  return _lastKnownLocation
}

// ── Events chip filters ───────────────────────────────────────────────────

export function getStoredEventsFilters(): { forYou: boolean; isNew: boolean } {
  const raw = safeGet('eventsFilters')
  if (!raw) return { forYou: false, isNew: false }
  try {
    const f = JSON.parse(raw) as { forYou?: boolean; isNew?: boolean }
    return { forYou: Boolean(f.forYou), isNew: Boolean(f.isNew) }
  } catch { return { forYou: false, isNew: false } }
}

export function setStoredEventsFilters(filters: { forYou: boolean; isNew: boolean }): void {
  safeSet('eventsFilters', JSON.stringify(filters))
}

// ── Filter (task 075) ─────────────────────────────────────────────────────

/** One filter for Mapa and Akcie, kept until the user changes or clears it. */
export function getStoredFilter(): EventFilter {
  return parseFilter(safeGet('filter'))
}

export function setStoredFilter(f: EventFilter): void {
  safeSet('filter', serializeFilter(f))
}

// ── Last fetched ───────────────────────────────────────────────────────────

export function setLastFetched(): void {
  safeSet('eventsLastFetched', String(Date.now()))
}

export function getLastFetched(): Date | null {
  const raw = safeGet('eventsLastFetched')
  if (!raw) return null
  const ts = parseInt(raw, 10)
  return isNaN(ts) ? null : new Date(ts)
}

// ── Preferences (task 079) ────────────────────────────────────────────────

/** Pre teba preferences besides favourite venues (those stay in `favorites`). */
export interface Preferences {
  types: FilterType[]
  subtypes: CultureSubtype[]
  /** Umbrella music genres, at most MAX_PREF_GENRES */
  genres: string[]
}

export const MAX_PREF_GENRES = 5
export const EMPTY_PREFERENCES: Preferences = { types: [], subtypes: [], genres: [] }

export function parsePreferences(raw: string | null): Preferences {
  if (!raw) return EMPTY_PREFERENCES
  try {
    const p = JSON.parse(raw) as Partial<Preferences>
    const arr = (v: unknown) => Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : []
    return {
      types: FILTER_TYPES.filter(t => arr(p.types).includes(t)),
      subtypes: CULTURE_SUBTYPES.filter(s => arr(p.subtypes).includes(s)),
      genres: arr(p.genres).slice(0, MAX_PREF_GENRES),
    }
  } catch { return EMPTY_PREFERENCES }
}

export function getPreferences(): Preferences {
  return parsePreferences(safeGet('preferences'))
}

export function setPreferences(p: Preferences): void {
  safeSet('preferences', JSON.stringify(p))
  notifyPreferencesChanged()
}

export const PREFERENCES_EVENT = 'eventapp:preferences'

/** Favourites or preferences changed: pages showing Pre teba recompute. */
export function notifyPreferencesChanged(): void {
  try { window.dispatchEvent(new Event(PREFERENCES_EVENT)) } catch { /* ignore */ }
}

// ── Onboarding (task 079) ─────────────────────────────────────────────────

/** Keys an existing install has written; any of them = not a new install. */
export const EXISTING_STATE_KEYS = [
  'favorites', 'going', 'filter', 'eventsPeriod', 'eventsFilters', 'language', 'eventsLastFetched', 'preferences',
] as const

/** Onboarding shows only on a new install: no done flag and no earlier state. */
export function shouldShowOnboarding(get: (key: string) => string | null = safeGet): boolean {
  if (get('onboardingDone')) return false
  // Started but not finished (app closed midway): show again, although state keys exist by now
  if (get('onboardingPending')) return true
  return EXISTING_STATE_KEYS.every(k => get(k) === null)
}

/** Mark the onboarding as started, before the app writes any other state. */
export function setOnboardingPending(): void {
  safeSet('onboardingPending', '1')
}

export function setOnboardingDone(): void {
  safeSet('onboardingDone', '1')
  try { localStorage.removeItem('onboardingPending') } catch { /* ignore */ }
}

/** Favourites + preferences in the shape isForYou takes. */
export function getForYouPrefs(): ForYouPrefs {
  return { favorites: getFavorites(), ...getPreferences() }
}

import type { Language } from './types'

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

// ── Language ───────────────────────────────────────────────────────────────

export function getStoredLanguage(): Language | null {
  const v = safeGet('language')
  if (v === 'sk' || v === 'cs' || v === 'en') return v
  return null
}

export function setStoredLanguage(lang: Language): void {
  safeSet('language', lang)
}

export function detectLanguage(): Language {
  const stored = getStoredLanguage()
  if (stored) return stored
  const nav = navigator.language ?? ''
  if (nav.startsWith('sk')) return 'sk'
  if (nav.startsWith('cs')) return 'cs'
  return 'en'
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

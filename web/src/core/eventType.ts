import type { EventType } from './types'

const CULTURE_FORMATS = new Set(['theatre', 'dance', 'talk', 'comedy', 'film', 'opening', 'workshop', 'quiz'])

export type EventIconKey = 'concert' | 'party' | 'dj' | 'film' | 'comedy' | 'dance' | 'culture'

/** Returns the event type for color and icon, using priority:
 * party → dj → concert/music → culture formats → other */
export function getEventType(formats: string[]): EventType {
  if (formats.includes('party')) return 'party'
  if (formats.includes('dj')) return 'dj'
  if (formats.includes('concert') || formats.includes('music')) return 'concert'
  if (formats.some(f => CULTURE_FORMATS.has(f))) return 'culture'
  return 'other'
}

export const EVENT_TYPE_COLOR: Record<EventType, string> = {
  party: '#FF8A3D',
  dj: '#2FD4C0',
  concert: '#8B6CFF',
  culture: '#C6F432',
  other: '#C6F432'
}

export const EVENT_TYPE_DARK: Record<EventType, string> = {
  party: '#2A1200',
  dj: '#002B26',
  concert: '#14063A',
  culture: '#1B2600',
  other: '#1B2600'
}

/** Returns the icon key for an event based on its formats.
 * concert/party/dj use their own icons; culture uses a subtype icon:
 * film → film-clapper, comedy → vintage mic, dance → filled silhouette, else → theatre masks.
 * other → culture (masks). */
export function eventIconKey(formats: string[]): EventIconKey {
  const type = getEventType(formats)
  if (type === 'party') return 'party'
  if (type === 'dj') return 'dj'
  if (type === 'concert') return 'concert'
  // culture or other — pick sub-icon from first matching culture format
  if (formats.includes('film')) return 'film'
  if (formats.includes('comedy')) return 'comedy'
  if (formats.includes('dance')) return 'dance'
  return 'culture'
}

/** Tag text color — lighter purple for concert so text stays legible on dark bg */
export const EVENT_TYPE_TAG_TEXT: Record<EventType, string> = {
  party: '#FF8A3D',
  dj: '#2FD4C0',
  concert: '#A48BFF',
  culture: '#C6F432',
  other: '#C6F432'
}

/** Tags to display on the event card, map panel and venue programme.
 * Returns culture subtypes first, then genres; type formats (party/dj/concert/music) excluded.
 * Falls back to [eventType] string when nothing else is available. */
export function eventTags(formats: string[], genres: string[]): string[] {
  const cultureSubs = formats.filter(f => CULTURE_FORMATS.has(f))
  const tags = [...cultureSubs, ...genres]
  if (tags.length > 0) return tags
  return [getEventType(formats)]
}

/** First tag for the event detail page: concert/party/dj → type string; culture → first subtype; other → null */
export function primaryTypeTag(formats: string[]): string | null {
  const type = getEventType(formats)
  if (type === 'party' || type === 'dj' || type === 'concert') return type
  if (type === 'culture') return formats.find(f => CULTURE_FORMATS.has(f)) ?? null
  return null
}

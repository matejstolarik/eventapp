import type { EventType } from './types'

const CULTURE_FORMATS = new Set(['theatre', 'dance', 'talk', 'performance', 'stand-up', 'film', 'opening', 'workshop', 'quiz'])

export type EventIconKey = 'concert' | 'party' | 'dj' | 'film' | 'standup' | 'dance'
  | 'talk' | 'workshop' | 'quiz' | 'opening' | 'culture'

/** Culture subtype → icon key (task 071). theatre, performance and the rest → masks ('culture'). */
const CULTURE_ICON: Record<string, EventIconKey> = {
  film: 'film', 'stand-up': 'standup', dance: 'dance',
  talk: 'talk', workshop: 'workshop', quiz: 'quiz', opening: 'opening',
}
/** Icon order when primary_format does not decide (task 071, set by the main chat). */
const CULTURE_ICON_ORDER = ['film', 'stand-up', 'dance', 'talk', 'workshop', 'quiz', 'opening']

/** Culture subtypes carried by the icon, not shown as tags in lists (task 071). performance stays a tag. */
const ICON_SUBTYPES = new Set(['film', 'stand-up', 'dance', 'theatre', 'talk', 'workshop', 'quiz', 'opening'])

/** Returns the event type for color and icon.
 * Task 053: if the AI gave `primary_format` (the main part of the event) and it is
 * one of the event's formats, it decides. Otherwise priority:
 * party → dj → concert/music → culture formats → other */
export function getEventType(formats: string[], primaryFormat?: string | null): EventType {
  if (primaryFormat && formats.includes(primaryFormat)) return typeByPriority([primaryFormat])
  return typeByPriority(formats)
}

function typeByPriority(formats: string[]): EventType {
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
 * concert/party/dj use their own icons; culture uses a subtype icon (task 071):
 * a culture `primary_format` decides; else the first of film → stand-up → dance →
 * talk → workshop → quiz → opening; else theatre masks. other → masks. */
export function eventIconKey(formats: string[], primaryFormat?: string | null): EventIconKey {
  const type = getEventType(formats, primaryFormat)
  if (type === 'party') return 'party'
  if (type === 'dj') return 'dj'
  if (type === 'concert') return 'concert'
  if (type === 'other') return 'culture'
  if (primaryFormat && formats.includes(primaryFormat) && CULTURE_FORMATS.has(primaryFormat)) {
    return CULTURE_ICON[primaryFormat] ?? 'culture'
  }
  const sub = CULTURE_ICON_ORDER.find(f => formats.includes(f))
  return sub ? CULTURE_ICON[sub] : 'culture'
}

/** Tag text color — lighter purple for concert so text stays legible on dark bg */
export const EVENT_TYPE_TAG_TEXT: Record<EventType, string> = {
  party: '#FF8A3D',
  dj: '#2FD4C0',
  concert: '#A48BFF',
  culture: '#C6F432',
  other: '#C6F432'
}

/** Tags to display in the Akcie row, map card and venue programme.
 * Task 071: culture subtypes are carried by the type icon and not shown, except
 * `performance`; then genres. Type formats (party/dj/concert/music) excluded.
 * No fallback tag: an event without tags gets an empty list (only the icon pill). */
export function eventTags(formats: string[], genres: string[], _primaryFormat?: string | null): string[] {
  const cultureSubs = formats.filter(f => CULTURE_FORMATS.has(f) && !ICON_SUBTYPES.has(f))
  return [...cultureSubs, ...genres]
}

/** First tag for the event detail page: concert/party/dj → type string; culture → first subtype; other → null */
export function primaryTypeTag(formats: string[], primaryFormat?: string | null): string | null {
  const type = getEventType(formats, primaryFormat)
  if (type === 'party' || type === 'dj' || type === 'concert') return type
  if (type === 'culture') return formats.find(f => CULTURE_FORMATS.has(f)) ?? null
  return null
}

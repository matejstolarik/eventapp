import type { EventType } from './types'

const CULTURE_FORMATS = new Set(['theatre', 'dance', 'talk', 'comedy', 'film', 'opening', 'workshop', 'quiz'])

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

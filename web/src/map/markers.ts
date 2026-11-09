import type { EventType } from '../core/types'
import { EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'

const ICON_SVG: Record<EventType, (color: string) => string> = {
  concert: (c) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><g transform="translate(12 12) scale(1.057) translate(-14.12 -11.09)" stroke-width="1.89"><g transform="rotate(45 12 12)"><circle cx="12" cy="5" r="4"/><path d="M8.3 6.5h7.4"/><path d="M9.6 9.2L10.6 17h2.8l1-7.8"/></g><path d="M8.5 15.5C6.6 17.4 6.2 19.6 7.6 20.5c1.4.9 2.9-.5 4.4-2 1.5-1.5 3.6-2 5 0l1 1.5"/></g></svg>`,
  party: (c) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h14l-7 8z"/><path d="M12 12v7"/><path d="M8 20h8"/><path d="M15 7l3-4"/></svg>`,
  dj: (c) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="11" cy="12" r="5"/><circle cx="11" cy="12" r="1"/><path d="M18 7v6l-3 2"/></svg>`,
  culture: (c) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h9v6a4.5 4.5 0 0 1-9 0z"/><path d="M11 10h9v5a4.5 4.5 0 0 1-9 0"/><path d="M6.5 8.5h.01M10.5 8.5h.01M14 13h.01M17.5 13h.01"/></svg>`,
  other: (c) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h9v6a4.5 4.5 0 0 1-9 0z"/><path d="M11 10h9v5a4.5 4.5 0 0 1-9 0"/><path d="M6.5 8.5h.01M10.5 8.5h.01M14 13h.01M17.5 13h.01"/></svg>`,
}

const HEART_SVG = `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19.5 12.6L12 20l-7.5-7.4A5 5 0 1 1 12 6a5 5 0 1 1 7.5 6.6z"/></svg>`

export interface MarkerData {
  venueId: string
  name: string
  eventType: EventType
  isFavorite: boolean
  isLive: boolean
  extraCount: number
  lat: number
  lng: number
  stackOffset: number
}

/** Creates the pill marker DOM element. */
export function createPillElement(data: MarkerData, isSelected: boolean, isDotMode: boolean): HTMLElement {
  const color = EVENT_TYPE_COLOR[data.eventType]
  const dark = EVENT_TYPE_DARK[data.eventType]

  const el = document.createElement('div')
  el.className = 'pill-marker'
    + (data.isLive ? ' live' : '')
    + (isSelected ? ' selected' : '')
    + (isDotMode ? ' dot-mode' : '')
  el.style.setProperty('--live-color', color)

  if (isSelected) {
    el.style.background = '#F4F2FF'
    el.style.color = '#111118'
  } else {
    el.style.background = color
    el.style.color = dark
  }

  // Icon circle
  const iconDiv = document.createElement('span')
  iconDiv.className = 'pill-icon'
  iconDiv.style.background = isSelected ? color : dark
  iconDiv.innerHTML = ICON_SVG[data.eventType](isSelected ? dark : color)
  el.appendChild(iconDiv)

  // Name
  const nameSpan = document.createElement('span')
  nameSpan.className = 'pill-name'
  nameSpan.textContent = data.name
  el.appendChild(nameSpan)

  // Heart (favorites)
  if (data.isFavorite && !isDotMode) {
    const heart = document.createElement('span')
    heart.className = 'pill-heart'
    heart.style.color = isSelected ? dark : dark
    heart.innerHTML = HEART_SVG
    el.appendChild(heart)
  }

  // Extra count badge
  if (data.extraCount > 0 && !isDotMode) {
    const badge = document.createElement('span')
    badge.className = 'pill-extra'
    badge.textContent = `+${data.extraCount}`
    el.appendChild(badge)
  }

  return el
}

/** Groups venues by coordinates and assigns stack offsets.
 * Venues at the same lat/lng are stacked vertically. */
export function assignStackOffsets(markers: MarkerData[]): MarkerData[] {
  const groups = new Map<string, MarkerData[]>()
  for (const m of markers) {
    const key = `${m.lat.toFixed(6)},${m.lng.toFixed(6)}`
    const group = groups.get(key) ?? []
    group.push(m)
    groups.set(key, group)
  }

  return markers.map(m => {
    const key = `${m.lat.toFixed(6)},${m.lng.toFixed(6)}`
    const group = groups.get(key)!
    const idx = group.indexOf(m)
    return { ...m, stackOffset: idx * 48 }
  })
}

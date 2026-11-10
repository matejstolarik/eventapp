import type { EventType } from '../core/types'
import { EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'

const PIN_PATH = 'M25 61 Q23.2 57.6 20.5 54.5 C10 43 3 36 3 25 A22 22 0 1 1 47 25 C47 36 40 43 29.5 54.5 Q26.8 57.6 25 61 Z'

const ICON_SVG: Record<EventType, (c: string) => string> = {
  concert: (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><g transform="translate(12 12) scale(1.057) translate(-14.12 -11.09)" stroke-width="1.89"><g transform="rotate(45 12 12)"><circle cx="12" cy="5" r="4"/><path d="M8.3 6.5h7.4"/><path d="M9.6 9.2L10.6 17h2.8l1-7.8"/></g><path d="M8.5 15.5C6.6 17.4 6.2 19.6 7.6 20.5c1.4.9 2.9-.5 4.4-2 1.5-1.5 3.6-2 5 0l1 1.5"/></g></svg>`,
  party:   (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h14l-7 8z"/><path d="M12 12v7"/><path d="M8 20h8"/><path d="M15 7l3-4"/></svg>`,
  dj:      (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="11" cy="12" r="5"/><circle cx="11" cy="12" r="1"/><path d="M18 7v6l-3 2"/></svg>`,
  culture: (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"/><path d="M11 10h9v5a4.5 4.5 0 0 1-9 0"/></svg>`,
  other:   (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"/><path d="M11 10h9v5a4.5 4.5 0 0 1-9 0"/></svg>`,
}

const HEART_SVG = `<svg width="12" height="12" viewBox="0 0 24 24" fill="#111118" stroke="#111118" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19.5 12.6L12 20l-7.5-7.4A5 5 0 1 1 12 6a5 5 0 1 1 7.5 6.6z"/></svg>`

export interface MarkerData {
  venueId: string
  name: string
  eventType: EventType
  isFavorite: boolean
  isLive: boolean
  extraCount: number
  lat: number
  lng: number
}

/**
 * Creates a pin element for a MapLibre marker.
 * DOM is built once; state changes are via CSS class toggles (no innerHTML rebuilds).
 * .pin-selected triggers scale(1.22), glow opacity, and bold white name.
 */
export function createPinElement(data: MarkerData, isSelected: boolean): HTMLElement {
  const el = document.createElement('div')
  el.className = 'map-pin'
  el.dataset.venueId = data.venueId
  el.style.cssText = 'filter:drop-shadow(0 8px 6px rgba(0,0,0,0.55)) drop-shadow(0 2px 2px rgba(0,0,0,0.35));cursor:pointer;'

  const color = EVENT_TYPE_COLOR[data.eventType]
  const dark = EVENT_TYPE_DARK[data.eventType]

  // pin-inner: scale transform anchor = bottom center (pin tip)
  const inner = document.createElement('div')
  inner.className = 'pin-inner'

  // Glow — always in DOM, opacity 0→1 via .pin-selected .pin-glow
  const glow = document.createElement('span')
  glow.className = 'pin-glow'
  glow.style.background = `radial-gradient(circle, ${color}88 0%, ${color}33 45%, transparent 70%)`
  inner.appendChild(glow)

  // Live pulse ring
  if (data.isLive) {
    const ring = document.createElement('span')
    ring.className = 'pin-live-ring'
    ring.style.setProperty('--pc', color)
    inner.appendChild(ring)
  }

  // Pin SVG shape
  const pinSvg = document.createElement('div')
  pinSvg.className = 'pin-svg'
  pinSvg.innerHTML = `<svg width="50" height="64" viewBox="0 0 50 64" aria-hidden="true"><path d="${PIN_PATH}" fill="${color}"/></svg>`
  inner.appendChild(pinSvg)

  // Icon circle
  const circle = document.createElement('span')
  circle.className = 'pin-circle'
  circle.style.background = dark
  circle.innerHTML = ICON_SVG[data.eventType](color)
  inner.appendChild(circle)

  // Favorite badge
  if (data.isFavorite) {
    const badge = document.createElement('span')
    badge.className = 'pin-badge-heart'
    badge.innerHTML = HEART_SVG
    inner.appendChild(badge)
  }

  // Extra count badge
  if (data.extraCount > 0) {
    const badge = document.createElement('span')
    badge.className = 'pin-badge-count'
    badge.textContent = `+${data.extraCount}`
    inner.appendChild(badge)
  }

  // Name label — hidden by default; shown at zoom ≥13 via .map-zoom-13 .pin-name
  const name = document.createElement('span')
  name.className = 'pin-name'
  name.textContent = data.name
  inner.appendChild(name)

  el.appendChild(inner)

  if (isSelected) {
    el.classList.add('pin-selected')
    el.style.zIndex = '999'
  }

  return el
}

/** Toggles selected state in-place via CSS class — transitions are in PIN_CSS. */
export function updatePinElement(el: HTMLElement, _data: MarkerData, isSelected: boolean): void {
  const wasSelected = el.classList.contains('pin-selected')
  if (isSelected === wasSelected) return
  el.classList.toggle('pin-selected', isSelected)
  el.style.zIndex = isSelected ? '999' : ''
}

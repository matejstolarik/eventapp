import type { EventType } from '../core/types'
import type { EventIconKey } from '../core/eventType'
import { EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'

const PIN_PATH = 'M25 61 Q23.2 57.6 20.5 54.5 C10 43 3 36 3 25 A22 22 0 1 1 47 25 C47 36 40 43 29.5 54.5 Q26.8 57.6 25 61 Z'

// Single source of truth for pin SVG icons, keyed by EventIconKey.
const ICON_SVG: Record<EventIconKey, (c: string) => string> = {
  // Lucide guitar-electric (ISC), scaled 1.12
  concert: (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><g transform="translate(12 12) scale(1.12) translate(-12 -12)" stroke-width="1.786"><path d="m12.172 11.828 4.242-4.242"/><path d="M16.414 7.586A2 2 0 0017 6.172V5a2 2 0 011.177-1.823L20.59 2.09a1 1 0 011.32 1.32l-1.088 2.412A2 2 0 0119 7h-1a2 2 0 00-1.586.586"/><path d="m6 16 2 2"/><path d="M8.23 9.85a3 3 0 011.28-1.454 1 1 0 011.496.815 4 4 0 003.783 3.783 1 1 0 01.815 1.496 3 3 0 01-1.454 1.28l-.92.38A2 2 0 0012 18a4 4 0 01-4 4 6 6 0 01-6-6 4 4 0 014-4 2 2 0 001.85-1.23z"/></g></svg>`,
  party:   (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h14l-7 8z"/><path d="M12 12v7"/><path d="M8 20h8"/><path d="M15 7l3-4"/></svg>`,
  dj:      (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="11" cy="12" r="5"/><circle cx="11" cy="12" r="1"/><path d="M18 7v6l-3 2"/></svg>`,
  // Lucide clapperboard (ISC)
  film:    (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.296 3.464 3.02 3.956"/><path d="M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3z"/><path d="M3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="m6.18 5.276 3.1 3.899"/></svg>`,
  comedy:  (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6.5" y="1.5" width="11" height="12.5" rx="5.5"/><path d="M6.8 5.5h5.5M6.5 8.3h5.8M6.8 11.1h5.5"/><path d="M12 14v1.5"/><path d="M9.8 15.5h4.4v2.8h-4.4z"/><path d="M12 18.3v4"/></svg>`,
  // Filled silhouette — fill only (exception from outline style)
  dance:   (c) => `<svg width="22" height="22" viewBox="0 0 24 24"><path fill="${c}" d="M6.81 22.4C6.63 22.22 6.66 22.07 7.37 19.35C8.35 15.61 8.08 16.14 9.93 14.14C11.12 12.84 11.19 12.76 11.15 12.54C11.11 12.36 11.23 12.59 9.19 8.78C8.22 6.97 7.4 5.39 7.35 5.27C7.27 5.03 7.28 4.69 7.37 4.51C7.61 4.05 9.06 1.59 9.15 1.5C9.36 1.28 9.63 1.33 10.01 1.66C10.32 1.93 10.31 1.98 9.47 3.34L8.79 4.42L8.79 4.67C8.79 4.95 8.91 5.21 9.47 6.15C10.05 7.13 10.07 7.14 11.57 7.12L12.59 7.11L12.83 6.99C13.02 6.9 13.17 6.76 13.68 6.19C14.83 4.89 14.78 4.97 15.46 3.22C16.09 1.6 16.12 1.57 16.72 1.82C17.09 1.98 17.17 2.07 17.19 2.37C17.21 2.59 17.18 2.68 16.81 3.68C16.17 5.38 16.21 5.31 14.88 7.02C13.82 8.39 13.84 8.36 13.84 8.64C13.84 8.9 13.88 8.99 14.64 10.41C15.62 12.25 15.69 12.64 15.34 14.19C15.23 14.69 13.8 20.41 13.49 21.59C13.27 22.43 13.17 22.5 12.28 22.5C11.72 22.5 11.7 22.5 11.6 22.4C11.46 22.26 11.46 22.22 11.81 20.83C12.37 18.56 12.78 16.42 12.92 15.07C12.99 14.45 12.98 14.36 12.9 14.36C12.82 14.36 10.12 17.05 9.99 17.25C9.78 17.58 9.7 17.86 9.19 19.84C8.66 21.86 8.61 22.03 8.48 22.22C8.31 22.45 8.14 22.5 7.49 22.5C6.93 22.5 6.91 22.5 6.81 22.4ZM11.33 6.19C9.93 5.82 9.5 4.0 10.59 3.03C11.68 2.05 13.39 2.66 13.65 4.11C13.88 5.4 12.62 6.54 11.33 6.19Z"/></svg>`,
  culture: (c) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"/><path d="M11 10h9v5a4.5 4.5 0 0 1-9 0"/></svg>`,
}

const HEART_SVG = `<svg width="12" height="12" viewBox="0 0 24 24" fill="#111118" stroke="#111118" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19.5 12.6L12 20l-7.5-7.4A5 5 0 1 1 12 6a5 5 0 1 1 7.5 6.6z"/></svg>`

/** Inject a shared SVG <defs> block with the pin drop-shadow filter into document.body. */
export function initPinShadows(): void {
  if (document.getElementById('pin-shadow-defs')) return
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.id = 'pin-shadow-defs'
  svg.setAttribute('width', '0')
  svg.setAttribute('height', '0')
  svg.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;pointer-events:none'
  svg.innerHTML = `<defs>
    <filter id="pin-drop-shadow" x="-40%" y="-10%" width="180%" height="150%" color-interpolation-filters="linearRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="blur"/>
      <feOffset in="blur" dx="0" dy="7" result="offset"/>
      <feFlood flood-color="#000" flood-opacity="0.50" result="color"/>
      <feComposite in="color" in2="offset" operator="in" result="shadow"/>
      <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>`
  document.body.appendChild(svg)
}

export interface MarkerData {
  venueId: string
  name: string
  eventType: EventType
  iconKey: EventIconKey
  isFavorite: boolean
  isLive: boolean
  extraCount: number
  lat: number
  lng: number
}

function pinDataKey(data: MarkerData): string {
  return `${data.eventType}|${data.iconKey}|${data.isLive ? 1 : 0}|${data.isFavorite ? 1 : 0}|${data.extraCount}|${data.name}`
}

function buildPinInner(data: MarkerData): HTMLElement {
  const color = EVENT_TYPE_COLOR[data.eventType]
  const dark = EVENT_TYPE_DARK[data.eventType]

  const inner = document.createElement('div')
  inner.className = 'pin-inner'

  const glow = document.createElement('span')
  glow.className = 'pin-glow'
  glow.style.background = `radial-gradient(circle, ${color}88 0%, ${color}33 45%, transparent 70%)`
  inner.appendChild(glow)

  if (data.isLive) {
    const ring = document.createElement('span')
    ring.className = 'pin-live-ring'
    ring.style.setProperty('--pc', color)
    ring.style.borderColor = color
    inner.appendChild(ring)
  }

  const pinSvg = document.createElement('div')
  pinSvg.className = 'pin-svg'
  pinSvg.innerHTML = `<svg width="50" height="64" viewBox="0 0 50 64" aria-hidden="true"><path d="${PIN_PATH}" fill="${color}" filter="url(#pin-drop-shadow)"/></svg>`
  inner.appendChild(pinSvg)

  const circle = document.createElement('span')
  circle.className = 'pin-circle'
  circle.style.background = dark
  circle.innerHTML = ICON_SVG[data.iconKey](color)
  inner.appendChild(circle)

  if (data.isFavorite) {
    const badge = document.createElement('span')
    badge.className = 'pin-badge-heart'
    badge.innerHTML = HEART_SVG
    inner.appendChild(badge)
  }

  if (data.extraCount > 0) {
    const badge = document.createElement('span')
    badge.className = 'pin-badge-count'
    badge.textContent = `+${data.extraCount}`
    inner.appendChild(badge)
  }

  const name = document.createElement('span')
  name.className = 'pin-name'
  name.textContent = data.name
  inner.appendChild(name)

  return inner
}

/**
 * Creates a pin element for a MapLibre marker.
 * Inner content is rebuilt by updatePinElement when data changes.
 */
export function createPinElement(data: MarkerData, isSelected: boolean): HTMLElement {
  const el = document.createElement('div')
  el.className = 'map-pin'
  el.dataset.venueId = data.venueId
  el.dataset.pinKey = pinDataKey(data)
  el.style.cssText = 'cursor:pointer;'
  el.appendChild(buildPinInner(data))

  if (isSelected) {
    el.classList.add('pin-selected')
    el.style.zIndex = '10'
  }

  return el
}

/** Updates pin content and selected state in-place. Rebuilds inner DOM only when data changes. */
export function updatePinElement(el: HTMLElement, data: MarkerData, isSelected: boolean): void {
  const key = pinDataKey(data)
  if (el.dataset.pinKey !== key) {
    el.dataset.pinKey = key
    const old = el.querySelector('.pin-inner')
    const newInner = buildPinInner(data)
    if (old) el.replaceChild(newInner, old)
    else el.appendChild(newInner)
  }
  const wasSelected = el.classList.contains('pin-selected')
  if (isSelected !== wasSelected) {
    el.classList.toggle('pin-selected', isSelected)
    el.style.zIndex = isSelected ? '10' : ''
  }
}

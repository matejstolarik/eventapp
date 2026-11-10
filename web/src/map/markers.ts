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

function buildContent(el: HTMLElement, data: MarkerData, isSelected: boolean, animate: boolean): void {
  const color = EVENT_TYPE_COLOR[data.eventType]
  const dark = EVENT_TYPE_DARK[data.eventType]

  el.innerHTML = ''

  const inner = document.createElement('div')
  inner.className = 'pin-inner'

  if (isSelected) {
    const wrap = document.createElement('div')
    wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;'

    const body = document.createElement('div')
    body.className = 'pin-pill-body'
    body.style.cssText = `display:flex;align-items:center;gap:8px;height:48px;padding:0 16px 0 6px;border-radius:24px;background:${color};white-space:nowrap;position:relative;overflow:hidden;max-width:300px;`

    const circle = document.createElement('span')
    circle.style.cssText = `width:36px;height:36px;border-radius:18px;background:${dark};display:flex;align-items:center;justify-content:center;flex-shrink:0;`
    circle.innerHTML = ICON_SVG[data.eventType](color)
    body.appendChild(circle)

    const nameEl = document.createElement('span')
    nameEl.className = 'pin-pill-name'
    nameEl.style.cssText = `color:${dark};font-size:16px;font-weight:700;font-family:'Outfit',sans-serif;padding-right:4px;flex-shrink:0;`
    nameEl.textContent = data.name
    body.appendChild(nameEl)

    if (data.isFavorite) {
      const badge = document.createElement('span')
      badge.style.cssText = 'position:absolute;top:-2px;right:-4px;width:20px;height:20px;border-radius:10px;background:#F4F2FF;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,0.4);flex-shrink:0;'
      badge.innerHTML = HEART_SVG
      body.appendChild(badge)
    }

    wrap.appendChild(body)

    const tailDiv = document.createElement('div')
    tailDiv.style.cssText = 'margin-top:-1px;line-height:0;'
    tailDiv.innerHTML = `<svg width="22" height="18" viewBox="0 0 22 18" aria-hidden="true"><path d="M0 0 H22 L11 18 Z" fill="${color}"/></svg>`
    wrap.appendChild(tailDiv)

    inner.appendChild(wrap)

    if (animate) {
      body.style.maxWidth = '50px'
      nameEl.style.opacity = '0'
      body.style.transition = 'max-width 220ms ease-out'
      nameEl.style.transition = 'opacity 180ms ease-out 80ms'
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          body.style.maxWidth = '300px'
          nameEl.style.opacity = '1'
        })
      })
    }
  } else {
    const wrap = document.createElement('div')
    wrap.style.cssText = 'position:relative;width:50px;height:64px;'

    if (data.isLive) {
      const ring = document.createElement('span')
      ring.className = 'pin-live-ring'
      ring.style.setProperty('--pc', color)
      ring.style.cssText += 'position:absolute;left:3px;top:3px;width:44px;height:44px;border-radius:22px;'
      ring.style.setProperty('--pc', color)
      wrap.appendChild(ring)
    }

    const pinSvgWrap = document.createElement('div')
    pinSvgWrap.style.cssText = 'position:absolute;inset:0;'
    pinSvgWrap.innerHTML = `<svg width="50" height="64" viewBox="0 0 50 64" aria-hidden="true"><path d="${PIN_PATH}" fill="${color}"/></svg>`
    wrap.appendChild(pinSvgWrap)

    const circle = document.createElement('span')
    circle.style.cssText = `position:absolute;left:7px;top:7px;width:36px;height:36px;border-radius:18px;background:${dark};display:flex;align-items:center;justify-content:center;`
    circle.innerHTML = ICON_SVG[data.eventType](color)
    wrap.appendChild(circle)

    if (data.isFavorite) {
      const badge = document.createElement('span')
      badge.style.cssText = 'position:absolute;top:-2px;right:-4px;width:20px;height:20px;border-radius:10px;background:#F4F2FF;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,0.4);'
      badge.innerHTML = HEART_SVG
      wrap.appendChild(badge)
    }

    if (data.extraCount > 0) {
      const badge = document.createElement('span')
      badge.style.cssText = 'position:absolute;top:-2px;left:-6px;height:20px;min-width:20px;padding:0 5px;box-sizing:border-box;border-radius:10px;background:#111118;color:#F4F2FF;border:1.5px solid #F4F2FF;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;font-family:Outfit,sans-serif;'
      badge.textContent = `+${data.extraCount}`
      wrap.appendChild(badge)
    }

    inner.appendChild(wrap)
  }

  el.appendChild(inner)
}

export function createPinElement(data: MarkerData, isSelected: boolean): HTMLElement {
  const el = document.createElement('div')
  el.className = 'map-pin'
  el.dataset.eventType = data.eventType
  el.dataset.selected = String(isSelected)
  el.style.cssText = 'filter:drop-shadow(0 8px 6px rgba(0,0,0,0.55)) drop-shadow(0 2px 2px rgba(0,0,0,0.35));cursor:pointer;'
  buildContent(el, data, isSelected, false)
  return el
}

/** Updates an existing pin element in-place. Uses dataset so MapLibre classes are never removed. */
export function updatePinElement(el: HTMLElement, data: MarkerData, isSelected: boolean): void {
  const wasSelected = el.dataset.selected === 'true'
  const switchingToSelected = isSelected && !wasSelected

  el.dataset.selected = String(isSelected)
  el.dataset.eventType = data.eventType

  buildContent(el, data, isSelected, switchingToSelected)
}

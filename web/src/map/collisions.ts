import type maplibregl from 'maplibre-gl'
import { decidePairLabel } from './pairLabel'
import { joinDot } from '../core/dot'

export type MarkerEntry = { marker: maplibregl.Marker; el: HTMLElement }

export function checkNameCollisions(
  map: maplibregl.Map,
  markers: Map<string, MarkerEntry>,
  pairs: Map<string, string>,
  combinedLabel: HTMLElement | null,
  combinedMarker: maplibregl.Marker | null,
  getVenueName: (id: string) => string,
): void {
  if (map.getZoom() < 13) return

  if (combinedLabel) combinedLabel.classList.remove('is-active')

  type PinEntry = { venueId: string; el: HTMLElement; nameEl: HTMLElement; priority: number }
  const entries: PinEntry[] = []

  for (const [venueId, { el }] of markers) {
    const nameEl = el.querySelector('.pin-name') as HTMLElement | null
    if (!nameEl) continue
    const isSelected = el.classList.contains('pin-selected')
    const isLive = el.querySelector('.pin-live-ring') !== null
    const isFav = el.querySelector('.pin-badge-heart') !== null
    entries.push({ venueId, el, nameEl, priority: isSelected ? 4 : isLive ? 3 : isFav ? 2 : 1 })
  }

  entries.sort((a, b) => b.priority - a.priority)

  const processedPairs = new Set<string>()
  const occupied: DOMRect[] = []

  for (const { venueId, el, nameEl, priority } of entries) {
    const partnerId = pairs.get(venueId)

    if (partnerId && !processedPairs.has(venueId)) {
      processedPairs.add(venueId)
      processedPairs.add(partnerId)

      const partnerEntry = entries.find(e => e.venueId === partnerId)
      if (!partnerEntry) continue

      const thisSelected = el.classList.contains('pin-selected')
      const partnerSelected = partnerEntry.el.classList.contains('pin-selected')

      if (thisSelected || partnerSelected) {
        const selectedEntry = thisSelected ? { venueId, el, nameEl } : partnerEntry
        const otherEntry = thisSelected ? partnerEntry : { venueId, el, nameEl }
        otherEntry.nameEl.style.visibility = 'hidden'
        selectedEntry.nameEl.style.visibility = ''
        const r = selectedEntry.nameEl.getBoundingClientRect()
        if (r.width > 0) occupied.push(r)
        continue
      }

      nameEl.style.visibility = 'visible'
      partnerEntry.nameEl.style.visibility = 'visible'

      const rA = nameEl.getBoundingClientRect()
      const rB = partnerEntry.nameEl.getBoundingClientRect()
      const markerA = markers.get(venueId)
      const markerB = markers.get(partnerId)

      if (rA.width > 0 && rB.width > 0 && markerA && markerB) {
        const ptA = map.project(markerA.marker.getLngLat())
        const ptB = map.project(markerB.marker.getLngLat())
        const llA = markerA.marker.getLngLat()
        const llB = markerB.marker.getLngLat()
        const decision = decidePairLabel(rA, rB, ptA, ptB, llA, llB)

        if (decision.action === 'combine' && combinedLabel && combinedMarker) {
          nameEl.style.visibility = 'hidden'
          partnerEntry.nameEl.style.visibility = 'hidden'

          const { order, midLng, lowerLat } = decision
          let firstName: string, secondName: string
          if (order === 'west-east') {
            const [westId, eastId] = ptA.x <= ptB.x ? [venueId, partnerId] : [partnerId, venueId]
            firstName = getVenueName(westId)
            secondName = getVenueName(eastId)
          } else {
            const [northId, southId] = ptA.y <= ptB.y ? [venueId, partnerId] : [partnerId, venueId]
            firstName = getVenueName(northId)
            secondName = getVenueName(southId)
          }

          combinedLabel.textContent = joinDot([firstName, secondName])
          combinedLabel.classList.add('is-active')
          combinedMarker.setLngLat([midLng, lowerLat])

          const rC = combinedLabel.getBoundingClientRect()
          if (rC.width > 0) occupied.push(rC)
        } else {
          for (const ne of [nameEl, partnerEntry.nameEl]) {
            ne.style.visibility = 'visible'
            const r = ne.getBoundingClientRect()
            if (r.width > 0) occupied.push(r)
          }
        }
      }
      continue
    }

    if (processedPairs.has(venueId)) continue

    if (priority === 4) {
      nameEl.style.visibility = ''
      const r = nameEl.getBoundingClientRect()
      if (r.width > 0) occupied.push(r)
      continue
    }
    nameEl.style.visibility = 'visible'
    const r = nameEl.getBoundingClientRect()
    if (r.width === 0) continue
    let overlaps = false
    for (const occ of occupied) {
      if (!(r.right < occ.left || r.left > occ.right || r.bottom < occ.top || r.top > occ.bottom)) {
        overlaps = true; break
      }
    }
    if (overlaps) nameEl.style.visibility = 'hidden'
    else occupied.push(r)
  }
}

export function checkPinOverlaps(
  map: maplibregl.Map,
  markers: Map<string, MarkerEntry>,
  pairs: Map<string, string>,
): void {
  type PinInfo = { venueId: string; el: HTMLElement; pt: { x: number; y: number }; lng: number }
  const pins: PinInfo[] = []
  for (const [venueId, { el, marker }] of markers) {
    const ll = marker.getLngLat()
    const pt = map.project([ll.lng, ll.lat])
    pins.push({ venueId, el, pt, lng: ll.lng })
  }

  pairs.clear()
  for (const { el } of pins) {
    el.style.removeProperty('--pin-dx')
  }

  for (let i = 0; i < pins.length; i++) {
    for (let j = i + 1; j < pins.length; j++) {
      const a = pins[i], b = pins[j]
      const dx = a.pt.x - b.pt.x
      const dy = a.pt.y - b.pt.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 200) {
        const west = a.lng <= b.lng ? a : b
        const east = a.lng <= b.lng ? b : a
        pairs.set(west.venueId, east.venueId)
        pairs.set(east.venueId, west.venueId)
        if (dist < 20) {
          const off = west === a ? -8 : 8
          a.el.style.setProperty('--pin-dx', `${off}px`)
          b.el.style.setProperty('--pin-dx', `${-off}px`)
        }
      }
    }
  }
}
